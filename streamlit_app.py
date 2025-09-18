import streamlit as st
import json
import os
import pandas as pd
from search.indexer import Indexer
from search.searcher import Searcher
from utils.ranking import apply_personalization

# -----------------------
# Helper functions for persistence
# -----------------------
PREF_FILE = "preference/user_prefs.json"

def load_prefs():
    """Load saved preferences from JSON file."""
    if os.path.exists(PREF_FILE):
        with open(PREF_FILE, "r") as f:
            return json.load(f).get("click_history", [])
    return []

def save_prefs(click_history):
    """Save preferences to JSON file."""
    with open(PREF_FILE, "w") as f:
        json.dump({"click_history": click_history}, f)


# -----------------------
# Streamlit App
# -----------------------
st.set_page_config(page_title="🛍️ AI-Powered E-commerce Search", layout="wide")

st.title("🛍️ AI-Powered E-commerce Search")
st.write("Type your query below (e.g., *blue sneakers under 5000*, *bags between 1000 and 3000*)")

# Initialize Searcher
@st.cache_resource
def load_searcher():
    return Searcher(catalog_csv="./data/sample_catalog.csv", index_path="./index/faiss_index.bin")

searcher = load_searcher()

# Initialize personalization session
if "click_history" not in st.session_state:
    st.session_state.click_history = load_prefs()  # ✅ load from file


# Sidebar: personalization reset
st.sidebar.header("⚙️ Personalization")
if st.sidebar.button("Reset personalization"):
    st.session_state.click_history = []
    save_prefs([])  # ✅ clear file


# Search input
query = st.text_input("Enter your search query:")

# -----------------------
# If query is empty, use preferences to recommend items
# -----------------------
if not query and st.session_state.click_history:
    clicked = st.session_state.click_history
    df_clicked = searcher.catalog[searcher.catalog['id'].isin(clicked)]

    if not df_clicked.empty:
        # Extract preferred categories (most clicked ones)
        pref_counts = df_clicked['category'].value_counts()
        top_categories = pref_counts.index.tolist()

        st.subheader("✨ Recommended for You (based on your preferences)")

        # Show top items from preferred categories
        for cat in top_categories:
            cat_items = searcher.catalog[searcher.catalog['category'] == cat].head(5)

            if not cat_items.empty:
                st.markdown(f"#### 🏷️ {cat}")
                for _, r in cat_items.iterrows():
                    with st.container():
                        cols = st.columns([1, 3])
                        with cols[0]:
                            if r.get("image_url"):
                                st.image(r["image_url"], use_column_width=True)
                            else:
                                st.image("https://via.placeholder.com/150", use_column_width=True)

                        with cols[1]:
                            st.markdown(f"### {r['title']}")
                            st.write(r['short_description'])
                            st.write(f"**Category:** {r['category']}")
                            st.write(f"**Price:** ₹{r['price']:.2f}")

                            if st.button(f"👍 Interested", key=f"pref_{r['id']}"):
                                st.session_state.click_history.append(r['id'])
                                save_prefs(st.session_state.click_history)
                                st.success("Added to your preferences!")

                st.markdown("---")


# -----------------------
# If user types query -> search
# -----------------------
elif query:
    results = searcher.search(query, top_k=50)

    if not results:
        st.warning("No results found. Try a different query.")
    else:
        ranked = apply_personalization(
            results,
            click_history_ids=st.session_state.click_history,
            catalog_df=searcher.catalog
        )

        df_results = pd.DataFrame(ranked)

        # -----------------------
        # Filters Section (show only after search)
        # -----------------------
        st.markdown("### 🔧 Filters")

        col1, col2, col3 = st.columns(3)

        # Price sort
        with col1:
            sort_option = st.selectbox(
                "Sort by Price",
                ["None", "Low → High", "High → Low"]
            )

        # Brand filter
        with col2:
            brands = ["All"] + sorted(df_results["brand"].dropna().unique().tolist())
            brand_filter = st.selectbox("Filter by Brand", brands)

        # Category filter
        with col3:
            categories = ["All"] + sorted(df_results["category"].dropna().unique().tolist())
            category_filter = st.selectbox("Filter by Category", categories)

        # Apply filters
        filtered_df = df_results.copy()

        if brand_filter != "All":
            filtered_df = filtered_df[filtered_df["brand"] == brand_filter]

        if category_filter != "All":
            filtered_df = filtered_df[filtered_df["category"] == category_filter]

        if sort_option == "Low → High":
            filtered_df = filtered_df.sort_values(by="price", ascending=True)
        elif sort_option == "High → Low":
            filtered_df = filtered_df.sort_values(by="price", ascending=False)

        # -----------------------
        # Display results
        # -----------------------
        st.subheader(f"🔎 Search Results for: **{query}**")

        for _, r in filtered_df.head(10).iterrows():
            with st.container():
                cols = st.columns([1, 3])

                with cols[0]:
                    if r.get("image_url"):
                        st.image(r["image_url"], use_column_width=True)
                    else:
                        st.image("https://via.placeholder.com/150", use_column_width=True)

                with cols[1]:
                    st.markdown(f"### {r['title']}")
                    st.write(r['short_description'])
                    st.write(f"**Brand:** {r['brand']}")
                    st.write(f"**Category:** {r['category']}")
                    st.write(f"**Price:** ₹{r['price']:.2f}")
                    st.write(f"**Score:** {r['score']:.4f}")

                    if st.button(f"👍 Interested", key=f"select_{r['id']}"):
                        st.session_state.click_history.append(int(r['id']))
                        save_prefs(st.session_state.click_history)
                        st.success("Added to your preferences!")

            st.markdown("---")


# Sidebar: show inferred preferences
st.sidebar.markdown("---")
st.sidebar.header("Your Preferences")
if st.session_state.click_history:
    clicked = st.session_state.click_history
    st.sidebar.write(f"✅ Items clicked: {len(clicked)}")
    df = searcher.catalog[searcher.catalog['id'].isin(clicked)]
    if not df.empty:
        pref_counts = df['category'].value_counts().to_dict()
        st.sidebar.write("**Preferred Categories:**")
        st.sidebar.write(pref_counts)
else:
    st.sidebar.write("No clicks yet")
