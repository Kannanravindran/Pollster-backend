"""
The driver script running the server
"""
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from pymongo import MongoClient
from flask_cors import CORS
import uuid
import config
import utils

app = Flask(__name__)
CORS(app)

client = MongoClient(
    "mongodb+srv://" + config.DB_USERNAME + ":" + config.DB_PASSWORD + "@andromeda-aghsp.mongodb.net/test?retryWrites"
                                                                       "=true&w=majority")


@app.route("/api/login/", methods=["POST"])
def login():
    email_id = request.form.get('email')
    password = request.form.get('password')
    print(email_id)
    db = client["unmatched-db"]
    user_obj = db.users.find_one({"email": email_id})
    print(user_obj)
    if user_obj is not None:
        if check_password_hash(str(user_obj["password"]), str(password)):
            return jsonify({"isAuthenticated": True, "uid": user_obj["uid"], "role": user_obj["role"]})
        else:
            return jsonify({"isAuthenticated": False, "uid": "", "role": ""})
    else:
        return jsonify({"isAuthenticated": False, "uid": "", "role": ""})


@app.route("/api/access/", methods=["GET"])
def feed_user_access():
    access_code = request.args.get('code').lower()
    db = client["unmatched-db"]
    is_authenticated = db.users.find_one({"uid": access_code})
    print(is_authenticated)
    if is_authenticated is not None:
        return jsonify({"isAuthenticated": True, "uid": access_code})
    else:
        return jsonify({"isAuthenticated": False, "uid": ""})


@app.route("/api/save_draft/", methods=["POST"])
def save_survey():
    data = request.get_json(force=True)
    db = client["unmatched-db"]
    res = db.answers.update({"uid": data["uid"]}, data, upsert=True)
    return jsonify({"isResponseUpdated": True})


@app.route("/api/register/", methods=["POST"])
def register():
    data = request.get_json(force=True)
    db = client["unmatched-db"]
    print(data)
    # check if the referrer is admin / super admin
    ref = db.users.find_one({"uid": data['ref']})
    print("manager: ", ref)
    new_user = {}
    if ref is not None:
        # check if the invited user exists
        existing_user = db.users.find_one({"email": data["email"]})
        print("existing user: ", existing_user)
        # admin privilege check
        if ref["role"] < 2:
            if existing_user is None:
                new_password = utils.generate_secure_password()
                print(data["email"], " : ", new_password)
                new_user = {
                    "email": data["email"],
                    "uid": str(uuid.uuid4()),
                    "role": 2,
                    "password": generate_password_hash(new_password),
                    "referrer": data["ref"],
                }
                # store the new user
                db.users.insert(new_user)
                # survey privileges
                db.surveyPrivileges.insert({"uid": new_user["uid"], "surveyids": data["surveyids"], "isSubmitted": False})
            else:
                print("user exists")
                existing_survey_privileges = db.surveyPrivileges.find_one({"uid": existing_user["uid"]})
                new_survey_privileges = data["surveyids"]
                # check if the user already has access to the surveys
                new_survey_privileges = existing_survey_privileges["surveyids"] + new_survey_privileges
                new_survey_privileges = list(set(new_survey_privileges))
                # give access to new surveys
                db.users.update(existing_user, {"$set": {"surveyids": new_survey_privileges}})
            # send an invitation email with new password and access link

    return jsonify({"isInvited": True})


if __name__ == '__main__':
    app.run()
