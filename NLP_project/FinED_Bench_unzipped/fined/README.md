## Are Large Language Models Reliable Reviewers? A Benchmark for Error Detection in Financial Documents
<img width="814" height="385" alt="intro" src="https://github.com/user-attachments/assets/bd2264c5-6197-41d0-ba9b-48aab5b85c42" />

## The example of FinED-Bench
<img width="1442" height="963" alt="example" src="https://github.com/user-attachments/assets/2cb0a791-ef1c-4d09-8054-f9e20562c28e" />

## Overview of FinED-Bench
<img width="1234" height="646" alt="taxn" src="https://github.com/user-attachments/assets/71ff5fe3-8fa6-40d2-b1b3-785384ca64ac" />


## Statistic Information about FinED-Bench
<img width="400" height="400" alt="rate" src="https://github.com/user-attachments/assets/492d768f-b2f8-4678-9bfb-da279741a8eb" />


---

## Local copy – added tooling (original files unchanged)

Only Python 3.8+ is required (standard library only).

```bash
python scripts/validate_data.py                 # check schema + dataset statistics
python scripts/evaluate.py --data fined_bench/eval_data.json --baseline   # random baseline
python scripts/evaluate.py --data fined_bench/eval_data.json --pred preds.json
python scripts/build_prompts.py prompts.json    # prompts + references from SFT data
```

`preds.json` is a JSON list aligned with the benchmark file, one item per document:
`{"errors": [{"error_type": "冗余语句", "error_span": ["sentence"]}]}`.
Metrics: micro P/R/F1 at type level and span level.

Note: some entries in the original data have `start_idx = -1` (position not recorded) and a few offsets are slightly misaligned; the data was left as published.

---

## Web app (FastAPI + Uvicorn)

A local browser UI over the existing scripts (they are imported/executed unchanged).

```powershell
pip install -r requirements.txt
python app.py
```

Then open <http://localhost:8000>. Tabs: **Overview** (stats + run `validate_data.py`), **Dataset** (browse documents with error spans highlighted), **Prompts** (`build_prompts.py` output, rebuild/download), **Evaluate** (random baseline, gold sanity check, or your own predictions via `evaluate.py`), **Results** (saved runs in `results/runs.json`).

Files added: `app.py`, `requirements.txt`, `web/` (index.html, style.css, app.js). The CLI commands above still work as before.

**English view:** error types and scene names are shown in English in the UI (display only; the data and scoring still use the original Chinese labels, and uploaded predictions may use either the English or original `error_type` names). The Prompts tab can show the instruction template in English. The benchmark documents, spans and reference answers are the original Chinese text and are not altered.

### Quick start / troubleshooting
1. `pip install -r requirements.txt` (Python 3.8+)
2. `python app.py` -> open the URL it prints (default <http://localhost:8000>; if the port is busy it uses the next free one, or set `PORT=9000`).
3. Health check: `python scripts/validate_data.py` should end with `RESULT: OK`; in the app, Evaluation -> "Gold sanity check" must give 100% everywhere.
4. Benchmark tab: tick **Show original text** to see the Chinese source with error spans highlighted. Language Review: **Load benchmark document** then **Check benchmark match**.


---

## Fixes in this version
- Prediction JSON now accepts English **or** original labels and maps them to the chosen dataset's own labels (previously English labels scored 0% on the Standard benchmark).
- Span matching now needs containment **and** >=50% length coverage, so a whole-document span no longer matches every gold span.
- Evaluation page text no longer claims to be the "original" evaluator.
- Removed unreachable code in the Language Review tab; cleared caches and saved runs.
- **New: Correct document.** In Language Review, the *Correct document* button fixes the detected errors and shows a diff (red = removed, green = added) with Copy / Download. With `ANTHROPIC_API_KEY` set, Claude proposes minimal edits that are applied only on an exact text match; without a key, built-in rules remove repeated sentences and clamp impossible days (e.g. 2025-02-30 -> 2025-02-28). Errors that need facts not in the document are listed under *Needs manual review*; nothing is invented. API: `POST /api/correct`.
