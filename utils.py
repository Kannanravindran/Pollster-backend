import secrets
import string
from werkzeug.security import check_password_hash, generate_password_hash
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import config as cfg
import uuid


# from Crypto.Cipher import AES


def send_email(recipient_email, password, uid):
    message = Mail(
            from_email='no-reply@unmatched.io',
            to_emails=recipient_email)

    message.dynamic_template_data = {
        "survey_url"       : cfg.REACT_HOST_ADDR,
        "access_code"      : uid,
        "survey_access_url": cfg.REACT_HOST_ADDR + "?code=" + uid,
        "sender_name"      : "team unmatched.io",
        "email"            : recipient_email,
        "password"         : password
    }

    message.template_id = 'd-9f8829271fdf4a07b180c412e3cd2a02'
    try:
        sendgrid_client = SendGridAPIClient(cfg.SG_API)
        response = sendgrid_client.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))


def generate_secure_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    return password


def isSublist(adminids, surveyids):
    for surveyid in surveyids:
        if surveyid not in adminids:
            return False
    return True

def register_new_user(db, existing_user, data, is_upgrade):

    if existing_user is None:
        new_password = generate_secure_password()
        print(data['email'], ' : ', new_password)
        if is_upgrade:
            new_user = {
                'email'   : data['email'],
                'uid'     : str(uuid.uuid4()),
                'role'    : 2,
                'password': generate_password_hash(new_password),
                'referrer': data['ref'],
            }
            # store the new user
            db.users.insert(new_user)
            # survey privileges
            db.surveyPrivileges.insert(
                    {'uid': new_user['uid'], 'surveyids': data['surveyids'], 'adminids': data['surveyids']})
        else:
            new_user = {
                'email'   : data['email'],
                'uid'     : str(uuid.uuid4()),
                'role'    : 1,
                'password': generate_password_hash(new_password),
                'referrer': data['ref'],
            }
            # store the new user
            db.users.insert(new_user)
            # survey privileges
            db.surveyPrivileges.insert(
                    {'uid': new_user['uid'], 'surveyids': data['surveyids'], 'adminids': []})

        # send an invitation email with new password and access link
        send_email(new_user['email'], new_password, new_user['uid'])
    else:
        print('user exists')
        db.users.update_one(existing_user, {"$set": {"role": "1"}})
        existing_survey_privileges = db.surveyPrivileges.find_one({'uid': existing_user['uid']})
        print("exist prev: ", existing_survey_privileges)
        new_survey_privileges = list(set(existing_survey_privileges['surveyids'] + data['surveyids']))
        new_admin_privileges = existing_survey_privileges['adminids']
        if is_upgrade:
            new_admin_privileges = list(set(existing_survey_privileges['adminids'] + data['surveyids']))

        print("new prev: ", type(new_survey_privileges))
        # give access to new surveys
        res = db.surveyPrivileges.update_one(
                existing_survey_privileges,
                {'$set': {'surveyids': new_survey_privileges, 'adminids': new_admin_privileges}}
        )
        print(res)
