import pickle
import re
import time
from itertools import product


def load_index(path="Dataset/positional_index.pkl"):
    with open(path, "rb") as f:
        return pickle.load(f)


# we exclude danda/double-danda as it is punctuation
# 964 and 965
token_pattern = re.compile(r"[a-zA-Z0-9ऀ-ॣ०-ॿ]+")


def tokenize(text: str) -> list[str]:
    # some english words are present so we apply lower case
    return token_pattern.findall(text.lower())


def get_position_lists(index, tokens, docID):
    return [index[term][1][docID] for term in tokens]


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

    # intersection of the document ids containing every query term
    sett = set(index[new_tokens[0]][1].keys())
    for token in new_tokens[1:]:
        sett &= set(index[token][1].keys())

    retrieved_docs = set()
    for docID in sett:
        position_lists = get_position_lists(index, tokens, docID)
        if within_window(position_lists, k):
            retrieved_docs.add(docID)

    return retrieved_docs


if __name__ == "__main__":
    # load the index once - do NOT reload it inside the query loop
    start = time.perf_counter()
    index = load_index()
    end = time.perf_counter()
    print(f"{end - start} index load time")

    while True:
        phrase_query = input("Enter marathi phrase to search (or 'exit' to quit): ")
        if phrase_query.strip().lower() == "exit":
            break

        start = time.perf_counter()
        retrieved_docs = search(index, phrase_query, k=1)
        end = time.perf_counter()

        print(sorted(retrieved_docs))
        print(f"{end - start} query time")
