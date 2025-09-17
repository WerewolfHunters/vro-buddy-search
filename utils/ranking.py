from typing import List, Dict, Optional
from collections import Counter


def build_profile_from_clicks(click_history_ids: List[int], catalog_df=None, top_k: int = 3) -> Dict:
    """
    Infer a lightweight user profile (preferred categories/colors) from click history.

    Args:
        click_history_ids: list of product ids clicked this session
        catalog_df: optional pandas.DataFrame with columns ['id','category','color']
        top_k: how many top categories/colors to keep

    Returns:
        profile dict: {"categories": [...], "colors": [...]}
    """
    profile = {"categories": [], "colors": []}
    if not click_history_ids:
        return profile

    if catalog_df is None:
        # Without catalog info we cannot infer category/color preferences
        return profile

    # Ensure id column exists
    if "id" not in catalog_df.columns:
        return profile

    # Filter clicked rows (keep order not required)
    clicked_rows = catalog_df[catalog_df["id"].isin(click_history_ids)]
    if clicked_rows.empty:
        return profile

    # Count categories
    if "category" in clicked_rows.columns:
        cats = clicked_rows["category"].fillna("").tolist()
        cat_counts = Counter([c for c in cats if c])
        profile["categories"] = [c for c, _ in cat_counts.most_common(top_k)]

    # Count colors if present
    if "color" in clicked_rows.columns:
        cols = clicked_rows["color"].fillna("").tolist()
        col_counts = Counter([c for c in cols if c])
        profile["colors"] = [c for c, _ in col_counts.most_common(top_k)]

    return profile


def apply_personalization(
    results: List[Dict],
    click_history_ids: List[int],
    catalog_df=None,
    boost_exact_click: float = 0.40,
    boost_category: float = 0.20,
    boost_color: float = 0.12,
) -> List[Dict]:
    """
    Apply simple personalization boosts to a list of search results.

    Args:
        results: list of product dicts (each must contain at least 'id' and 'score'; optional 'category', 'color')
        click_history_ids: list of product ids clicked this session
        catalog_df: optional pandas DataFrame to infer category/color preferences from clicks
        boost_exact_click: score boost for items the user already clicked
        boost_category: boost for items matching user's preferred categories
        boost_color: boost for items matching user's preferred colors

    Returns:
        new_results: list of results with updated 'score' values (original list is not modified)
    """
    if not click_history_ids:
        return results

    # Build user profile if possible
    profile = build_profile_from_clicks(click_history_ids, catalog_df=catalog_df)

    # If no profile could be inferred and no meta in results, fallback to exact-id boosting only
    pref_categories = set(profile.get("categories", []))
    pref_colors = set(profile.get("colors", []))

    # Create a Counter of clicks for potential weighted boosting (optional use)
    click_counter = Counter(click_history_ids)
    max_clicks = max(click_counter.values()) if click_counter else 1

    boosted = []
    for item in results:
        base_score = float(item.get("score", 0.0))
        new_score = base_score

        # Exact-click boost (if this item was clicked already)
        try:
            item_id = int(item.get("id"))
        except Exception:
            item_id = None

        if item_id is not None and item_id in click_counter:
            # scale exact-click boost a little by how many times it was clicked
            times = click_counter[item_id]
            # e.g., if clicked multiple times, increase boost slightly
            new_score += boost_exact_click * (1.0 + (times - 1) * 0.15)

        # Category boost
        if pref_categories and item.get("category") in pref_categories:
            new_score += boost_category

        # Color boost
        if pref_colors and item.get("color") in pref_colors:
            new_score += boost_color

        # Return a shallow copy with updated score to avoid mutating original objects
        item_copy = item.copy()
        item_copy["score"] = new_score
        boosted.append(item_copy)

    return boosted


def update_user_profile(user_profile: Optional[Dict], clicked_item: Dict, keep_top: int = 3) -> Dict:
    """
    Update a persisted user_profile dict from a clicked_item record.

    Args:
        user_profile: existing profile dict or None
        clicked_item: product dict with keys like 'category' and 'color'
        keep_top: keep only top-N frequent categories/colors

    Returns:
        updated profile
    """
    if user_profile is None:
        user_profile = {"categories": [], "colors": []}

    if clicked_item.get("category"):
        user_profile.setdefault("categories", []).append(clicked_item["category"])

    if clicked_item.get("color"):
        user_profile.setdefault("colors", []).append(clicked_item["color"])

    # Reduce to most common
    user_profile["categories"] = [c for c, _ in Counter(user_profile.get("categories", [])).most_common(keep_top)]
    user_profile["colors"] = [c for c, _ in Counter(user_profile.get("colors", [])).most_common(keep_top)]

    return user_profile
