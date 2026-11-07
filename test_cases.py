# Writes output.txt: 5 test queries + 10 rare terms with their positional index.
import random

from retrieval import get_postings, load_index, search

index = load_index()
out = []

out.append("=== 5 TEST CASES (query, k, matching doc ids) ===")
for q, k in [("चाचणीस", 1), ("करताना १९", 1), ("मिळणार आहे की", 1),
             ("बालगृहात कोरोनाच्या", 3), ("अज्ञातशब्द", 1)]:
    try:
        res = sorted(search(index, q, k))
    except KeyError:  # term not in vocabulary
        res = []
    out.append(f"query={q!r} k={k} -> {len(res)} docs {res[:20]}")

out.append("\n=== 10 RARE TERMS (df=1) : term, (df, cf), {doc_id: [positions]} ===")
rare = [t for t, v in index.items() if v[0][0] == 1 and 2 <= v[0][1] <= 5]
for t in random.Random(42).sample(rare, 10):
    out.append(f"{t} {index[t][0]} {get_postings(index, t)}")

open("output.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
