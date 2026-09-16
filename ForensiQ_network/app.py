import sqlite3
import subprocess
from flask import Flask, request

app = Flask(__name__)

@app.route("/user")
def get_user():
    user_id = request.args.get("id")          # untrusted source
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE id = {user_id}")  # SQL injection sink
    return str(cur.fetchall())

@app.route("/ping")
def ping():
    host = request.args.get("host")           # untrusted source
    return subprocess.check_output(f"ping -c 1 {host}", shell=True)  # command injection sink
