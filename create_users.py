from pymongo import MongoClient
from pymongo.errors import OperationFailure
from config import MONGO_HOST, MONGO_PORT, MONGO_DB

USERS = [
    ("sl_read", "Read@2026", [{"role": "read", "db": MONGO_DB}]),
    ("sl_rw", "ReadWrite@2026", [{"role": "readWrite", "db": MONGO_DB}]),
    ("sl_admin", "Admin@2026", [{"role": "dbOwner", "db": MONGO_DB}]),
]


def main():
    client = MongoClient(MONGO_HOST, MONGO_PORT, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]
    for name, pwd, roles in USERS:
        try:
            db.command("createUser", name, pwd=pwd, roles=roles)
            print("created", name)
        except OperationFailure as e:
            if e.code == 51003 or "already exists" in str(e):
                db.command("updateUser", name, pwd=pwd, roles=roles)
                print("updated", name)
            else:
                raise


if __name__ == "__main__":
    main()
