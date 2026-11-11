from datetime import datetime, timezone
from audit import log


def borrow_book(db, card_no, isbn, actor="cli"):
    book = db.books.find_one({"isbn": isbn})
    reader = db.readers.find_one({"card_no": card_no})
    if not book or not reader:
        return None, "图书或读者不存在"
    if book.get("stock", 0) <= 0:
        return None, "库存不足"
    now = datetime.now(timezone.utc)
    doc = {"borrow_date": now, "reader_card": card_no, "book_isbn": isbn,
           "status": "借出", "duration_days": 0}
    db.borrow_logs.insert_one(doc)
    db.books.update_one({"isbn": isbn}, {"$inc": {"stock": -1, "borrow_count": 1}})
    log(db, "BORROW", isbn, f"{card_no}", actor)
    return doc, "借阅成功"


def return_book(db, card_no, isbn, actor="cli"):
    row = db.borrow_logs.find_one({"reader_card": card_no, "book_isbn": isbn, "status": "借出"},
                                  sort=[("borrow_date", -1)])
    if not row:
        return None, "未找到借出记录"
    now = datetime.now(timezone.utc)
    days = max((now - row["borrow_date"]).days, 0)
    db.borrow_logs.update_one({"_id": row["_id"]},
                              {"$set": {"return_date": now, "status": "已归还", "duration_days": days}})
    db.books.update_one({"isbn": isbn}, {"$inc": {"stock": 1}})
    log(db, "RETURN", isbn, f"{card_no}", actor)
    return row, "归还成功"


def overdue_logs(db, limit=20):
    return list(db.borrow_logs.find({"status": "逾期"}).sort("borrow_date", 1).limit(limit))
