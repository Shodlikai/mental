import os
import asyncio
import google.generativeai as genai
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

# 1. Kalitlarni olish (Render Environment Variables'dan)
api_id = int(os.environ.get("API_ID", 0))
api_hash = os.environ.get("API_HASH", "")
session_str = os.environ.get("SESSION", "")
gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

# 2. Gemini AI sozlamalari
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    system_instruction="Sen Shodlikning yordamchi sun'iy intellektisan. Javoblaringni qisqa, samimiy va o'zbek tilida yoz."
)

# 3. Telegram mijozini sozlash
client = TelegramClient(StringSession(session_str), api_id, api_hash)

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply(event):
    # O'zimizga yoki botlarga javob bermaymiz
    sender = await event.get_sender()
    if sender.bot or sender.is_self:
        return

    print(f"📩 Xabar keldi: {event.raw_text}")

    try:
        # Gemini orqali javob tayyorlash
        response = model.generate_content(event.raw_text)
        await event.reply(response.text)
        print(f"✅ AI javob yubordi: {response.text[:20]}...")
    except Exception as e:
        print(f"❌ Gemini xatoligi: {e}")

# 4. Veb-server (Render uxlab qolmasligi uchun hiyla)
async def handle(request):
    return web.Response(text="Shodlikning AI Userboti 24/7 rejimda ishlamoqda! 🚀")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Veb-server {port}-portda yoqildi.")

# 5. ASOSIY ISHGA TUSHIRISH QISMI
async def main():
    print("🚀 Bot ishga tushishni boshladi...")
    
    try:
        # Telegramga ulanish
        await client.start()
        print("✅ TELEGRAMGA MUVAFFAQIYATLI ULANDI!")
        
        # Veb-serverni fonda ishga tushiramiz (Parallel ishlash)
        asyncio.create_task(start_web_server())
        
        print("🤖 Xabarlar kutilmoqda (Listening)...")
        # Botni doimiy aloqada ushlab turamiz
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ JIDDIY XATO: {e}")

if __name__ == '__main__':
    # Python 3.11+ uchun eng to'g'ri va xavfsiz ishga tushirish usuli
    asyncio.run(main())
    
