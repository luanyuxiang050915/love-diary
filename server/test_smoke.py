r"""冒烟自测脚本：跑通全部接口。
用法：先启动服务（uvicorn main:app --port 8000），再执行：
    python test_smoke.py
"""
import base64
import sys

# Windows 控制台默认 GBK，强制 UTF-8 输出，避免打印 emoji/中文报错
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import httpx

BASE = "http://127.0.0.1:8000"


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

    print("\n全部通过! ALL PASS")


if __name__ == "__main__":
    main()
