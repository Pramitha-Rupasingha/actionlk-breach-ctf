"""
STAGE-05 "Behind the Door" — ActionLK internal file portal.

Intentionally vulnerable to Insecure Direct Object Reference (IDOR): the
app trusts whatever `user_id` it is handed in the query string and never
checks it against any session/identity. This is deliberate for the
ActionLK Breach CTF (IE3132 Assignment 01) — do not add auth checks to
the running challenge container.
"""
from flask import Flask, request, send_from_directory, abort, render_template_string

app = Flask(__name__)
FILES_DIR = "/app/files"

# user_id -> files that account is allowed to see (never actually enforced
# against who is asking — that's the vulnerability).
USER_FILES = {
    "1042": ["readme.txt"],
    "1000": ["admin_notes.txt", "vault_backup.zip.enc"],
}

LISTING_TMPL = """
<!doctype html><html><head><meta charset="utf-8">
<title>ActionLK File Portal</title>
<style>
body{font-family:sans-serif;background:#0f1628;color:#e6e6e6;padding:40px;}
.box{background:#182236;padding:24px 32px;border-radius:10px;max-width:520px;}
a{color:#8ab4ff;} li{margin:6px 0;}
</style></head><body>
<div class="box">
<h2>ActionLK Internal File Portal</h2>
<p>Viewing files for user_id={{ uid }}</p>
<ul>
{% for f in files %}
  <li><a href="/download?user_id={{ uid }}&name={{ f }}">{{ f }}</a></li>
{% endfor %}
</ul>
</div></body></html>
"""

INDEX_HTML = """
<!doctype html><html><head><meta charset="utf-8">
<title>ActionLK File Portal</title></head>
<body style="font-family:sans-serif;background:#0f1628;color:#e6e6e6;padding:40px;">
<h2>ActionLK Internal File Portal</h2>
<p>Pass your user ID to see your files: <code>/files?user_id=&lt;id&gt;</code></p>
</body></html>
"""


@app.route("/")
def index():
    return INDEX_HTML


@app.route("/files")
def files():
    uid = request.args.get("user_id", "")
    flist = USER_FILES.get(uid)
    if flist is None:
        abort(404)
    return render_template_string(LISTING_TMPL, uid=uid, files=flist)


@app.route("/download")
def download():
    uid = request.args.get("user_id", "")
    name = request.args.get("name", "")
    allowed = USER_FILES.get(uid, [])
    if name not in allowed:
        abort(403)
    return send_from_directory(FILES_DIR, name, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
