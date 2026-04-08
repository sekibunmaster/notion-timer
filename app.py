from flask import Flask, render_template, request, redirect
import requests
import json
import os
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

import os

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("DATABASE_ID")

JST = timezone(timedelta(hours=9))

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    # すでに動いているかチェック
    if os.path.exists("state.json"):
        return "すでにタイマー動作中です（STOPしてから再開してください）"

    task = request.form.get("task")

    if not task:
        return "タスク名が空です"

    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "タスク名": {
                "title": [{"text": {"content": task}}]
            },
            "開始": {
                "date": {"start": datetime.now(JST).isoformat()}
            }
        }
    }

    res = requests.post(url, headers=headers, json=data)

    if res.status_code != 200:
        return res.text

    page_id = res.json()["id"]

    with open("state.json", "w") as f:
        json.dump({"page_id": page_id}, f)

    return redirect("/")

@app.route("/stop", methods=["POST"])
def stop():
    if not os.path.exists("state.json"):
        return "開始していない"

    with open("state.json", "r") as f:
        state = json.load(f)

    page_id = state["page_id"]

    url = f"https://api.notion.com/v1/pages/{page_id}"

    data = {
        "properties": {
            "終了": {
                "date": {"start": datetime.now(JST).isoformat()}
            }
        }
    }

    res = requests.patch(url, headers=headers, json=data)

    if res.status_code != 200:
        return res.text

    os.remove("state.json")

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)