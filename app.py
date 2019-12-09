"""
The driver script running the server
"""
from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import uuid
import config

app = Flask(__name__)
CORS(app)

client = MongoClient(
    "mongodb+srv://" + config.DB_USERNAME + ":" + config.DB_PASSWORD + "@andromeda-aghsp.mongodb.net/test?retryWrites=true&w=majority")


@app.route("/api/login/", methods=["POST"])
def login():
    email_id = request.form.get('emailId')
    password = request.form.get('password')
    print(email_id," ; ",password)
    return jsonify({"success": "ok"})

@app.route("/api/access/", methods=["GET"])
def feed_user_access():
    access_code = request.args.get('code').lower()
    db = client.unmatched
    is_authenticated = db.users.find_one({"user_id": access_code})
    if is_authenticated is not None:
        return jsonify({"isAuthenticated": True})
    else:
        return jsonify({"isAuthenticated": False})


@app.route("/api/save_draft/", methods=["POST"])
def save_survey():
    data = request.get_json(force=True)
    db = client.unmatched
    res = db.answers.update({"uid": data["uid"]},data,upsert=True)
    print(res)
    return jsonify({"success": "ok"})


if __name__ == '__main__':
    app.run()
