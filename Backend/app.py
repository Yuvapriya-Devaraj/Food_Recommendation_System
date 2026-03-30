from flask import Flask, request, jsonify, render_template, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus
from sqlalchemy import text, func
from models.hybrid import recommend as hybrid_recommend
from utils.data_loader import load_food_schema, load_history_df, seed_food_from_csv

# ----------------------------
# APP CONFIG
# ----------------------------

app = Flask(
    __name__,
    template_folder="../Frontend/pages",
    static_folder="../Frontend"
)

load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------------------
# DATABASE MODELS
# ----------------------------

class Kid(db.Model):
    __tablename__ = 'kids'

    kid_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50))
    nickname = db.Column(db.String(50))
    age = db.Column(db.Integer)
    favorite_food = db.Column(db.JSON)          # store as list
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Food(db.Model):
    __tablename__ = 'food'

    food_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    food_name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    health = db.Column(db.String(50))
    timing = db.Column(db.String(50))
    season = db.Column(db.String(50))
    score = db.Column(db.Integer)
    taste = db.Column(db.String(50))
    min_age = db.Column(db.Integer)
    frequency_limit = db.Column(db.Integer)


class KidFoodHistory(db.Model):
    __tablename__ = 'kid_food_history'

    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kid_id = db.Column(db.String(20), db.ForeignKey('kids.kid_id'))
    food_id = db.Column(db.Integer, db.ForeignKey('food.food_id'))
    liked = db.Column(db.Boolean)
    score = db.Column(db.Integer)
    consumed_at = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------------------
# INITIALIZATION
# ----------------------------

with app.app_context():
    db.create_all()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CSV_PATH = os.path.join(BASE_DIR, "food.csv")

    seed_food_from_csv(CSV_PATH, db, Food)

    FOOD_SCHEMA = load_food_schema(Food)
    HISTORY_DF = load_history_df(db)

# ----------------------------
# LOGIN FLOW
# ----------------------------

# FIRST PAGE → SELECT PROFILE
@app.route("/")
def select_profile():

    kids = Kid.query.all()

    return render_template("select.html", kids=kids)


# LOGIN KID
@app.route("/login/<kid_id>")
def login_kid(kid_id):

    session.clear()   # important
    session["kid_id"] = kid_id

    return redirect("/home")


# HOME PAGE
@app.route("/home")
def home():

    kid_id = request.args.get("kid_id")

    if kid_id:
        session["kid_id"] = kid_id
    else:
        kid_id = session.get("kid_id")

    if not kid_id:
        return redirect("/")

    total_score = (
        db.session.query(func.sum(KidFoodHistory.score))
        .filter(KidFoodHistory.kid_id == kid_id)
        .scalar()
    )

    total_score = total_score or 0

    return render_template("index.html", total_score=total_score)


# ----------------------------
# PROFILE CREATION
# ----------------------------

@app.route("/personalize")
def personalize():

    return render_template("personalize.html")

@app.route("/save_profile", methods=["POST"])
def save_profile():
    data = request.json

    kid_id = data.get("kid_id")
    name = data.get("name")
    nickname = data.get("nickname")
    age = data.get("age_group")   # already numeric
    favorite_food = data.get("favorite_food")

    existing_kid = Kid.query.filter_by(nickname=nickname).first()
    if existing_kid:
        return jsonify({"status": "error", "message": "Nickname already exists."})

    new_kid = Kid(
        kid_id=kid_id,
        name=name,
        nickname=nickname,
        age=age,
        favorite_food=",".join(favorite_food) if favorite_food else None
    )

    db.session.add(new_kid)
    db.session.commit()

    session["kid_id"] = kid_id

    return jsonify({"status": "success"})

# ----------------------------
# FOOD HISTORY
# ----------------------------

@app.route("/history", methods=["POST"])
def save_history():

    data = request.json

    kid_id = session.get("kid_id")

    if not kid_id:
        return jsonify({"error": "Kid not logged in"}), 401

    food_name = data["food_name"]
    liked = data.get("liked", True)

    food = Food.query.filter_by(food_name=food_name).first()

    if not food:
        return jsonify({"error": "Food not found"}), 404

    entry = KidFoodHistory(
        kid_id=kid_id,
        food_id=food.food_id,
        liked=liked,
        score=food.score
    )

    db.session.add(entry)
    db.session.commit()

    global HISTORY_DF

    HISTORY_DF = pd.concat(
        [
            HISTORY_DF,
            pd.DataFrame([{
                "kid_id": kid_id,
                "food_id": food.food_id,
                "liked": liked,
                "consumed_at": datetime.now()
            }])
        ],
        ignore_index=True
    )

    return jsonify({"status": "saved"})


# ----------------------------
# SCORE API
# ----------------------------

@app.route("/api/kids/score")
def get_kid_score():

    kid_id = session.get("kid_id")
    print("Current kid:", kid_id)

    total_score = (
        db.session.query(func.sum(KidFoodHistory.score))
        .filter(KidFoodHistory.kid_id == kid_id)
        .scalar()
    )

    return jsonify({"score": total_score or 0})


# ----------------------------
# FOOD CONSUMPTION API
# ----------------------------

@app.route("/api/consume_food", methods=["POST"])
def consume_food():

    data = request.get_json()

    kid_id = session.get("kid_id")
    food_id = data.get("food_id")

    if not kid_id or not food_id:
        return jsonify({"error": "kid_id and food_id required"}), 400

    food = Food.query.get(food_id)

    if not food:
        return jsonify({"error": "Food not found"}), 404

    history = KidFoodHistory(
        kid_id=kid_id,
        food_id=food_id,
        liked=True,
        score=food.score
    )

    db.session.add(history)
    db.session.commit()

    total_score = (
        db.session.query(func.sum(KidFoodHistory.score))
        .filter_by(kid_id=kid_id)
        .scalar()
    )

    total_score = total_score or 0

    return jsonify({"total_score": total_score})


# ----------------------------
# UI PAGES
# ----------------------------

@app.route("/snack")
def snack():

    if not session.get("kid_id"):
        return redirect("/")

    return render_template("snack.html")


@app.route("/lunch")
def lunch():

    if not session.get("kid_id"):
        return redirect("/")

    return render_template("lunch.html")

@app.route("/select")
def select():
    kids = Kid.query.all()
    return render_template("select.html", kids=kids)


# ----------------------------
# RECOMMENDATION SYSTEM
# ----------------------------
@app.route("/recommend")
def recommend_page():

    if not session.get("kid_id"):
        return redirect("/")

    return render_template("recommend.html")

import pandas as pd

@app.route("/api/recommend", methods=["POST"])
def recommend_food():

    data = request.json

    kid_id = data.get("kid_id")
    age = data.get("age_group")
    favorite_food = data.get("favorite_food", [])
    time_of_day = data.get("time_of_day")

    if not age:
        return jsonify({"foods": []})

    # ✅ get history from DB
    history = KidFoodHistory.query.all()

    history_df = pd.DataFrame([{
        "kid_id": h.kid_id,
        "food_id": h.food_id,
        "liked": h.liked,
        "score": h.score,
        "consumed_at": h.consumed_at
    } for h in history])

    results = hybrid_recommend(
        kid_id,
        int(age),
        favorite_food,
        time_of_day,
        history_df,
        FOOD_SCHEMA,
        top_n=3
    )

    foods = [f['name'] for f in results]

    return jsonify( results)


# ----------------------------
# RUN APP
# ----------------------------

if __name__ == "__main__":
    app.run(debug=True)