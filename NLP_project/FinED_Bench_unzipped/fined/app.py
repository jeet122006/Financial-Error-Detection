#!/usr/bin/env python3
"""FinED-Bench local web app (FastAPI + Uvicorn).

Thin web layer over the existing scripts in ./scripts -- the benchmark logic in
validate_data.py, build_prompts.py and evaluate.py is imported / executed as-is.

Run:  python app.py      then open  http://localhost:8000
"""
import collections
import contextlib
import importlib.util
import io
import json
import os
import runpy
import sys
import threading
import time
import uuid
from functools import lru_cache
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(ROOT, "scripts")
WEB = os.path.join(ROOT, "web")
RESULTS_DIR = os.path.join(ROOT, "results")
RUNS_FILE = os.path.join(RESULTS_DIR, "runs.json")
PROMPTS_FILE = os.path.join(RESULTS_DIR, "prompts.json")


# --- load the existing scripts unchanged (by path, no sys.path pollution) -----------------
def _load_script(name):
    spec = importlib.util.spec_from_file_location("fined_" + name, os.path.join(SCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

evaluate_mod = _load_script("evaluate")          # evaluate(), baseline(), gold_items()...
validate_mod = _load_script("validate_data")     # load(), main(), BENCH, SFT

BENCH = {os.path.splitext(os.path.basename(p))[0]: p for p in validate_mod.BENCH}
SFT = {os.path.splitext(os.path.basename(p))[0]: p for p in validate_mod.SFT}

_stdout_lock = threading.Lock()   # scripts print() to stdout; capture one at a time
_runs_lock = threading.Lock()


@lru_cache(maxsize=None)
def _data(rel: str):
    return validate_mod.load(rel)


def _bench(name: str):
    if name not in BENCH:
        raise HTTPException(404, f"unknown dataset '{name}'")
    return _data(BENCH[name])


def _sft(name: str):
    if name not in SFT:
        raise HTTPException(404, f"unknown sft file '{name}'")
    return _data(SFT[name])


app = FastAPI(title="FinED-Bench", version="1.0")

# --- English display labels (display only: the data files and scoring keep the original Chinese) ---
TYPE_EN = {
    "数值缺失": "Missing numeric value", "数值缺失错误": "Missing numeric value",
    "语句缺失错误": "Missing statement", "格式错误": "Format error",
    "时间信息非法": "Invalid time information", "数值单位错误": "Unit error",
    "冗余语句": "Redundant statement", "时间矛盾": "Time contradiction",
    "时间矛盾错误": "Time contradiction", "计算错误": "Calculation error",
    "语义逻辑矛盾": "Semantic / logical contradiction", "数值不一致错误": "Numeric inconsistency",
    "术语误用": "Terminology misuse", "属性值缺失错误": "Missing attribute value",
    "金融要素缺失": "Missing financial element", "法规引用错误": "Incorrect regulation citation",
    "不一致条款": "Inconsistent clause", "模糊语言": "Vague language",
}
SCENE_EN = {
    "招标": "Tender / bidding", "行业研报": "Industry research report", "保险合同": "Insurance contract",
    "个股研报": "Stock research report", "法规": "Laws & regulations", "管理办法": "Administrative measures",
    "公司章程": "Articles of association", "上市公告书": "Listing announcement",
    "债券募集说明书": "Bond prospectus",
}
INPUT_MARK = "【输入文本】：\n"
INSTRUCTION_EN = """You are a financial-document quality checker. Errors in financial documents fall roughly into the following ten categories:
(1) Missing numeric value: a numeric item that should be stated explicitly (quantity, amount, ratio, time, URL, etc.) is omitted, leaving the meaning incomplete or unclear.
(2) Missing statement: a structural or content omission, especially in lists, parallel structures or coordinate sentences, where an expected sentence, component or item is missing, making the meaning incomplete or the wording abrupt.
(3) Format error: a data item in the document does not follow the expected or common format. Typical cases: incomplete URL, postal code that is not 6 digits, email missing "@", phone number with the wrong number of digits.
(4) Invalid time information: a time expression that is unrealistic or non-standard. Typical cases: a day beyond the last day of the month, a month above 12, an hour outside 0-23, a year that does not fit the context.
(5) Unit error: an inappropriate unit for a value. Typical cases: an unreasonable unit (e.g. area in square decimetres, audience counted in "person-times" with a fractional number); a unit that does not match the meaning of the value (e.g. an auditorium renovation budget of 200.00 yuan).
(6) Redundant statement: a passage that repeats content or wording without adding information. Typical cases: identical data; repeated phrasing.
(7) Time contradiction: a description that violates temporal logic. Typical cases: wrong chronological order (e.g. "bid opening earlier than the bid submission deadline"); an unreasonable time expression (e.g. "23 a.m.").
(8) Calculation error: a result of calculation, proportion allocation or growth-rate change that is inconsistent with the correct computation. Typical cases: wrong arithmetic, proportions summing to more than 100%, wrongly computed increases or decreases.
(9) Semantic / logical contradiction: content that clearly conflicts with itself. Typical cases: conclusion inconsistent with the condition; ranking inconsistent with its scope; self-contradictory statements.
(10) Numeric inconsistency: numeric information that should be the same appears differently in different places in one document, usually in key fields such as tender numbers, amounts, quantities and dates.====
Based on the definitions above, decide whether the following text contains one of these error types. Note that each text contains at most one error; choose the most suitable type. If there is an error, return the error type and the erroneous sentences as a JSON list; otherwise return an empty JSON object {}. Example JSON:
```
{
"error": "Missing numeric value",
"sents":["Contact person and phone: Li San."]
}
```
Output requirements: on the first line give your analysis (first locate the erroneous sentence, then decide the error type). On the second line return the error type found and the corresponding erroneous sentences.
====
[Input text]:
"""


def _canon_type(t, gold_types):
    """Map a predicted label (English or original Chinese) onto the label used by the dataset."""
    if not isinstance(t, str):
        return t
    t = t.strip()
    if t in gold_types:
        return t
    want = TYPE_EN.get(t, t).lower()
    for g in gold_types:
        if TYPE_EN.get(g, g).lower() == want:
            return g
    return t


def _normalize_predictions(preds, data):
    gold_types = {e["error_type"] for d in data for e in d["errors"]}
    for p in preds:
        errs = p.get("errors") if isinstance(p, dict) else p
        if isinstance(errs, list):
            for e in errs:
                if isinstance(e, dict):
                    if "error_type" in e:
                        e["error_type"] = _canon_type(e["error_type"], gold_types)
                    # a bare string span would be iterated character by character -> wrap it
                    if isinstance(e.get("error_span"), str):
                        e["error_span"] = [e["error_span"]]
    return preds



# --- error detection for arbitrary pasted text -----------------------------------------------
import calendar
import re
import urllib.request

_SENT_SPLIT = re.compile(r"(?<=[.!?;])\s+|(?<=[。！？；])|\n+")


def _sentences(text):
    return [s.strip() for s in _SENT_SPLIT.split(text) if s and s.strip()]


def rule_check(text):
    """Local heuristic checks (no API key needed). Covers invalid dates/times, percentages, emails, postal codes, and repeated sentences."""
    out = []

    def add(t, sent, why, val=None):
        out.append({
            "error_type": t,
            "sentence": sent,
            "problematic_text": val if val is not None else sent,
            "value": val if val is not None else sent,
            "reason": why
        })

    sents = _sentences(text)
    seen = {}
    for s in sents:
        # 1. Repeated sentences (>= 12 alphanumeric characters)
        key = re.sub(r"\W+", "", s.lower())
        if len(key) >= 12:
            if key in seen:
                add("Redundant statement", s, "This sentence repeats an earlier one.", val=s)
            seen[key] = True

        # 2. Dates with year first: YYYY-MM-DD or YYYY/MM/DD or YYYY.MM.DD or YYYY年MM月DD日
        for m in re.finditer(r"(?<!\d)(\d{4})\s*[-/.年]\s*(\d{1,2})\s*[-/.月]\s*(\d{1,2})(?:日)?(?!\d)", s):
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            raw = m.group(0).strip()
            inv_m = not (1 <= mo <= 12)
            inv_d = False
            if inv_m:
                inv_d = (d < 1 or d > 31)
            else:
                max_d = calendar.monthrange(y, mo)[1]
                inv_d = (d < 1 or d > max_d)
            if inv_m or inv_d:
                reasons = []
                if inv_m:
                    reasons.append(f"month {mo} is not valid")
                if inv_d:
                    if 1 <= mo <= 12:
                        reasons.append(f"day {d} does not exist in {y}-{mo:02d} (month has {calendar.monthrange(y, mo)[1]} days)")
                    else:
                        reasons.append(f"day {d} is not valid")
                add("Invalid time information", s, f"Date '{raw}' is invalid: {'; '.join(reasons)}.", val=raw)

        # 3. Dates with day/month first: DD/MM/YYYY or MM/DD/YYYY or DD-MM-YYYY or MM-DD-YYYY or DD.MM.YYYY
        for m in re.finditer(r"(?<!\d)(\d{1,2})\s*([-/.])\s*(\d{1,2})\s*\2\s*(\d{4})(?!\d)", s):
            p1, delim, p2, y = int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4))
            raw = m.group(0).strip()
            # check if valid as DD/MM/YYYY
            dmy_ok = (1 <= p2 <= 12 and 1 <= p1 <= calendar.monthrange(y, p2)[1])
            # check if valid as MM/DD/YYYY
            mdy_ok = (1 <= p1 <= 12 and 1 <= p2 <= calendar.monthrange(y, p1)[1])
            if not (dmy_ok or mdy_ok):
                reasons = []
                if p1 > 12 and p2 > 12:
                    reasons.append(f"neither {p1} nor {p2} is a valid month")
                elif p1 > 31 or p2 > 31:
                    reasons.append("day or month value exceeds 31")
                elif p2 in (2, 4, 6, 9, 11) or p1 in (2, 4, 6, 9, 11):
                    reasons.append("day value exceeds number of days in that month")
                else:
                    reasons.append("date values are out of range")
                add("Invalid time information", s, f"Date '{raw}' is invalid: {'; '.join(reasons)}.", val=raw)

        # 4. Times: 24-hour clock HH:MM or HH:MM:SS
        for m in re.finditer(r"(?<!\d)(\d{1,2}):(\d{2})(?::(\d{2}))?(?!\d)", s):
            h, mi = int(m.group(1)), int(m.group(2))
            raw = m.group(0).strip()
            sec = int(m.group(3)) if m.group(3) else None
            inv_h = not (0 <= h <= 23)
            inv_mi = not (0 <= mi <= 59)
            inv_s = sec is not None and not (0 <= sec <= 59)
            if inv_h or inv_mi or inv_s:
                add("Invalid time information", s, f"Time '{raw}' is not a valid clock time.", val=raw)

        # 5. 12-hour AM/PM: e.g. 23 a.m.
        for m in re.finditer(r"(?<!\d)(\d{1,2})\s*(a\.?m\.?|p\.?m\.?)", s, re.I):
            h, ap = int(m.group(1)), m.group(2)
            raw = m.group(0).strip()
            if h > 12 or h == 0:
                add("Time contradiction", s, f"'{raw}' is not a valid 12-hour time.", val=raw)

        # 6. Emails
        for val in re.findall(r"(?:e-?mail|邮箱|电子邮件)\s*[:：]?\s*([^\s,;，；]+)", s, re.I):
            val_clean = val.rstrip(".。;")
            if "@" not in val_clean or re.search(r"@\.", val_clean) or val_clean.endswith("@"):
                add("Format error", s, f"Email address '{val_clean}' is not valid.", val=val_clean)

        # 7. Postal codes
        for val in re.findall(r"(?:postal code|post code|zip(?: code)?|邮编|邮政编码)\s*[:：]?\s*(\d+)", s, re.I):
            if len(val) != 6:
                add("Format error", s, f"Postal code '{val}' is not 6 digits.", val=val)

        # 8. Percentages:
        # A) Single percentage exceeding 100%
        single_excess = set()
        for m in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?)\s*%", s):
            val = float(m.group(1))
            raw = m.group(0).strip()
            if val > 100.0:
                single_excess.add(raw)
                add("Calculation error", s, f"Percentage '{raw}' ({val:g}%) exceeds 100%.", val=raw)

        # B) Multiple percentages summing to > 100%
        pcts = [float(x) for x in re.findall(r"(?<![\w.])(\d+(?:\.\d+)?)\s*%", s)]
        if len(pcts) >= 2 and re.search(r"respectively|proportion|share|split|占比|比例|分别", s, re.I):
            if sum(pcts) > 100.5 and not any(p > 100 for p in pcts):
                pct_str = ", ".join(f"{x:g}%" for x in pcts)
                add("Calculation error", s, f"Percentages ({pct_str}) add up to {sum(pcts):g}%, which exceeds 100%.", val=pct_str)

    return out


def _type_en(t):
    return TYPE_EN.get(t, t)


def _call_claude(prompt, max_tokens=1000):
    """Send one prompt to Claude. Returns the reply text, or None when no ANTHROPIC_API_KEY is set."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    body = json.dumps({"model": os.environ.get("FINED_MODEL", "claude-sonnet-5-5"), "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", body, {
        "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["content"][0]["text"]


def llm_check(text):
    """Optional: ask Claude using the benchmark prompt. Needs ANTHROPIC_API_KEY."""
    reply = _call_claude(INSTRUCTION_EN + text)
    if reply is None:
        return None
    found = []
    for blob in re.findall(r"\{[^{}]*\}", reply, re.S):
        try:
            j = json.loads(blob)
        except ValueError:
            continue
        if j.get("error"):
            for sent in j.get("sents") or [""]:
                found.append({"error_type": j["error"], "sentence": sent, "reason": "Flagged by Claude."})
    return {"analysis": reply.strip().split("\n")[0], "findings": found}


# --- document correction ---------------------------------------------------------------------
MANUAL_HINT = {
    "Missing numeric value": "A number is missing; add the correct value from the source document.",
    "Missing statement": "A sentence or item is missing; add it from the source document.",
    "Format error": "Fix the malformed value (URL, e-mail, postal code, phone) using the source document.",
    "Invalid time information": "Replace the impossible date/time with the correct one from the source.",
    "Unit error": "Replace the unit with the one that matches the meaning of the value.",
    "Time contradiction": "Make the dates/times consistent with each other.",
    "Calculation error": "Recompute the figures (shares must not exceed 100%).",
    "Semantic / logical contradiction": "Rewrite so the statements no longer contradict each other.",
    "Numeric inconsistency": "Use the same value everywhere it appears.",
    "Terminology misuse": "Replace the term with the correct financial term.",
    "Missing attribute value": "Add the missing attribute value from the source document.",
    "Missing financial element": "Add the missing financial element from the source document.",
}


def _fix_date(raw):
    """Clamp an impossible day to the last day of its month. Returns None when it cannot be fixed safely."""
    m = re.fullmatch(r"(\d{4})\s*[-/.年]\s*(\d{1,2})\s*[-/.月]\s*(\d{1,2})(日?)", raw)
    if not m:
        return None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not 1 <= mo <= 12:
        return None
    last = calendar.monthrange(y, mo)[1]
    if 1 <= d <= last:
        return None
    return re.sub(r"(\d{1,2})(?=\D*$)", lambda g: f"{last:0{len(g.group(1))}d}", raw)


def rule_correct(text, findings):
    """Safe automatic fixes (no API key): drop repeated sentences, clamp impossible days. Returns (edits, manual)."""
    edits, manual = [], []
    for f in findings:
        t, val = f.get("error_type", ""), f.get("problematic_text") or f.get("sentence") or ""
        if t == "Redundant statement" and val and text.count(val) > 1:
            edits.append({"original": val, "corrected": "", "which": "last", "error_type": t,
                          "reason": "Removed the repeated sentence."})
            continue
        if t == "Invalid time information":
            fixed = _fix_date(val)
            if fixed:
                edits.append({"original": val, "corrected": fixed, "which": "first", "error_type": t,
                              "reason": f"Impossible day replaced by the last day of the month. Please verify '{fixed}'."})
                continue
        manual.append({"error_type": t, "sentence": f.get("sentence", ""), "problematic_text": val,
                       "hint": f.get("reason") or MANUAL_HINT.get(t, "Needs manual review.")})
    return edits, manual


def llm_correct(text, findings):
    """Ask Claude for minimal replacements; they are applied locally by exact substring match. None = no key."""
    listing = "\n".join(f"- [{f.get('error_type')}] {f.get('problematic_text') or f.get('sentence')}" for f in findings)
    prompt = ("You are a financial-document editor. The text below contains the listed errors.\n"
              "Fix ONLY these errors with the smallest possible edits. Do not rewrite anything else. If a fix needs facts "
              "that are not in the document, leave that error out of 'edits' and put it in 'manual'.\n"
              "Reply with JSON only: {\"edits\":[{\"original\":\"exact substring of the text\",\"corrected\":\"replacement, "
              "empty string to delete\",\"error_type\":\"...\",\"reason\":\"short\"}],\"manual\":[{\"error_type\":\"...\","
              "\"sentence\":\"...\",\"hint\":\"what to check\"}]}\n\nERRORS:\n" + listing + "\n\nTEXT:\n" + text)
    reply = _call_claude(prompt, max_tokens=4000)
    if reply is None:
        return None
    m = re.search(r"\{.*\}", reply, re.S)
    j = json.loads(m.group(0)) if m else {}
    edits = [dict(e, which="first") for e in j.get("edits", []) if isinstance(e, dict) and e.get("original")]
    return edits, [x for x in j.get("manual", []) if isinstance(x, dict)]


def apply_edits(text, edits):
    """Apply edits by exact substring match. Returns (corrected_text, segments, applied, skipped)."""
    spans, applied, skipped = [], [], []
    for e in edits:
        o, c = e["original"], e.get("corrected", "")
        pos = text.rfind(o) if e.get("which") == "last" else text.find(o)
        if pos < 0 or any(pos < b and pos + len(o) > a for a, b, _ in spans):
            skipped.append(e)
            continue
        end = pos + len(o)
        if not c:                                  # deleting: also swallow the spaces that followed it
            while end < len(text) and text[end] in " \t":
                end += 1
        spans.append((pos, end, c))
        applied.append(e)
    spans.sort()
    segs, out, p = [], [], 0
    for a, b, c in spans:
        if a > p:
            segs.append({"t": "keep", "text": text[p:a]}); out.append(text[p:a])
        segs.append({"t": "del", "text": text[a:b]})
        if c:
            segs.append({"t": "ins", "text": c})
        out.append(c)
        p = b
    segs.append({"t": "keep", "text": text[p:]}); out.append(text[p:])
    return "".join(out), segs, applied, skipped


class CorrectRequest(BaseModel):
    text: str
    findings: List[dict] = []


@app.post("/api/correct")
def correct(req: CorrectRequest):
    """Correct a document according to its detected errors (given, or detected here)."""
    text = req.text
    if not text.strip():
        raise HTTPException(400, "text is required")
    findings = [f for f in req.findings if isinstance(f, dict)]
    note = ""
    if not findings:
        try:
            res = llm_check(text)
        except Exception as e:
            res, note = None, f"Claude check failed ({type(e).__name__}); used rules. "
        findings = res["findings"] if res is not None else rule_check(text)
    if not findings:
        return {"engine": "none", "corrected": text, "segments": [{"t": "keep", "text": text}],
                "edits": [], "manual": [], "message": "No errors to correct."}
    engine, result = "rules", None
    try:
        result = llm_correct(text, findings)
    except Exception as e:
        note += f"Claude correction failed ({type(e).__name__}); used rules. "
    if result is not None:
        engine = "claude"
    else:
        result = rule_correct(text, findings)
    edits, manual = result
    corrected, segs, applied, skipped = apply_edits(text, edits)
    for e in skipped:   # a replacement that does not match the text exactly is never guessed
        manual.append({"error_type": e.get("error_type", ""), "sentence": e["original"],
                       "hint": "Suggested fix could not be applied automatically: " + (e.get("reason") or "")})
    return {"engine": engine, "corrected": corrected, "segments": segs, "edits": applied, "manual": manual,
            "message": (note + (f"{len(applied)} fix(es) applied, {len(manual)} need manual review." if manual
                                else f"{len(applied)} fix(es) applied.")).strip()}


class AnalyzeRequest(BaseModel):
    dataset: str = "eval_data"
    text: str
    include_text: bool = False


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    """Match complete-language input to the published benchmark without inventing labels."""
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "text is required")
    data = _bench(req.dataset)
    for i, d in enumerate(data):
        if d.get("content", "").strip() == text:
            return {"matched": True, "index": i,
                    "title": d.get("title") or f"Financial Document #{i + 1}",
                    "scene": d.get("scene", ""),
                    "content": d.get("content", "") if req.include_text else "",
                    "source_language": "English",
                    "errors": d.get("errors", [])}
    # not a benchmark document -> actually check the text
    engine, analysis, findings = "rules", "", []
    try:
        res = llm_check(text)
    except Exception as e:  # network / key problems: fall back to rules
        res, analysis = None, f"Claude check failed ({type(e).__name__}); showing rule-based results."
    if res is not None:
        engine, analysis, findings = "claude", res["analysis"], res["findings"]
    else:
        findings = rule_check(text)
    return {"matched": False, "checked": True, "engine": engine, "analysis": analysis, "content": text,
            "findings": findings, "sentences": len(_sentences(text))}


class PromptRequest(BaseModel):
    text: str


@app.post("/api/prompt")
def make_prompt(req: PromptRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "text is required")
    return {"prompt": INSTRUCTION_EN + text}


@app.get("/api/labels")
def labels():
    return {"types": TYPE_EN, "scenes": SCENE_EN}



# --- datasets -----------------------------------------------------------------------------
@app.get("/api/datasets")
def datasets():
    out = []
    for name, rel in BENCH.items():
        d = _data(rel)
        out.append({"name": name, "kind": "benchmark", "file": rel, "documents": len(d),
                    "errors": sum(len(x["errors"]) for x in d)})
    for name, rel in SFT.items():
        out.append({"name": name, "kind": "sft", "file": rel, "documents": len(_data(rel)), "errors": None})
    return out


@app.get("/api/stats/{name}")
def stats(name: str):
    data = _bench(name)
    types, scenes = collections.Counter(), collections.Counter()
    spans = unknown = bad = 0
    for d in data:
        scenes[d["scene"]] += 1
        for e in d["errors"]:
            types[e["error_type"]] += 1
            for i, s in zip(e["start_idx"], e["error_span"]):
                spans += 1
                if i == -1:
                    unknown += 1
                elif d["content"][i:i + len(s)] != s:
                    bad += 1
    return {"name": name, "documents": len(data), "errors": sum(types.values()),
            "types": types.most_common(), "scenes": scenes.most_common(),
            "spans": spans, "unknown_idx": unknown, "misaligned": bad,
            "no_error_docs": sum(1 for d in data if not d["errors"])}


@app.get("/api/documents/{name}")
def documents(name: str, q: str = "", scene: str = "", error_type: str = "",
              offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=200)):
    data = _bench(name)
    rows = []
    for i, d in enumerate(data):
        if scene and d["scene"] != scene:
            continue
        if error_type and not any(e["error_type"] == error_type for e in d["errors"]):
            continue
        if q and q.lower() not in (d["title"] + d["content"]).lower():
            continue
        rows.append({"index": i, "scene": d["scene"],
                     "title": d.get("title") or f"Financial Document #{i + 1}",
                     "length": len(d["content"]), "n_errors": len(d["errors"]),
                     "error_types": sorted({e["error_type"] for e in d["errors"]})})
    return {"total": len(rows), "offset": offset, "items": rows[offset:offset + limit]}


@app.get("/api/documents/{name}/{index}")
def document(name: str, index: int, include_text: bool = True):
    data = _bench(name)
    if not 0 <= index < len(data):
        raise HTTPException(404, "document index out of range")
    d = data[index]
    return {"index": index, "scene": d["scene"],
            "title": d.get("title") or f"Financial Document #{index + 1}",
            "length": len(d.get("content", "")),
            "content": d.get("content", "") if include_text else "",
            "errors": d.get("errors", []),
            "source_language": "English"}


@app.get("/api/sft/{name}")
def sft_items(name: str, offset: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    data = _sft(name)
    return {"total": len(data), "offset": offset, "items": data[offset:offset + limit]}


# --- validation (existing validate_data.main) ----------------------------------------------
@app.post("/api/validate")
def validate():
    buf = io.StringIO()
    with _stdout_lock, contextlib.redirect_stdout(buf):
        code = validate_mod.main()
    return {"ok": code == 0, "exit_code": code, "output": buf.getvalue()}


# --- prompts (existing build_prompts.py, executed as a script) -----------------------------
def _build_prompts():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    buf = io.StringIO()
    argv = sys.argv
    with _stdout_lock, contextlib.redirect_stdout(buf):
        sys.argv = ["build_prompts.py", PROMPTS_FILE]
        try:
            runpy.run_path(os.path.join(SCRIPTS, "build_prompts.py"), run_name="__main__")
        finally:
            sys.argv = argv
    return buf.getvalue().strip()


def _read_prompts():
    if not os.path.exists(PROMPTS_FILE):
        _build_prompts()
    with open(PROMPTS_FILE, encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/prompts/build")
def prompts_build():
    msg = _build_prompts()
    return {"message": msg, "total": len(_read_prompts())}


@app.get("/api/prompts")
def prompts(source: str = "", offset: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    items = []
    for i, p in enumerate(_read_prompts()):
        head, mark, tail = p["prompt"].partition(INPUT_MARK)
        items.append(dict(p, id=i, prompt_en=(INSTRUCTION_EN + tail) if mark else None))
    if source:
        items = [p for p in items if p["source"] == source]
    return {"total": len(items), "offset": offset, "items": items[offset:offset + limit],
            "sources": sorted(SFT_FILES())}


def SFT_FILES():
    return list(SFT.values())


@app.get("/api/prompts/download")
def prompts_download():
    _read_prompts()
    return FileResponse(PROMPTS_FILE, media_type="application/json", filename="prompts.json")


# --- evaluation (existing evaluate.evaluate / evaluate.baseline) ---------------------------
class EvalRequest(BaseModel):
    dataset: str = "eval_data"
    mode: str = "baseline"            # baseline | gold | predictions
    seed: int = 0
    predictions: Optional[Any] = None
    label: Optional[str] = None


def _load_runs():
    if not os.path.exists(RUNS_FILE):
        return []
    try:
        with open(RUNS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def _save_runs(runs):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    tmp = RUNS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(runs, f, ensure_ascii=False, indent=1)
    os.replace(tmp, RUNS_FILE)


def _gold_predictions(data):
    return [{"errors": [{"error_type": e["error_type"], "error_span": list(e["error_span"])}
                        for e in d["errors"]]} for d in data]


@app.post("/api/evaluate")
def run_evaluation(req: EvalRequest):
    data = _bench(req.dataset)
    if req.mode == "baseline":
        preds, default_label = evaluate_mod.baseline(data, req.seed), f"random baseline (seed {req.seed})"
    elif req.mode == "gold":
        preds, default_label = _gold_predictions(data), "gold labels (sanity check)"
    elif req.mode == "predictions":
        preds, default_label = req.predictions, "uploaded predictions"
        if isinstance(preds, str):
            try:
                preds = json.loads(preds)
            except ValueError as e:
                raise HTTPException(400, f"predictions are not valid JSON: {e}")
        if not isinstance(preds, list):
            raise HTTPException(400, "predictions must be a JSON list, one item per document")
        if len(preds) != len(data):
            raise HTTPException(400, f"{len(preds)} predictions vs {len(data)} documents")
    else:
        raise HTTPException(400, "mode must be baseline, gold or predictions")
    try:
        if req.mode == "predictions":
            preds = _normalize_predictions(preds, data)
        res = evaluate_mod.evaluate(data, preds)
    except Exception as e:  # malformed prediction items
        raise HTTPException(400, f"could not score predictions: {type(e).__name__}: {e}")
    run = {"id": uuid.uuid4().hex[:8], "time": time.strftime("%Y-%m-%d %H:%M:%S"),
           "dataset": req.dataset, "documents": len(data), "mode": req.mode,
           "label": (req.label or "").strip() or default_label,
           "metrics": {k: {"precision": p, "recall": r, "f1": f} for k, (p, r, f) in res.items()}}
    with _runs_lock:
        runs = _load_runs()
        runs.insert(0, run)
        _save_runs(runs)
    return run


@app.get("/api/results")
def results():
    return _load_runs()


@app.delete("/api/results/{run_id}")
def delete_result(run_id: str):
    with _runs_lock:
        runs = _load_runs()
        new = [r for r in runs if r["id"] != run_id]
        if len(new) == len(runs):
            raise HTTPException(404, "run not found")
        _save_runs(new)
    return {"deleted": run_id}


@app.delete("/api/results")
def clear_results():
    with _runs_lock:
        _save_runs([])
    return {"cleared": True}


@app.get("/api/results/download")
def results_download():
    return Response(json.dumps(_load_runs(), ensure_ascii=False, indent=1), media_type="application/json",
                    headers={"Content-Disposition": 'attachment; filename="fined_results.json"'})


@app.get("/api/template/{name}")
def prediction_template(name: str):
    """Empty predictions list aligned with the dataset (fill in and upload)."""
    data = _bench(name)
    body = json.dumps([{"errors": []} for _ in data], indent=1)
    return Response(body, media_type="application/json",
                    headers={"Content-Disposition": f'attachment; filename="preds_{name}_template.json"'})


# --- frontend ------------------------------------------------------------------------------
@app.get("/")
def index():
    return FileResponse(os.path.join(WEB, "index.html"))


app.mount("/static", StaticFiles(directory=WEB), name="static")


def _free_port(start):
    import socket
    for port in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:   # nothing listening -> free
                return port
    return start


def main():
    import uvicorn
    port = _free_port(int(os.environ.get("PORT", "8000")))
    print(f"FinED-Bench running at http://localhost:{port}  (Ctrl+C to stop)")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
