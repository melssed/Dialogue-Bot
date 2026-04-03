from flask import Flask, request
import requests
import os

TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "OK"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("🔥 ПРИШЛО:", data)  # ВАЖНО — будет в логах

    # обычные сообщения
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "не текст")

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": f"Получил: {text}"
            }
        )

    return "ok", 200
