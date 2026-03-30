"""
def recommend(kid_id, age_group, favorite_food, time_of_day, history_df, food_schema, top_n=3):
    others = history_df[history_df['kid_id'] != kid_id]
    counts = others['food_id'].value_counts()
    recommendations = []

    for food_id, score in counts.items():
        item = next(f for f in food_schema if f['food_id'] == food_id)
        if age_group in item['age_groups'] and time_of_day in item['time_of_day']:
            recommendations.append({**item, "score": score})

    recommendations.sort(key=lambda x: (x['type'] in favorite_food, x.get("score", 0)), reverse=True)
    return recommendations[:top_n]
"""
def recommend(kid_id, age_group, favorite_food, time_of_day, history_df, food_schema, top_n=3):

    others = history_df[history_df['kid_id'] != kid_id]
    counts = others['food_id'].value_counts()

    kid_history = history_df[history_df['kid_id'] == kid_id]
    eaten_foods = set(kid_history['food_id'])

    recommendations = []

    for food_id, score in counts.items():

        if food_id in eaten_foods:
            continue

        item = next(f for f in food_schema if f['food_id'] == food_id)

        if age_group in item['age_groups'] and time_of_day in item['time_of_day']:

            recommendations.append({**item, "score": score})

    recommendations.sort(
        key=lambda x: (x['type'] in favorite_food, x.get("score", 0)),
        reverse=True
    )

    return recommendations[:top_n]