import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("fined_bench/eval_data.json", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total documents: {len(data)}")

# Sort or filter docs by reasonable length (e.g. 500-2500 chars) so that translation is high quality, complete, and contains diverse errors
candidates = []
for i, d in enumerate(data):
    l = len(d["content"])
    errs = len(d["errors"])
    candidates.append((i, d["scene"], d["title"], l, errs))

# Show docs with various lengths
candidates.sort(key=lambda x: x[3])
print("\nSmallest 10 documents:")
for c in candidates[:10]:
    print(f"Doc {c[0]}: [{c[1]}] {c[2]} (len={c[3]}, errors={c[4]})")

print("\nDocuments around 500-1500 chars:")
mid = [c for c in candidates if 400 <= c[3] <= 1500]
for c in mid[:25]:
    print(f"Doc {c[0]}: [{c[1]}] {c[2]} (len={c[3]}, errors={c[4]})")
