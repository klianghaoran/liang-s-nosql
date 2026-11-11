from db import get_db
from config import DATA_DIR
from books import search_books, top_rated, missing_tags, add_book, delete_book
from readers import search_readers
from borrows import borrow_book, return_book
from stats import category_stats, college_top5, monthly_trend, top_borrowed, save_category_stats
from gridfs_store import upload_all, download_by_title, list_files
from audit import recent


def line():
    print("-" * 60)


def show_books(rows, limit=10):
    print(f"共 {len(rows)} 条")
    for b in rows[:limit]:
        parts = [str(b.get(k)) for k in ("isbn", "title", "author", "category") if b.get(k) is not None]
        if b.get("rating") is not None:
            parts.append(f"评分 {b.get('rating')}")
        if b.get("stock") is not None:
            parts.append(f"库存 {b.get('stock')}")
        print(" | ".join(parts))


def main():
    db = get_db()
    while True:
        print("""
===== 智慧图书馆数字资源平台 =====
1. 图书组合检索（类别/价格/标签/书名/年份）
2. 评分 Top10
3. 新增图书
4. 删除图书
5. 读者检索
6. 借阅登记
7. 归还登记
8. 分类统计
9. 学院借阅 Top5
10. 借阅月度趋势
11. 上传电子书/封面到 GridFS
12. 按书名下载电子书并校验
13. GridFS 文件清单
14. 导出分类统计结果
15. 最近操作日志
0. 退出
""")
        choice = input("请选择: ").strip()
        try:
            if choice == "0":
                break
            elif choice == "1":
                category = input("类别(可空): ").strip() or None
                title = input("书名关键字(可空): ").strip() or None
                lo = input("最低价(可空): ").strip()
                hi = input("最高价(可空): ").strip()
                tags = input("标签，逗号分隔(可空): ").strip()
                tag_list = [x.strip() for x in tags.split(",") if x.strip()] if tags else None
                rows = search_books(db, category=category, title=title,
                                    min_price=float(lo) if lo else None,
                                    max_price=float(hi) if hi else None, tags=tag_list)
                show_books(rows)
            elif choice == "2":
                show_books(top_rated(db, 10))
            elif choice == "3":
                isbn = input("ISBN: ").strip()
                title = input("书名: ").strip()
                author = input("作者: ").strip()
                category = input("类别: ").strip()
                price = float(input("价格: ").strip() or 0)
                doc = {"isbn": isbn, "title": title, "author": author, "publisher": "",
                       "category": category, "price": price, "stock": 1, "rating": 0,
                       "borrow_count": 0, "location": {"floor": "", "shelf": "", "copies": 1}}
                add_book(db, doc, actor="menu")
                print("新增成功")
            elif choice == "4":
                isbn = input("ISBN: ").strip()
                print("删除条数:", delete_book(db, isbn, actor="menu"))
            elif choice == "5":
                kw = input("姓名/借阅证关键字: ").strip()
                rows = search_readers(db, kw)
                print(f"共 {len(rows)} 条")
                for r in rows[:10]:
                    print(f"{r.get('card_no')} | {r.get('name')} | {r.get('college')} | {r.get('level')}")
            elif choice == "6":
                card = input("借阅证号: ").strip()
                isbn = input("ISBN: ").strip()
                _, msg = borrow_book(db, card, isbn, actor="menu")
                print(msg)
            elif choice == "7":
                card = input("借阅证号: ").strip()
                isbn = input("ISBN: ").strip()
                _, msg = return_book(db, card, isbn, actor="menu")
                print(msg)
            elif choice == "8":
                for r in category_stats(db):
                    print(f"{r['category']} | 数量 {r['count']} | 均价 {r['avg_price']:.2f} | 均分 {r['avg_rating']:.2f}")
            elif choice == "9":
                for r in college_top5(db):
                    print(f"{r['college']} | {r['borrows']}")
            elif choice == "10":
                for r in monthly_trend(db):
                    print(f"{r['month']} | {r['count']}")
            elif choice == "11":
                print("已上传:", upload_all(db, DATA_DIR))
            elif choice == "12":
                title = input("书名关键字: ").strip()
                info, msg = download_by_title(db, title, DATA_DIR / "downloads")
                print(msg, info)
            elif choice == "13":
                for f in list_files(db):
                    print(f"{f['filename']} | {f['size']} bytes | {f['upload_date']}")
            elif choice == "14":
                rows = save_category_stats(db)
                print("已写入 category_stats，行数:", len(rows))
            elif choice == "15":
                for a in recent(db, 20):
                    print(f"{a['ts']} | {a['action']} | {a['target']} | {a['detail']}")
            else:
                print("无效选项")
        except Exception as e:
            print("操作失败:", type(e).__name__, e)


if __name__ == "__main__":
    main()

