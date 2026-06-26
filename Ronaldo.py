import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import uuid
import warnings
warnings.filterwarnings("ignore")

# ---------- ВАШИ ДАННЫЕ ----------
TELEGRAM_TOKEN = "8285164342:AAE_DdPNBmYVqC2mRVWm4S_0cWNuDdt3ZM0"
GIGACHAT_CLIENT_SECRET = "a2e1223f-d640-43ba-ade6-a00ea978a5ce"
# ---------------------------------

AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

user_history = {}

def get_access_token():
    headers = {
        "Authorization": f"Basic {GIGACHAT_CLIENT_SECRET}",
        "RqUID": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {"scope": "GIGACHAT_API_CORP"}
    resp = requests.post(AUTH_URL, headers=headers, data=payload, verify=False)
    return resp.json()["access_token"]

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я бот с GigaChat. Задавайте вопросы.")

@dp.message()
async def chat(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    if user_id not in user_history:
        user_history[user_id] = [
            {"role": "system", "content": "Ты вежливый и полезный ассистент на русском языке."}
        ]
    user_history[user_id].append({"role": "user", "content": user_text})

    await bot.send_chat_action(message.chat.id, "typing")

    try:
        token = get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "GigaChat",
            "messages": user_history[user_id],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        resp = requests.post(API_URL, headers=headers, json=payload, verify=False)
        reply = resp.json()["choices"][0]["message"]["content"]

        user_history[user_id].append({"role": "assistant", "content": reply})
        await message.answer(reply)

    except Exception as e:
        await message.answer(f"Ошибка: {e}")

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())