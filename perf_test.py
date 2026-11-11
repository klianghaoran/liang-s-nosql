import json
from pymongo import MongoClient, ASCENDING, DESCENDING
from config import MONGO_HOST, MONGO_PORT, MONGO_DB


def explain(db, coll, flt):
    r = db.command("explain", {"find": coll, "filter": flt}, verbosity="executionStats")
    stats = r.get("executionStats", {})
    plan = stats.get("executionStages", {})
    return {
        "nReturned": stats.get("nReturned"),
        "executionTimeMillis": stats.get("executionTimeMillis"),
        "totalDocsExamined": stats.get("totalDocsExamined"),
        "totalKeysExamined": stats.get("totalKeysExamined"),
        "stage": plan.get("stage"),
    }


def main():
    client = MongoClient(MONGO_HOST, MONGO_PORT, username="sl_admin", password="Admin@2026",
                          authSource=MONGO_DB, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]
    out = {}
    # books category + price
    name = "category_1_price_1"
    try:
        db.books.drop_index(name)
    except Exception:
        pass
    before = explain(db, "books", {"category": "计算机", "price": {"$gte": 50, "$lte": 100}})
    db.books.create_index([("category", ASCENDING), ("price", ASCENDING)], name=name)
    after = explain(db, "books", {"category": "计算机", "price": {"$gte": 50, "$lte": 100}})
    out["books_category_price"] = {"before": before, "after": after}
    # borrow reader + date
    name = "reader_card_1_borrow_date_-1"
    try:
        db.borrow_logs.drop_index(name)
    except Exception:
        pass
    flt = {"reader_card": "R20240001"}
    before = explain(db, "borrow_logs", flt)
    db.borrow_logs.create_index([("reader_card", ASCENDING), ("borrow_date", DESCENDING)], name=name)
    after = explain(db, "borrow_logs", flt)
    out["borrow_reader_date"] = {"before": before, "after": after}
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

