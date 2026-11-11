# 智慧图书馆数字资源平台

《NoSQL 数据库技术与应用（第2版）》期末项目，单人完成。  
作者：梁浩然 / 202414870231 / 24 数据科学与大数据

## 1. 目录

- `config.py`：连接参数（host/port/db/user/password），支持环境变量覆盖
- `db.py`：MongoClient 与索引定义
- `books.py` / `readers.py` / `borrows.py`：业务 CRUD
- `stats.py`：分类统计、学院 Top5、月度趋势、借阅 Top10
- `gridfs_store.py`：GridFS 上传、下载、清单、字节校验
- `audit.py`：操作日志（capped collection）
- `seed.py`：导入三份 JSON，转换日期，上传 6 个文件
- `create_users.py`：创建 sl_read / sl_rw / sl_admin
- `verify.py` / `perf_test.py`：权限、统计、索引验证
- `main.py`：15 项菜单程序

## 2. 运行

```bash
# VM 上使用内置 vendor（无外网）
export PYTHONPATH=/opt/smartlibrary/vendor:/opt/smartlibrary
cd /opt/smartlibrary
python3 seed.py --reset
python3 create_users.py
python3 main.py
```

单机 27017 启动命令：

```bash
/export/servers/mongodb-7.0.12/bin/mongod \
  --port 27017 --dbpath /export/data/smartlibrary/single \
  --bind_ip_all --auth --fork \
  --logpath /export/logs/smartlibrary/single.log \
  --wiredTigerCacheSizeGB 0.25
```

## 3. 账号

| 账号 | 密码 | 角色 |
|---|---|---|
| sl_read | Read@2026 | read@smartlibrary |
| sl_rw | ReadWrite@2026 | readWrite@smartlibrary |
| sl_admin | Admin@2026 | dbOwner@smartlibrary |

## 4. 端口规划

| 组件 | 机器 | 端口 | 说明 |
|---|---|---|---|
| 单机 MongoDB | nosql01 | 27017 | --auth，业务库 + GridFS |
| 副本集 rsSmart | 三台 | 27018 | 134 主，135/136 从 |
| 配置服务器 cfgRS | nosql01 | 27019 | 1 节点副本集 |
| 分片 shard1RS | nosql02 | 27020 | 单节点副本集 |
| 分片 shard2RS | nosql03 | 27021 | 单节点副本集 |
| mongos | nosql01 | 27022 | 连接 cfgRS |

## 5. 数据

`data/` 下为任务书提供的 books.txt、readers.txt、borrow_logs.txt、ebook_1~3.pdf、cover_1~3.png、files_manifest.txt。导入后数量为 50 / 30 / 3000，GridFS 6 个文件。
