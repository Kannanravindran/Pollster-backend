from pymongo import MongoClient
import config
import uuid

client = MongoClient(
    "mongodb+srv://" + config.DB_USERNAME + ":" + config.DB_PASSWORD + "@andromeda-aghsp.mongodb.net/test?retryWrites=true&w=majority")


def test_insert():
    user_db = client.unmatched
    res = user_db.users.insert_one(
        {
            "emailId": "kannan.cyberpunk@gmail.com",
            "user_id": str(uuid.uuid4()),
            "role": "super",
            "password": "pbkdf2:sha256:150000$4jsKVoL5$a525769c5ac0d793a0232c871c33e06957ddf25f8619e8942e560b93952d1de5",
            "isSubmitted": False
        }
    )
    print({"response": res})

test_insert()
