r"""冒烟自测脚本：跑通全部接口。
用法：先启动服务（uvicorn main:app --port 8000），再执行：
    python test_smoke.py
"""
import base64
import os
import sys

# Windows 控制台默认 GBK，强制 UTF-8 输出，避免打印 emoji/中文报错
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx

# 默认测本地，可用环境变量 BASE_URL 指定（如 http://47.93.241.64:8000）
BASE = os.getenv("BASE_URL", "http://127.0.0.1:8000")


def check(cond, msg):
    if not cond:
        print(f"FAIL [FAIL] {msg}")
        sys.exit(1)
    print(f"ok [PASS] {msg}")


def main():
    c = httpx.Client(base_url=BASE, timeout=15)

    # 1. 注册两个用户
    for name in ("alice", "bob"):
        r = c.post("/api/auth/register", json={"username": name, "password": "123456", "nickname": name.title()})
        check(r.status_code == 200, f"注册 {name}")

    # 2. 重复注册应失败
    r = c.post("/api/auth/register", json={"username": "alice", "password": "123456"})
    check(r.status_code == 400, "重复用户名被拒绝")

    # 3. 登录 alice，拿 token
    r = c.post("/api/auth/login", json={"username": "alice", "password": "123456"})
    check(r.status_code == 200, "登录 alice")
    token = r.json()["token"]
    h = {"Authorization": f"Bearer {token}"}

    # 4. UA 记录（本轮需求重点）
    r = c.get("/api/me", headers=h)
    ua = r.json()["last_user_agent"]
    check(ua != "", "last_user_agent 已记录")
    print(f"      UA = {ua}")
    r = c.get("/api/login-logs", headers=h)
    check(len(r.json()) >= 1, "login_logs 有登录记录")

    # 5. 写日记 + 列表
    r = c.post("/api/diaries", headers=h, json={"content": "今天想你啦", "mood": "开心", "visible_to_partner": True})
    check(r.status_code == 200, "写日记")
    did = r.json()["id"]
    r = c.get("/api/diaries", headers=h)
    check(len(r.json()) == 1, "日记列表有 1 篇")

    # 6. 改日记
    r = c.put(f"/api/diaries/{did}", headers=h, json={"content": "今天更想你啦", "mood": "开心"})
    check(r.status_code == 200 and r.json()["content"] == "今天更想你啦", "修改日记")

    # 7. 纪念日
    r = c.post("/api/anniversaries", headers=h, json={"name": "在一起", "date": "2025-01-01"})
    check(r.status_code == 200, "新增纪念日")
    check(isinstance(r.json()["days_left"], int), "纪念日返回倒计时 days_left")

    # 8. 上传图片（1x1 像素的 png）
    png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    )
    r = c.post("/api/upload", headers=h, files={"file": ("a.png", png, "image/png")})
    check(r.status_code == 200 and r.json()["url"].startswith("/uploads/"), "上传图片")
    r = c.post("/api/upload", headers=h, files={"file": ("a.txt", b"hello", "text/plain")})
    check(r.status_code == 400, "非图片文件被拒绝")

    # 9. 修改密码
    r = c.put("/api/auth/password", headers=h, json={"old_password": "123456", "new_password": "654321"})
    check(r.status_code == 200, "修改密码")
    r = c.post("/api/auth/login", json={"username": "alice", "password": "654321"})
    check(r.status_code == 200, "新密码可登录")
    token = r.json()["token"]
    h = {"Authorization": f"Bearer {token}"}

    # 10. 绑定流程
    r = c.post("/api/bind/code", headers=h)
    check(r.status_code == 200, "alice 生成绑定码")
    code = r.json()["bind_code"]
    r = c.post("/api/auth/login", json={"username": "bob", "password": "123456"})
    hb = {"Authorization": f"Bearer {r.json()['token']}"}
    r = c.post("/api/bind/accept", headers=hb, json={"code": code})
    check(r.status_code == 200, f"bob 输入绑定码 {code} 绑定成功")

    # 11. bob 写一篇可见日记，alice 能看到；alice 再写一篇"私密"，bob 看不到
    c.post("/api/diaries", headers=hb, json={"content": "bob 的公开日记", "visible_to_partner": True})
    c.post("/api/diaries", headers=hb, json={"content": "bob 的私密日记", "visible_to_partner": False})
    r = c.get("/api/partner/diaries", headers=h)
    contents = [d["content"] for d in r.json()]
    check("bob 的公开日记" in contents and "bob 的私密日记" not in contents, "互看日记：只看得到对方公开的")

    # 12. 越权防护：alice 删 bob 的日记应 404
    bob_diary_id = c.get("/api/diaries", headers=hb).json()[0]["id"]
    r = c.delete(f"/api/diaries/{bob_diary_id}", headers=h)
    check(r.status_code == 404, "不能操作别人的日记")

    # 13. 删除自己的日记
    r = c.delete(f"/api/diaries/{did}", headers=h)
    check(r.status_code == 200, "删除自己的日记")

    # 14. 双人聊天
    r = c.post("/api/messages", headers=h, json={"content": "想你了", "msg_type": "text"})
    check(r.status_code == 200, "alice 发文本消息")
    r = c.post("/api/messages", headers=hb, json={"content": "😘", "msg_type": "emoji"})
    check(r.status_code == 200, "bob 发表情消息")
    r = c.post("/api/messages", headers=hb, json={"content": "", "msg_type": "sticker", "sticker_url": "/uploads/sticker-demo.png"})
    check(r.status_code == 200 and r.json()["msg_type"] == "sticker", "bob 发自定义贴图")
    r = c.post("/api/messages", headers=h, json={"content": "   ", "msg_type": "text"})
    check(r.status_code == 400, "空白消息被拒绝")
    r = c.get("/api/messages", headers=h)
    msgs = r.json()
    check(len(msgs) == 3 and msgs[0]["content"] == "想你了", "alice 拉到 3 条聊天记录（正序）")
    first_id = msgs[0]["id"]
    r = c.get("/api/messages", headers=h, params={"after_id": first_id})
    check(len(r.json()) == 2, "after_id 增量拉取生效")

    # 15. 共享相册
    r = c.post("/api/album", headers=h, json={"url": "/uploads/album-a.png", "caption": "第一次旅行"})
    check(r.status_code == 200, "alice 上传相册照片")
    r = c.post("/api/album", headers=hb, json={"url": "/uploads/album-b.png", "caption": ""})
    check(r.status_code == 200, "bob 上传相册照片")
    r = c.get("/api/album", headers=h)
    check(len(r.json()) == 2, "双方都能看到 2 张照片")
    bob_photo_id = r.json()[0]["id"]  # 列表按 id 倒序，最新一张是 bob 的
    r = c.delete(f"/api/album/{bob_photo_id}", headers=h)
    check(r.status_code == 404, "不能删除对方的照片")
    r = c.delete(f"/api/album/{bob_photo_id}", headers=hb)
    check(r.status_code == 200, "bob 删除自己的照片")
    r = c.get("/api/album", headers=h)
    check(len(r.json()) == 1, "删除后剩 1 张")

    # 16. 自定义表情包
    r = c.post("/api/stickers", headers=h, json={"url": "/uploads/sticker-1.png"})
    check(r.status_code == 200, "alice 添加自定义表情")
    r = c.get("/api/stickers", headers=hb)
    check(len(r.json()) == 1, "bob 能看到共享表情")
    sticker_id = r.json()[0]["id"]
    r = c.delete(f"/api/stickers/{sticker_id}", headers=hb)
    check(r.status_code == 404, "不能删除对方的表情")
    r = c.delete(f"/api/stickers/{sticker_id}", headers=h)
    check(r.status_code == 200, "alice 删除自己的表情")

    # 17. 纪念日类型（日历着色用）
    r = c.post("/api/anniversaries", headers=h, json={"name": "我的生日", "date": "2026-06-01", "kind": "birthday"})
    check(r.status_code == 200 and r.json()["kind"] == "birthday", "纪念日支持类型 birthday")
    bid = r.json()["id"]
    r = c.put(f"/api/anniversaries/{bid}", headers=h, json={"name": "我的生日", "date": "2026-06-01", "kind": "trip"})
    check(r.status_code == 200 and r.json()["kind"] == "trip", "纪念日类型可修改")

    # 18. 未绑定用户不能聊天/相册/表情
    r = c.post("/api/auth/register", json={"username": "carol", "password": "123456", "nickname": "Carol"})
    check(r.status_code == 200, "注册 carol")
    r = c.post("/api/auth/login", json={"username": "carol", "password": "123456"})
    hc = {"Authorization": f"Bearer {r.json()['token']}"}
    r = c.post("/api/messages", headers=hc, json={"content": "hi", "msg_type": "text"})
    check(r.status_code == 400, "未绑定不能发消息")
    r = c.post("/api/album", headers=hc, json={"url": "/uploads/x.png"})
    check(r.status_code == 400, "未绑定不能传相册")
    r = c.post("/api/stickers", headers=hc, json={"url": "/uploads/x.png"})
    check(r.status_code == 400, "未绑定不能加表情")

    # 19. 管理后台删除用户时级联清理聊天/相册/表情
    r = c.post("/api/auth/register", json={"username": "dave", "password": "123456", "nickname": "Dave"})
    r = c.post("/api/auth/login", json={"username": "dave", "password": "123456"})
    hd = {"Authorization": f"Bearer {r.json()['token']}"}
    r = c.post("/api/bind/code", headers=hd)
    code2 = r.json()["bind_code"]
    r = c.post("/api/bind/accept", headers=hc, json={"code": code2})
    check(r.status_code == 200, "carol/dave 绑定成功")
    c.post("/api/messages", headers=hc, json={"content": "dave 你好", "msg_type": "text"})
    c.post("/api/album", headers=hc, json={"url": "/uploads/carol.png"})
    c.post("/api/stickers", headers=hc, json={"url": "/uploads/carol-st.png"})
    r = c.get("/api/messages", headers=hd)
    check(len(r.json()) == 1, "dave 能看到 carol 的消息")
    import os as _os
    admin_secret = _os.getenv("ADMIN_SECRET", "admin-secret-change-me")
    users = c.get("/api/admin/users", headers={"X-Admin-Token": admin_secret}).json()
    carol_id = [u for u in users if u["username"] == "carol"][0]["id"]
    r = c.delete(f"/api/admin/users/{carol_id}", headers={"X-Admin-Token": admin_secret})
    check(r.status_code == 200, "管理后台删除 carol")
    r = c.get("/api/messages", headers=hd)
    check(r.status_code == 400, "dave 的绑定已被解除（消息随 carol 级联清理）")

    print("\n全部通过! ALL PASS")


if __name__ == "__main__":
    main()
