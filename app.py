import os
from flask import Flask, request, jsonify
from telegram.ext import Application, CommandHandler
from telegram import Update

TOKEN = os.environ["BOT_TOKEN"]
APP_URL = os.environ["APP_URL"]

app = Flask(__name__)
tg_app = Application.builder().token(TOKEN).build()

# /start komutu
async def start(update: Update, context):
    await update.message.reply_text("Webhook bot aktif!")

tg_app.add_handler(CommandHandler("start", start))

# Health check
@app.route("/healthz")
def healthz():
    return "ok", 200

# Webhook endpoint
@app.post(f"/webhook/{TOKEN}")
def webhook():
    data = request.get_json(force=True, silent=True)
    if not data:
        return "no data", 400
    update = Update.de_json(data, tg_app.bot)
    tg_app.update_queue.put_nowait(update)
    return jsonify(ok=True)

# Webhook ayarla
@app.before_first_request
def set_webhook():
    import requests
    url = f"{APP_URL}/webhook/{TOKEN}"
    requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook", params={"url": url})

# Sadece Flask web server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
