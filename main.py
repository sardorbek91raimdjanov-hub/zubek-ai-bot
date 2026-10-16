import io
import os
import re

import telebot
from gtts import gTTS
import google.generativeai as genai

# --- Muhit o'zgaruvchilari ---
BOT_TOKEN = os.environ["BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# --- Botni tayyorlash ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- Gemini'ni sozlash ---
genai.configure(api_key=GEMINI_API_KEY)

BOT_NAME = "ZuBek Group AI"

SYSTEM_INSTRUCTION = f"""
Sen "{BOT_NAME}" — ZuBek Group kompaniyasining rasmiy yordamchisisan.

Faoliyat sohalari:
- Qurilish
- Ta'mirlash
- Interyer dizayn
- Loyihalarni boshqarish

Muloqot qoidalari:
- Faqat o'zbek tilida javob ber.
- Professional, qat'iy va ishchan ruhda gapir.
- Javoblar aniq, qisqa va amaliy bo'lsin; ortiqcha so'zlardan qoch.
- Faqat yuqoridagi sohalarga oid savollarga javob ber. Boshqa mavzularda muloyimlik bilan o'z vakolat doirangni eslat.
- Narx, muddat yoki texnik ma'lumotni aniq bilmasang, taxmin qilma — mijozni ZuBek Group mutaxassislari bilan bog'lanishga yo'nalt.
- O'zingni har doim ZuBek Group vakili sifatida tut.
"""

# --- Gemini modeli ---
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION,
)


# --- /start va /help buyruqlari ---
OWNER_NAME = "Sardorbek"

WELCOME_TEXT = f"""
👋 Assalomu alaykum, hurmatli {OWNER_NAME}!

✅ *{BOT_NAME}* muvaffaqiyatli ishga tushdi va xizmatingizga tayyor.

Men ZuBek Group kompaniyasining rasmiy yordamchisiman. Quyidagi yo'nalishlarda sizga yordam bera olaman:

🏗 Qurilish
🔨 Ta'mirlash
🛋 Interyer dizayn
📋 Loyihalarni boshqarish

Savolingizni yozing, aniq va amaliy javob beraman.

📌 *Buyruqlar:*
/start — botni qayta ishga tushirish
/help — yordam va imkoniyatlar

_ZuBek Group — ishonchli qurilish hamkori._
"""


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.send_message(message.chat.id, WELCOME_TEXT, parse_mode="Markdown")


# --- Matnli xabarlarga AI javobi (matn + ovoz) ---
TTS_LANG = "uz"  # gTTS tili


def clean_for_tts(text: str) -> str:
    """Ovozga o'girishdan oldin Markdown belgilarini olib tashlaydi."""
    text = re.sub(r"[*_`#>~]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def make_voice(text: str):
    """Matndan gTTS orqali ovozli fayl (BytesIO) yasaydi."""
    audio = io.BytesIO()
    gTTS(text=clean_for_tts(text), lang=TTS_LANG).write_to_fp(audio)
    audio.seek(0)
    audio.name = "javob.mp3"
    return audio


@bot.message_handler(content_types=["text"])
def handle_text(message):
    chat_id = message.chat.id

    # 1) Gemini'dan javob olish
    try:
        bot.send_chat_action(chat_id, "typing")
        response = model.generate_content(message.text)
        answer = response.text.strip()
    except Exception as e:
        print(f"Gemini xatosi: {e}")
        bot.send_message(
            chat_id,
            "⚠️ Kechirasiz, hozir javob tayyorlay olmadim. Iltimos, birozdan so'ng qayta urinib ko'ring.",
        )
        return

    if not answer:
        bot.send_message(chat_id, "Savolingizni aniqroq yozing, iltimos.")
        return

    # 2) Matnli javobni yuborish
    bot.send_message(chat_id, answer)

    # 3) Ovozli javobni yuborish
    try:
        bot.send_chat_action(chat_id, "record_voice")
        bot.send_voice(chat_id, make_voice(answer))
    except Exception as e:
        print(f"Ovoz xatosi: {e}")


# --- Botni ishga tushirish ---
if __name__ == "__main__":
    print(f"{BOT_NAME} ishga tushdi...")
    bot.infinity_polling()
