# ! py
# Bot lấy thông tin quốc gia
# Copyright by @Truongchinh304

import telebot, requests, os
from telebot import types 
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from deep_translator import GoogleTranslator

# Phần thay thông tin 
API_TOKEN = 'THAY API BOT'
ID_GROUP_CHAT = 'THAY ID GROUP'
ID_ADMIN = 'THAY ID ADMIN'
bot = telebot.TeleBot(API_TOKEN)
FILE_PATH_LIST_COUNTRY = "/sdcard/download/codingpython/list_country.txt"
TEMP_IMAGE_PATH = '/sdcard/download/codingpython/temp_flag.png'
print("Bot đã được khởi động ...")

# Hàm xử lý lệnh của người dùng
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.username
    if not user_name :
        full_name = message.from_user.first_name + " " + message.from_user.last_name
    else:    
        full_name = user_name
    danh_sach_lenh = telebot.types.InlineKeyboardButton("📜 Danh sách lệnh", callback_data="dsl")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(danh_sach_lenh)
    bot.send_message(message.chat.id, f"<b>Chào mừng {user_name} đến với bot tiện ích ! Nhấn nút dưới đây để xem các lệnh 👇</b>", parse_mode = "HTML", reply_markup = keyboard)

def danh_sach_lenh(message):
    danh_sach_lenh = (
        "<b>DANH SÁCH LỆNH\n"
        "Lệnh 1: /countryname (Lấy thông tin quốc gia)\nVí dụ: /vietnam\n"
        "Lệnh 2: /nhan (Thông báo bằng bot [Admin])\n"
        "LƯU Ý: Lệnh chỉ khả dụng trong group dưới đây 👇</b>"
    )    
    nut_vao_group = InlineKeyboardButton("🐧 Group tiện ích", url='https://t.me/+b-27lb0mxoZmY2I1')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(nut_vao_group)
    bot.send_message(message.chat.id, danh_sach_lenh, parse_mode = "HTML", reply_markup = keyboard)
    
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query_game(call):
    if call.data == "dsl":
        danh_sach_lenh(call.message)

# Hàm lấy thời gian hiện tại
def thoi_gian():
    thoi_gian = datatime.now().strftime("%d/%m/%Y - %H:%M:%S")
    return thoi_gian 

# Hàm dịch tên quốc gia sang tiếng Việt
def dich_sang_tieng_viet(text):
    try:
        translator = GoogleTranslator(source='auto', target='vi')
        return translator.translate(text)
    except Exception as e:
        bot.send_message(ID_ADMIN, f"<b>Lỗi khi dịch: {e}\nLúc: {datetime.now()}</b>", parse_mode="HTML")
        return text
            
# Kiểm tra xem người dùng có nhắn trong group không
def kiem_tra_group(message):
    if message.chat.type != "group" and message.chat.type != "supergroup":
        nut_vao_group = InlineKeyboardButton("🐧 Group tiện ích", url='https://t.me/+b-27lb0mxoZmY2I1')
        keyboard = InlineKeyboardMarkup()
        keyboard.row(nut_vao_group)
        bot.send_message(message.chat.id, "<b>Lệnh chỉ khả dụng trong group chat. Vui lòng vào group để sử dụng bot.</b>", parse_mode="HTML", reply_markup=keyboard)
        return False
    return True

# Hàm thông báo bằng bot
@bot.message_handler(commands=['nhan'])
def nhan(message):
    user_id = str(message.chat.id)
    if user_id != ID_ADMIN:
        bot.send_message(message.chat.id, "❌ Bạn không có quyền sử dụng lệnh này")
        return 
    msg_content = message.text[6:].strip()
    if msg_content:
        bot.send_message(ID_GROUP_CHAT, f"{msg_content}")
    else:
        bot.send_message(ID_ADMIN, "Vui lòng nhập nội dung tin nhắn sau lệnh /nhan")
        
# Hàm chuyển alpha2 thành icon flags
def ma_quoc_gia_thanh_flag_icon(ma_quoc_gia_alpha2):
    if len(ma_quoc_gia_alpha2) != 2:
        return 'N/A'
    return chr(ord(ma_quoc_gia_alpha2[0].upper()) + 127397) + chr(ord(ma_quoc_gia_alpha2[1].upper()) + 127397)
    
# Hàm lấy thông tin quốc gia         
def lay_thong_tin_quoc_gia(ten_quoc_gia):
    try:
        api = f"https://restcountries.com/v3.1/name/{ten_quoc_gia}"
        response = requests.get(api)
        if response.status_code == 200:
            cac_quoc_gia = response.json()
            for quoc_gia in cac_quoc_gia:
                if quoc_gia['name']['common'].lower() == ten_quoc_gia.lower():
                    ten = quoc_gia['name']['common']
                    #ten_day_du = quoc_gia['name']['official'] # Tên đầy đủ tiếng anh
                    ten_day_du = dich_sang_tieng_viet(quoc_gia['name']['official'])
                    thu_do = quoc_gia.get('capital', ['N/A'])[0]
                    khu_vuc = quoc_gia.get('region', 'N/A')
                    dan_so = quoc_gia.get('population', 'N/A')
                    mui_gio = ', '.join(quoc_gia.get('timezones', []))
                    dien_tich = quoc_gia.get('area', 'N/A')
                    ngon_ngu = ', '.join(quoc_gia.get('languages', {}).values())
                    tien_te = ', '.join([f"{cur['name']} ({cur['symbol']})" for cur in quoc_gia.get('currencies', {}).values()])
                    quoc_ky = quoc_gia.get('flags', {}).get('png', 'N/A')
                    vi_tri = quoc_gia.get('latlng', 'N/A')
                    ma_quoc_gia_alpha2 = quoc_gia.get('cca2', 'N/A')
                    ma_quoc_gia_alpha3 = quoc_gia.get('cca3', 'N/A')
                    bien_gioi_cac_quoc_gia_khac = ', '.join(quoc_gia.get('borders', ['Không có']))
                    ten_mien = ', '.join(quoc_gia.get('tld', []))
                    dan_toc_chinh = quoc_gia.get('demonym', 'N/A')
                    che_do_chinh_tri = quoc_gia.get('government', 'N/A')
                    da_doc_lap = quoc_gia.get('independent', 'N/A')
                    if da_doc_lap == True:
                        da_doc_lap = "Có"
                    elif da_doc_lap == False:
                        da_doc_lap = "Không"
                    da_tham_gia_lien_hop_quoc = quoc_gia.get('unMember', 'N/A')
                    if da_tham_gia_lien_hop_quoc == True:
                        da_tham_gia_lien_hop_quoc = "Có"
                    elif da_tham_gia_lien_hop_quoc == False:
                        da_tham_gia_lien_hop_quoc = "Không"
                    bieu_tuong_co = ma_quoc_gia_thanh_flag_icon(ma_quoc_gia_alpha2)    
                    thong_tin = (
                        f"<b>📋<u>THÔNG TIN QUỐC GIA {ten.upper()}</u></b>\n\n"
                        f"<b>{bieu_tuong_co}Quốc gia:</b> {ten}\n"
                        f"<b>{bieu_tuong_co}Tên đầy đủ:</b> {ten_day_du}\n"
                        f"<b>{bieu_tuong_co}Thủ đô:</b> {thu_do}\n"
                        f"<b>{bieu_tuong_co}Chế độ chính trị:</b> {che_do_chinh_tri}\n"
                        f"<b>{bieu_tuong_co}Đã độc lập:</b> {da_doc_lap}\n"
                        f"<b>{bieu_tuong_co}Đã tham gia LHQ:</b> {da_tham_gia_lien_hop_quoc}\n"
                        f"<b>{bieu_tuong_co}Khu vực:</b> {khu_vuc}\n"
                        f"<b>{bieu_tuong_co}Dân số:</b> {dan_so}\n"
                        f"<b>{bieu_tuong_co}Múi giờ:</b> {mui_gio}\n"
                        f"<b>{bieu_tuong_co}Diện tích:</b> {dien_tich} km²\n"
                        f"<b>{bieu_tuong_co}Ngôn ngữ:</b> {ngon_ngu}\n"
                        f"<b>{bieu_tuong_co}Tiền tệ:</b> {tien_te}\n"
                        f"<b>{bieu_tuong_co}Mã quốc gia (Alpha-2):</b> {ma_quoc_gia_alpha2}\n"
                        f"<b>{bieu_tuong_co}Mã quốc gia (Alpha-3):</b> {ma_quoc_gia_alpha3}\n"
                        f"<b>{bieu_tuong_co}Toạ độ:</b> {vi_tri}\n"
                        f"<b>{bieu_tuong_co}Biên giới cùng:</b> {bien_gioi_cac_quoc_gia_khac}\n"
                        f"<b>{bieu_tuong_co}Tên miền quốc gia:</b> {ten_mien.upper()}\n"
                    )        
                    return thong_tin, quoc_ky
            return None, None         
        else:
            return None, None 
    except Exception as e:
        bot.send_message(ID_ADMIN, f"<b>Đã xảy ra lỗi: {e}\nLúc: {thoi_gian()}</b>", parse_mode = "HTML")        
        return None, None 

# Hàm lấy list các quốc gia có thể xem thông tin
@bot.message_handler(commands=['list'])
def lay_danh_sach_quoc_gia(message):
    try:
        url = "https://restcountries.com/v3.1/all"
        response = requests.get(url)
        if response.status_code == 200:
            cac_quoc_gia = response.json()
            noi_dung_list = "<b><u>DANH SÁCH CÁC QUỐC GIA</u></b>\n"
            danh_sach_quoc_gia = [quoc_gia['name']['common'] for quoc_gia in cac_quoc_gia]
            noi_dung_list += "\n".join(danh_sach_quoc_gia) + "\n"
            if len(noi_dung_list) > 4096:
                with open(FILE_PATH_LIST_COUNTRY, "w", encoding = "utf-8") as file:
                    file.write(noi_dung_list)
                with open(FILE_PATH_LIST_COUNTRY, "rb") as file:
                    bot.send_document(message.chat.id, file, caption = "Danh sách các quốc gia")
            else:
                bot.send_message(message.chat.id, f"DANH SÁCH CÁC QUỐC GIA\n{noi_dung_list}\n")        
        else:
            bot.send_message(message.chat.id, "<b>Không có danh sách các quốc gia</b>", parse_mode = "HTML")
    except Exception as e:
        bot.send_message(ID_ADMIN, f"<b>Đã xảy ra lỗi: {e}\nLúc {datetime.now()}</b>", parse_mode = "HTML")    
                
@bot.message_handler(func=lambda message: message.text.startswith('/'))
def gui_thong_tin_quoc_gia(message):
    if kiem_tra_group(message):  
        ten_quoc_gia = message.text[1:]
        thong_tin, quoc_ky = lay_thong_tin_quoc_gia(ten_quoc_gia)
        if thong_tin and quoc_ky:
            bot.send_photo(message.chat.id, quoc_ky)
            bot.send_message(message.chat.id, thong_tin, parse_mode = "HTML")
        else:
            bot.send_message(message.chat.id, f"<b>Không tìm thấy thông tin quốc gia: {ten_quoc_gia}</b>", parse_mode = "HTML")
        
@bot.message_handler(func=lambda message: True)
@bot.message_handler(content_types=['sticker','photo','video','document'])    
def tra_loi_ngoai_le(message):
    danh_sach_lenh = telebot.types.InlineKeyboardButton("📜 Danh sách lệnh", callback_data="dsl")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(danh_sach_lenh)
    bot.send_message(message.chat.id, f"<b>❌ Sai lệnh. Vui lòng xem lại</b>", parse_mode = "HTML", reply_markup = keyboard)
    
bot.infinity_polling()











    
