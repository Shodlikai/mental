import os
import asyncio
import google.generativeai as genai
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

# 1. Kalitlarni olish
api_id = int(os.environ.get("API_ID", 0))
api_hash = os.environ.get("API_HASH", "")
session_str = os.environ.get("SESSION", "")
gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

# 2. Gemini sozlamalari
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    system_instruction="Sen Shodlikning yordamchisisan. Qisqa va o'zbekcha javob ber."
)

# 3. Telegram mijoz
client = TelegramClient(StringSession(session_str), api_id, api_hash)

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply(event):
    sender = await event.get_sender()
    if sender.bot or sender.is_self: return
    try:
        response = model.generate_content(event.raw_text)
        await event.reply(response.text)
        print(f"✅ Javob yuborildi: {sender.first_name}")
    except Exception as e:
        print(f"❌ Gemini xatosi: {e}")

# 4. Veb-server (Render uchun)
async def handle(request):
    return web.Response(text="Bot 24/7 holatda! 🚀")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
    await site.start()

# 5. ASOSIY QISM (Python 3.14 uchun to'g'irlangan)
async def main():
    print("🚀 Bot ishga tushmoqda...")
    try:
        await client.start()
        print("✅ TELEGRAMGA MUVAFFAQIYATLI ULANDI!")
        asyncio.create_task(start_web_server())
        print("🤖 XABARLAR KUTILMOQDA...")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"❌ XATO: {e}")

if __name__ == '__main__':
    # Yangi Python versiyalari uchun eng to'g'ri usul
    asyncio.run(main())
