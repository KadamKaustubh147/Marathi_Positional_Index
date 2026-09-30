# Tokenisation

import re

# we exclude danda/double-danda as it is punctuation
# 964 and 965
token_pattern = re.compile(r"[a-zA-Z0-9\u0900-\u0963\u0966-\u097F]+")


def tokenize(text: str) -> list[str]:
    # some english words are present so we apply lower case
    return token_pattern.findall(text.lower())


import pandas as pd

df = pd.read_csv("Dataset/Final_docID.csv")

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


# pickling and saving the index

# defaultdict with lambda is not pickleable
# syntax
# [(df,cf), dictionary]

# it is very important we calculate df and cf offline so that we don't take extra time during retrieval
plain_idx = {term: [(len(index[term]), sum(len(positions) for positions in index[term].values()) ), dict(docs)] for term, docs in index.items()}

# print(plain_idx["मारुती"])

import pickle

def save_index(index, path="Dataset/positional_index.pkl"):
    with open(path, "wb") as f:
        pickle.dump(index,f)


save_index(plain_idx)