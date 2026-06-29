import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import AsyncOpenAI

# ---------- ВАШИ ДАННЫЕ ----------
TELEGRAM_TOKEN = "8285164342:AAE_DdPNBmYVqC2mRVWm4S_0cWNuDdt3ZM0"
OPENROUTER_API_KEY = "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"
# ---------------------------------

# Настройка OpenRouter
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

MODEL = "google/gemini-2.0-flash"  # Бесплатная модель!

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

user_history = {}


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я бот с Gemini. Задавайте вопросы.")


@dp.message()
async def chat(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    if user_id not in user_history:
        user_history[user_id] = [
            {"role": "system", "content": "Ты полезный ассистент. Отвечай на русском языке."}
        ]
    user_history[user_id].append({"role": "user", "content": user_text})

    await bot.send_chat_action(message.chat.id, "typing")

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=user_history[user_id],
            temperature=0.7,
            max_tokens=1000
        )

        reply = response.choices[0].message.content
        user_history[user_id].append({"role": "assistant", "content": reply})
        await message.answer(reply)

    except Exception as e:
        await message.answer(f"Ошибка: {e}")


async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    
