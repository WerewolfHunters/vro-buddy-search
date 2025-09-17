import pandas as pd
import numpy as np
import faiss
from .embeddings import Embedder
import re


class Searcher:
    def __init__(self, catalog_csv='./data/sample_catalog.csv', index_path='./index/faiss_index.bin'):
        self.catalog = pd.read_csv(catalog_csv)
        self.index_path = index_path
        self.embedder = Embedder()
        # load index
        try:
            self.index = faiss.read_index(self.index_path)
        except Exception:
            self.index = None

    def parse_price_from_query(self, query: str):
        # Very simple parser for phrases like 'under ₹5000' or 'below 5000' or 'under 5000'
        match = re.search(r"under\s*[₹]?(\d{2,6})", query, flags=re.I)
        if match:
            return None, int(match.group(1))
        match = re.search(r"over\s*[₹]?(\d{2,6})|above\s*[₹]?(\d{2,6})", query, flags=re.I)
        if match:
            g = match.groups()
            for x in g:
                if x:
                    return int(x), None
        return None, None
    
    def search(self, query: str, top_k=50, category_filter=None, price_min=0, price_max=10**9):
        if not query:
            # fallback: return top products by price or random sample
            subset = self.catalog.copy()
            subset = subset[(subset['price'] >= price_min) & (subset['price'] <= price_max)]
            if category_filter:
                subset = subset[subset['category'].isin(category_filter)]
            records = subset.head(top_k).to_dict('records')
            return [{'id': r['id'], 'score': 0.0, 'title': r['title'], 'short_description': r['short_description'], 'price': r['price'], 'category': r['category'], 'image_url': r['image_url']} for r in records]
        
        low, high = self.parse_price_from_query(query)
        if low is not None:
            price_min = max(price_min, low)
        if high is not None:
            price_max = min(price_max, high)

        vec = self.embedder.encode([query], normalize=True)
        if self.index is None:
            raise RuntimeError("FAISS index not found. Build it first using Indexer.build_index()")
        
        D, I = self.index.search(vec, top_k)
        ids = I[0]
        scores = D[0]

        results = []
        for idx, score in zip(ids, scores):
            # map index row to catalog row
            try:
                row = self.catalog.iloc[idx]
            except Exception:
                continue
            # apply filters
            if not (price_min <= row['price'] <= price_max):
                continue
            if category_filter and row['category'] not in category_filter:
                continue
            results.append({
            'id': int(row['id']),
            'score': float(score),
            'title': row['title'],
            'short_description': row['short_description'],
            'brand': row.get('brand', ''),
            'color': row.get('color', ''),
            'rating': float(row.get('rating', 0.0)),
            'price': float(row['price']),
            'category': row['category'],
            'image_url': row['image_url']
            })
        return results