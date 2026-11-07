import pickle
import re
from itertools import product


POSTINGS_PATH = "Dataset/postings.bin"


def load_index(path="Dataset/vocab.pkl"):
    # only the vocabulary {term: [(df, cf), offset, length]} is loaded into memory
    with open(path, "rb") as f:
        return pickle.load(f)


def get_postings(index, term):
    # postings live on disk: read just this term's bytes -> {doc_id: [positions]}
    _, offset, length = index[term]
    with open(POSTINGS_PATH, "rb") as f:
        f.seek(offset)
        return pickle.loads(f.read(length))


# we exclude danda/double-danda as it is punctuation
# 964 and 965
token_pattern = re.compile(r"[a-zA-Z0-9ऀ-ॣ०-ॿ]+")


def tokenize(text: str) -> list[str]:
    # some english words are present so we apply lower case
    return token_pattern.findall(text.lower())


def get_position_lists(postings, tokens, docID):
    return [postings[term][docID] for term in tokens]


def within_window(position_lists, k):
    # k = max allowed gap between each consecutive pair of terms (sorted by
    # position), not the total span - so k=1 matches an exact adjacent phrase
    for combo in product(*position_lists):
        ordered = sorted(combo)
        if all(ordered[i + 1] - ordered[i] <= k for i in range(len(ordered) - 1)):
            return True
    return False


def search(index, phrase_query, k):
    tokens = tokenize(phrase_query)

    # start with the term having the lowest document frequency
    new_tokens = sorted(tokens, key=lambda x: index[x][0][0])

    # fetch each distinct term's postings from disk once
    postings = {t: get_postings(index, t) for t in set(tokens)}

    # intersection of the document ids containing every query term
    sett = set(postings[new_tokens[0]].keys())
    for token in new_tokens[1:]:
        sett &= set(postings[token].keys())

    retrieved_docs = set()
    for docID in sett:
        position_lists = get_position_lists(postings, tokens, docID)
        if within_window(position_lists, k):
            retrieved_docs.add(docID)

    return sorted(retrieved_docs)  # array of matching doc ids


if __name__ == "__main__":
    # load the index once - do NOT reload it inside the query loop
    index = load_index()

    # document texts are only used to display results, not for searching
    import pandas as pd
    docs = pd.read_csv("Dataset/Final_docID.csv").set_index("doc_id")

    MAX_SHOWN = 10  # ponytail: no paging, add when results need browsing

    while True:
        phrase_query = input("\nEnter marathi phrase to search (or 'exit' to quit): ")
        if phrase_query.strip().lower() == "exit":
            break

        k_input = input("Enter k (max gap between words, 1 = exact phrase) [1]: ").strip()
        k = int(k_input) if k_input.isdigit() and int(k_input) > 0 else 1

        # step 1: retrieve the matching doc ids (an array) from the index
        try:
            doc_ids = search(index, phrase_query, k)
        except (KeyError, IndexError):  # a query word is not in the vocabulary / empty query
            doc_ids = []

        # step 2: look the documents up by id and display them
        print(f"\n{len(doc_ids)} documents found")
        for n, doc_id in enumerate(doc_ids[:MAX_SHOWN], 1):
            row = docs.loc[doc_id]
            snippet = " ".join(str(row["Text"]).split())[:300]
            print(f"\n[{n}] ({row['Label']})\n    {snippet}...")
        if len(doc_ids) > MAX_SHOWN:
            print(f"\n... and {len(doc_ids) - MAX_SHOWN} more")
