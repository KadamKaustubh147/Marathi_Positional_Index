# Marathi Positional Index

A positional inverted index over a Marathi news-article dataset. It supports
phrase and proximity queries from a command line and from a small web page.

Code: https://github.com/KadamKaustubh147/Marathi_Positional_Index

**Key design point:** the *vocabulary* is held in main memory; the entire
*postings list* is stored on disk (`data/postings.bin`) and only the bytes
for the queried terms are read at query time.

---

## 1. Setup

### Requirements
- Python **3.14** or newer (set in `pyproject.toml`)
- Packages: `pandas`, `fastapi`, `uvicorn`

### Install
With [uv](https://docs.astral.sh/uv/) (recommended):
```
uv sync
```
Or with pip:
```
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pandas fastapi uvicorn
```
(With pip, run the commands below as `python <script>` instead of `uv run python <script>`.)

### Get the data
1. Download the preprocessed dataset `Final_docID.csv` (27,560 Marathi news articles;
   columns `Text`, `Label`, `doc_id`) from Google Drive: _add Drive link here_
   (original source: https://github.com/l3cube-pune/MarathiNLP)
2. Create a folder `data/` in the project root and put the file at `data/Final_docID.csv`.

### Build and run (in this order)
```
uv run python indexing.py      # 1. builds the index (~35 s): data/postings.bin + data/vocab.pkl
uv run python retrieval.py     # 2a. interactive command-line search
uv run uvicorn server:app      # 2b. web UI: open http://localhost:8000
uv run python test_cases.py    # writes output.txt (5 test queries + 10 rare terms)
uv run python stats.py         # index statistics
```
Step 1 is needed only once.

---

## 2. Using the search

**Command line** (`retrieval.py`): it asks for a phrase, then for `k`
(press Enter for `k = 1`). Results show the document label and the start of its text.

**Web page** (`server.py`): type a phrase, set `k`, press Search. The first 20
matching documents are shown with their label and text. The API behind it is
`GET /search?q=<phrase>&k=<k>`.

**What `k` means:** the maximum gap between consecutive query words.
- `k = 1`: the words must be adjacent (exact phrase)
- `k = 3`: the words must each be within 3 positions of each other

Example: `बालगृहात कोरोनाच्या` with `k = 3` finds the document where the two words are
2 positions apart.

---

## 3. How it works

### Index structure
| File | Where it lives | Content |
|---|---|---|
| `data/vocab.pkl` | loaded into **RAM** at startup | `vocab[term] = [(df, cf), offset, length]` |
| `data/postings.bin` | stays on **disk** (~44 MB) | each term's `{doc_id: [positions]}`, pickled, written back to back |

`df` (document frequency) and `cf` (collection frequency) are precomputed at build
time, so they need no disk access.

### Tokenizer
Regex over Latin letters/digits and the Devanagari block, excluding the danda `।`
and double-danda `॥` (punctuation). Text is lower-cased because some English words
occur. Positions are 0-based token positions within a document. Stop words are
**not** removed, since removing them would shift positions.

### Query flow (`search()`)
1. Tokenize the query.
2. Order the terms by document frequency (rarest first).
3. Read each distinct term's postings from `postings.bin` (seek to `offset`, read `length` bytes).
4. Intersect the document-id sets.
5. For each remaining document, check that the terms' positions fit within window `k`.

### Modules
| File | Description |
|---|---|
| `indexing.py` | tokenizer; builds `term -> {doc_id: [positions]}` in memory, then `save_index()` writes `postings.bin` and `vocab.pkl` |
| `retrieval.py` | `load_index()` (vocabulary only), `get_postings()` (one term from disk), `search()`, and the interactive loop |
| `server.py` | FastAPI app: loads the vocabulary once and serves `/` and `/search` |
| `index.html` | minimal search page that calls `/search` |
| `stats.py` | index statistics and query-time measurements |
| `test_cases.py` | 5 test queries + 10 rare terms with their positional index -> `output.txt` |

---

## 4. Index statistics

| Metric | Value |
|---|---|
| Documents | 27,560 |
| Unique terms (vocabulary size) | 274,975 |
| Total term occurrences (collection size) | 6,305,723 |
| Average document length (terms/doc) | 228.8 |
| Vocabulary in RAM | ~90 MB (process memory grows 12 MB -> 102 MB on load) |
| `postings.bin` on disk | 44 MB |

## 5. Tests (`output.txt`)

`test_cases.py` runs 5 test queries (single term, 2-word phrase, 3-word phrase,
proximity with `k = 3`, and a term that is not in the corpus) and prints 10 rare terms
(`df = 1`, picked with a fixed random seed) together with their positional index,
`term (df, cf) {doc_id: [positions]}`. Two of the rare terms were also checked by
hand against the raw text.
