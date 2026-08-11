# 💕 恋爱日记 Love Diary

情侣专属日记应用 —— 安卓 App + FastAPI 服务端 + PostgreSQL，**已上线运行**。
两人各自注册账号、一键绑定后，共享日记、纪念日、相册，还有一堆恋爱互动小功能。

## ✨ 功能总览

**基础**

- **账号**：注册 / 登录（JWT）/ 修改密码 / 头像昵称，登录自动记录设备 UA 与 IP
- **情侣绑定**：生成 6 位绑定码，对方输入即配对；可互看对方设为公开的日记
- **日记**：文字 + 心情标签 + 图片（单张 ≤5MB，每篇最多 9 张），按日期查看 / 修改 / 删除
- **纪念日**：支持类型（恋爱 / 生日 / 旅行 / 纪念 / 其他），自动倒计时，日历按类型着色

**恋爱互动（底部“互动”Tab，9 个入口）**

- 戳一戳 💓：想 TA 就点一下，对方看到未读提醒
- 心愿清单 ✨：一起列心愿，共同勾选完成
- 爱的打卡 🔥：每天打卡，统计连续 / 累计 / 最长天数
- 悄悄话 💌：两人共享的留言墙
- 心情月报 📊：每月自动生成心情排行
- 双人聊天 💬：实时聊天，基础 emoji + 自定义表情包；服务器保存全部记录，App 本地只留最近 24 小时
- 共享相册 📷：两人照片墙，按月归档
- 纪念日日历 📅：彩色圆点标记不同类型的纪念日
- 每日一签 🎋：摇签筒抽今日缘分签（大吉 ~ 大凶，日式风格）

**个性化**

- 四套主题：白色 / 暗色 / 浅粉 / 香芋紫，全局生效并记住选择

**配套**

- 营销落地页（下载二维码、微信分享卡片、互动小预览）
- 管理后台 `admin.html`（统计 / 用户 / 日记 / 日志，删除用户级联清理全部关联数据）

## 🏗️ 技术栈

| 部分 | 技术 |
|---|---|
| 客户端 | uni-app（Vue3），HBuilderX 云打包安卓 APK |
| 服务端 | Python + FastAPI + Uvicorn + SQLAlchemy |
| 数据库 | PostgreSQL（生产）/ SQLite（本地开发） |
| 认证 | JWT + bcrypt 密码哈希 |
| 部署 | 阿里云 Ubuntu + Nginx + systemd 守护 |
| 落地页 | 原生 HTML/CSS/JS 单页（canvas 粒子 + 3D 动效） |

## 📁 目录结构

```
恋爱日记/
├── README.md                # 本说明
├── PLAN.md                  # 完整开发规划
├── landing.html             # 营销落地页（部署为服务器 index.html）
├── admin.html               # 管理后台页面
├── share.png                # 微信/QQ 分享卡片图
├── 测试用例.md               # 测试用例（Markdown）
├── 恋爱日记测试用例.docx     # 测试用例（Word，由 build_testcases_docx.py 生成）
├── build_testcases_docx.py  # Markdown → Word 生成脚本
├── server/                  # 服务端（Python FastAPI）
│   ├── main.py              # 入口：自动建表、挂载全部路由
│   ├── models.py            # 数据表（users / diaries / anniversaries / pokes / wishes / checkins / whispers / messages / album_photos / stickers …）
│   ├── schemas.py           # 请求/响应模型
│   ├── security.py          # 密码哈希 + JWT
│   ├── deps.py              # 登录鉴权依赖
│   ├── database.py          # 数据库连接（.env 切换 SQLite/PostgreSQL）
│   ├── routers/             # 14 个模块接口
│   └── test_smoke.py        # 接口自动化测试（46 项断言）
└── app/                     # 安卓客户端（uni-app）
    ├── common/              # api.js / store.js / util.js / theme.js
    ├── pages/               # 17 个页面
    ├── static/              # Tab 图标等
    ├── pages.json           # 页面与底部 4 Tab 注册
    ├── manifest.json        # 打包配置
    ├── App.vue / main.js
```

## 🌐 已上线（服务器 47.93.241.64）

- 落地页：http://47.93.241.64/
- 接口文档：http://47.93.241.64:8000/docs
- APK 下载：http://47.93.241.64/love-diary.apk
- 管理后台：http://47.93.241.64/admin.html（需 Admin Token）
- 服务：`love-diary.service`（systemd 守护，开机自启）

## 🚀 快速开始（本地开发，Windows）

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

## 📡 API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录，返回 JWT |
| PUT | /api/auth/password | 修改密码 |
| GET / PUT | /api/me | 我的资料 / 更新资料 |
| GET | /api/login-logs | 我的登录记录 |
| POST | /api/upload | 上传图片（jpg/png/webp ≤5MB） |
| POST / GET | /api/diaries | 写日记 / 日记列表 |
| GET / PUT / DELETE | /api/diaries/{id} | 单篇日记 |
| POST / GET | /api/bind/code、/api/bind/accept | 生成绑定码 / 输入对方码绑定 |
| GET | /api/partner/diaries | 看对方公开日记 |
| POST / GET / PUT / DELETE | /api/anniversaries | 纪念日增删改查（含类型 kind） |
| POST / GET / DELETE | /api/pokes、/api/pokes/unread、/api/pokes/read | 戳一戳 / 未读 / 全部已读 |
| POST / GET / PUT / DELETE | /api/wishes、/api/wishes/{id}/done | 心愿清单 |
| POST / GET | /api/checkins | 爱的打卡 |
| POST / GET | /api/whispers | 悄悄话 |
| GET | /api/stats/moods?month= | 心情月报 |
| POST / GET | /api/messages | 双人聊天（after_id 增量拉取） |
| POST / GET / DELETE | /api/album | 共享相册 |
| POST / GET / DELETE | /api/stickers | 自定义表情包 |
| GET / DELETE | /api/admin/* | 管理后台（统计/用户/日记/日志/删除用户） |

## 🧪 测试

- 接口自动化：`test_smoke.py` 46 项断言，覆盖 16 个模块，全部通过
- 文档化用例：94 项（见 [测试用例.md](测试用例.md)，Word 版同内容）
- App 静态检查：17 个页面全部通过语法检查（无 BOM、无报错）
- 手机人工验收清单：见 [测试用例.md](测试用例.md) 第三节

## 📋 开发状态

- [x] 阶段 0：环境搭建
- [x] 阶段 1：服务端全部接口（14 个模块）
- [x] 阶段 2：安卓 App 全部页面（17 页，底部 4 Tab）
- [x] 阶段 3：情侣绑定 + 恋爱互动
- [x] 阶段 4：落地页 + 管理后台 + 主题 + 打磨
- [x] 已上线运行，自动化测试全部通过

## 🗓️ 待办 / 规划

- [ ] 重新云打包发布最新版 APK（仓库代码已含全部新功能，等最后打包）
- [ ] HTTPS 证书（需要域名解析，当前是裸 IP）
- [ ] 推送通知（uniPush 2.0，需开通 DCloud 服务）
- [ ] 新功能规划：每日一问、时光胶囊、恋爱等级积分等（随时可加）

## 📄 更多文档

- [PLAN.md](PLAN.md) —— 架构、数据库设计、部署清单、小白避坑指南
- [测试用例.md](测试用例.md) —— 94 项测试用例与手机验收清单
- [PostgreSQL使用教程.md](PostgreSQL使用教程.md) —— 数据库安装与维护
