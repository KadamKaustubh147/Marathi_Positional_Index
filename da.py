import pandas as pd

df = pd.read_csv("./Dataset/Final.csv")

print(df.head(5))

df["doc_id"] = df.index

df.to_csv("./Dataset/Final_docID.csv", index=False)

