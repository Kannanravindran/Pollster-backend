"""
The driver script running the server
"""
from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import uuid
import config


app = Flask(__name__)

client = MongoClient("mongodb+srv://"+config.DB_USERNAME+":"+config.DB_PASSWORD+"@andromeda-aghsp.mongodb.net/test?retryWrites=true&w=majority")



@app.route('/test')
def test_insert():
    user_db = client.unmatched
    res = user_db.users.insert_one(
        {
            "emailId": "kannan.cyberpunk@gmail.com",
            "user_id": str(uuid.uuid4()),
            "role":"super",
            "password": "pbkdf2:sha256:150000$4jsKVoL5$a525769c5ac0d793a0232c871c33e06957ddf25f8619e8942e560b93952d1de5",
            "isSurveyCompleted": False
        }
    )
    print({"response":res})
    # return jsonify({"response":res})
    return jsonify({"success":"ok"})

@app.route('/api/access/',methods=["GET"])
def feed_user_access():
    access_code = request.args.get('code').lower()
    user_db = client.unmatched
    is_authenticated = user_db.users.find_one({"user_id":access_code})
    if is_authenticated is not None:
        return jsonify({"isAuthenticated": True})
    else:
        return jsonify({"isAuthenticated": False})

# @app.route('/save_survey', methods=["POST"])
# def ():



if __name__ == '__main__':
    app.run()
