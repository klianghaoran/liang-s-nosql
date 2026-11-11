import argparse
import json
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient
from config import MONGO_HOST, MONGO_PORT, MONGO_DB, DATA_DIR
from db import ensure_indexes
from utils import parse_dt
from gridfs_store import upload_all


def load(name):
    return json.loads((Path(DATA_DIR) / name).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args()
    client = MongoClient(MONGO_HOST, MONGO_PORT, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]
    if args.reset:
        client.drop_database(MONGO_DB)
    # capped audit collection: fixed 50 MB, max 100k entries
    if "audit_logs" not in db.list_collection_names():
        db.create_collection("audit_logs", capped=True, size=50 * 1024 * 1024, max=100000)
    books = load("books.txt")
    readers = load("readers.txt")
    logs = load("borrow_logs.txt")
    for b in books:
        b["publish_date"] = parse_dt(b.get("publish_date"))
    for r in readers:
        r["register_date"] = parse_dt(r.get("register_date"))
    for l in logs:
        l["borrow_date"] = parse_dt(l.get("borrow_date"))
        if l.get("return_date"):
            l["return_date"] = parse_dt(l["return_date"])
        else:
            l.pop("return_date", None)
    db.books.delete_many({})
    db.readers.delete_many({})
    db.borrow_logs.delete_many({})
    db.books.insert_many(books)
    db.readers.insert_many(readers)
    db.borrow_logs.insert_many(logs)
    ensure_indexes(db)
    up = upload_all(db, DATA_DIR)
    counts = {c: db[c].count_documents({}) for c in ["books", "readers", "borrow_logs", "audit_logs"]}
    print(json.dumps({"counts": counts, "gridfs_uploaded": up}, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
