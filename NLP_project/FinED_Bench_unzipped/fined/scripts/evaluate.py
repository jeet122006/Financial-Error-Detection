#!/usr/bin/env python3
"""Score predictions against FinED-Bench (stdlib only).

Predictions file: JSON list aligned with the benchmark file, one item per
document:  {"errors": [{"error_type": "...", "error_span": ["sentence", ...]}]}
(an empty list / {} means "no error found").

Metrics (micro-averaged over errors):
  type-level  : predicted error_type matches a gold type in that document
  span-level  : predicted span matches a gold span of the same type (containment + >=50% length coverage)
Usage:
  python scripts/evaluate.py --data fined_bench/eval_data.json --pred preds.json
  python scripts/evaluate.py --data fined_bench/eval_data.json --baseline
"""
import argparse, json, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def norm(s): return "".join(s.split())

MIN_COVERAGE = 0.5   # shorter span must cover >= 50% of the longer one

def overlap(a, b):
    """Spans match if one contains the other AND they are of comparable length.
    (Plain containment let a whole-document prediction match every gold span.)"""
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    short, long_ = (a, b) if len(a) <= len(b) else (b, a)
    return short in long_ and len(short) / len(long_) >= MIN_COVERAGE

def gold_items(doc):
    return [(e["error_type"], s) for e in doc["errors"] for s in e["error_span"]]

def pred_items(p):
    if not p: return []
    errs = p.get("errors", []) if isinstance(p, dict) else p
    return [(e.get("error_type", ""), s) for e in errs for s in e.get("error_span", [])]

def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f

def evaluate(data, preds):
    t_tp = t_fp = t_fn = s_tp = s_fp = s_fn = 0
    for doc, pr in zip(data, preds):
        gold, pred = gold_items(doc), pred_items(pr)
        used = set()
        for pt, ps in pred:                       # span-level
            hit = next((i for i, (gt, gs) in enumerate(gold)
                        if i not in used and gt == pt and overlap(gs, ps)), None)
            if hit is None: s_fp += 1
            else: used.add(hit); s_tp += 1
        s_fn += len(gold) - len(used)
        gtypes = [g[0] for g in gold]             # type-level (multiset)
        for pt in [p[0] for p in pred]:
            if pt in gtypes: gtypes.remove(pt); t_tp += 1
            else: t_fp += 1
        t_fn += len(gtypes)
    return {"type_level": prf(t_tp, t_fp, t_fn), "span_level": prf(s_tp, s_fp, s_fn)}

def baseline(data, seed=0):
    """Random-guess baseline: sentence-level guess with a random type."""
    rnd = random.Random(seed)
    types = sorted({e["error_type"] for d in data for e in d["errors"]})
    out = []
    for d in data:
        sents = [s for s in d["content"].replace("\n", "。").split("。") if s.strip()]
        out.append({"errors": [{"error_type": rnd.choice(types),
                                "error_span": [rnd.choice(sents)]}]})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="fined_bench/eval_data.json")
    ap.add_argument("--pred")
    ap.add_argument("--baseline", action="store_true")
    a = ap.parse_args()
    path = a.data if os.path.isabs(a.data) else os.path.join(ROOT, a.data)
    data = json.load(open(path, encoding="utf-8"))
    if a.baseline:
        preds = baseline(data)
    elif a.pred:
        preds = json.load(open(a.pred, encoding="utf-8"))
        if len(preds) != len(data):
            sys.exit(f"ERROR: {len(preds)} predictions vs {len(data)} documents")
    else:
        sys.exit("give --pred FILE or --baseline")
    for k, (p, r, f) in evaluate(data, preds).items():
        print(f"{k:11s}  P={p:.4f}  R={r:.4f}  F1={f:.4f}")

if __name__ == "__main__":
    main()
