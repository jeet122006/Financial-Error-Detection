#!/usr/bin/env python3
"""Build model-ready prompts from the SFT files (instruction + input text)."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = []
for rel in ["sft_data/sft_data_w_errors.json", "sft_data/sft_data_wo_errors.json"]:
    for d in json.load(open(os.path.join(ROOT, rel), encoding="utf-8")):
        out.append({"source": rel, "prompt": d["instruction"] + (d.get("input") or ""),
                    "reference": d["output"]})
dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "prompts.json")
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"wrote {len(out)} prompts -> {dst}")
