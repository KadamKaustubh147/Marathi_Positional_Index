# Tokenisation

import re

# we exclude danda/double-danda as it is punctuation
# 964 and 965
token_pattern = re.compile(r"[a-zA-Z0-9\u0900-\u0963\u0966-\u097F]+")


def tokenize(text: str) -> list[str]:
    # some english words are present so we apply lower case
    return token_pattern.findall(text.lower())


import pandas as pd

df = pd.read_csv("data/Final_docID.csv")

# with open("op.txt", "w", encoding="utf-8") as f:
#     f.write(str(tokenize(df["Text"].iloc[0])[:20]))


# Building Positional Index

from collections import defaultdict

index = defaultdict(lambda: defaultdict(list))

# zip gives you a tuple (1, "blabla")
for doc_id, text in zip(df["doc_id"], df["Text"]):
    tokens = tokenize(str(text))
    
    for pos, token in enumerate(tokens):
        index[token][doc_id].append(pos)
        
# document frequency of a term
# len(index[term])

# collection frequency
# sum(len(positions) for position in index[term].values())

# print(index["मारुती"])

# print(len(index["मारुती"]))

# print(sum(len(positions) for positions in index["मारुती"].values()))


# Vocabulary stays in main memory, postings go to disk.
# vocab[term] = [(df, cf), offset, length]  -> pickled, loaded fully into RAM at query time
# postings.bin = each term's {doc_id: [positions]} pickled and written back to back;
#                a query reads only the bytes [offset, offset+length) of the terms it needs
# it is very important we calculate df and cf offline so that we don't take extra time during retrieval

import pickle


def save_index(index, postings_path="data/postings.bin", vocab_path="data/vocab.pkl"):
    vocab = {}
    with open(postings_path, "wb") as f:
        for term, docs in index.items():
            blob = pickle.dumps(dict(docs))  # plain dict: defaultdict with lambda is not picklable
            vocab[term] = [(len(docs), sum(len(p) for p in docs.values())), f.tell(), len(blob)]
            f.write(blob)
    with open(vocab_path, "wb") as f:
        pickle.dump(vocab, f)


save_index(index)
