import pandas as pd
from fastapi import FastAPI
from fastapi.responses import FileResponse

from retrieval import load_index, search

app = FastAPI()
index = load_index()  # vocabulary in RAM; postings are read from disk per query
docs = pd.read_csv("Dataset/Final_docID.csv").set_index("doc_id")  # only for display

MAX_SHOWN = 20


@app.get("/")
def page():
    return FileResponse("index.html")


@app.get("/search")
def do_search(q: str, k: int = 1):
    try:
        ids = sorted(search(index, q, max(k, 1)))
    except (KeyError, IndexError):  # unknown word / empty query
        ids = []
    return {
        "total": len(ids),
        "results": [{"label": docs.loc[i, "Label"], "text": str(docs.loc[i, "Text"])} for i in ids[:MAX_SHOWN]],
    }
