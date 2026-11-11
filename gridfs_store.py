import json
from pathlib import Path
import gridfs


def get_fs(db):
    return gridfs.GridFS(db, collection="fs")


def upload_all(db, data_dir):
    data_dir = Path(data_dir)
    manifest = json.loads((data_dir / "files_manifest.txt").read_text(encoding="utf-8"))
    fs = get_fs(db)
    uploaded = []
    for kind, items in (("ebook", manifest["ebooks"]), ("cover", manifest["covers"])):
        for item in items:
            name = item["filename"]
            path = data_dir / name
            for old in fs.find({"filename": name}):
                fs.delete(old._id)
            with path.open("rb") as fh:
                fid = fs.put(fh, filename=name, metadata={
                    "isbn": item["related_isbn"], "kind": kind, "original_name": name,
                })
            uploaded.append({"filename": name, "bytes": path.stat().st_size,
                             "isbn": item["related_isbn"], "kind": kind, "file_id": str(fid)})
    return uploaded


def list_files(db):
    fs = get_fs(db)
    return [{"filename": f.filename, "size": f.length, "upload_date": f.upload_date,
             "metadata": f.metadata} for f in fs.find().sort("uploadDate", 1)]


def download_by_title(db, title, out_dir):
    book = db.books.find_one({"title": {"$regex": title, "$options": "i"}})
    if not book or not book.get("ebook_name"):
        return None, "未找到匹配图书或该图书无电子书"
    name = book["ebook_name"]
    fs = get_fs(db)
    grid_out = fs.find_one({"filename": name})
    if not grid_out:
        return None, f"GridFS 中不存在文件 {name}"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / name
    with target.open("wb") as fh:
        fh.write(grid_out.read())
    ok = target.stat().st_size == grid_out.length
    return {"path": str(target), "bytes": target.stat().st_size,
            "expected": grid_out.length, "verified": ok, "title": book["title"]}, "下载完成"


def verify_manifest(db, data_dir):
    data_dir = Path(data_dir)
    manifest = json.loads((data_dir / "files_manifest.txt").read_text(encoding="utf-8"))
    fs = get_fs(db)
    rows = []
    for items in (manifest["ebooks"], manifest["covers"]):
        for item in items:
            g = fs.find_one({"filename": item["filename"]})
            rows.append({"filename": item["filename"], "source_bytes": item["bytes"],
                         "gridfs_bytes": g.length if g else None,
                         "ok": bool(g) and g.length == item["bytes"]})
    return rows

