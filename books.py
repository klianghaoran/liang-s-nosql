from datetime import datetime
from audit import log
from utils import parse_dt


def search_books(db, category=None, min_price=None, max_price=None, tags=None,
                 title=None, year_from=None, year_to=None):
    q = {}
    if category:
        q["category"] = category
    if min_price is not None or max_price is not None:
        q["price"] = {}
        if min_price is not None:
            q["price"]["$gte"] = float(min_price)
        if max_price is not None:
            q["price"]["$lte"] = float(max_price)
    if tags:
        q["tags"] = {"$all": tags}
    if title:
        q["title"] = {"$regex": title, "$options": "i"}
    if year_from or year_to:
        y1 = int(year_from or 1900)
        y2 = int(year_to or 2100)
        q["publish_date"] = {"$gte": datetime(y1, 1, 1), "$lt": datetime(y2 + 1, 1, 1)}
    return list(db.books.find(q).sort("rating", -1))


def top_rated(db, limit=10):
    return list(db.books.find({}, {"_id": 0, "title": 1, "author": 1, "rating": 1})
                .sort("rating", -1).limit(limit))


def missing_tags(db):
    return list(db.books.find({"tags": {"$exists": False}}, {"_id": 0, "isbn": 1, "title": 1}))


def add_book(db, doc, actor="cli"):
    doc = dict(doc)
    doc["price"] = float(doc.get("price", 0))
    doc["rating"] = float(doc.get("rating", 0))
    doc["stock"] = int(doc.get("stock", 0))
    doc["borrow_count"] = int(doc.get("borrow_count", 0))
    if isinstance(doc.get("publish_date"), str):
        doc["publish_date"] = parse_dt(doc["publish_date"])
    db.books.insert_one(doc)
    log(db, "ADD_BOOK", doc.get("isbn", ""), doc.get("title", ""), actor)
    return doc


def delete_book(db, isbn, actor="cli"):
    r = db.books.delete_one({"isbn": isbn})
    if r.deleted_count:
        log(db, "DELETE_BOOK", isbn, "", actor)
    return r.deleted_count


def get_book(db, isbn):
    return db.books.find_one({"isbn": isbn})
