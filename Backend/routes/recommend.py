from flask import Blueprint, request, jsonify
from database.db import mysql

recommend_bp = Blueprint('recommend', __name__, url_prefix='/recommend')

@recommend_bp.route('/food', methods=['POST'])
def recommend_food():
    data = request.json
    kid_id = data['kid_id']
    timing = data['timing']
    season = data['season']

    cur = mysql.connection.cursor()

    query = """
        SELECT f.food_id, f.food_name, f.score
        FROM food f
        WHERE f.timing = %s
          AND (f.season = %s OR f.season = 'All')
          AND f.food_id NOT IN (
              SELECT food_id
              FROM kid_food_history
              WHERE kid_id = %s
              GROUP BY food_id
              HAVING COUNT(*) >= f.frequency_limit
          )
        ORDER BY f.score DESC
        LIMIT 5
    """

    cur.execute(query, (timing, season, kid_id))
    result = cur.fetchall()

    cur.close()

    foods = [{"food_id": r[0], "name": r[1], "score": r[2]} for r in result]

    return jsonify(foods)
