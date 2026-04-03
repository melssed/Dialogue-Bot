from flask import Flask, request
import os
import requests

TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "OK"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("🔥 ПРИШЛО:", data)  # Логирование в Railway

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
    return "OK", 200

if __name__ == "__main__":
    # Важно: использовать host=0.0.0.0 и порт из окружения Railway
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
