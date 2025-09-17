import faiss
import numpy as np
import pandas as pd
from .embeddings import Embedder
from .searcher import Searcher

class Indexer:
    def __init__(self, dim: int = 384, index_path: str = "./index/faiss_index.bin"):
        self.dim = dim
        self.index_path = index_path
        self.embedder = Embedder()

    def build_index(self, catalog_csv="./data/sample_catalog.csv"):
        df = pd.read_csv(catalog_csv)
        texts = (df['title'].fillna('') + ' . ' + df['short_description'].fillna(''))
        vecs = self.embedder.encode(texts.tolist(), normalize=True)


        index = faiss.IndexFlatIP(self.dim) # use inner product on normalized vectors => cosine
        index.add(vecs)


        # Save index & ids mapping
        faiss.write_index(index, self.index_path)
        df[['id']].to_csv(self.index_path + ".meta.csv", index=False)
        print("Index built and saved to", self.index_path)


if __name__ == "__main__":
    # Step 1: Build the index from sample_catalog.csv
    indexer = Indexer()
    indexer.build_index("./data/sample_catalog.csv")  # Use the dataset we created earlier

    # Step 2: Load the index into Searcher
    searcher = Searcher()

    # Step 3: Run a test query
    query = "blue sneakers under 5000"
    results = searcher.search(query, top_k=5)

    # Step 4: Print results
    print("\n🔎 Search Results for:", query)
    for r in results:
        print(f"ID: {r['id']}, Title: {r['title']}, Price: {r['price']}, Category: {r['category']}, Score: {r['score']:.4f}")
