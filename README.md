# 💕 恋爱日记 Love Diary

情侣专属日记应用 —— 安卓 App + 服务端 + 数据库，C/S 架构。每人有独立账号，数据存在服务器上，支持情侣一对一绑定、互看对方日记。

## ✨ 功能

- **账号体系**：注册 / 登录（JWT 令牌）/ 修改密码，登录自动记录设备 UA 与 IP（`login_logs`）
- **日记**：写日记、按日期查看历史、修改、删除；支持心情标签、图片（≤5MB）
- **情侣绑定**：一键生成 6 位绑定码，对方输入后两人互相绑定；可查看另一半**公开**的日记
- **纪念日**：记录在一起/生日等重要日期，自动计算倒计时
- **头像**：上传头像，个性化资料

## 🏗️ 技术栈

| 部分 | 技术 |
|---|---|
| 客户端 | uni-app（Vue3），HBuilderX 云打包安卓 APK |
| 服务端 | Python + FastAPI + Uvicorn + SQLAlchemy |
| 数据库 | PostgreSQL（生产）/ SQLite（本地开发，一键切换） |
| 认证 | JWT + bcrypt 密码哈希 |

## 📁 目录结构

```
恋爱日记/
├── PLAN.md              # 完整开发规划（架构/数据库/API/路线图）
├── server/              # 服务端（Python FastAPI）
│   ├── main.py          # 应用入口
│   ├── database.py      # 数据库连接（.env 切换 SQLite/PostgreSQL）
│   ├── models.py        # 数据表：users / diaries / login_logs / anniversaries
│   ├── schemas.py       # 请求/响应模型
│   ├── security.py      # 密码哈希 + JWT
│   ├── deps.py          # 登录鉴权依赖
│   ├── routers/         # 接口：auth / diaries / anniversaries / upload / bind
│   └── test_smoke.py    # 冒烟测试（19 项）
└── app/                 # 安卓客户端（uni-app，开发中）
```

## 🚀 快速开始

### 本地开发（Windows）

```powershell
cd server
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 复制环境变量模板，本地自测改用 SQLite
copy .env.example .env
# 编辑 .env：取消注释 DATABASE_URL=sqlite:///./dev.db，注释掉 PostgreSQL 那行

uvicorn main:app --reload
```

打开 http://127.0.0.1:8000/docs 即可看到接口测试台。

### 服务器部署（阿里云 Ubuntu + PostgreSQL）

```bash
# 1. 装 PostgreSQL 并建库
sudo apt update && sudo apt install postgresql
sudo systemctl enable --now postgresql
sudo -u postgres psql <<'EOF'
CREATE USER loveuser WITH PASSWORD '换成强密码';
CREATE DATABASE love_diary OWNER loveuser;
EOF

# 2. 拉代码、装依赖、配环境变量
git clone https://github.com/luanyuxiang050915/love-diary.git
cd love-diary/server
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env   # 编辑：DATABASE_URL 填 PostgreSQL 连接串、JWT_SECRET 填随机串

# 3. 启动（生产建议用 systemd 守护，详见 PLAN.md 六·五节）
./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
```

> ⚠️ 阿里云**安全组**和服务器防火墙都要放行 8000 端口（开发期）；正式上线用 Nginx + HTTPS 后关掉 8000。

## 📡 API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录，返回 JWT |
| PUT | /api/auth/password | 修改密码 |
| GET | /api/me | 我的资料 |
| PUT | /api/me | 更新资料（昵称/头像） |
| GET | /api/login-logs | 我的登录记录（UA+IP） |
| POST | /api/diaries | 写日记 |
| GET | /api/diaries | 日记列表（按日期/分页） |
| GET/PUT/DELETE | /api/diaries/{id} | 单篇日记 |
| POST | /api/upload | 上传图片（jpg/png/webp ≤5MB） |
| POST | /api/bind/code | 生成我的绑定码 |
| POST | /api/bind/accept | 输入对方绑定码绑定 |
| GET | /api/partner/diaries | 看对方公开日记 |
| POST | /api/anniversaries | 新增纪念日 |
| GET | /api/anniversaries | 纪念日列表（含倒计时） |
| PUT/DELETE | /api/anniversaries/{id} | 修改/删除纪念日 |

## 📋 开发进度

- [x] 阶段 0：环境搭建
- [x] 阶段 1：服务端全部接口（已测试通过）
- [ ] 阶段 2：安卓 App（登录/写日记/纪念日/我的）
- [ ] 阶段 3：情侣绑定页
- [ ] 阶段 4：打磨 + 正式上线

## 📄 详细规划

见 [PLAN.md](PLAN.md) —— 包含完整架构图、数据库设计、分阶段路线、部署清单、小白避坑指南。
