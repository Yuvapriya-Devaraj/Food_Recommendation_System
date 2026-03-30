from flask import Blueprint, request, jsonify
from database.db import mysql

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register_kid():
    data = request.json
    device_id = data['device_id']
    kid_id = data['kid_id']
    name = data['name']
    age = data['age']

    cur = mysql.connection.cursor()

    # Insert device if not exists
    cur.execute(
        "INSERT IGNORE INTO devices (device_id) VALUES (%s)",
        (device_id,)
    )

    # Insert kid
    cur.execute("""
        INSERT IGNORE INTO kids (kid_id, device_id, name, age)
        VALUES (%s, %s, %s, %s)
    """, (kid_id, device_id, name, age))

    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Kid registered successfully"})
