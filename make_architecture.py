from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out = Path(r"C:\Users\12254\Documents\deepseek-harness\default-workspace\smartlibrary\reports\images\00_architecture.png")
W, H = 1800, 1000
img = Image.new("RGB", (W, H), "#f7f9f9")
d = ImageDraw.Draw(img)
F = r"C:\Windows\Fonts\msyh.ttc"
def f(s): return ImageFont.truetype(F, s)

def box(x,y,w,h,title,lines,color="#264653",fill="#ffffff"):
    d.rounded_rectangle([x,y,x+w,y+h], radius=16, fill=fill, outline=color, width=3)
    d.rectangle([x,y,x+w,y+46], fill=color)
    d.text((x+18,y+10), title, font=f(24), fill="#ffffff")
    yy=y+62
    for line in lines:
        d.text((x+18,yy), line, font=f(20), fill="#2b3a3a")
        yy+=34

d.text((40,30), "智慧图书馆数字资源平台 · 部署拓扑", font=f(40), fill="#264653")
d.text((40,90), "三台 CentOS Stream 10 虚拟机（VMware NAT 192.168.121.0/24）", font=f(22), fill="#6b7c7c")

box(60,220,360,250,"客户端 / 应用层",["Python 菜单程序 (main.py)","统一连接模块 db.py","GridFS 上传/下载","FinalShell SSH 管理"], "#2a9d8f")
box(60,560,360,300,"单机业务库",["端口 27017（--auth）","dbpath: /export/data/","  smartlibrary/single","集合: books / readers","borrow_logs / audit_logs","GridFS: fs.files / fs.chunks"], "#e76f51")

box(560,220,520,310,"nosql01  192.168.121.134",["单机 MongoDB 27017 (auth)","副本集 rsSmart 27018  PRIMARY","配置服务器 cfgRS 27019","路由 mongos 27022","第四节点演练 27023"], "#264653")
box(1160,220,520,310,"nosql02  192.168.121.135",["副本集 rsSmart 27018  SECONDARY","分片 shard1RS 27020","dbpath: .../shard1"], "#264653")
box(1160,620,520,310,"nosql03  192.168.121.136",["副本集 rsSmart 27018  SECONDARY","分片 shard2RS 27021","dbpath: .../shard2"], "#264653")

# replica arrows
d.line([(1080,360),(1160,360)], fill="#2a9d8f", width=5)
d.line([(1420,530),(1420,620)], fill="#2a9d8f", width=5)
d.text((1090,330), "复制/心跳", font=f(18), fill="#2a9d8f")
d.text((1430,555), "复制/心跳", font=f(18), fill="#2a9d8f")

# app to single and mongos
d.line([(420,340),(560,340)], fill="#e9c46a", width=6)
d.text((430,310), "SSH / 业务连接", font=f(18), fill="#b0892f")
d.line([(420,345),(520,690),(560,690)], fill="#e9c46a", width=6)
d.text((430,700), "单机 27017", font=f(18), fill="#b0892f")

# mongos to shards
d.line([(1080,420),(1160,420)], fill="#e76f51", width=6)
d.text((1085,390), "mongos 路由", font=f(18), fill="#e76f51")
d.line([(1080,460),(1120,700),(1160,700)], fill="#e76f51", width=6)

# bottom notes
d.text((60,920), "说明：单机 27017 承载业务与 GridFS；副本集 27018 验证高可用；27019/27020/27021/27022 组成分片集群。", font=f(22), fill="#465656")
d.text((60,955), "所有实例使用独立 dbpath、独立日志、--wiredTigerCacheSizeGB 0.25，避免相互影响。", font=f(22), fill="#465656")
img.save(out)
print(out)
