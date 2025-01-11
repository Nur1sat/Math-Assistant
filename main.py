import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from openai import OpenAI
import io
import contextlib

# Replace with your actual OpenAI API key and Telegram bot token
OPENAI_API_KEY = "Api_key"
TELEGRAM_API_TOKEN = "Bot_Token"
client = OpenAI(api_key=OPENAI_API_KEY)

# Set up logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Helper function to run Python code
def run_python_code(code: str) -> str:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        try:
            exec(code, {"__builtins__": {}})
        except Exception as e:
            return f"Error: {e}"
    return output.getvalue()


async def query_math_tutor(prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "assistant", "content": "You are a helpful math assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        assistant_code = completion.choices[0].message.content
        return assistant_code
    except Exception as e:
        return f"Error communicating with OpenAI API: {e}"


@router.message(Command(commands=["start"]))
async def start_command(message: Message):
    await message.answer("Hello! I'm your Math Tutor bot. Send me a math question, and I'll solve it for you!")


# Handler for user messages
@router.message()
async def handle_message(message: Message):
    user_query = message.text
    await message.answer("Let me think...")

    assistant_code = await query_math_tutor(user_query)
    print(assistant_code)

    await message.answer(f"Answer:\n{assistant_code}\n", parse_mode="MARKDOWN")



async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
