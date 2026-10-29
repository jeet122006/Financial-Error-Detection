#!/usr/bin/env python3
"""Validate FinED-Bench files and print dataset statistics (stdlib only)."""
import json, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = ["fined_bench/eval_data.json", "fined_bench/eval_data_hard.json"]
SFT = ["sft_data/sft_data_w_errors.json", "sft_data/sft_data_wo_errors.json"]

def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)

def main():
    ok = True
    for rel in BENCH:
        data = load(rel)
        need = {"scene", "title", "content", "errors"}
        types = collections.Counter()
        scenes = collections.Counter()
        spans = bad = unknown = 0
        for d in data:
            if not need <= d.keys():
                ok = False
            scenes[d["scene"]] += 1
            for e in d["errors"]:
                types[e["error_type"]] += 1
                for i, s in zip(e["start_idx"], e["error_span"]):
                    spans += 1
                    if i == -1:
                        unknown += 1          # upstream: position not recorded
                    elif d["content"][i:i + len(s)] != s:
                        bad += 1
        print(f"\n== {rel}: {len(data)} documents, {sum(types.values())} errors, {len(types)} error types")
        print("   scenes:", dict(scenes))
        print(f"   spans: {spans} total | {unknown} with start_idx=-1 (upstream) | {bad} misaligned (upstream)")
        if bad:
            print(f"   WARNING: {bad} misaligned (upstream) offsets exist in the original upstream data (not modified)")
    for rel in SFT:
        data = load(rel)
        print(f"\n== {rel}: {len(data)} samples")
        need = {"instruction", "input", "output", "name", "origin_text"}
        if not all(need <= d.keys() for d in data):
            ok = False
    print("\nRESULT:", "OK" if ok else "PROBLEMS FOUND")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
