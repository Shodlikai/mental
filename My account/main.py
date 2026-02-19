import os
import asyncio
import google.generativeai as genai
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from aiohttp import web

# 1. Barcha maxfiy ma'lumotlarni Render (yoki .env) dan olamiz
api_id = int(os.environ.get("API_ID", "BU_YERGA_YANGI_API_ID")) 
api_hash = os.environ.get("API_HASH", "BU_YERGA_YANGI_API_HASH")
session_str = os.environ.get("SESSION", "BU_YERGA_YANGI_SESSION")
gemini_api_key = os.environ.get("GEMINI_API_KEY", "BU_YERGA_GEMINI_KALIT")

# 2. Gemini AI sozlamalari
genai.configure(api_key=gemini_api_key)

system_instruction = """
Sen Shodlikning yordamchi sun'iy intellektisan. 
Sening vazifang - Shodlik hozir band bo'lgani uchun uning o'rniga Telegramda odamlarga javob berish.
Javoblaringni qisqa, samimiy, do'stona va toza O'zbek tilida yoz. 
O'zingni "Men Shodlikning AI yordamchisiman" deb tanishtir.
"""

model = genai.GenerativeModel(
    model_name='gemini-1.5-pro',
    system_instruction=system_instruction
)

# 3. Telethon (Telegram) mijozini sozlash
client = TelegramClient(StringSession(session_str), api_id, api_hash)

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply(event):
    sender = await event.get_sender()
    user_message = event.raw_text
    
    # O'zimizga o'zimiz yoki botlarga javob bermaslik uchun
    if sender.bot or sender.is_self:
        return

    print(f"[{sender.first_name}] dan xabar: {user_message}")

    try:
        response = model.generate_content(user_message)
        ai_reply = response.text
        await event.reply(ai_reply)
        print(f"AI javob yubordi: {ai_reply}")
    except Exception as e:
        print(f"Xatolik: {e}")

# 4. RENDER UCHUN MITTI VEB-SERVER (Hiyla qismi)
async def handle(request):
    return web.Response(text="Shodlikning AI Userboti mukammal 24/7 ishlayapti! 🚀")

async def web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080)) # Render o'zi port ajratadi
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Veb-server {port}-portda ishga tushdi.")

# 5. Ikkalasini (Web Server + Telegram Bot) birga ishga tushirish
async def main():
    await web_server() # Saytni yoqamiz
    
    await client.start() # Botni yoqamiz
    print("🤖 AI Userbot ishga tushdi va shaxsiy xabarlarni kutyapti...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Asynchronous loop'ni ishga tushirish
    asyncio.run(main())
