import random
import statistics
import time

import pandas as pd

from retrieval import load_index, search, tokenize

SAMPLE_SIZE = 1000
PHRASE_SAMPLE_SIZE = 200
SEED = 42
CSV_PATH = "Dataset/Final_docID.csv"


def index_stats(index):
    num_terms = len(index)
    total_occurrences = sum(v[0][1] for v in index.values())

    doc_ids = set()
    for v in index.values():
        doc_ids.update(v[1].keys())
    num_docs = len(doc_ids)

    avg_doc_len = total_occurrences / num_docs

    return {
        "num_docs": num_docs,
        "num_unique_terms": num_terms,
        "total_occurrences": total_occurrences,
        "avg_doc_len": avg_doc_len,
    }


def query_time_stats(index, sample_size=SAMPLE_SIZE, seed=SEED):
    random.seed(seed)
    sample_words = random.sample(list(index.keys()), sample_size)

    times = []
    for word in sample_words:
        start = time.perf_counter()
        search(index, word, k=1)
        end = time.perf_counter()
        times.append(end - start)

    return {
        "mean_sec": statistics.mean(times),
        "std_sec": statistics.stdev(times),
        "min_sec": min(times),
        "max_sec": max(times),
    }


def sample_phrases(csv_path=CSV_PATH, n=PHRASE_SAMPLE_SIZE, phrase_len=3, seed=SEED):
    """Pick real n-word windows from the corpus so terms are guaranteed to co-occur."""
    random.seed(seed)
    texts = pd.read_csv(csv_path)["Text"].tolist()

    phrases = []
    attempts = 0
    while len(phrases) < n and attempts < n * 20:
        attempts += 1
        tokens = tokenize(str(random.choice(texts)))
        if len(tokens) < phrase_len:
            continue
        start = random.randint(0, len(tokens) - phrase_len)
        phrases.append(" ".join(tokens[start:start + phrase_len]))

    return phrases


def phrase_query_time_stats(index, phrases, k):
    times = []
    for phrase in phrases:
        start = time.perf_counter()
        search(index, phrase, k)
        end = time.perf_counter()
        times.append(end - start)

    return {
        "mean_sec": statistics.mean(times),
        "std_sec": statistics.stdev(times),
        "min_sec": min(times),
        "max_sec": max(times),
    }


if __name__ == "__main__":
    index = load_index()

    print("--- index stats ---")
    for k, v in index_stats(index).items():
        print(f"{k}: {v}")

    print(f"\n--- single-term query time over {SAMPLE_SIZE} sampled terms ---")
    for k, v in query_time_stats(index).items():
        print(f"{k}: {v}")

    for phrase_len in (2, 3):
        phrases = sample_phrases(phrase_len=phrase_len)
        print(f"\n--- {phrase_len}-word phrase query time over {len(phrases)} sampled phrases (k=1) ---")
        for k, v in phrase_query_time_stats(index, phrases, k=1).items():
            print(f"{k}: {v}")
