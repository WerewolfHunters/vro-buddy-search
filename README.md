# 🛍️ AI-Powered E-commerce Search

An **AI-driven product search system** for e-commerce catalogs that supports natural language queries like:

- *"blue sneakers under ₹5000"*
- *"bags between 1000 and 3000"*

The system leverages **semantic search with vector embeddings (SentenceTransformers + FAISS)** and provides **personalized ranking** based on user preferences and past interactions.

---

## 📖 How It Works

1. **Catalog Ingestion**
   - A sample catalog (`data/sample_catalog.csv`) with product details (title, description, category, price, image) is used.
   - An **Indexer** (`search/indexer.py`) generates embeddings for each product and builds a FAISS vector index.

2. **Semantic Search**
   - User query is embedded into the same vector space using SentenceTransformers.
   - FAISS retrieves top-k most relevant items.

3. **Personalization**
   - The system tracks clicked/viewed categories and keywords in-session (`preference/user_prefs.json`).
   - A **ranking module** (`search/ranking.py`) reorders results, boosting items that match user preferences.

4. **Web Interface**
   - A **Streamlit app** (`streamlit_app.py`) provides an interactive search UI:
     - Input search queries
     - View product image, title, description, price, category, and relevance score
     - Results update dynamically based on preferences

---

## 🛠️ Technologies Used

- **[Python 3.11](https://www.python.org/)** – Core programming language
- **[Streamlit](https://streamlit.io/)** – Web UI for interactive search
- **[SentenceTransformers](https://www.sbert.net/)** – Pre-trained embeddings for semantic similarity
- **[FAISS](https://github.com/facebookresearch/faiss)** – Efficient similarity search
- **[Pandas](https://pandas.pydata.org/)** – Data handling for catalog
- **Docker** – Containerized deployment

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/ai-ecommerce-search.git
cd ai-ecommerce-search
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
```

Activate it:
1) Windows (PowerShell):
```bash
venv\Scripts\activate
```
2) Mac/Linux:
```bash
source venv/bin/activate
```

### 3️⃣ Install Requirements
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Build the Index
Before running the app, ensure the FAISS index is created:
```bash
python -m search.indexer
```
This will generate `index/faiss_index.bin`.

### 5️⃣ Run the Streamlit App
```bash
streamlit run streamlit_app.py
```
Open the app in your browser:
👉 http://localhost:8501

---

## 🐳 Running with Docker
### Build Image
```bash
docker build -t shopping-companion:latest .
```
### Run Container
```bash
docker run -p 8501:8501 \
  -v $(pwd)/index:/app/index \
  -v $(pwd)/preference:/app/preference \
  shopping-companion:latest
```
Open in browser: http://localhost:8501

---

## 📂 Project Structure
```bash
.
├── data/
│   └── sample_catalog.csv     # Sample product catalog
├── index/
│   └── faiss_index.bin        # Vector index (generated)
├── preference/
│   └── user_prefs.json        # User preferences (generated)
├── search/
│   ├── indexer.py             # Builds FAISS index
│   ├── searcher.py            # Semantic search logic
│   └── embeddings.py          # Creating embeddings
├── utils/
│   └── ranking.py             # Personalization & ranking
├── streamlit_app.py           # Main Streamlit app
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker setup
└── README.md                  # Project documentation
```

---

## ✅ Features

- 🔍 Semantic Search – Search by natural queries instead of exact keyword matches
- 🖼 Multi-modal display – Image, title, category, price, description
- 🧠 Personalization – Adjust results based on user preferences (categories, keywords)
- ⚡ Fast Retrieval – FAISS index for scalable similarity search
- 🌐 Streamlit UI – Easy-to-use interactive interface

---

## ⚠️ Limitations

- Works on a small static catalog; scaling to millions of items requires distributed indexing.

- Preferences are session-based (stored locally) and don’t support user accounts.

- Embeddings are general-purpose (from SentenceTransformers) and may not fully capture domain-specific product nuances.

- Search supports only text input (no voice/image queries).

---

## 🔮 Future Directions

- 🤖 LLM Integration: Use GPT-powered query understanding for more natural, conversational searches.

- 🧾 Advanced Personalization: Store long-term user histories and apply collaborative filtering.

- 📊 Filters & Facets: Support structured filtering (brand, size, rating, availability).

- 🖼 Multi-Modal Queries: Allow image-based search using CLIP embeddings.

- ☁️ Scalable Deployment: Move to cloud infra with vector DBs like Pinecone, Weaviate, or Milvus.

---

## 📜 License
This project is licensed under the MIT License – see the LICENSE
file for details.
