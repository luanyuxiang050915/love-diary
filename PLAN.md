# 恋爱日记 — 开发规划（C/S 架构）

> 目标：一个安卓 App，两人各自有账号，日记数据存在服务器上，支持情侣一对一绑定、互看对方日记。
> 阅读对象：编程小白（会一点 Python / 前端）。

---

## 一、架构长什么样

```
┌──────────────────────┐        HTTP 请求        ┌─────────────────────────┐
│   安卓 App（客户端）   │  ───────────────────▶  │  服务器（服务端）          │
│  · 登录/注册          │                        │  Python + FastAPI        │
│  · 写日记/看日记      │  ◀───────────────────  │  · 校验登录令牌           │
│  · 情侣绑定           │        返回 JSON 数据   │  · 读写数据库             │
└──────────────────────┘                        └─────────────────────────┘
                                                     │ 读写
                                              ┌───────────────┐
                                              │  PostgreSQL    │
                                              │ （存账号/日记）  │
                                              └───────────────┘
```

**白话解释：**
- **服务端** = 一个一直运行的程序，负责存数据、管账号。它跑在哪，数据就在哪。
- **客户端** = 手机上的 App，只负责"展示界面 + 把请求发给服务器"。
- 本项目：服务端和 PostgreSQL **直接跑在你的阿里云服务器上**（它就是开发+测试环境）。代码在本地电脑写好，用 git 推到服务器上运行测试。

---

## 二、技术选型（为什么选这些）

| 部分 | 选择 | 理由 |
|---|---|---|
| 服务端语言 | Python 3.12 | 你学过，上手快 |
| 服务端框架 | FastAPI + Uvicorn | 自带 `/docs` 网页测试台，**不用写前端就能测所有接口**；代码量少 |
| 数据库 | **PostgreSQL** | 第一版就用，直接装在服务器上；个人项目免费够用 |
| 数据库操作 | SQLAlchemy（ORM） | 用 Python 类代替手写 SQL，小白友好 |
| 登录认证 | JWT 令牌 | 登录后发一个"令牌"，App 每次请求带上它，服务器就知道是谁 |
| 客户端 | uni-app（Vue3 语法） | 你学过前端；一套代码可打包安卓/iOS/网页 |
| 安卓打包 | HBuilderX 云打包 | **不需要安装安卓 SDK**，图形界面点几下就出 APK 安装包 |
| 版本管理 | Git + GitHub/Gitee 私有仓库 | 每阶段存档，代码不丢 |

---

## 三、开发环境准备（一次性）

**本地电脑（Windows）：**
1. **Python**（已装，3.12）✅
2. 装依赖包（在项目目录执行，注意多了 PostgreSQL 驱动）：
   ```powershell
   pip install fastapi "uvicorn[standard]" sqlalchemy "psycopg[binary]" pydantic pyjwt passlib bcrypt
   ```
3. **HBuilderX**（去官网下载，免费）— 用于开发安卓 App
4. **Git**（已装）✅ + 注册一个 GitHub 或 Gitee 账号（建私有仓库）

**阿里云服务器（Ubuntu）：**
5. 装 PostgreSQL：`sudo apt install postgresql`，然后创建数据库和专用账号（见阶段 0）

> **开发工作流（最重要的一节，记牢）：**
> ```
> 本地电脑写代码 → git push → 服务器上 git pull → 重启服务 → 浏览器打开 http://服务器IP:8000/docs 测试
> ```
> 你不在服务器上直接写代码，只负责把它拉下来跑。

> 注意：不需要安装安卓 SDK / Android Studio！云打包帮你搞定。

---

## 四、数据库设计（第一版）

五张表（前四张必做，绑定请求表可选）：

**1. users（用户表）**
| 字段 | 类型 | 说明 |
|---|---|---|
| id | 整数 | 主键 |
| username | 文本 | 账号（唯一） |
| password_hash | 文本 | 密码哈希（**绝不存明文密码**） |
| nickname | 文本 | 昵称 |
| avatar | 文本 | 头像地址（可后补） |
| partner_id | 整数 | 绑定的对方 id（空 = 未绑定） |
| bind_code | 文本 | 我的专属绑定码 |
| last_user_agent | 文本 | 最近一次登录的设备 UA（user-agent） |
| created_at | 时间 | 注册时间 |

**2. diaries（日记表）**
| 字段 | 类型 | 说明 |
|---|---|---|
| id | 整数 | 主键 |
| user_id | 整数 | 作者 id（外键→users） |
| content | 文本 | 日记内容 |
| mood | 文本 | 心情标签（开心/难过/想你…） |
| images | 文本 | 图片地址列表（JSON 存） |
| date | 日期 | 日记日期（默认当天） |
| visible_to_partner | 布尔 | 是否允许对方看到 |
| created_at / updated_at | 时间 | 创建/修改时间 |

**3. login_logs（登录日志表）**
| 字段 | 类型 | 说明 |
|---|---|---|
| id | 整数 | 主键 |
| user_id | 整数 | 用户 id（外键→users） |
| user_agent | 文本 | 这次登录的设备 UA（从请求头 `user-agent` 取） |
| ip | 文本 | 这次登录的来源 IP |
| created_at | 时间 | 登录时间 |

**4. anniversaries（纪念日表）**
| 字段 | 类型 | 说明 |
|---|---|---|
| id | 整数 | 主键 |
| user_id | 整数 | 所属用户 id（外键→users） |
| name | 文本 | 纪念日名称（在一起/生日/领证…） |
| date | 日期 | 纪念日日期 |
| created_at | 时间 | 创建时间 |

> 倒计时不用存：App 拿到日期后用当天日期一减就算出来了，后端只存日期。

**5. partner_requests（绑定请求表）**（可选，第一版可先不做）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | 整数 | 主键 |
| from_user_id | 整数 | 发起方 |
| code | 文本 | 邀请码 |
| status | 文本 | pending / accepted |
| created_at | 时间 | 时间 |

> 第一版简化：A 生成绑定码 → B 输入绑定码 → 直接绑定成功（不做"同意"确认，想加后面加）。

> **UA 怎么存（实现约定）：** 登录/注册接口里用 `request.headers.get("user-agent")` 取到 UA → 写入 `login_logs`（每次登录都插一条），同时更新 `users.last_user_agent`（覆盖为最新）。App 端用 `uni.request` 时也可自定义 header 的 User-Agent，让服务器看到的是自己设置的标识。

---

## 五、API 接口清单（服务端要做的事）

| 方法 | 路径 | 作用 |
|---|---|---|
| POST | /api/auth/register | 注册（用户名+密码+昵称） |
| POST | /api/auth/login | 登录，返回 JWT 令牌 |
| GET | /api/login-logs | 我的登录记录（UA + IP + 时间） |
| PUT | /api/auth/password | 修改密码（需旧密码） |
| POST | /api/upload | 上传图片（日记/头像共用），返回图片 URL |
| PUT | /api/me | 更新我的资料（昵称/头像） |
| GET | /api/me | 查看自己信息 |
| POST | /api/diaries | 写日记 |
| GET | /api/diaries | 我的日记列表（按日期/分页） |
| GET | /api/diaries/{id} | 看单篇日记 |
| PUT | /api/diaries/{id} | 修改日记 |
| DELETE | /api/diaries/{id} | 删除日记 |
| POST | /api/bind/code | 生成我的绑定码 |
| POST | /api/bind/accept | 输入对方的绑定码，绑定 |
| GET | /api/partner/diaries | 看对方可见的日记 |
| POST | /api/anniversaries | 新增纪念日 |
| GET | /api/anniversaries | 我的纪念日列表 |
| PUT | /api/anniversaries/{id} | 修改纪念日 |
| DELETE | /api/anniversaries/{id} | 删除纪念日 |

**重要规则：** 除注册/登录外，所有接口都要求带令牌；每个接口只允许操作**自己的**数据（改别人日记 id 会被拒绝——这是安全底线）。

---

## 六、分阶段开发路线（每阶段都能"跑通验证"）

### 阶段 0：环境搭建（0.5~1 天）
- 本地装好第 3 节的东西；建项目文件夹结构：
  ```
  恋爱日记/
    server/        ← 服务端（Python）
    app/           ← 安卓 App（uni-app）
    docs/          ← 文档
  ```
- **服务器上装 PostgreSQL 并建库**（SSH 登录后执行）：
  ```bash
  sudo apt update && sudo apt install postgresql
  sudo systemctl enable --now postgresql          # 开机自启 + 启动
  sudo -u postgres psql <<'EOF'
  CREATE USER loveuser WITH PASSWORD '换成强密码';
  CREATE DATABASE love_diary OWNER loveuser;
  EOF
  ```
- **验证：** 本地 `python --version`、`git --version` 有输出；服务器上 `psql -U loveuser -d love_diary -h 127.0.0.1` 能登录进去。

### 阶段 1：服务端 — 全部接口（1~2 周，最重要）
- 搭 FastAPI 项目，连**服务器的 PostgreSQL**（连接串：`postgresql+psycopg://loveuser:密码@服务器IP/love_diary`），建好四张表。
- 实现注册、登录（密码哈希 + JWT；**登录时把 UA + IP 写入 `login_logs`，并更新 `users.last_user_agent`**）。
- 实现修改密码；日记的增删改查；纪念日增删改查；图片上传（限制 jpg/png、≤5MB）。
- 每写完一个接口就打开 `http://服务器IP:8000/docs` 在网页上点着测试。
- **验证（跑通标准）：** 用 `/docs` 完成"注册→登录→写日记→改日记→删日记→加纪念日→上传图片"一整套，然后在服务器上 `psql` 查询确认数据真的进了 PostgreSQL。

### 阶段 2：安卓 App — 登录 + 写日记界面（2 周）
- HBuilderX 建 uni-app 项目，搭出 4 组页面：登录/注册页、日记列表页+写日记页、纪念日页、"我的"页（头像上传/修改密码/绑定码）。
- 用 `uni.request` 调服务端接口，App 里的服务器地址直接填**你服务器的公网 IP**（如 `http://47.x.x.x:8000`），**绝不能写 `127.0.0.1`**（那是手机自己）。
- **验证：** 手机装 App，**用流量也行**（不依赖 WiFi），能登录、能写一篇日记、能在列表看到它。

### 阶段 3：情侣绑定 + 互看日记（1 周）
- "我的"页面：显示我的绑定码、绑定状态。
- 输入对方绑定码 → 绑定成功，双方 `partner_id` 互指。
- 日记列表加一个"另一半的日记"页签，只显示对方 `visible_to_partner=true` 的日记。
- **验证：** 两台手机/两个账号互相绑定，A 写的日记 B 能看到（且只能看到 A 允许的）。

### 阶段 4：打磨上线（1~2 周）
- 心情标签完善、纪念日倒计时美化、日记图片展示优化等。
- **正式上线**：加 Nginx + 域名 + HTTPS（Certbot 一键配），App 地址从 `http://IP:8000` 换成 `https://你的域名`，然后在**阿里云安全组里关掉 8000 端口**（只留 22/80/443）。
- **验证：** 手机用 4G/5G 网络打开 App 一切正常，地址栏是 `https://` 没有安全警告。

---

## 六·五、服务器部署组件清单（阿里云 Ubuntu）

> 你的服务器 = 一台一直开机的电脑。下面是要装的组件，**够用就行，别多装**。

**必须装的 5 样：**

| 组件 | 用途 | 安装命令 |
|---|---|---|
| Python 3（3.10+） | 跑 FastAPI | Ubuntu 自带，无需装新版 |
| python3-venv / python3-pip | Python 虚拟环境，隔离依赖 | `sudo apt install python3-venv python3-pip` |
| Nginx | 反向代理：公网 80/443 → 内部 8000；挂 HTTPS | `sudo apt install nginx` |
| systemd | 让服务端常驻后台、开机自启、崩溃自动重启（Ubuntu 自带） | 无需安装，写 service 文件 |
| Certbot | 免费 HTTPS 证书 | `sudo apt install certbot python3-certbot-nginx` |

**数据库：** PostgreSQL（第一版就用）—— `sudo apt install postgresql`，建库命令见阶段 0。

**明确别装的：** Docker、Redis、MySQL、宝塔/phpMyAdmin 面板 —— 小项目用不上，反而增加维护负担。

**两个小白必踩的坑：**
1. 光在服务器里配防火墙没用，还要去**阿里云控制台 → 安全组**放行端口：开发期 22 / 80 / 443 / **8000**，正式上线后关掉 8000。
2. 服务器防火墙（UFW）也要同步开：`sudo ufw allow 22,80,443,8000/tcp`（上线后改成 `22,80,443`）。

**部署后的架构：** `Nginx(80/443 + HTTPS) → FastAPI(8000) → PostgreSQL`，后台由 systemd 守护，图片存在服务器磁盘目录由 Nginx 直接对外提供。

---

## 七、小白常见坑（提前告诉你）

1. **密码不要明文存** —— 必须用 `passlib` 哈希。这是最重要的安全意识。
2. **手机连不上服务器** —— 90% 是 App 里地址写了 `127.0.0.1`，或阿里云安全组/服务器防火墙没放行端口。App 里必须填服务器**公网 IP**。
3. **改了代码没生效** —— 服务端改完要**重启**（按 Ctrl+C 停掉再 `uvicorn` 启动）。
4. **数据库表结构变了** —— 开发期直接重建：`psql` 里 `DROP TABLE users, diaries CASCADE;` 然后重启服务自动建表（数据不重要时）；后期再上迁移工具 Alembic。
5. **密钥别提交到 git** —— 用 `.gitignore` 排除配置文件里的密钥。
6. **别一开始就想做完美** —— 先跑通"写日记→看日记"这条主线，其余都是加分项。

---

## 八、后续扩展方向（做完主线再说）

- 情侣共享空间 / 一起写同一篇日记
- 纪念日、倒计时、打卡
- 图片/视频日记、语音日记
- 消息推送（对方给你写了日记提醒你）
- 加 HTTPS（已含在上线步骤）、数据库定时备份（`pg_dump` 写个定时任务）

---

## 九、第一件事（明天就做）

1. 本地按第 3 节装好依赖；服务器上装好 PostgreSQL（命令见阶段 0）。
2. 建好目录结构。
3. 用 git 初始化仓库并推到 GitHub/Gitee 私有仓库。
4. 回来告诉我，我们开始写**阶段 1 的服务端**。

> 进度建议：每天投入 1~2 小时，6~8 周能做出一版能用的。别急，每阶段都有"跑通验证"，跑通再进下一阶段。
