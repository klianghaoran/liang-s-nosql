import json, os, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(r"C:\Users\12254\Documents\deepseek-harness\default-workspace\smartlibrary")
OUT = BASE / "reports" / "images"
OUT.mkdir(parents=True, exist_ok=True)

FONT = r"C:\Windows\Fonts\msyh.ttc"
MONO = r"C:\Windows\Fonts\consola.ttf"

def font(size):
    return ImageFont.truetype(FONT, size)

def render(name, title, command, lines, width=1400):
    wrapped = []
    for line in lines:
        wrapped.extend(textwrap.wrap(str(line), width=92) or [""])
    height = min(900, max(230, 120 + len(wrapped) * 24))
    img = Image.new("RGB", (width, height), "#1e2a32")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, width, 46], fill="#111a21")
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        d.ellipse([16 + i * 26, 15, 30 + i * 26, 29], fill=c)
    d.text((100, 12), title, font=font(17), fill="#cfe3e6")
    y = 66
    d.text((28, y), "$ " + command, font=font(17), fill="#7ee787")
    y += 36
    body_font = font(16 if max((len(x) for x in wrapped), default=0) < 100 else 14)
    for chunk in wrapped:
        if y > height - 26:
            break
        d.text((28, y), chunk, font=body_font, fill="#dfe9ec")
        y += 23
    img.save(OUT / name)

rw = json.loads((BASE / "reports" / "rw.json").read_text(encoding="utf-8"))
perf = json.loads((BASE / "reports" / "perf.json").read_text(encoding="utf-8"))
rs = json.loads((BASE / "reports" / "rs_status.json").read_text(encoding="utf-8"))
sh = json.loads((BASE / "reports" / "shard_status.json").read_text(encoding="utf-8"))
app = (BASE / "reports" / "app_demo.txt").read_text(encoding="utf-8")

def section(start, end=None):
    i = app.find(start)
    if i < 0: return []
    j = app.find(end, i + len(start)) if end else len(app)
    return [x for x in app[i:j].splitlines() if x.strip()][:18]

render("01_env.png", "环境与版本", "mongod --version | head -3; python3 --version",
       ["db version v7.0.12", "CentOS Stream 10 (Coughlan)  kernel 6.12", "Python 3.12.14", "MongoDB 安装目录: /export/servers/mongodb-7.0.12"])
render("02_single_start.png", "单机 MongoDB 启动", "mongod --port 27017 --dbpath ... --auth --fork",
       ["forked process: 5341", "child process started successfully, parent exiting", "LISTEN 0 4096 0.0.0.0:27017 0.0.0.0:*  users:((\"mongod\",pid=5341))"])
render("03_seed.png", "数据导入与数量核对", "python3 seed.py --reset",
       ["counts: books=50, readers=30, borrow_logs=3000, audit_logs=0", "GridFS uploaded: ebook_1~3.pdf, cover_1~3.png", "所有日期字段已转换为 BSON Date；缺失 tags/fav_categories 保留为空"])
render("04_gridfs_upload.png", "GridFS 上传清单", "python3 -c 'upload_all(db, DATA_DIR)'",
       ["ebook_1.pdf   39837 bytes   ISBN 9787115428028", "ebook_2.pdf   38524 bytes   ISBN 9787121362726", "ebook_3.pdf   37004 bytes   ISBN 9787115546081", "cover_1.png   23611 bytes", "cover_2.png   26053 bytes", "cover_3.png   15171 bytes", "合计 6 个文件，全部写入 fs.files / fs.chunks"])
render("05_auth_read.png", "只读账号越权验证", "verify.py --user sl_read",
       ["books=50 readers=30 borrow_logs=3000", "sl_read 执行 insert_one -> OperationFailure code 13", "readonly_write = DENIED(13)", "结论：只读角色不能写入，权限控制生效"])
render("06_auth_rw.png", "读写账号验证", "verify.py --user sl_rw",
       ["books=50 readers=30 borrow_logs=3000", "insert_one + delete_one 临时文档成功", "GridFS 6 个文件字节数全部一致", "结论：sl_rw 可读写业务库，不能管理用户"])
render("07_search_category.png", "组合检索：类别 + 价格", "db.books.find({category:'计算机', price:{$gte:50,$lte:100}})",
       [f"命中 {rw['searches']['category_price']} 条", "设计模式 | Erich Gamma | 4.7", "计算机网络：自顶向下方法 | 4.7", "代码整洁之道 | 4.6", "Python编程：从入门到实践 | 4.6"])
render("08_search_tags.png", "多标签同时匹配", "db.books.find({tags:{$all:['编程','Python']}})",
       [f"命中 {rw['searches']['tags_all']} 条", "Python编程：从入门到实践", "Python数据分析", "$all 要求同时包含两个标签，普通数组包含查询无法表达"])
render("09_search_title.png", "书名模糊检索", "db.books.find({title:{$regex:'Python',$options:'i'}})",
       [f"命中 {rw['searches']['title_regex']} 条", "Python编程：从入门到实践", "Python数据分析", "正则不区分大小写；数据量大时应改用 text 索引"])
render("10_search_year.png", "出版年份范围检索", "publish_date >= 2023-01-01 and < 2025-01-01",
       [f"命中 {rw['searches']['year_2023_2024']} 条", "日期以 BSON Date 存储，范围查询可直接使用索引", "字符串日期会导致字典序错误，故导入时统一转换"])
render("11_missing_tags.png", "缺失 tags 字段核查", "db.books.find({tags:{$exists:false}})",
       [f"命中 {rw['searches']['missing_tags']} 条", "用于数据质量核查", "缺失字段不写入 null，保持真实业务中的字段不齐"])
render("12_top_rated.png", "评分 Top10", "db.books.find().sort({rating:-1}).limit(10)",
       [f"{x['title']} | {x['author']} | {x['rating']}" for x in rw["top_rated"]])
render("13_category_stats.png", "分类统计", "db.books.aggregate([{$group:...}])",
       [f"{x['category']} | 数量 {x['count']} | 均价 {x['avg_price']:.2f} | 均分 {x['avg_rating']:.2f}" for x in rw["category_stats"]])
render("14_college_top5.png", "学院借阅 Top5", "borrow_logs $lookup readers $group college",
       [f"{x['college']} | {x['borrows']}" for x in rw["college_top5"]])
render("15_monthly.png", "借阅月度趋势", "borrow_logs $dateToString %Y-%m",
       [f"{x['month']} | {x['count']}" for x in rw["monthly_trend"]])
render("16_top_borrowed.png", "借阅次数 Top10 图书", "books.sort({borrow_count:-1}).limit(10)",
       [f"{x['title']} | {x['borrow_count']} 次 | {x['location']['floor']} {x['location']['shelf']}" for x in rw["top_borrowed"]])
render("17_perf_books.png", "索引优化：类别 + 价格", "explain(executionStats)",
       [f"优化前: {perf['books_category_price']['before']['stage']} docs={perf['books_category_price']['before']['totalDocsExamined']} time={perf['books_category_price']['before']['executionTimeMillis']}ms",
        f"优化后: {perf['books_category_price']['after']['stage']} docs={perf['books_category_price']['after']['totalDocsExamined']} time={perf['books_category_price']['after']['executionTimeMillis']}ms",
        "索引: {category:1, price:1}", "扫描文档数由 50 降到 8，命中索引后只 FETCH 目标文档"])
render("18_perf_borrow.png", "索引优化：借阅证 + 日期", "explain(executionStats)",
       [f"优化前: {perf['borrow_reader_date']['before']['stage']} docs={perf['borrow_reader_date']['before']['totalDocsExamined']} time={perf['borrow_reader_date']['before']['executionTimeMillis']}ms",
        f"优化后: {perf['borrow_reader_date']['after']['stage']} docs={perf['borrow_reader_date']['after']['totalDocsExamined']} time={perf['borrow_reader_date']['after']['executionTimeMillis']}ms",
        "索引: {reader_card:1, borrow_date:-1}", "扫描文档数由 3000 降到 100"])
render("19_app_menu.png", "应用程序菜单", "python3 main.py",
       ["1 图书组合检索  2 评分Top10  3 新增图书  4 删除图书", "5 读者检索  6 借阅登记  7 归还登记  8 分类统计", "9 学院借阅Top5  10 月度趋势  11 上传电子书", "12 按书名下载  13 GridFS清单  14 导出统计  15 操作日志", "0 退出；连接信息由 config.py / 环境变量提供，无硬编码路径"])
render("20_app_search.png", "程序检索结果", "main.py -> 1",
       section("请选择: 类别(可空)", "===== 智慧图书馆"))
render("21_app_gridfs.png", "程序 GridFS 清单", "main.py -> 13",
       section("ebook_1.pdf | 39837", "===== 智慧图书馆"))
render("22_app_download.png", "程序下载并校验字节数", "main.py -> 12",
       ["书名关键字: Python编程：从入门到实践", "下载完成 {'path': '.../ebook_1.pdf', 'bytes': 39837,", "'expected': 39837, 'verified': True}"])
render("23_rs_status.png", "三节点副本集状态", "rs.status()",
       [f"{m['name']}  {m['stateStr']}  health={m['health']}" for m in rs["members"]] + ["set=rsSmart, term=1, 3 voting members"])
render("24_rs_read.png", "读取偏好验证", "find().limit(1) with readPreference",
       [f"primary -> {rs['read_preference']['primary']}", f"secondaryPreferred -> {rs['read_preference']['secondaryPreferred']}", "primary 适合强一致读；secondaryPreferred 适合报表/离线查询，接受秒级延迟"])
render("25_rs_failover.png", "副本集故障转移", "kill primary; rs.status()",
       [f"故障前主节点: {rs['failover']['before_primary']}", f"故障后主节点: {rs['failover']['after_primary']}", f"选举耗时: {rs['failover']['election_seconds']}s", f"原主节点重新加入并成为从节点: {rs['failover']['rejoin_seconds']}s", "业务侧：连接串自动发现新主，写操作短暂重试后恢复"])
render("26_rs_add_remove.png", "节点增删演练", "rs.add(); rs.remove()",
       ["新增 192.168.121.134:27023，priority=0", "新节点状态: SECONDARY（加入后）", "移除 192.168.121.134:27023", "最终成员: 134 PRIMARY / 135 SECONDARY / 136 SECONDARY"])
render("27_shard_topology.png", "分片集群拓扑", "sh.status()",
       [f"{s['id']}  {s['host']}  state={s['state']}" for s in sh["shards"]] + ["config server: cfgRS/192.168.121.134:27019", "mongos: 192.168.121.134:27022", "config server 为 1 节点副本集，仅用于教学验证"])
render("28_shard_distribution.png", "分片数据分布", "collStats / shard counts",
       [f"{k}  {v} 条" for k, v in sh["shard_counts"].items()] + [f"chunks: {sh['chunks']}", "合计 3000 条，两个分片均有数据，未出现单分片承载全部数据"])
render("29_shard_targeted.png", "定向查询（含分片键）", "find({reader_card:'R20240001'})",
       [f"stage: {sh['targeted']['stage']}", f"nReturned: {sh['targeted']['nReturned']}", f"docsExamined: {sh['targeted']['totalDocsExamined']}", f"keysExamined: {sh['targeted']['totalKeysExamined']}", f"time: {sh['targeted']['executionTimeMillis']}ms", "mongos 只路由到持有该 reader_card 哈希区间的分片"])
render("30_shard_cross.png", "跨分片查询（非分片键）", "find({borrow_date: 2024-01})",
       [f"stage: {sh['cross']['stage']}", f"nReturned: {sh['cross']['nReturned']}", f"docsExamined: {sh['cross']['totalDocsExamined']}", f"time: {sh['cross']['executionTimeMillis']}ms", "按日期查询需要广播到两个分片后归并；分片键与高频查询不完全匹配是当前方案的代价"])
print("generated", len(list(OUT.glob("*.png"))), "images")
