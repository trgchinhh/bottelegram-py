# ! py
# Bot tradingview 
# Copyright by @Truongchinh304

import telebot
from telebot import types

bot = telebot.TeleBot("THAY_API_BOT")

print("Chờ tin nhắn...\n")
# Hàm xử lý lệnh /start
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_markup = types.ReplyKeyboardMarkup(row_width=1)
    phone_button = types.KeyboardButton(text="Nhập số điện thoại", request_contact=True)
    user_markup.add(phone_button)
    bot.send_message(message.chat.id, "Vui lòng chọn nút bên dưới để nhập số điện thoại", reply_markup=user_markup)
    

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    global phone_number
    if message.contact is not None:
        if message.contact.phone_number:
            phone_number = message.contact.phone_number
            handle_infor(message)
    else:
        bot.reply_to(message, "Xin lỗi, đã xảy ra lỗi")
        
def handle_infor(message):
    global user_id, user_first_name, user_last_name, user_language, username, is_bot, is_bot_ans
    user_id = message.from_user.id # Lấy id 
    user_first_name = message.from_user.first_name # Lấy tên đầu
    user_last_name = message.from_user.last_name # Lấy tên cuối
    user_language = message.from_user.language_code # Ngôn ngữ
    username = message.from_user.username # Tên ng dùng
    is_bot = message.from_user.is_bot # Ktra phải bot không
    if is_bot:
        is_bot_ans = "true"
    else:
        is_bot_ans = "false"
    
    full_name = user_first_name + " " + user_last_name
    bot.reply_to(message, f"Xin chào {full_name} ! Tôi là bot lấy ID chat trên telegram\n\nDưới đây là thông tin cuả bạn\n👤 You\n ├ id: {user_id}\n ├ is_bot: {is_bot_ans}\n ├ first_name: {user_first_name}\n ├ last_name: {user_last_name}\n ├ username: {username}\n ├ language_code: {user_language}\n └ phone_number: {phone_number}\n\nTÁC GIẢ\nhttps://t.me/Chinhcoder")    
    print(f"👤 You\n ├ id: {user_id}\n ├ is_bot: {is_bot_ans}\n ├ first_name: {user_first_name}\n ├ last_name: {user_last_name}\n ├ username: {username}\n ├ language_code: {user_language}\n └ phone_number: {phone_number}")


@bot.message_handler(commands=["getid"])
def handle_start(message):
    bot.reply_to(message, f"👤 You\n ├ id: {user_id}\n ├ is_bot: {is_bot_ans}\n ├ first_name: {user_first_name}\n ├ last_name: {user_last_name}\n ├ username: {username}\n ├ language_code: {user_language}\n └ phone_number: {phone_number}")
    
# Xử lý ngoại lệ
@bot.message_handler(func=lambda message: True)    
def handle_else(message):
    bot.reply_to(message, f"👤 You\n ├ id: {user_id}\n ├ is_bot: {is_bot_ans}\n ├ first_name: {user_first_name}\n ├ last_name: {user_last_name}\n ├ username: {username}\n ├ language_code: {user_language}\n └ phone_number: {phone_number}")
    
bot.polling()