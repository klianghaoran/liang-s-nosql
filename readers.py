from audit import log
from utils import parse_dt


def search_readers(db, keyword="", college=None, level=None):
    q = {}
    if keyword:
        q["$or"] = [
            {"name": {"$regex": keyword, "$options": "i"}},
            {"card_no": {"$regex": keyword, "$options": "i"}},
        ]
    if college:
        q["college"] = college
    if level:
        q["level"] = level
    return list(db.readers.find(q).sort("card_no", 1))


def add_reader(db, doc, actor="cli"):
    doc = dict(doc)
    if isinstance(doc.get("register_date"), str):
        doc["register_date"] = parse_dt(doc["register_date"])
    db.readers.insert_one(doc)
    log(db, "ADD_READER", doc.get("card_no", ""), doc.get("name", ""), actor)
    return doc


def delete_reader(db, card_no, actor="cli"):
    r = db.readers.delete_one({"card_no": card_no})
    if r.deleted_count:
        log(db, "DELETE_READER", card_no, "", actor)
    return r.deleted_count
