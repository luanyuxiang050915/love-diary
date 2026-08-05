# PostgreSQL 使用教程（恋爱日记项目版）

> 本教程写给**一直用 MySQL、刚接触 PostgreSQL** 的你，全程结合本项目的实际环境：
> - 服务器：Ubuntu 22.04，PostgreSQL 14
> - 数据库：`love_diary`，用户：`loveuser`
> - 数据表：`users` / `diaries` / `login_logs` / `anniversaries`
> - 数据库密码：见 `/opt/love-diary/server/.env` 的 `DATABASE_URL`（下文用 `<密码>` 代替）

---

## 目录

1. [MySQL → PostgreSQL 快速对照](#1-mysql--postgresql-快速对照)
2. [怎么登录](#2-怎么登录)
3. [psql 内置命令（\ 开头）](#3-psql-内置命令--开头)
4. [常用 SQL（结合项目表）](#4-常用-sql结合项目表)
5. [用户与权限管理](#5-用户与权限管理)
6. [备份与恢复](#6-备份与恢复)
7. [连接串与特殊字符](#7-连接串与特殊字符)
8. [常见坑速查（血泪版）](#8-常见坑速查血泪版)

---

## 1. MySQL → PostgreSQL 快速对照

### 1.1 常用命令对照表

| 你想做的事 | MySQL | PostgreSQL |
|---|---|---|
| 列出所有数据库 | `SHOW DATABASES;` | `\l` |
| 切换数据库 | `USE love_diary;` | `\c love_diary` |
| 列出所有表 | `SHOW TABLES;` | `\dt` |
| 看表结构 | `DESC users;` | `\d users` |
| 看建表语句 | `SHOW CREATE TABLE users;` | `\d+ users` |
| 查版本 | `SELECT VERSION();` | `SELECT version();` |
| 退出 | `exit` | `\q` |
| 看所有用户 | `SELECT User FROM mysql.user;` | `\du` |

> ⚠️ **MySQL 的 `SHOW database` / `USE xxx` 在 PostgreSQL 里全都不存在**，会直接报 `syntax error`。要用 `\` 开头的 psql 命令代替。

### 1.2 核心概念差异

| 概念 | MySQL | PostgreSQL | 说明 |
|---|---|---|---|
| 自增主键 | `AUTO_INCREMENT` | `SERIAL` 或 `GENERATED ALWAYS AS IDENTITY` | 本项目用的是 `Integer + primary_key`，SQLAlchemy 自动生成 `SERIAL` |
| 取刚插入的 id | `LAST_INSERT_ID()` | `INSERT ... RETURNING id;` | PostgreSQL 更强大，能返回任意字段 |
| 引擎 | `ENGINE=InnoDB/MyISAM` | 无此概念 | PostgreSQL 只有一个存储引擎，不用选 |
| 字符串引号 | `'abc'` 或 `"abc"` 都行 | 字符串只能用**单引号** `'abc'` | 双引号 `"abc"` 表示**标识符**（表名/列名），乱用会报错 |
| 标识符 | 默认不区分大小写 | **区分大小写**（未加引号会被折叠成小写） | 项目里的表名都是小写，正常用没问题 |
| 空值函数 | `IFNULL(x, 0)` | `COALESCE(x, 0)` | 两个都支持，PostgreSQL 推荐 COALESCE |
| 日期格式化 | `DATE_FORMAT(d, '%Y-%m-%d')` | `TO_CHAR(d, 'YYYY-MM-DD')` | 格式符从 `%` 换成 `YYYY/MM/DD` |
| 当前日期 | `CURDATE()` / `NOW()` | `CURRENT_DATE` / `NOW()` | 两个库都有 `NOW()` |
| 拼接字符串 | `CONCAT(a, b)` | `CONCAT(a, b)` 或 `a \|\| b` | 都支持 CONCAT |
| 分页 | `LIMIT 10 OFFSET 20` | `LIMIT 10 OFFSET 20` | 语法相同 |
| 改表 | `ALTER TABLE ... MODIFY COLUMN` | `ALTER TABLE ... ALTER COLUMN` | 关键字略有不同 |

### 1.3 数据类型差异（常见）

| 用途 | MySQL | PostgreSQL |
|---|---|---|
| 整数 | `INT` | `INTEGER`（可简写 `INT`） |
| 自增 | `INT AUTO_INCREMENT` | `SERIAL` |
| 小数 | `DECIMAL(10,2)` | `NUMERIC(10,2)` |
| 文本 | `VARCHAR(255)` / `TEXT` | `VARCHAR(255)` / `TEXT`（都支持） |
| JSON | `JSON` | `JSONB`（推荐，支持索引和查询） |
| 布尔 | `TINYINT(1)` | `BOOLEAN`（`true/false`） |
| 日期 | `DATE` / `DATETIME` | `DATE` / `TIMESTAMP` |
| 二进制 | `BLOB` | `BYTEA` |

---

## 2. 怎么登录

PostgreSQL 有**两种连接方式**，认证规则完全不同（这是最大的坑之一）：

### 2.1 方式一：socket 连接 + peer 认证（免密）

```bash
sudo -u postgres psql            # 以 postgres 系统用户身份进入（免密）
sudo -u postgres psql -d love_diary   # 直接进 love_diary 库（推荐）
```

**规则**：`peer` 认证 = 系统用户名 == 数据库用户名，直接放行。
你用 `sudo -u postgres` 把系统用户切成了 `postgres`，正好匹配数据库里的 `postgres` 用户，所以免密。

### 2.2 方式二：TCP 连接 + 密码认证（要输密码）

```bash
psql -h localhost -U loveuser -d love_diary
# 提示 Password for user loveuser: 输入 .env 里的密码
```

**规则**：`-h localhost` 走 TCP，认证方式是 `scram-sha-256`（密码认证），所以必须输密码。

### 2.3 你踩过的坑

```bash
psql -U loveuser -d love_diary        # ❌ 报 Peer authentication failed
psql -h localhost -U loveuser -d love_diary  # ✅ 走密码认证，能进
```

> 不带 `-h` 走 socket + peer，系统里没有叫 `loveuser` 的系统用户 → 认证失败。
> **记住：本地日常查库用 `sudo -u postgres psql -d love_diary`（免密、省事）。**

### 2.4 登录后先确认自己在哪

```sql
\conninfo          -- 看当前连的哪个库、哪个用户
SELECT current_database();   -- 或者用这个
```

> ⚠️ **血泪教训**：`sudo -u postgres psql` 默认连的是 `postgres` 库，不是 `love_diary`！在 `postgres` 库里 `SELECT * FROM users` 会报"表不存在"，或查不到任何数据。**一定要先 `\c love_diary` 或登录时直接 `-d love_diary`。**

---

## 3. psql 内置命令（\ 开头）

```sql
\l              -- 列出所有数据库（对应 SHOW DATABASES）
\c love_diary   -- 切换数据库（对应 USE love_diary）
\dt             -- 列出所有表（对应 SHOW TABLES）
\d users        -- 看 users 表结构（对应 DESC users）
\d+ users       -- 更详细，含注释、索引
\du             -- 列出所有角色/用户
\dn             -- 列出 schema
\dp             -- 看表的权限
\x              -- 竖排显示（字段多时超好用，再按一次取消）
\timing         -- 显示每条 SQL 的执行耗时
\conninfo       -- 当前连接信息
\q              -- 退出
```

---

## 4. 常用 SQL（结合项目表）

先登录并切库：

```bash
sudo -u postgres psql -d love_diary
```

### 4.1 查询

```sql
-- 所有用户（注意：密码是哈希，看不到明文，这是正常的）
SELECT id, username, nickname, partner_id, bind_code FROM users;

-- 所有日记，带作者名
SELECT u.username, d.date, d.mood, left(d.content, 30) AS 内容预览
FROM diaries d
JOIN users u ON u.id = d.user_id
ORDER BY d.date DESC;

-- 最近 10 条登录记录
SELECT u.username, l.ip, l.created_at
FROM login_logs l JOIN users u ON u.id = l.user_id
ORDER BY l.created_at DESC
LIMIT 10;

-- 纪念日 + 用户名
SELECT u.username, a.name, a.date
FROM anniversaries a JOIN users u ON u.id = a.user_id;

-- 模糊查询（和 MySQL 一样）
SELECT * FROM users WHERE username LIKE '%测试%';
```

### 4.2 统计

```sql
SELECT count(*) FROM users;        -- 用户总数
SELECT count(*) FROM diaries;      -- 日记总数

-- 每人日记数排行
SELECT u.username, count(d.id) AS 日记数
FROM users u LEFT JOIN diaries d ON d.user_id = u.id
GROUP BY u.username
ORDER BY 日记数 DESC;

-- 未绑定伴侣的人
SELECT username FROM users WHERE partner_id IS NULL;

-- 今天的日记
SELECT * FROM diaries WHERE date = CURRENT_DATE;
```

### 4.3 插入（含 RETURNING）

```sql
-- 手动插入一条用户（仅测试用，真实注册请走接口，密码要哈希！）
INSERT INTO users (username, password_hash, nickname)
VALUES ('test1', '这里是bcrypt哈希', '测试一')
RETURNING id;              -- 立即返回新行的 id（对应 LAST_INSERT_ID）

-- 插入日记
INSERT INTO diaries (user_id, content, mood, date)
VALUES (1, '今天很开心', '开心', CURRENT_DATE)
RETURNING id;
```

### 4.4 修改 / 删除（慎用！）

```sql
-- 解除某人绑定
UPDATE users SET partner_id = NULL, bind_code = NULL WHERE id = 2;

-- 把某篇日记设为"仅自己可见"
UPDATE diaries SET visible_to_partner = false WHERE id = 5;

-- 删除
DELETE FROM login_logs WHERE id = 123;
DELETE FROM anniversaries WHERE id = 8;
```

> ⚠️ **铁律**：生产库执行 UPDATE / DELETE 前，**先 SELECT 同款 WHERE 确认选中的行**，再执行。

---

## 5. 用户与权限管理

### 5.1 创建用户 / 建库 / 授权（README 部署脚本）

```bash
sudo -u postgres psql <<'EOF'
CREATE USER loveuser WITH PASSWORD '你的密码';
CREATE DATABASE love_diary OWNER loveuser;
EOF
```

> 库的 `OWNER` 设为该用户，则该用户对该库有全部权限（包括建表），不用再单独 GRANT。

### 5.2 改密码

```bash
sudo -u postgres psql -c "ALTER USER loveuser WITH PASSWORD '新密码';"
```

> 改完**必须同步改 `.env` 里的 `DATABASE_URL` 并重启服务**，否则服务连不上。

### 5.3 常用权限语句

```sql
-- 授权（一般用 OWNER 就不需要了）
GRANT ALL PRIVILEGES ON DATABASE love_diary TO loveuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO loveuser;

-- 查看某表权限
\dp users
```

---

## 6. 备份与恢复

### 6.1 逻辑备份（最常用）

```bash
# 备份整个库（纯 SQL 文本，可读、可 diff）
pg_dump -h localhost -U loveuser -d love_diary > love_diary_$(date +%Y%m%d).sql
# 会提示输密码；或加环境变量免交互：
# PGPASSWORD='密码' pg_dump -h localhost -U loveuser -d love_diary > backup.sql

# 压缩格式（体积小、恢复快，推荐）
pg_dump -Fc -h localhost -U loveuser -d love_diary > love_diary.dump
```

### 6.2 恢复

```bash
# 从纯 SQL 备份恢复（目标库需已存在）
psql -h localhost -U loveuser -d love_diary < backup.sql

# 从压缩格式恢复
pg_restore -h localhost -U loveuser -d love_diary love_diary.dump
```

### 6.3 日常小抄

```sql
-- 看每张表的行数（估算，不用真的 count）
SELECT relname AS 表名, n_live_tup AS 行数
FROM pg_stat_user_tables ORDER BY relname;
```

---

## 7. 连接串与特殊字符

连接串格式：

```
postgresql+psycopg://用户名:密码@主机/数据库名
```

**特殊字符必须 URL 编码**（这是本项目密码踩过的坑）：

| 字符 | 编码 | 说明 |
|---|---|---|
| `@` | `%40` | 是分隔符，密码里有必须编码，否则解析错乱 |
| `#` | `%23` | 是片段分隔符，密码里有必须编码 |
| `:` | `%3A` | 分隔符，密码里有要编码 |
| `/` | `%2F` | 路径分隔符，密码里有要编码 |

例如密码是 `Lyx20050915@`，连接串写：

```
DATABASE_URL=postgresql+psycopg://loveuser:Lyx20050915%40@127.0.0.1/love_diary
```

> 改密码三步曲：**① `ALTER USER` 改库密码 → ② 同步改 `.env`（特殊字符编码）→ ③ 重启服务**。漏了第 ②③ 步，服务会连不上数据库。

---

## 8. 常见坑速查（血泪版）

| # | 现象 | 原因 | 解决 |
|---|---|---|---|
| 1 | `psql -U loveuser` 报 `Peer authentication failed` | 走了 socket + peer 认证，系统无此用户 | 加 `-h localhost` 走密码认证，或 `sudo -u postgres psql` |
| 2 | 输入 `show database` 报 `syntax error at or near "database"` | 这是 MySQL 语法 | 用 `\l` |
| 3 | 查 `users` 表报"表不存在" / 查不到数据 | 没切库，还在 `postgres` 库 | `\c love_diary` 或登录加 `-d love_diary` |
| 4 | 改了 `.env` 密码，服务连不上 | 密码含 `@`/`#` 没编码，或没重启 | 编码成 `%40`/`%23`，重启服务 |
| 5 | 插入中文乱码 | 客户端/服务器编码不一致 | PostgreSQL 默认 UTF-8，一般不会；确认终端是 UTF-8 |
| 6 | `SELECT * FROM Users` 报错 | PostgreSQL 标识符区分大小写 | 表名小写直接写 `users` |
| 7 | 用双引号包字符串 `"abc"` 报错 | 双引号是标识符，不是字符串 | 字符串用单引号 `'abc'` |
| 8 | 想取刚插入的 id | — | 用 `INSERT ... RETURNING id;` |

---

## 附：本项目数据库结构速查

```sql
users          -- 用户表
  id, username, password_hash, nickname, avatar,
  partner_id(绑定的对方id), bind_code(绑定码),
  last_user_agent, created_at

diaries        -- 日记表
  id, user_id(作者), content, mood(心情),
  images(JSON字符串), date(日记日期),
  visible_to_partner(是否对伴侣可见), created_at, updated_at

login_logs     -- 登录日志
  id, user_id, user_agent(设备UA), ip, created_at

anniversaries  -- 纪念日
  id, user_id, name(名称), date, created_at
```

> 关联关系：`diaries.user_id → users.id`，`login_logs.user_id → users.id`，`anniversaries.user_id → users.id`，`users.partner_id → users.id`（自关联）。
