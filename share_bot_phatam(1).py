# ! py
# Bot phat am (tuy bien)
# Copyright by @Truongchinh304

import telebot, os
from datetime import datetime
from gtts import gTTS

API_BOT = "THAY_API_BOT"
bot = telebot.TeleBot(API_BOT)

@bot.message_handler(commands=["noi"])
def start(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            bot.send_message(message.chat.id, "<b>Nhập theo mẫu /noi [noi dung muon phat am]</b>", parse_mode="HTML")
            return
        noi_dung = parts[1]    
        tts = gTTS(noi_dung, lang='vi')
        audio_path = "D:\\Python\\greeting.mp3"
        tts.save(audio_path)
        with open(audio_path, 'rb') as audio:
            bot.send_audio(message.chat.id, audio)
        os.remove(audio_path)
        bot.send_message(message.chat.id, f"<b>{noi_dung}</b>", parse_mode = "HTML")
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi {e}</b>", parse_mode="HTML")         

if __name__ == "__main__":
    bot.infinity_polling()    
