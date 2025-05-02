# ! py
# Bot hash dữ liệu nhập vào
# Copyright by @Truongchinh304

import hashlib, telebot, mmh3, xxhash, cityhash
from telebot import types
from argon2 import PasswordHasher

API_KEY_BOT = "THAY API BOT VÀO ĐÂY"
bot = telebot.TeleBot(API_KEY_BOT)

# Khởi tạo kiểu hash 
type_hash = ""

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.username
    if not user_name :
        full_name = message.from_user.first_name + " " + message.from_user.last_name
    else:    
        full_name = user_name
    huong_dan_su_dung = telebot.types.InlineKeyboardButton("📜 Hướng dẫn sử dụng", callback_data="hsds")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(huong_dan_su_dung)
    bot.send_message(message.chat.id, f"<b>Chào mừng {user_name} đến với bot bảo mật thông tin! Nhấn nút dưới đây để xem các lệnh 👇</b>", parse_mode = "HTML", reply_markup = keyboard)
    
# Hàm trả về hash pass khi chọn button 
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query_game(call):
    try:
        if call.data == "sha256":
            type_hash = "Sha256"
            hash_content = hashlib.sha256(noi_dung_can_hash.encode()).hexdigest()
        elif call.data == "md5":
            type_hash = "Md5"
            hash_content = hashlib.md5(noi_dung_can_hash.encode()).hexdigest()
        elif call.data == "sha1":
            type_hash = "Sha1"
            hash_content = hashlib.sha1(noi_dung_can_hash.encode()).hexdigest()
        elif call.data == "sha512":
            type_hash = "Sha512"
            hash_content = hashlib.sha512(noi_dung_can_hash.encode()).hexdigest()
        elif call.data == "b2b":
            type_hash = "Blake2b"
            hash_content = hashlib.blake2b(noi_dung_can_hash.encode()).hexdigest()
        elif call.data == "sha3_256":
            type_hash = "Sha3_256"
            hash_content = hashlib.sha3_256(noi_dung_can_hash.encode()).hexdigest()
        elif call.data == "mmh3":
            type_hash = "MMH3"
            hash_content = mmh3.hash(noi_dung_can_hash)
        elif call.data == "cityhash":
            type_hash = "CityHash"
            hash_content = cityhash.CityHash64(noi_dung_can_hash)
        elif call.data == "xxhash":
            type_hash = "XXHash"
            hash_content = xxhash.xxh64(noi_dung_can_hash).hexdigest()
        elif call.data == "argon2":
            type_hash = "Argon2"
            hash_content = PasswordHasher().hash(noi_dung_can_hash)
        elif call.data == "all":
            choice_all(call.message)    
            return 
        elif call.data == "hsds":
            danh_sach_lenh = (
               "<b>HƯỚNG DẪN SỬ DỤNG\n"
               "Lệnh: /hash + [nội dung muốn bảo mật] (như thông tin mật v.v.)\nVí dụ: /hash baomat123\n"
            )       
            bot.send_message(message.chat.id, danh_sach_lenh, parse_mode = "HTML")
        elif call.data == "cancel":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            return
        cancel_button = telebot.types.InlineKeyboardButton("❌ Huỷ bỏ", callback_data="cancel")
        keyboard = telebot.types.InlineKeyboardMarkup() 
        keyboard.row(cancel_button)     
        bot.send_message(call.message.chat.id, f"*Kiểu hash:* {type_hash}\n*Nội dung sau khi hash:* `{hash_content}`", parse_mode="MarkdownV2", reply_markup=keyboard)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"<b>Đã xảy ra lỗi: {e}</b>", parse_mode = "HTML")

# Hàm tổng cho lựa hash pass
@bot.message_handler(commands=['hash'])
def hash_password(message):
    global noi_dung_can_hash
    try:
        phan_thong_tin = message.text.split(maxsplit=1)
        if len(phan_thong_tin) != 2:
            bot.send_message(message.chat.id, "</b>Vui lòng nhập đúng mẫu /hash [nội dung]</b>", parse_mode="HTML")
            return 
        noi_dung_can_hash = " ".join(phan_thong_tin[1:]) if len(phan_thong_tin) > 1 else ""   
        sha256_button = telebot.types.InlineKeyboardButton("Sha256", callback_data="sha256")
        md5_button = telebot.types.InlineKeyboardButton("Md5", callback_data="md5")
        sha1_button = telebot.types.InlineKeyboardButton("Sha1", callback_data="sha1")
        sha512_button = telebot.types.InlineKeyboardButton("Sha512", callback_data="sha512")
        b2b_button = telebot.types.InlineKeyboardButton("Blake2b", callback_data="b2b")
        sha3_256_button = telebot.types.InlineKeyboardButton("Sha3-256", callback_data="sha3_256")
        mmh3_button = telebot.types.InlineKeyboardButton("MMH3", callback_data="mmh3")
        cityhash_button = telebot.types.InlineKeyboardButton("CityHash", callback_data="cityhash")
        xxhash_button = telebot.types.InlineKeyboardButton("XXHash", callback_data="xxhash")
        argon2_button = telebot.types.InlineKeyboardButton("Argon2", callback_data="argon2")
        all_button = telebot.types.InlineKeyboardButton("Choice all", callback_data="all")
        cancel_button = telebot.types.InlineKeyboardButton("❌ Huỷ bỏ", callback_data="cancel")
        keyboard = telebot.types.InlineKeyboardMarkup() 
        keyboard.row(argon2_button) 
        keyboard.row(sha256_button, md5_button, sha1_button)  
        keyboard.row(sha512_button, b2b_button, sha3_256_button)  
        keyboard.row(mmh3_button, cityhash_button, xxhash_button)  
        keyboard.row(all_button)
        keyboard.row(cancel_button) 
        bot.send_message(message.chat.id, f"*Nội dung của bạn:* ||{noi_dung_can_hash}||\n*Chọn kiểu Hash bên dưới 👇*", parse_mode="MarkdownV2", reply_markup=keyboard)
    except ValueError:
        bot.send_message(message.chat.id, f"<b>Vui lòng nhập đúng mẫu /hash [nội dung]</b>", parse_mode="HTML")   
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi: {e}</b>", parse_mode="HTML")

# Hàm trả về all nội dung hash 
def choice_all(message):
    try:
        hash_sha256 = hashlib.sha256(noi_dung_can_hash.encode()).hexdigest()
        hash_md5 = hashlib.md5(noi_dung_can_hash.encode()).hexdigest()
        hash_sha1 = hashlib.sha1(noi_dung_can_hash.encode()).hexdigest()
        hash_sha512 = hashlib.sha512(noi_dung_can_hash.encode()).hexdigest()
        hash_blake2b = hashlib.blake2b(noi_dung_can_hash.encode()).hexdigest()
        hash_sha3_256 = hashlib.sha3_256(noi_dung_can_hash.encode()).hexdigest()
        hash_mmh3 = mmh3.hash(noi_dung_can_hash)
        hash_cityhash = cityhash.CityHash64(noi_dung_can_hash)
        hash_xxhash = xxhash.xxh64(noi_dung_can_hash).hexdigest()
        ph = PasswordHasher()
        hash_ph = ph.hash(noi_dung_can_hash)
        noi_dung_choice_all = (
            f"<b>NỘI DUNG CUẢ BẠN</b>\n"
            f"<pre><b>Sha256:</b> {hash_sha256}\n"
            f"<b>Md5:</b> {hash_md5}\n"
            f"<b>Sha1:</b> {hash_sha1}\n"
            f"<b>Sha512:</b> {hash_sha512}\n"
            f"<b>Blake2b:</b> {hash_blake2b}\n"
            f"<b>Sha3_256:</b> {hash_sha3_256}\n"
            f"<b>MMH3:</b> {hash_mmh3}\n"
            f"<b>CityHash:</b> {hash_cityhash}\n"
            f"<b>XXHash:</b> {hash_xxhash}\n"
            f"<b>Argon2:</b> {hash_ph}</pre>"
        )
        cancel_button = telebot.types.InlineKeyboardButton("❌ Huỷ bỏ", callback_data="cancel")
        keyboard = telebot.types.InlineKeyboardMarkup() 
        keyboard.row(cancel_button)     
        bot.send_message(message.chat.id, noi_dung_choice_all, parse_mode = "HTML")
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi: {e}</b>", parse_mode = "HTML")        
            
# Hàm trả lời ngoại lệ
@bot.message_handler(func=lambda message: True)
@bot.message_handler(content_types=['sticker','photo','video','document'])    
def tra_loi_ngoai_le(message):
    huong_dan_su_dung = telebot.types.InlineKeyboardButton("📜 Hướng dẫn sử dụng", callback_data="hsds")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(huong_dan_su_dung)
    bot.send_message(message.chat.id, f"<b>❌ Sai lệnh. Vui lòng xem lại</b>", parse_mode = "HTML", reply_markup = keyboard)
    
bot.infinity_polling()