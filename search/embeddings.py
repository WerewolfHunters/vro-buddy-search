from sentence_transformers import SentenceTransformer
import numpy as np


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts, normalize=True):
        # Ensure input is always a list
        if isinstance(texts, str):
            texts = [texts]

        vecs = self.model.encode(texts, show_progress_bar=False)
        vecs = np.array(vecs, dtype="float32")

        if normalize:
            norms = np.linalg.norm(vecs, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            vecs = vecs / norms

        return vecs


if __name__ == "__main__":
    embd = Embedder()
    vecs = embd.encode("hello, my name is awwab")
    print(vecs.shape)   # (1, 384)
    print(vecs)