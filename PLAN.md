# Positional Index — Plan

Dataset: `Dataset/Final_docID.csv` (27,560 Marathi articles; columns `Text`, `Label`, `doc_id`)

## 1. Tokenizer — done
- `tokenize(text) -> list[str]` in `indexing.py`
- Regex over Devanagari block + latin/digits, excluding danda/double-danda (`।`, `॥`) since those are punctuation, not word chars
- Open decision: lowercase or not (affects mixed English terms like "CNG")

## 2. Build the positional index
- Loop over CSV rows: `doc_id`, `Text`
- Tokenize each `Text`, enumerate to get `(position, term)`
- Store as `index[term][doc_id] = [positions]`
- Use `defaultdict(lambda: defaultdict(list))` while building

## 3. Sanity-check
- Pick a common term, print its postings, manually verify positions against raw text of one doc_id

## 4. Cache to disk
- Convert nested defaultdict -> plain dict (lambdas aren't picklable)
- `pickle.dump` to save, `pickle.load` to reload
- `load_or_build_index()`: load from `.pkl` if present, else build from CSV and save

## 5. Phrase query
- Tokenize the query the same way as documents
- Intersect doc_ids across all query terms' postings
- For each candidate doc, check consecutive positions in order

## 6. Proximity query
- Same setup as phrase query, relax "consecutive" to "within k" (`abs(pos1 - pos2) <= k`)
- Use two-pointer merge over the two sorted position lists per doc (avoid nested-loop comparison)
- Decide: order-sensitive or symmetric?

## 7. Stop words — decision
- Do NOT strip stop words before indexing — breaks position accuracy needed for phrase/proximity
- Optional: keep a stop word list for filtering single-term/ranked queries only, separate from the index itself

## 8. Stretch: biword index for frequent terms
- Only after 2–6 work end-to-end
- Compute term frequency from the finished index
- Pick top-N frequent terms, build `{(word1, word2): set(doc_ids)}` for consecutive frequent-word pairs
- Use as fast path for phrase queries; fall back to positional intersection otherwise
