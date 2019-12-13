import secrets
import string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import config as cfg


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
