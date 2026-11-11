from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.errors import CollectionInvalid
from config import MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_USER, MONGO_PASSWORD, MONGO_AUTH


def get_client(auth=None):
    if auth is None:
        auth = MONGO_AUTH
    kwargs = dict(host=MONGO_HOST, port=MONGO_PORT, serverSelectionTimeoutMS=5000)
    if auth:
        kwargs.update(username=MONGO_USER, password=MONGO_PASSWORD, authSource=MONGO_DB)
    return MongoClient(**kwargs)


def get_db(auth=None):
    return get_client(auth)[MONGO_DB]


def ensure_indexes(db):
    db.books.create_index([("isbn", ASCENDING)], unique=True)
    db.books.create_index([("category", ASCENDING), ("price", ASCENDING)])
    db.books.create_index([("tags", ASCENDING)])
    db.books.create_index([("title", TEXT), ("author", TEXT)])
    db.books.create_index([("publish_date", ASCENDING)])
    db.books.create_index([("rating", DESCENDING)])
    db.readers.create_index([("card_no", ASCENDING)], unique=True)
    db.readers.create_index([("college", ASCENDING)])
    db.borrow_logs.create_index([("reader_card", ASCENDING), ("borrow_date", DESCENDING)])
    db.borrow_logs.create_index([("book_isbn", ASCENDING), ("borrow_date", DESCENDING)])
    db.borrow_logs.create_index([("borrow_date", ASCENDING)])
    db.borrow_logs.create_index([("status", ASCENDING)])
    db.audit_logs.create_index([("ts", DESCENDING)])
