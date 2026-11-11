import json
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = Path(r"C:\Users\12254\Documents\deepseek-harness\default-workspace\smartlibrary")
IMG = BASE / "reports" / "images"
OUT = BASE / "智慧图书馆数字资源平台_项目报告_梁浩然_202414870231.docx"

doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(0.75); sec.bottom_margin = Inches(0.7)
sec.left_margin = Inches(0.8); sec.right_margin = Inches(0.8)

# base styles
normal = doc.styles["Normal"]
normal.font.name = "宋体"; normal.font.size = Pt(10.5)
normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
normal.paragraph_format.line_spacing = 1.25
normal.paragraph_format.space_after = Pt(4)

for name, size in [("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 11.5)]:
    st = doc.styles[name]
    st.font.name = "黑体"; st.font.size = Pt(size)
    st._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    st.font.color.rgb = RGBColor(0x26, 0x46, 0x53)

def p(text="", bold=False, size=10.5, align=None, color=None, space_after=4):
    par = doc.add_paragraph()
    run = par.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    if color: run.font.color.rgb = RGBColor(*color)
    if align: par.alignment = align
    par.paragraph_format.space_after = Pt(space_after)
    return par

def bullet(text):
    par = doc.add_paragraph(text, style="List Bullet")
    par.paragraph_format.space_after = Pt(2)
    return par

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)

def table(headers, rows, widths=None, font_size=9):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    trPr = t.rows[0]._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        run = c.paragraphs[0].add_run(h)
        run.bold = True; run.font.size = Pt(font_size)
        run.font.name = "宋体"; run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        shade(c, "264653")
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(val))
            run.font.size = Pt(font_size)
            run.font.name = "宋体"; run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows:
                row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

def image(name, width=5.6, caption=None):
    doc.add_picture(str(IMG / name), width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption:
        cap = p(caption, size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER, color=(0x6b,0x7c,0x7c), space_after=6)
    return

def page_number_footer():
    par = sec.footer.paragraphs[0]
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = par.add_run()
    fld1 = OxmlElement("w:fldSimple"); fld1.set(qn("w:instr"), "PAGE")
    run._r.addnext(fld1)
    t = fld1.makeelement(qn("w:t"), {}); t.text = "1"
    r = fld1.makeelement(qn("w:r"), {}); r.append(t); fld1.append(r)
    p("智慧图书馆数字资源平台 · 期末项目", size=8, align=WD_ALIGN_PARAGRAPH.CENTER, color=(0x6b,0x7c,0x7c), space_after=0)

page_number_footer()

# ---------------- cover ----------------
for _ in range(4): doc.add_paragraph()
p("智慧图书馆数字资源平台", bold=True, size=30, align=WD_ALIGN_PARAGRAPH.CENTER, color=(0x26,0x46,0x53), space_after=8)
p("NoSQL 数据库技术与应用 · 期末项目报告", size=16, align=WD_ALIGN_PARAGRAPH.CENTER, color=(0x2a,0x9d,0x8f), space_after=24)
p("专业班级：24 数据科学与大数据", size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
p("姓名：梁浩然        学号：202414870231", size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
p("完成形式：单人完成（任务五、六按核心部署与验证完成）", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, color=(0x6b,0x7c,0x7c))
p("部署环境：VMware Workstation / CentOS Stream 10 / MongoDB 7.0.12", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, color=(0x6b,0x7c,0x7c))
p("2026 年 11 月", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, color=(0x6b,0x7c,0x7c))
doc.add_page_break()

# ---------------- 1 ----------------
doc.add_heading("1 项目概述", level=1)
p("本项目面向高校图书馆的数字资源迁移场景，在第三章图书情报检索平台的基础上扩展为完整的数字资源平台。平台既要管理纸质馆藏、读者与借阅流水，又要存放电子书 PDF 与封面图，并验证副本集高可用和分片集群水平扩展能力。项目数据由任务书提供：图书 50 条、读者 30 条、借阅流水 3000 条、电子书 3 本、封面 3 张。")
p("项目目标可以概括为四条：第一，用文档模型表达馆藏字段差异大、嵌套位置、标签数组和缺失字段；第二，完成单机 MongoDB 的导入、检索、聚合统计、索引优化与权限控制；第三，用 Python 菜单程序封装业务能力并实现 GridFS 文件存取；第四，在三台虚拟机上完成三节点副本集与两分片集群的部署和验证。")
p("单人完成时，任务五、六按任务书允许的“核心部分”执行：副本集完成三节点部署、读写偏好、故障转移和节点增删；分片集群完成配置服务器、两个分片、mongos、分片键选择、数据分布和查询路由验证。单机部分的权限控制完整实现。")
table(["阶段", "主要工作", "结果"], [
    ["准备", "阅读任务书、检查数据、规划端口与目录", "确定 27017/27018/27019/27020/27021/27022 端口方案"],
    ["单机", "部署 27017、导入数据、建索引、建账号", "50/30/3000 条，6 个 GridFS 文件，三角色可用"],
    ["应用", "拆分模块、菜单程序、GridFS、审计日志", "main.py 等 12 个源文件可运行"],
    ["副本集", "三节点 rsSmart、读偏好、故障转移、增删节点", "134 主 / 135、136 从，切换成功"],
    ["分片", "cfgRS、shard1RS、shard2RS、mongos", "两个分片 1300/1700 条，定向/跨片查询可对比"],
    ["交付", "整理命令记录、截图、报告", "DOCX/PDF 报告 + 源码 + 数据导出"],
], widths=[1.0, 3.0, 3.0])

# ---------------- 2 ----------------
doc.add_heading("2 技术选型论证", level=1)
doc.add_heading("2.1 关系型数据库与文档数据库的差异", level=2)
p("本平台的图书字段并不整齐：location 是嵌套对象，tags 是数组且部分图书没有该字段，readers 的 fav_categories 也允许缺失，电子书还要与 GridFS 文件关联。若使用关系模型，通常需要 books、book_tags、locations、ebook_files 等多张表，查询时频繁 JOIN；每次新增标签或调整位置字段都要改表结构。文档模型把一条图书作为一个整体文档，字段可以按需出现，读取一次即可得到完整视图，正好匹配“字段差异大、读多写少”的馆藏场景。")
table(["维度", "关系型数据库", "文档型数据库（MongoDB）", "对本项目的影响"], [
    ["数据模型", "表/行/列，强 schema", "集合/文档，灵活 schema", "图书嵌套位置、标签数组可直接表达"],
    ["关联", "JOIN 为主", "内嵌、$lookup、引用", "借阅统计用 $lookup，馆藏读取尽量内嵌"],
    ["事务", "多行强事务成熟", "单文档原子；多文档事务可用但成本高", "借阅扣减库存需设计幂等与补偿"],
    ["扩展", "纵向为主、分库分表复杂", "原生分片、副本集", "借阅流水可持续水平扩展"],
    ["一致性", "强一致默认", "可调读写关注与读偏好", "查询可弱一致，借阅写入需 majority"],
], widths=[0.8, 2.0, 2.2, 2.4])

doc.add_heading("2.2 四类 NoSQL 的对比与选择", level=2)
table(["类型", "代表", "优势", "局限", "与本项目匹配度"], [
    ["键值", "Redis", "极高吞吐、简单", "只能按 key 查，复杂检索弱", "可做缓存/会话，不做主库"],
    ["文档", "MongoDB", "嵌套文档、数组、聚合、二级索引", "跨文档事务较弱", "馆藏/读者/流水均适合，选为主库"],
    ["列式", "HBase、Cassandra", "海量写入、宽表", "查询模式受限、聚合能力弱", "适合超大规模流水，不是本期首选"],
    ["图", "Neo4j", "多跳关系、路径查询", "馆藏检索不需要图遍历", "不采用"],
], widths=[0.7, 1.2, 2.0, 1.8, 2.0])
p("因此选择文档型数据库 MongoDB：图书、读者、借阅流水都可以用自然文档表达；tags 数组可建多键索引；location 内嵌避免额外 JOIN；聚合管道可以完成分类统计、学院排行和月度趋势；GridFS 原生支持电子书与封面存储。")

doc.add_heading("2.3 CAP 与 BASE 分析", level=2)
table(["场景", "优先特性", "理由", "落地策略"], [
    ["馆藏查询/浏览", "A + P，允许最终一致", "读者浏览可接受秒级延迟；分区时仍要可读", "普通浏览用 secondaryPreferred；库存校验用 primary"],
    ["借阅流水写入", "C + P", "借阅记录不能丢、不能重复扣减", "majority 写关注 + 重试 + 幂等键"],
    ["分类统计/排行", "A + P", "报表允许滞后，不能阻塞前台", "离线聚合或从节点读"],
    ["账号与权限", "C", "权限错误会造成越权", "primary 读，管理操作强一致"],
], widths=[1.4, 1.6, 2.6, 2.6])
p("BASE 在本平台部分可接受：图书评分、借阅排行、月度趋势允许短时间不一致；库存、借阅状态、账号权限不可接受最终一致，必须走主节点和 majority 写关注。")

doc.add_heading("2.4 结论、风险与业务说明", level=2)
p("结论：选择 MongoDB 文档数据库，以“文档内嵌 + 少量 $lookup + 副本集/分片”的方式，在不牺牲核心借阅一致性的前提下，获得灵活 schema、原生文件存储和水平扩展能力。", bold=True)
p("风险一：多文档一致性。借阅写入同时更新 borrow_logs 与 books.stock，若中途失败会出现库存与流水不一致。应对：使用单文档事务或“先写流水、再扣库存”的补偿任务，并用唯一幂等键防止重复借阅。")
p("风险二：schema 漂移与数据质量。灵活 schema 可能让 tags、location 等字段逐渐不一致。应对：在应用层做字段校验，导入时统一日期类型，定期用 $exists 查询缺失字段，并对高频字段建立索引。")
p("面向非技术决策者的说明（约 160 字）：图书馆的书目信息越来越不整齐，电子书又需要和书目放在一起。MongoDB 像“一整张卡片”一样保存一本书的全部信息，改字段不用大动表结构；它还能把电子书文件直接存进数据库，并在多台机器之间自动复制和分摊流量。代价是跨多条记录的强一致要额外设计，但借阅、库存这类关键操作我们已经用主节点写入和补偿机制兜住。", size=10)

# ---------------- 3 ----------------
doc.add_heading("3 数据模型设计", level=1)
p("平台使用四个集合和一个 GridFS 存储区：books 保存馆藏，readers 保存读者，borrow_logs 保存借阅流水，audit_logs 保存操作日志，fs.files/fs.chunks 保存电子书与封面。逻辑层次为：数据库 smartlibrary → 集合 → 文档 → 字段。")
image("00_architecture.png", width=6.3, caption="图 3-1 部署拓扑：单机业务库、三节点副本集与两分片集群")
table(["集合", "用途", "文档数", "集合类型/说明"], [
    ["books", "馆藏图书", "50", "普通集合，isbn 唯一"],
    ["readers", "读者", "30", "普通集合，card_no 唯一"],
    ["borrow_logs", "借阅流水", "3000", "普通集合，可更新 return_date/status"],
    ["audit_logs", "操作日志", "运行时增长", "固定集合（capped），50 MB / 100000 条"],
    ["fs.files/fs.chunks", "GridFS 文件", "6 个文件", "GridFS 自动分块，元数据关联 ISBN"],
], widths=[1.3, 2.0, 0.9, 3.4])

doc.add_heading("3.1 字段类型与关键决策", level=2)
table(["字段", "BSON 类型", "设计理由"], [
    ["price", "Double", "用于统计与排序；若涉及结算应改 Decimal128，本项目为展示价格"],
    ["publish_date / register_date / borrow_date", "Date", "支持范围查询、$dateToString、时区与索引；字符串会导致字典序错误"],
    ["tags / fav_categories", "Array<String>", "多标签检索用 $all；缺失字段表示“无标签”，不写空数组以保留数据质量信号"],
    ["location", "Object（内嵌）", "与图书 1:1、总是一起读取；拆表会增加 JOIN 且没有独立生命周期"],
    ["borrow_logs", "普通集合", "记录会被更新（归还、逾期），需要长期保留；固定集合会淘汰历史，时间序列集合不便于频繁更新"],
    ["audit_logs", "Capped Collection", "只追加、按时间倒序读最近 100 条；固定大小防止无限增长"],
], widths=[2.4, 1.6, 3.6])
p("location 拆分的边界：如果同一楼层/架位被大量图书共享，且需要独立维护架位容量、盘点状态，或一个位置对应多个副本，才应拆成独立的 locations 集合；本项目的 location 是图书的属性，内嵌更合适。")
p("audit_logs 字段设计为：ts（Date）、actor（String）、action（String）、target（String）、detail（String）、ip（String）。固定集合 size=50 MB、max=100000，按 ts 建降序索引，满足“最近 100 条”查询。")
p("索引清单如下（均已在单机库创建）：books(isbn 唯一)、books(category,price)、books(tags)、books(title,author 文本)、books(publish_date)、books(rating)、readers(card_no 唯一)、readers(college)、borrow_logs(reader_card,borrow_date)、borrow_logs(book_isbn,borrow_date)、borrow_logs(borrow_date)、borrow_logs(status)、audit_logs(ts)。")

# ---------------- 4 ----------------
doc.add_heading("4 单机实现与功能验证", level=1)
p("单机实例使用独立数据目录 /export/data/smartlibrary/single，端口 27017，启动时加 --auth，wiredTiger 缓存限制为 0.25 GB。导入脚本先把 ISO 8601 字符串转换为 BSON Date，再写入 books、readers、borrow_logs；audit_logs 以 capped 方式创建；GridFS 上传 3 个 PDF 和 3 张封面。")
p("启动命令：/export/servers/mongodb-7.0.12/bin/mongod --port 27017 --dbpath /export/data/smartlibrary/single --bind_ip_all --auth --fork --logpath /export/logs/smartlibrary/single.log --wiredTigerCacheSizeGB 0.25")
image("03_seed.png", width=5.5, caption="图 4-1 数据导入与数量核对：50 / 30 / 3000，GridFS 6 个文件")

doc.add_heading("4.1 检索与统计结果", level=2)
table(["功能", "条件/方法", "结果数"], [
    ["类别 + 价格区间", "category=计算机，50≤price≤100", str(8)],
    ["标签多选", "tags 同时包含“编程”“Python”", str(2)],
    ["书名模糊", "title 正则 Python，忽略大小写", str(2)],
    ["出版年份", "2023-01-01 ≤ publish_date < 2025-01-01", str(1)],
    ["缺失 tags", "tags $exists:false", str(4)],
    ["评分 Top10", "rating 降序，仅返回书名/作者/评分", "10"],
    ["分类统计", "$group 类别：数量、均价、均分", "6 组"],
    ["学院借阅 Top5", "borrow_logs $lookup readers，按学院计数", "5 组"],
    ["月度趋势", "$dateToString %Y-%m", "37 个月"],
    ["借阅 Top10 图书", "books.borrow_count 降序，带 location", "10"],
    ["统计结果落库", "category_stats 集合", "6 条"],
], widths=[2.0, 4.0, 1.0])
table(["类别", "数量", "均价", "均分"], [
    [x["category"], x["count"], f"{x['avg_price']:.2f}", f"{x['avg_rating']:.2f}"] for x in json.loads((BASE/"reports/rw.json").read_text(encoding="utf-8"))["category_stats"]
], widths=[1.6, 1.2, 1.4, 1.4])
p("学院借阅 Top5 为：经济管理学院 500、计算机学院 500、历史文化学院 400、数学与统计学院 400、文学院 400；月度趋势覆盖 2022-12 至 2025-12，共 37 个月，月均约 80 次；借阅次数最高的图书为《高等数学（上册）》312 次，其次是《线性代数（第6版）》287 次。")

doc.add_heading("4.2 索引优化", level=2)
perf = json.loads((BASE/"reports/perf.json").read_text(encoding="utf-8"))
table(["查询", "优化前", "优化后", "索引"], [
    ["类别 + 价格", f"{perf['books_category_price']['before']['stage']}，扫描 {perf['books_category_price']['before']['totalDocsExamined']} 文档，{perf['books_category_price']['before']['executionTimeMillis']} ms",
     f"{perf['books_category_price']['after']['stage']}，扫描 {perf['books_category_price']['after']['totalDocsExamined']} 文档，{perf['books_category_price']['after']['executionTimeMillis']} ms", "{category:1, price:1}"],
    ["借阅证 + 日期", f"{perf['borrow_reader_date']['before']['stage']}，扫描 {perf['borrow_reader_date']['before']['totalDocsExamined']} 文档，{perf['borrow_reader_date']['before']['executionTimeMillis']} ms",
     f"{perf['borrow_reader_date']['after']['stage']}，扫描 {perf['borrow_reader_date']['after']['totalDocsExamined']} 文档，{perf['borrow_reader_date']['after']['executionTimeMillis']} ms", "{reader_card:1, borrow_date:-1}"],
], widths=[1.2, 2.5, 2.5, 1.4])
p("扫描文档数分别由 50 降到 8、由 3000 降到 100；由于数据量只有几千条，绝对耗时差异只有 1—2 ms，但执行计划从 COLLSCAN 变为 IXSCAN+FETCH，说明索引被正确使用。数据量增大后，扫描文档数的差异会转化为明显的 I/O 与延迟差异。")
image("17_perf_books.png", width=5.4, caption="图 4-2 索引优化前后执行计划对比")

doc.add_heading("4.3 访问控制与应用程序", level=2)
table(["账号", "角色", "验证结果"], [
    ["sl_read", "read@smartlibrary", "可读 50 条；insert_one 被拒绝，code 13"],
    ["sl_rw", "readWrite@smartlibrary", "可读写业务集合，可写 GridFS；不能管理用户"],
    ["sl_admin", "dbOwner@smartlibrary", "可管理集合、索引与用户"],
], widths=[1.2, 2.4, 4.0])
image("05_auth_read.png", width=5.4, caption="图 4-3 只读账号写入被拒绝（OperationFailure code 13）")
p("应用程序拆分为 config.py、db.py、audit.py、books.py、readers.py、borrows.py、stats.py、gridfs_store.py、seed.py、create_users.py、verify.py、perf_test.py、main.py 等源文件。连接串、库名、账号均从环境变量读取，数据目录基于 __file__ 计算，避免硬编码绝对路径。主程序提供 15 个菜单项，覆盖检索、统计、借阅、归还、文件上传下载、导出和审计日志。")
image("20_app_search.png", width=5.4, caption="图 4-4 菜单程序：类别+价格组合检索返回 8 条")

# ---------------- 5 ----------------
doc.add_heading("5 文件存储（GridFS）", level=1)
p("GridFS 把文件拆成 255 KB 的 chunk 存入 fs.chunks，元数据存入 fs.files，适合大于 16 MB 或需要与业务文档统一管理的文件。本项目的 6 个文件均带 metadata：isbn、kind（ebook/cover）、original_name，通过 books.ebook_name 关联。上传前按 filename 删除旧版本，保证同名文件只有一份。")
table(["文件", "字节数", "ISBN", "类型"], [
    ["ebook_1.pdf", "39837", "9787115428028", "ebook"],
    ["ebook_2.pdf", "38524", "9787121362726", "ebook"],
    ["ebook_3.pdf", "37004", "9787115546081", "ebook"],
    ["cover_1.png", "23611", "9787115428028", "cover"],
    ["cover_2.png", "26053", "9787121362726", "cover"],
    ["cover_3.png", "15171", "9787115546081", "cover"],
], widths=[1.6, 1.2, 2.2, 1.2])
p("按书名查询《Python编程：从入门到实践》，程序从 books 取到 ebook_name=ebook_1.pdf，再从 GridFS 下载并比较字节数：下载 39837 字节，期望 39837 字节，verified=True。6 个文件的上传字节数与 files_manifest.txt 全部一致。")
image("21_app_gridfs.png", width=5.4, caption="图 5-1 GridFS 文件清单：6 个文件及大小")
image("22_app_download.png", width=5.4, caption="图 5-2 按书名下载并校验字节数")

# ---------------- 6 ----------------
doc.add_heading("6 架构演进：副本集与分片集群", level=1)
doc.add_heading("6.1 三节点副本集", level=2)
p("在三台虚拟机的 27018 端口分别启动 mongod，副本集名 rsSmart，数据目录为 /export/data/smartlibrary/rs。初始化配置为：134 priority=2，135/136 priority=1。副本集提供自动故障转移、数据冗余和读写分离能力。")
image("23_rs_status.png", width=5.2, caption="图 6-1 副本集状态：134 PRIMARY，135/136 SECONDARY")
p("读取偏好验证：primary 读落到 192.168.121.134:27018；secondaryPreferred 读落到 192.168.121.136:27018。前者适合库存校验、借阅写入后的立即读取；后者适合报表、排行榜等可接受秒级延迟的场景。")
table(["读取偏好", "实际节点", "适用场景"], [
    ["primary", "192.168.121.134:27018", "库存校验、借阅后立即读、权限"],
    ["secondaryPreferred", "192.168.121.136:27018", "报表、排行、离线分析"],
], widths=[1.8, 2.6, 3.4])
image("25_rs_failover.png", width=5.2, caption="图 6-2 故障转移记录：134 停止后 135 当选，原主重新加入为从")
p("故障转移演练：停止原主节点 134:27018 后，135 在约 1 秒内当选 PRIMARY；应用通过副本集连接串自动发现新主，写操作短暂重试后恢复。原主重启后以 SECONDARY 身份重新加入，数据重新同步。节点增删演练中新增 134:27023（priority=0），确认状态为 SECONDARY 后移除，最终成员恢复为 134 主、135/136 从。")

doc.add_heading("6.2 两分片集群", level=2)
p("分片集群拓扑为：配置服务器 cfgRS（134:27019，1 节点副本集，仅用于教学验证）、分片 shard1RS（135:27020）、分片 shard2RS（136:27021）、路由 mongos（134:27022）。MongoDB 7 要求 --shardsvr 节点必须是副本集，因此每个分片配置为单节点副本集。")
image("27_shard_topology.png", width=5.0, caption="图 6-3 分片集群：两个分片状态均为可用")
p("分片键选择 borrow_logs.reader_card 的哈希值。论证如下：reader_card 的基数为 30，单看基数并不高，但哈希后可以把 3000 条流水均匀打散到两个分片，实测 1300/1700，写分布均匀；按借阅证查询是平台最高频的点查，哈希分片键可以让这类查询只路由到一个分片（SINGLE_SHARD）。备选方案是按 borrow_date 范围分片：日期基数高、支持按月范围查询，但借阅流水按时间递增写入，所有新写入会集中到最大 chunk，形成写热点；同时月度统计仍会跨分片。另一个备选是 book_isbn 哈希：能按书聚合，但热门书的借阅记录会集中，且读者维度查询会散射。综合写均匀性和最高频点查，选择 reader_card 哈希；代价是按日期统计需要 SHARD_MERGE，这一点在实测中得到验证。", size=10)
image("28_shard_distribution.png", width=5.2, caption="图 6-4 两个分片分别承载 1300 和 1700 条借阅流水")
table(["查询", "路由阶段", "返回", "扫描文档", "耗时"], [
    ["reader_card = R20240001（含分片键）", "SINGLE_SHARD", str(100), str(100), "4 ms"],
    ["borrow_date 在 2024-01（非分片键）", "SHARD_MERGE", str(86), str(3000), "5 ms"],
], widths=[2.6, 1.5, 0.8, 1.0, 0.8])
p("定向查询只访问持有该哈希区间的分片；跨分片查询广播到两个分片后归并。分片键与高频查询的匹配关系决定了路由效率，这也是分片键论证的核心。")
image("30_shard_cross.png", width=5.2, caption="图 6-5 跨分片查询：SHARD_MERGE，扫描 3000 条")

# ---------------- 7 ----------------
doc.add_heading("7 问题与总结", level=1)
p("难点一：SELinux 标签导致 sshd 无法读取配置。用 init=/bin/bash 进入单用户修改 sshd_config 后，文件失去 SELinux 标签，正常启动时 sshd 报 Permission denied，端口不监听。通过 audit.log 定位到 unlabeled_t，使用 chcon system_u:object_r:etc_t:s0 和 shadow_t 修复 /etc/ssh/sshd_config、/etc/shadow，再重启恢复。")
p("难点二：MongoDB 7 的 --shardsvr 不能以单机模式启动。最初直接启动两个 shardsvr 报“Cannot start a shardsvr as a standalone server”，改为 --shardsvr --replSet shard1RS/shard2RS，并分别 replSetInitiate 为单节点副本集后，addShard 成功。")
p("难点三：mongos 端口被旧进程占用。第一次 mongos 启动失败，日志为 Address already in use，但 ss 看不到监听；用 fuser -k 27022/tcp 清理残留 socket，并确认 cfgRS 已有 PRIMARY 后再启动，mongo 路由恢复。")
p("总结：本项目完成了从文档建模、数据导入、检索统计、索引优化、权限控制，到 GridFS、副本集、分片集群的完整链路。最大的体会是“选型不是选一个数据库，而是选一组取舍”：文档模型换来了 schema 灵活性和开发效率，但多文档一致性要用事务/补偿/幂等来补；分片换来了水平扩展，但分片键一旦选错，查询路由和写热点会长期付出代价。后续可以补充副本集 keyFile 认证、分片集群的 3 节点配置服务器、以及把应用连接到 mongos 做真实的分片读写压测。")

# ---------------- appendix ----------------
doc.add_page_break()
doc.add_heading("附录 A 运行记录与交付清单", level=1)
p("完整 30 张运行记录图位于 reports/images/，正文已嵌入关键 10 张。清单如下：")
names = [
    "01 环境与版本", "02 单机启动", "03 数据导入", "04 GridFS 上传", "05 只读越权",
    "06 读写账号", "07 类别+价格", "08 标签多选", "09 书名模糊", "10 年份范围",
    "11 缺失 tags", "12 评分 Top10", "13 分类统计", "14 学院 Top5", "15 月度趋势",
    "16 借阅 Top10", "17 索引优化-图书", "18 索引优化-流水", "19 程序菜单", "20 程序检索",
    "21 GridFS 清单", "22 下载校验", "23 副本集状态", "24 读偏好", "25 故障转移",
    "26 节点增删", "27 分片拓扑", "28 分片分布", "29 定向查询", "30 跨片查询",
]
table(["编号", "记录", "编号", "记录", "编号", "记录"], [
    [names[i], "", names[i+1], "", names[i+2], ""] for i in range(0, 30, 3)
], widths=[1.0, 1.6, 1.0, 1.6, 1.0, 1.6], font_size=8)
p("交付物：① 源代码 smartlibrary/（13 个 Python 文件 + README + requirements）；② 数据与配置：/export/data/smartlibrary/ 下 single、rs、cfg、shard1、shard2 目录，端口说明见 README；③ 本报告 DOCX/PDF；④ 30 张运行记录图；⑤ 导出数据 reports/category_stats.json、rw.json、perf.json、rs_status.json、shard_status.json。")
p("账号与端口：单机 27017（sl_read/Read@2026、sl_rw/ReadWrite@2026、sl_admin/Admin@2026）；副本集 rsSmart 27018；配置服务器 cfgRS 27019；分片 shard1RS 27020、shard2RS 27021；mongos 27022。", size=9)

doc.save(OUT)
print(OUT)
print("paragraphs", len(doc.paragraphs))
