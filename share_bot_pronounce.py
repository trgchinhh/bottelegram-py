# ! py
# Bot phat am
# Copyright by @Truongchinh304

import telebot, os
from datetime import datetime
from gtts import gTTS

API_BOT = "THAY API BOT"
bot = telebot.TeleBot(API_BOT)

@bot.message_handler(commands=["start"])
def start(message):
    user_first_name = message.from_user.first_name
    user_last_name = message.from_user.last_name
    full_name = f"{user_first_name} {user_last_name}"
    time = datetime.now().strftime('%H:%M:%S ngày %d/%m/%Y')
    text = f"Xin chào {full_name}\nBây giờ là {time}"
    tts = gTTS(text, lang='vi')
    audio_path = "D:\\Python\\greeting.mp3"
    tts.save(audio_path)
    with open(audio_path, 'rb') as audio:
        bot.send_audio(message.chat.id, audio)
    os.remove(audio_path)
    bot.send_message(message.chat.id, f"<b>{text}</b>", parse_mode = "HTML")

if __name__ == "__main__":
    bot.polling()    
