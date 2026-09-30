# Marathi Positional Index

A positional inverted index over a Marathi news-article dataset, supporting
phrase and proximity queries.

## Dataset

- Source: `Dataset/Final_docID.csv`
- 27,560 documents (`Text`, `Label`, `doc_id` columns)
- Dataset link: https://github.com/l3cube-pune/MarathiNLP

## Index

- Tokenizer: matches Devanagari letters/marks (`ऀ-ॿ`, excluding
  danda/double-danda punctuation `।`/`॥`) plus latin letters and
  digits; lowercased for mixed English terms.
- Structure: `index[term] = [(df, cf), {doc_id: [positions]}]`
- Cached to `Dataset/positional_index.pkl` via `pickle` so it's built once
  and loaded on subsequent runs.

## Index stats

| Metric | Value |
|---|---|
| Documents | 27,560 |
| Unique terms (vocabulary size) | 274,975 |
| Total term occurrences (collection size) | 6,305,723 |
| Average document length (terms/doc) | 228.8 |

## Query performance

Sampled 1,000 random terms from the vocabulary and ran a single-term query
through the full `search()` pipeline (tokenize -> intersect postings ->
proximity check) for each, using `time.perf_counter()`.

| Metric | Value |
|---|---|
| Mean query time | 40.2 µs |
| Std deviation | 489.4 µs |
| Min | 2.3 µs |
| Max | 14.9 ms |

Note the high std relative to the mean: most queries resolve in
microseconds, but a handful of very high-document-frequency terms (large
posting lists to intersect) pull the tail out to the millisecond range.

## Usage

```
uv run python indexing.py    # builds and caches the positional index
uv run python retrieval.py   # interactive phrase/proximity search
```
# Marathi_Positional_Index
