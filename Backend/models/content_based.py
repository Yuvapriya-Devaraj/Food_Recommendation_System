import random


def get_history_df(history_df, kid_id, action="shown", limit=10):

    if history_df is None or history_df.empty:
        return []

    df = history_df[history_df['kid_id'] == kid_id]

    # ✅ If action column exists
    if 'action' in history_df.columns:
        df = df[df['action'] == action]

    else:
        # ✅ fallback logic
        if action == "clicked":
            df = df[df.get('liked', 0) == 1]
        # "shown" = all history

    # Sort if timestamp exists
    if 'timestamp' in df.columns:
        df = df.sort_values(by='timestamp', ascending=False)

    if limit:
        df = df.head(limit)

    return df['food_id'].tolist()

def recommend(age_group, favorite_food, time_of_day, history_df,
              food_schema, kid_id=None, top_n=3):

    results = []
    time = time_of_day.strip().lower()

    # ✅ Favorite handling
    if isinstance(favorite_food, str):
        fav_list = [favorite_food.lower()]
    else:
        fav_list = [x.lower() for x in (favorite_food or [])]

    # ✅ GET HISTORY (from DataFrame)
    recent_shown = get_history_df(history_df, kid_id, "shown", limit=5) if kid_id else []
    clicked = get_history_df(history_df, kid_id, "clicked") if kid_id else []

    for f in food_schema:

        score = 0

        # ----------------------------
        # ✅ Age scoring
        # ----------------------------
        min_age = f.get("min_age", 0)
        score += 2 if age_group >= min_age else -2

        # ----------------------------
        # ✅ Timing scoring
        # ----------------------------
        timing = (f.get("timing") or "").lower()

        if time == "snack":
            valid_times = ["morning", "afternoon", "evening"]
        elif time == "lunch":
            valid_times = ["afternoon"]
        else:
            valid_times = []

        score += 2 if any(t in timing for t in valid_times) else -1

        # ----------------------------
        # ✅ Favorite match
        # ----------------------------
        food_name = (f.get("name") or "").lower()
        if any(fav in food_name for fav in fav_list):
            score += 3

        # ----------------------------
        # ✅ Health boost
        # ----------------------------
        if (f.get('health') or "").lower() == "very healthy":
            score += 1

        # ----------------------------
        # ✅ Base score
        # ----------------------------
        score += f.get("score", 0)

        # ----------------------------
        # 🔥 Avoid repetition
        # ----------------------------
        if f.get("food_id") in recent_shown:
            score -= 5

        # ----------------------------
        # 🔥 Boost liked foods
        # ----------------------------
        if f.get("food_id") in clicked:
            score += 3

        # ----------------------------
        # 🔥 Randomness
        # ----------------------------
        score += random.uniform(0, 1)

        results.append({
            "food_id": f.get("food_id"),
            "name": f.get("name", "Unknown Food"),
            "score": score
        })

    # ----------------------------
    # ✅ Sort
    # ----------------------------
    results.sort(key=lambda x: x['score'], reverse=True)

    # ----------------------------
    # 🔥 Random selection (top 10)
    # ----------------------------
    top_results = results[:10]

    if len(top_results) <= top_n:
        return top_results

    return random.sample(top_results, top_n)