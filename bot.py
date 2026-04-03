from flask import Flask, request
import requests
import os

TOKEN = os.getenv("BOT_TOKEN")  # токен бота от BotFather

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "business_message" in data:
        msg = data["business_message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text") or "<не текст>"
        business_connection_id = msg["business_connection_id"]

        send_text = f"Пользователь написал: {text}"
        payload = {
            "chat_id": chat_id,
            "business_connection_id": business_connection_id,
            "text": send_text
        }
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)

    if "deleted_business_messages" in data:
        deleted = data["deleted_business_messages"]
        for item in deleted:
            payload = {
                "chat_id": item["chat"]["id"],
                "business_connection_id": item["business_connection_id"],
                "text": f"❌ Сообщение {item['message_id']} удалено"
            }
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)

    if "edited_business_message" in data:
        msg = data["edited_business_message"]
        chat_id = msg["chat"]["id"]
        old_text = msg.get("old_text", "<неизвестно>")
        new_text = msg.get("text", "<не текст>")
        payload = {
            "chat_id": chat_id,
            "business_connection_id": msg["business_connection_id"],
            "text": f"✏️ Сообщение изменено\nOLD: {old_text}\nNEW: {new_text}"
        }
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)

    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
