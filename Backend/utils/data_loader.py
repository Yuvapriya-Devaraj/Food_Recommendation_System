import pandas as pd

def seed_food_from_csv(csv_path, db, Food):
    """
    Seed the Food table from a CSV file if not already populated.
    """
    df = pd.read_csv(csv_path)

    # If already seeded → skip
    if Food.query.first():
        print("✅ Food table already populated")
        return

    foods = []

    for _, row in df.iterrows():
        # Make sure optional numeric fields are safely converted
        min_age = int(row["min_age"]) if pd.notna(row["min_age"]) else 0
        frequency_limit = int(row["frequency_limit"]) if pd.notna(row["frequency_limit"]) else 0
        score = int(row["score"]) if pd.notna(row["score"]) else 0

        foods.append(
            Food(
                food_name=row.get("food_name", ""),
                category=row.get("category", ""),
                health=row.get("health", ""),
                timing=row.get("timing", ""),
                season=row.get("season", ""),
                score=score,
                taste=row.get("taste", ""),
                min_age=min_age,
                frequency_limit=frequency_limit,
            )
        )

    db.session.add_all(foods)
    db.session.commit()

    print(f"🍎 Inserted {len(foods)} foods from CSV")


def load_food_schema(FoodModel, default_age_span=5):
    """
    Load all food items and convert to schema for models.

    - default_age_span: number of years after min_age the food is suitable
    - Returns a list of dicts with keys:
        food_id, name, type, age_groups, time_of_day, score
    """
    food_items = FoodModel.query.all()
    schema = []

    for f in food_items:
        # Ensure min_age is integer
        min_age = f.min_age if f.min_age is not None else 0

        # Build age range
        age_groups = list(range(min_age, min_age + default_age_span + 1))  # inclusive

        # Timing may be empty
        times = f.timing.split('|') if f.timing else []

        schema.append({
            "food_id": f.food_id,
            "name": f.food_name,
            "type": f.category,
            "age_groups": age_groups,
            "time_of_day": times,
            "score": f.score if f.score is not None else 0  # Ensure score is not None
        })

    return schema


def load_history_df(db):
    """
    Load kid_food_history table into a pandas DataFrame.
    """
    query = "SELECT * FROM kid_food_history"
    df = pd.read_sql(query, db.engine)

    # Ensure score column exists and fill NA with 0
    if "score" in df.columns:
        df["score"] = df["score"].fillna(0)
    else:
        df["score"] = 0

    return df
