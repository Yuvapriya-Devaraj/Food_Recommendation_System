import random

def recommend(kid_id, age_group, favorite_food, time_of_day, history_df, food_schema, top_n=3):

    if history_df.empty:
        return []

    # 🔥 Get current kid history
    current_kid = history_df[history_df['kid_id'] == kid_id]

    recent_shown = current_kid[current_kid['action'] == 'shown']['food_id'].tail(5).tolist() \
        if 'action' in history_df.columns else []

    liked = current_kid[current_kid.get('liked', 0) == 1]['food_id'].tolist()

    # 🔥 Other users data
    others = history_df[history_df['kid_id'] != kid_id].copy()

    if others.empty:
        return []

    # ✅ Weighted scoring
    others['weight'] = (
        others.get('liked', 0).fillna(0) * 3 +
        others.get('score', 0).fillna(0)
    )

    counts = others.groupby('food_id')['weight'].sum().sort_values(ascending=False)

    food_map = {f.get("food_id"): f for f in food_schema}

    results = []

    time = time_of_day.strip().lower()

    if isinstance(favorite_food, str):
        fav_list = [favorite_food.lower()]
    else:
        fav_list = [x.lower() for x in (favorite_food or [])]

    def map_time(t):
        if t == "snack":
            return ["morning", "afternoon", "evening"]
        elif t == "lunch":
            return ["afternoon"]
        return []

    valid_times = map_time(time)

    for food_id, base_score in counts.items():

        food = food_map.get(food_id)
        if not food:
            continue

        score = float(base_score)

        # ✅ Age scoring
        min_age = food.get('min_age', 0)
        if age_group >= min_age:
            score += 2
        else:
            score -= 2

        # ✅ Timing scoring
        timing = (food.get('timing') or "").lower()
        if any(t in timing for t in valid_times):
            score += 2
        else:
            score -= 1

        # ✅ Favorite match
        food_name = (food.get("name") or "").lower()
        if any(fav in food_name for fav in fav_list):
            score += 3

        # 🔥 NEW: Avoid repetition
        if food_id in recent_shown:
            score -= 5

        # 🔥 NEW: Boost liked foods
        if food_id in liked:
            score += 3

        # 🔥 NEW: Add randomness
        score += random.uniform(0, 1)

        results.append({
            "food_id": food_id,
            "name": food.get("name", "Unknown Food"),
            "score": score
        })

    if not results:
        return []

    # ✅ Sort
    results.sort(key=lambda x: x['score'], reverse=True)

    # 🔥 NEW: Random selection from top 10
    top_results = results[:10]
    final = random.sample(top_results, min(top_n, len(top_results)))

    return final