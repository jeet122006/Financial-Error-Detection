import json

with open("selected_15_raw.json", encoding="utf-8") as f:
    docs = json.load(f)

with open("dump_raw.txt", "w", encoding="utf-8") as out:
    for idx, d in enumerate(docs):
        out.write(f"\n==================== DOC {idx+1} ====================\n")
        out.write(f"Scene: {d['scene']}\n")
        out.write(f"Title: {d['title']}\n")
        out.write(f"Content:\n{d['content']}\n")
        out.write("Errors:\n")
        for e in d['errors']:
            out.write(f"  Type: {e['error_type']}\n")
            for s in e['error_span']:
                out.write(f"  Span: {s}\n")

print("Dumped 15 docs to dump_raw.txt")
