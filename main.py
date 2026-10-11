import os
import telebot

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! ZuBek Group AI boshqaruv tizimi ishga tushdi.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Buyruq qabul qilindi. Obyekt monitoringi va hisobotlar nazorati faol.")

if __name__ == '__main__':
    bot.infinity_polling()
  
