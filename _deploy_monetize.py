"""수익화 업데이트 배포 — 변경된 파일만 PA에 업로드 + reload."""
import uuid
from urllib import request

TOKEN = "15f08580dcd72d36519893c8e512f0a827bc1962"
BASE = "https://www.pythonanywhere.com/api/v0/user/tarofortune"
ROOT = "/home/tarofortune/mysite"

FILES = [
    "flask_app.py",
    "saju/analytics.py",
    "saju/coupang.py",
    "saju/support.py",
    "saju/dream.py",
    "auto_index.py",
    "templates/admin_stats.html",
    "templates/_coupang_section.html",
    "templates/premium.html",
    "templates/support.html",
    "templates/dream_index.html",
    "templates/dream_detail.html",
    "templates/result.html",
    "templates/today.html",
    "templates/compatibility.html",
    "templates/index.html",
    "templates/base.html",
    "static/css/style.css",
]


def upload(local):
    with open(local, "rb") as f:
        data = f.read()
    boundary = "----b" + uuid.uuid4().hex
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="content"; filename="x"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = request.Request(f"{BASE}/files/path{ROOT}/{local}", data=body, method="POST")
    req.add_header("Authorization", f"Token {TOKEN}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with request.urlopen(req) as r:
        return r.status


for fn in FILES:
    try:
        st = upload(fn)
        print(f"  {st}  {fn}")
    except Exception as e:
        print(f"  ERR {fn}: {e}")

req2 = request.Request(f"{BASE}/webapps/tarofortune.pythonanywhere.com/reload/", method="POST")
req2.add_header("Authorization", f"Token {TOKEN}")
with request.urlopen(req2) as r:
    print("reload:", r.status)
