from dotenv import load_dotenv
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mcstatus import JavaServer
from datetime import datetime

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVER_IP = os.getenv("SERVER_IP")
OWNER_ID = int(os.getenv("OWNER_ID", 0))

last_players = 0
today_max_online = 0
start_time = datetime.now()

async def get_server_status():
    try:
        server = JavaServer.lookup(f"{SERVER_IP}:25565")
        status = await server.async_status()
        return {
            "online": True,
            "players": status.players.online,
            "max": status.players.max,
            "list": [p.name for p in (status.players.sample or [])],
            "ping": round(status.latency)
        }
    except:
        return {"online": False}

async def monitor(context: ContextTypes.DEFAULT_TYPE):
    global last_players, today_max_online
    s = await get_server_status()
    current = s.get("players", 0)

    if current > today_max_online:
        today_max_online = current

    if current > last_players:
        if last_players == 0 and current == 1:
            await context.bot.send_message(OWNER_ID, "🎉 Первый игрок зашёл на сервер!")
        else:
            await context.bot.send_message(OWNER_ID, f"🎮 Игрок зашёл! Сейчас: {current}")
    elif current < last_players:
        if current == 0:
            await context.bot.send_message(OWNER_ID, "🌙 Сервер снова пуст.")
        else:
            await context.bot.send_message(OWNER_ID, f"📤 Игрок вышел. Сейчас онлайн: {current}")

    last_players = current

# ==================== КОМАНДЫ ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Уведомления включены. Напиши /help")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 <b>Все команды:</b>\n\n"
        "/online — Показать кто сейчас онлайн и список игроков\n\n"
        "/serverinfo — Полная информация о сервере\n\n"
        "/say &lt;текст&gt; — Отправить сообщение в игровой чат\n\n"
        "/stats — Показать статистику игрового времени игроков — В РАЗРАБОТКЕ\n\n"
        "/startserver — Запустить сервер — В РАЗРАБОТКЕ\n\n"
        "/restartserver — Перезапустить сервер — В РАЗРАБОТКЕ\n\n"
        "/stopserver — Остановить сервер — В РАЗРАБОТКЕ\n\n"
        "/killserver — Принудительная остановка сервера — В РАЗРАБОТКЕ\n\n"
        "/help — Этот список",
        parse_mode='HTML'
    )

async def online(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = await get_server_status()
    if s["online"]:
        text = f"🟢 Онлайн: {s['players']}/{s['max']}"
        if s["list"]:
            text += "\n\nИгроки:\n" + "\n".join([f"• {name}" for name in s["list"]])
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("🔴 Сервер выключен")

async def serverinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = await get_server_status()
    if s["online"]:
        await update.message.reply_text(
            f"🟢 <b>Информация о сервере</b>\n\n"
            f"👥 Онлайн: {s['players']}/{s['max']}\n"
            f"🏓 Пинг: {s.get('ping', '—')} ms\n"
            f"📍 IP: <code>{SERVER_IP}</code>",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text("🔴 Сервер выключен")

async def say_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /say Привет всем!")
        return
    text = " ".join(context.args)
    await update.message.reply_text(f"📢 Сообщение отправлено: {text}\n(Пока без RCON)")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Показать статистику игрового времени игроков — пока в разработке.")

async def startserver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Запустить сервер — пока в разработке.")

async def restartserver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Перезапустить сервер — пока в разработке.")

async def stopserver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛑 Остановить сервер — пока в разработке.")

async def killserver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Принудительная остановка сервера — пока в разработке.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("online", online))
    app.add_handler(CommandHandler("serverinfo", serverinfo))
    app.add_handler(CommandHandler("say", say_command))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("startserver", startserver))
    app.add_handler(CommandHandler("restartserver", restartserver))
    app.add_handler(CommandHandler("stopserver", stopserver))
    app.add_handler(CommandHandler("killserver", killserver))

    # Автоматический мониторинг
    job_queue = app.job_queue
    job_queue.run_repeating(monitor, interval=10, first=5)

    print("🤖 Fantasia Server Bot запущен с уведомлениями!")
    app.run_polling()

if __name__ == "__main__":
    main()