import argparse
import json
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from config import MONGO_HOST, MONGO_PORT, MONGO_DB, DATA_DIR
from gridfs_store import verify_manifest, list_files


def connect(user, password):
    return MongoClient(MONGO_HOST, MONGO_PORT, username=user, password=password,
                       authSource=MONGO_DB, serverSelectionTimeoutMS=5000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="sl_rw")
    ap.add_argument("--password", default="ReadWrite@2026")
    ap.add_argument("--out", default="reports/verification.json")
    args = ap.parse_args()
    c = connect(args.user, args.password)
    db = c[MONGO_DB]
    result = {"user": args.user, "counts": {x: db[x].count_documents({}) for x in
              ["books", "readers", "borrow_logs", "audit_logs"]}}
    result["searches"] = {
        "category_price": db.books.count_documents({"category": "计算机", "price": {"$gte": 50, "$lte": 100}}),
        "tags_all": db.books.count_documents({"tags": {"$all": ["编程", "Python"]}}),
        "title_regex": db.books.count_documents({"title": {"$regex": "Python", "$options": "i"}}),
        "year_2023_2024": db.books.count_documents({"publish_date": {"$gte": datetime(2023, 1, 1), "$lt": datetime(2025, 1, 1)}}),
        "missing_tags": db.books.count_documents({"tags": {"$exists": False}}),
    }
    result["top_rated"] = list(db.books.find({}, {"_id": 0, "title": 1, "author": 1, "rating": 1}).sort("rating", -1).limit(10))
    result["category_stats"] = list(db.books.aggregate([
        {"$group": {"_id": "$category", "count": {"$sum": 1}, "avg_price": {"$avg": "$price"},
                    "avg_rating": {"$avg": "$rating"}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "category": "$_id", "count": 1, "avg_price": 1, "avg_rating": 1}},
    ]))
    result["college_top5"] = list(db.borrow_logs.aggregate([
        {"$lookup": {"from": "readers", "localField": "reader_card", "foreignField": "card_no", "as": "r"}},
        {"$unwind": "$r"}, {"$group": {"_id": "$r.college", "borrows": {"$sum": 1}}},
        {"$sort": {"borrows": -1}}, {"$limit": 5},
        {"$project": {"_id": 0, "college": "$_id", "borrows": 1}},
    ]))
    result["monthly_trend"] = list(db.borrow_logs.aggregate([
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m", "date": "$borrow_date"}}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}, {"$project": {"_id": 0, "month": "$_id", "count": 1}},
    ]))
    result["top_borrowed"] = list(db.books.find({}, {"_id": 0, "title": 1, "borrow_count": 1, "location": 1})
                                  .sort("borrow_count", -1).limit(10))
    result["gridfs"] = verify_manifest(db, DATA_DIR)
    result["gridfs_files"] = [{"filename": x["filename"], "size": x["size"],
                               "upload_date": str(x["upload_date"])} for x in list_files(db)]
    # permission checks only meaningful for read-only user
    if args.user == "sl_read":
        try:
            db.books.insert_one({"isbn": "__FORBIDDEN__", "title": "x"})
            result["readonly_write"] = "UNEXPECTED_SUCCESS"
            db.books.delete_one({"isbn": "__FORBIDDEN__"})
        except OperationFailure as e:
            result["readonly_write"] = f"DENIED({e.code})"
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"out": str(out), "counts": result["counts"], "readonly_write": result.get("readonly_write")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
