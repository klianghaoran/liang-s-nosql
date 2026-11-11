from datetime import datetime, timezone


def log(db, action, target, detail="", actor="cli"):
    db.audit_logs.insert_one({
        "ts": datetime.now(timezone.utc),
        "actor": actor,
        "action": action,
        "target": target,
        "detail": detail,
    })


def recent(db, limit=100):
    return list(db.audit_logs.find({}, {"_id": 0}).sort("ts", -1).limit(limit))
