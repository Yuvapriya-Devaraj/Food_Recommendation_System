from models.content_based import recommend as content_recommend
from models.collaborative import recommend as collab_recommend


def recommend(kid_id, age_group, favorite_food, time_of_day, history_df, food_schema, top_n=3):
    time = time_of_day.strip().lower()
    
    filtered_food = [
    f for f in food_schema
    if time in (f.get("type") or "").strip().lower()
]

    content_rec = content_recommend(age_group, favorite_food, time_of_day,history_df, filtered_food, top_n)
    collab_rec = collab_recommend(kid_id, age_group, favorite_food, time_of_day, history_df, filtered_food, top_n)

    print("Content Rec:", content_rec)
    print("Collab Rec:", collab_rec)

    combined = {}

    # ✅ Dynamic weights
    if collab_rec:
        CONTENT_WEIGHT = 0.5
        COLLAB_WEIGHT = 0.5
    else:
        CONTENT_WEIGHT = 1.0
        COLLAB_WEIGHT = 0.0

    # ✅ Normalize content
    max_content = max([item['score'] for item in content_rec], default=1)

    for item in content_rec:
        norm_score = item['score'] / max_content

        combined[item['food_id']] = {
            "food_id": item['food_id'],
            "name": item['name'],
            "score": norm_score * CONTENT_WEIGHT
        }

    # ✅ FIXED: Normalize collaborative correctly
    max_collab = max([item['score'] for item in collab_rec], default=1)

    for item in collab_rec:
        norm_score = item['score'] / max_collab

        if item['food_id'] in combined:
            combined[item['food_id']]['score'] += norm_score * COLLAB_WEIGHT
        else:
            combined[item['food_id']] = {
                "food_id": item['food_id'],
                "name": item['name'],
                "score": norm_score * COLLAB_WEIGHT
            }

    results = list(combined.values())

    # ✅ SOFT remove eaten (important fix)
    if not history_df.empty:
        eaten = set(history_df[history_df['kid_id'] == kid_id]['food_id'])

        for r in results:
            if r['food_id'] in eaten:
                r['score'] *= 0.5   # instead of removing

    # 🔥 MAIN FALLBACK
    if not results:
        print("⚠️ FALLBACK USED")

        fallback = filtered_food if filtered_food else food_schema

        if not fallback:
            fallback = food_schema

        fallback = sorted(
            fallback,
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        return [
            {
                "food_id": f.get("food_id"),
                "name": f.get("name")
            }
            for f in fallback[:top_n]
        ]

    # ✅ Final sort
    results.sort(key=lambda x: x['score'], reverse=True)

    # ✅ Ensure minimum results
    if len(results) < top_n:
        extra = [
            f for f in filtered_food
            if f.get("food_id") not in [r['food_id'] for r in results]
        ]

        extra = sorted(extra, key=lambda x: x.get("score", 0), reverse=True)

        for f in extra:
            results.append({
                "food_id": f.get("food_id"),
                "name": f.get("name"),
                "score": 0
            })
            if len(results) >= top_n:
                break
    print(results)
    return results[:top_n]