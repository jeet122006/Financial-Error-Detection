import json

with open("fined_bench/eval_data.json", encoding="utf-8") as f:
    data = json.load(f)

selected_indices = [30, 55, 66, 95, 876, 815, 715, 814, 367, 423, 513, 621, 560, 672, 220]

selected_docs = [data[i] for i in selected_indices]
with open("selected_15_raw.json", "w", encoding="utf-8") as f:
    json.dump(selected_docs, f, ensure_ascii=False, indent=2)

print(f"Saved {len(selected_docs)} documents to selected_15_raw.json")
