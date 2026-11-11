from datetime import datetime, timezone
from audit import log


def category_stats(db):
    return list(db.books.aggregate([
        {"$group": {"_id": "$category", "count": {"$sum": 1},
                    "avg_price": {"$avg": "$price"}, "avg_rating": {"$avg": "$rating"}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "category": "$_id", "count": 1, "avg_price": 1, "avg_rating": 1}},
    ]))


def college_top5(db):
    return list(db.borrow_logs.aggregate([
        {"$lookup": {"from": "readers", "localField": "reader_card",
                     "foreignField": "card_no", "as": "reader"}},
        {"$unwind": "$reader"},
        {"$group": {"_id": "$reader.college", "borrows": {"$sum": 1}}},
        {"$sort": {"borrows": -1}},
        {"$limit": 5},
        {"$project": {"_id": 0, "college": "$_id", "borrows": 1}},
    ]))


def monthly_trend(db):
    return list(db.borrow_logs.aggregate([
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m", "date": "$borrow_date"}},
                    "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "month": "$_id", "count": 1}},
    ]))


def top_borrowed(db, limit=10):
    return list(db.books.find({}, {"_id": 0, "title": 1, "author": 1,
                                   "borrow_count": 1, "location": 1})
                .sort("borrow_count", -1).limit(limit))


def save_category_stats(db):
    rows = category_stats(db)
    db.category_stats.delete_many({})
    if rows:
        db.category_stats.insert_many([dict(r, generated_at=datetime.now(timezone.utc)) for r in rows])
    log(db, "EXPORT_CATEGORY_STATS", "category_stats", f"{len(rows)} rows")
    return rows
