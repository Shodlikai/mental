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
model = genai.GenerativeModel('gemini-1.5-pro')

# 3. Telegram mijoz
client = TelegramClient(StringSession(session_str), api_id, api_hash)

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply(event):
    if event.is_group or event.is_channel: return
    sender = await event.get_sender()
    if sender.bot or sender.is_self: return
    
    try:
        response = model.generate_content(f"Sen Shodlikning yordamchisisan. Javob ber: {event.raw_text}")
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
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Veb-server yoqildi: {port}")

# 5. ASOSIY QISM: Ikkalasini parallel ishga tushirish
async def main():
    print("🚀 Bot ishga tushmoqda...")
    
    # 1-qadam: Telegramga ulanish
    await client.start()
    print("✅ Telegramga ulandi!")
    
    # 2-qadam: Veb-serverni fonda ishga tushirish
    asyncio.create_task(start_web_server()) 
    
    # 3-qadam: Telegram xabarlarini doimiy eshitish
    print("🤖 Xabarlar kutilmoqda...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
