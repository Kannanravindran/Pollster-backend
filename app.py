'''
The driver script running the server
'''
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from pymongo import MongoClient
from flask_cors import CORS
import pprint
import uuid
import config
import utils

app = Flask(__name__)
CORS(app)

client = MongoClient(
        'mongodb+srv://' + config.DB_USERNAME + ':' + config.DB_PASSWORD + '@andromeda-aghsp.mongodb.net/test?retryWrites'
                                                                           '=true&w=majority')


@app.route('/api/login/', methods=['POST'])
def login():
    email_id = request.form.get('email')
    password = request.form.get('password')
    print(email_id)
    db = client['unmatched-db']
    user_obj = db.users.find_one({'email': email_id})
    print(user_obj)
    if user_obj is not None:
        if check_password_hash(str(user_obj['password']), str(password)):
            survey_privileges_obj = db.surveyPrivileges.find_one({'uid': user_obj['uid']})
            return jsonify({
                'isAuthenticated' : True, 'uid': user_obj['uid'],
                'role'            : user_obj['role'],
                'surveyPrivileges': survey_privileges_obj['surveyids'],
                'adminPrivileges' : survey_privileges_obj['adminids']
            })
        else:
            return jsonify({'isAuthenticated': False, 'uid': '', 'role': ''})
    else:
        return jsonify({'isAuthenticated': False, 'uid': '', 'role': ''})


@app.route('/api/access/', methods=['GET'])
def feed_user_access():
    access_code = request.args.get('code').lower()
    db = client['unmatched-db']
    user_obj = db.users.find_one({'uid': access_code})
    survey_privileges_obj = db.surveyPrivileges.find_one({'uid': user_obj['uid']})
    print(survey_privileges_obj)
    if user_obj is not None:
        return jsonify({
            'isAuthenticated' : True,
            'uid'             : access_code,
            'surveyPrivileges': survey_privileges_obj['surveyids'],
            'adminPrivileges' : survey_privileges_obj['adminids'],
            'role'            : user_obj['role']
        })
    else:
        return jsonify({'isAuthenticated': False, 'uid': ''})


@app.route('/api/register/', methods=['POST'])
def register():
    data = request.get_json(force=True)
    db = client['unmatched-db']
    # check if the referrer is admin / super admin
    ref = db.users.find_one({'uid': data['ref']})
    new_user = {}

    if ref is not None:
        # check if the invited user exists
        existing_user = db.users.find_one({'email': data['email']})
        # admin privilege check
        existing_privileges = db.surveyPrivileges.find_one({'uid': data['ref']})['adminids']
        if utils.isSublist(existing_privileges, data['surveyids']):
            utils.register_new_user(db, existing_user, data, is_upgrade=False)

    return jsonify({'isInvited': True})


@app.route('/api/store-survey/', methods=['POST'])
def save_survey():
    data = request.get_json(force=True)
    db = client['unmatched-db']
    user_obj = db.users.find_one({'uid': data['uid']})
    data['email'] = user_obj['email']
    print(data)
    db.answers.update({'uid': data['uid'], 'surveyId': data['surveyId']}, data, upsert=True)
    return jsonify({'isResponseUpdated': True})


@app.route('/api/get-response/', methods=['GET'])
def get_survey_response():
    uid = request.args.get('uid')
    surveyid = request.args.get('surveyid')
    db = client['unmatched-db']
    res = db.answers.find_one({'uid': uid, 'surveyId': surveyid})
    if res:
        del res['_id']
        res['success'] = True
    else:
        res = {'success': False}
    return jsonify(res)


# admin apis
@app.route('/api/admin/get-all-response/', methods=['GET'])
def get_admin_all_response():
    uid = request.args.get('uid')
    surveyid = request.args.get('surveyid')
    db = client['unmatched-db']
    user_obj = db.users.find_one({'uid': uid})
    if user_obj['role'] < 2:
        res = db.answers.find({'surveyId': surveyid, 'isSubmitted': True})
        data = []
        for entry in res:
            del entry['_id']
            data.append(entry)
        return jsonify({'success': True, 'answers': data})
    else:
        return jsonify({'success': False})


@app.route('/api/admin/upgrade/', methods=['POST'])
def admin_upgrade():
    data = request.get_json(force=True)
    db = client['unmatched-db']
    # check if the referrer is admin / super admin
    ref = db.users.find_one({'uid': data['ref']})
    print(ref)

    if ref is not None:
        # check if the invited user exists
        existing_user = db.users.find_one({'email': data['email']})
        # print(existing_user)
        # admin privilege check
        if ref['role'] == 0:
            utils.register_new_user(db, existing_user, data, is_upgrade=True)

    return jsonify({'isUpgraded': True})


if __name__ == '__main__':
    app.run()
