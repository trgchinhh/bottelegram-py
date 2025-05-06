# ! py
# Bot dich
# Copyright by @Truongchinh304

import os
import telebot 
import datetime
import threading
from gtts import gTTS
from datetime import datetime, timedelta    
from deep_translator import GoogleTranslator
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from collections import defaultdict, deque


ID_ADMIN = "THAY_ID_ADMIN"
print("\nBot đang hoạt động ...\n")       
bot = telebot.TeleBot("THAY_API_BOT")


# Lưu thông tin người dùng vào biến tạm thời 
user_lsdich = defaultdict(lambda: deque(maxlen=10)) # Lưu lại lịch sử 10 lần gần nhất


@bot.message_handler(commands=['start'])
def start(message):
    global file_path_main
    User_id = str(message.chat.id)
    user_name = message.from_user.username
    if not user_name :
        full_name = message.from_user.first_name + " " + message.from_user.last_name
    else:    
        full_name = user_name
    # Đường dẫn tạo file main lưu lịch sử dịch người dùng     
    file_path_main = "/sdcard/download/codingpython/User_infor_translate_main.txt"
    user_infor = (
        #f"📜 Thông tin lịch sử dịch\n"
        " ➤ Lịch sử dịch gồm \n"
    )
    # Kiểm tra User_id có trong file chưa      
    try:
        if not os.path.exists(file_path_main):
            with open(file_path_main, "w", encoding="utf-8") as file:
                file.write("")
        with open(file_path_main, "r", encoding="utf-8") as file:
            kiem_tra_id_trong_file = file.read()
        if User_id not in kiem_tra_id_trong_file:
            with open(file_path_main, "a", encoding="utf-8") as file:
                file.write(f"--------- THÔNG TIN USER ID {User_id} ---------\n")
                file.write(user_infor)
                file.write("-------------------------------------------------\n\n")
            huong_dan_ki_tu_ngon_ngu = telebot.types.InlineKeyboardButton("Language Symbols 🧾", callback_data="ki_tu_ngon_ngu")
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(huong_dan_ki_tu_ngon_ngu)
            bot.send_message(message.chat.id, f"<b>🗺️ Chào mừng {full_name} đến với bot phiên dịch trên telegram !\n\nNhấp vào nút bên dưới để xem kí hiệu ngôn ngữ các quốc gia</b>", parse_mode='HTML',reply_markup=keyboard)    
            handle_button(message)
        else:
            huong_dan_ki_tu_ngon_ngu = telebot.types.InlineKeyboardButton("Kí Tự Ngôn Ngữ 🌐", callback_data="ki_tu_ngon_ngu")
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(huong_dan_ki_tu_ngon_ngu)
            bot.send_message(message.chat.id, f"<b>👇 nút xem kí hiệu ngôn ngữ các quốc gia !</b>", parse_mode='HTML',reply_markup=keyboard)    
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi: {e}!</b>", parse_mode='HTML')    


# Lưu lại thời gian dịch đưa vào ls
def thoi_gian_hien_tai():
    thoi_gian_hien_tai = datetime.now() + timedelta(hours=0)
    gio_phut_giay = thoi_gian_hien_tai.strftime("%H:%M:%S")
    ngay_hien_tai = thoi_gian_hien_tai.strftime("%d-%m-%Y")
    return ngay_hien_tai, gio_phut_giay
def cap_nhat_thoi_gian():
    global thoigian, ngay
    while True:
        ngay, thoigian = thoi_gian_hien_tai()
threading.Thread(target=cap_nhat_thoi_gian, daemon=True).start()
    

def handle_button(message):
    user_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button0 = types.KeyboardButton(text="📋 Hướng dẫn")
    button1 = types.KeyboardButton(text="👤 Tài khoản")
    user_markup.add(button0, button1)
    bot.send_message(message.chat.id, "<b>Chọn 1 trong 2 nút bên dưới 👇</b>", reply_markup=user_markup, parse_mode='HTML')    


@bot.message_handler(func=lambda message: message.text == "👤 Tài khoản")
def account(message):
    User_id = str(message.chat.id)
    user_name = message.from_user.username
    if not user_name :
        full_name = message.from_user.first_name + " " + message.from_user.last_name
    else:    
        full_name = user_name
    Account = (
        f"👤 Tên tài khoản : `{full_name}`\n"
        f"💳 ID tài khoản : `{User_id}`\n"
    )    
    lsdich_button = telebot.types.InlineKeyboardButton("⏱️ Lịch sử dịch ⏱️", callback_data="lsdich")
    text_button = telebot.types.InlineKeyboardButton("TEXT (Chỉ có văn bản) 📝", callback_data="text")
    sound_button = telebot.types.InlineKeyboardButton("SOUND (Văn bản và âm thanh) 🔊", callback_data="sound")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(text_button)
    keyboard.row(sound_button)
    keyboard.row(lsdich_button)
    bot.send_message(message.chat.id, Account, parse_mode='Markdown',reply_markup=keyboard)
            

@bot.message_handler(func=lambda message: message.text == "📋 Hướng dẫn") 
def instruct(message):
    bot.send_message(message.chat.id, "<b>Bot Translate On Telegram 🗺️\n\n➤ Bạn muốn dịch từ trên bot ? Chỉ cần làm theo hướng dẫn sau 👇\n\nNếu bạn muốn dịch chỉ có văn bản dịch thì gõ theo cú pháp\n\n➤ /text [dấu cách] kí hiệu ngôn ngữ [dấu cách] văn bản cần dịch\n➤ Ví dụ : muốn dịch từ 'Information' từ tiếng anh sang tiếng việt chỉ cần gõ cú pháp sau\n/dich vi information\nGiải thích :\n- /text là cú pháp bắt buộc để bot hiểu và thực hiện\n- vi : là kí hiệu ngôn ngữ quốc gia cuả Việt Nam 🇻🇳\n- sau kí tự ngôn ngữ là văn bản cần dịch bot sẽ hiểu và thực hiện dịch từ phần đó !!!\n\nNếu bạn muốn kèm theo file âm thanh để có thể nghe thì gõ theo cú pháp sau 👇\n➤ /sound [dấu cách] kí hiệu ngôn ngữ gốc [dấu cách] kí hiệu ngôn ngữ muốn dịch [dấu cách] văn bản cần dịch\n➤ Ví dụ : Ví dụ : muốn dịch từ 'Information' từ tiếng anh sang tiếng việt kèm âm thanh chỉ cần gõ cú pháp sau\n/sound en vi information\nGiải thích :\n- /sound là cú pháp bắt buộc để bot hiểu và thực hiện\n- en : là kí hiệu ngôn ngữ gốc\n- vi : là kí hiệu ngôn ngữ cần dịch\n- sau kí tự ngôn ngữ cần dịch là văn bản cần dịch bot sẽ hiểu và thực hiện dịch từ phần đó !!!</b>", parse_mode='HTML')
    

def see_translation_history(message):
    User_id = str(message.chat.id)
    # Đọc nội dung từ file
    try:
        with open(file_path_main, "r", encoding="utf-8") as file:
            noi_dung = file.read()
        phan_bat_dau = f"--------- THÔNG TIN USER ID {User_id} ---------"
        phan_ket_thuc = "-------------------------------------------------"
        chi_so_bat_dau = noi_dung.find(phan_bat_dau)
        chi_so_ket_thuc = noi_dung.find(phan_ket_thuc, chi_so_bat_dau)
        if chi_so_bat_dau == -1 or chi_so_ket_thuc == -1:
            bot.send_message(message.chat.id, "<b>Chưa có lịch sử dịch</b>", parse_mode='HTML')
            return
        thong_tin_user = noi_dung[chi_so_bat_dau:chi_so_ket_thuc]
        lich_su_dich = thong_tin_user.split("\n")
        history_text = "<b>LỊCH SỬ 10 PHIÊN DỊCH GẦN NHẤT\n\nThời gian  |  Từ cần dịch  |  Từ đã dịch\n</b>"
        lich_su = [line for line in lich_su_dich if "|" in line]
        latest_history = lich_su[-10:]  # Lấy 10 phiên gần nhất
        for idx, record in enumerate(latest_history, start=1):
            history_text += f"{idx}. {record}\n"
        bot.send_message(message.chat.id, history_text, parse_mode='HTML')
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi khi lấy lịch sử dịch: {e}</b>", parse_mode='HTML')                
        

# Cập nhật lịch sử dịch vào file 
def cap_nhat_lich_su_dich(User_id, thoi_gian, van_ban_can_dich, van_ban_duoc_dich):
    lich_su_dich_moi = f"\n{thoi_gian} | {van_ban_can_dich} | {van_ban_duoc_dich}\n"
    with open(file_path_main, "r", encoding="utf-8") as file:
        noi_dung = file.readlines()
    vi_tri_bat_dau = None
    for i, line in enumerate(noi_dung):
        if line.strip() == f"--------- THÔNG TIN USER ID {User_id} ---------":
            vi_tri_bat_dau = i
            break
    if vi_tri_bat_dau is not None:
        for i in range(vi_tri_bat_dau, len(noi_dung)):
            if noi_dung[i].strip() == "-------------------------------------------------":
                noi_dung.insert(i, lich_su_dich_moi)
                break
        with open(file_path_main, "w", encoding="utf-8") as file:
            file.writelines(noi_dung)
            
                                
@bot.message_handler(commands=['get'])
def lay_thong_tin(message):
    User_id = str(message.chat.id)
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "<b>❌ Yêu cầu không đúng định dạng. Vui lòng nhập theo mẫu: /get [dấu cách] id muốn lấy dữ liệu</b>", parse_mode='HTML')
        return
    ID_can_tim = parts[1]
    try:
        if User_id != ID_ADMIN:
            bot.send_message(message.chat.id, "<b>🚫 Bạn không có quyền sử dụng lệnh này !!!</b>", parse_mode='HTML')
            return   
        if parts[1] == "ALL" and User_id == ID_ADMIN:
            with open(file_path_main, "rb") as file:
                bot.send_document(message.chat.id, file)
            bot.send_message(message.chat.id, "<b>LSDịch toàn bộ người dùng !</b>", parse_mode='HTML')    
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xãy ra lỗi {e} !</b>", parse_mode='HTML') 
    # Phần tách 1 phần thông tin từ file main          
    try:  
        with open(file_path_main, "r", encoding="utf-8") as file:
            noi_dung = file.read()
        if ID_can_tim not in noi_dung:
            if ID_can_tim == "ALL":
                return 
            bot.send_message(message.chat.id, f"<b>ID: {ID_can_tim} không tìm thấy trong file</b>", parse_mode='HTML')
            return
        phan_bat_dau = f"--------- THÔNG TIN USER ID {ID_can_tim} ---------"
        phan_ket_thuc = "-------------------------------------------------"
        chi_so_bat_dau = noi_dung.find(phan_bat_dau)
        chi_so_ket_thuc = noi_dung.find(phan_ket_thuc, chi_so_bat_dau) + len(phan_ket_thuc)
        thong_tin_user = noi_dung[chi_so_bat_dau:chi_so_ket_thuc]
        file_path_user = f"/sdcard/download/codingpython/{ID_can_tim}.txt"
        with open(file_path_user, "w", encoding="utf-8") as file:
            file.write(thong_tin_user)
        with open(file_path_user, "rb") as file:
            bot.send_document(message.chat.id, file)
            bot.send_message(message.chat.id, f"<b>➤ ID : {ID_can_tim}\nHoàn thành xuất file lịch sử dịch</b>", parse_mode='HTML')
        os.remove(file_path_user) # Xoá file trích xuất 
    except Exception as e: 
        bot.send_message(message.chat.id, f"<b>Đã xãy ra lỗi {e} !</b>", parse_mode='HTML') 


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query_game(call):
    if call.data == "ki_tu_ngon_ngu":
        bot.send_message(call.message.chat.id, """<b>Dưới đây là danh sách các ngôn ngữ và ký hiệu quốc gia tương ứng:
        
- **af** - Afrikaans 🇿🇦
- **sq** - Albanian 🇦🇱
- **am** - Amharic 🇪🇹
- **ar** - Arabic 🇸🇦
- **hy** - Armenian 🇦🇲
- **az** - Azerbaijani 🇦🇿
- **eu** - Basque 🇪🇸
- **be** - Belarusian 🇧🇾
- **bn** - Bengali 🇧🇩
- **bs** - Bosnian 🇧🇦
- **bg** - Bulgarian 🇧🇬
- **ca** - Catalan 🇪🇸
- **ceb** - Cebuano 🇵🇭
- **ny** - Chichewa 🇲🇼
- **zh-CN** - Chinese (Simplified) 🇨🇳
- **zh-TW** - Chinese (Traditional) 🇹🇼
- **co** - Corsican 🇫🇷
- **hr** - Croatian 🇭🇷
- **cs** - Czech 🇨🇿
- **da** - Danish 🇩🇰
- **nl** - Dutch 🇳🇱
- **en** - English 🇬🇧
- **eo** - Esperanto 🇵🇱
- **et** - Estonian 🇪🇪
- **tl** - Filipino 🇵🇭
- **fi** - Finnish 🇫🇮
- **fr** - French 🇫🇷
- **fy** - Frisian 🇳🇱
- **gl** - Galician 🇪🇸
- **ka** - Georgian 🇬🇪
- **de** - German 🇩🇪
- **el** - Greek 🇬🇷
- **gu** - Gujarati 🇮🇳
- **ht** - Haitian Creole 🇭🇹
- **ha** - Hausa 🇳🇬
- **haw** - Hawaiian 🇺🇸
- **iw** - Hebrew 🇮🇱
- **he** - Hebrew 🇮🇱
- **hi** - Hindi 🇮🇳
- **hmn** - Hmong 🇲🇲
- **hu** - Hungarian 🇭🇺
- **is** - Icelandic 🇮🇸
- **ig** - Igbo 🇳🇬
- **id** - Indonesian 🇮🇩
- **ga** - Irish 🇮🇪
- **it** - Italian 🇮🇹
- **ja** - Japanese 🇯🇵
- **jw** - Javanese 🇮🇩
- **kn** - Kannada 🇮🇳
- **kk** - Kazakh 🇰🇿
- **km** - Khmer 🇲🇲
- **ko** - Korean 🇰🇷
- **ku** - Kurdish (Kurmanji) 🇹🇯
- **ky** - Kyrgyz 🇰🇬
- **lo** - Lao 🇱🇦
- **la** - Latin 🇻🇦
- **lv** - Latvian 🇱🇻
- **lt** - Lithuanian 🇱🇹
- **lb** - Luxembourgish 🇱🇺
- **mk** - Macedonian 🇲🇰
- **mg** - Malagasy 🇲🇬
- **ms** - Malay 🇲🇾
- **ml** - Malayalam 🇮🇳
- **mt** - Maltese 🇲🇹
- **mi** - Maori 🇳🇿
- **mr** - Marathi 🇮🇳
- **mn** - Mongolian 🇲🇳
- **my** - Myanmar (Burmese) 🇲🇲
- **ne** - Nepali 🇳🇵
- **no** - Norwegian 🇳🇴
- **or** - Odia 🇮🇳
- **ps** - Pashto 🇦🇫
- **fa** - Persian 🇮🇷
- **pl** - Polish 🇵🇱
- **pt** - Portuguese 🇵🇹
- **pa** - Punjabi 🇮🇳
- **ro** - Romanian 🇷🇴
- **ru** - Russian 🇷🇺
- **sm** - Samoan 🇼🇸
- **gd** - Scots Gaelic 🇬🇧
- **sr** - Serbian 🇷🇸
- **st** - Sesotho 🇱🇸
- **sn** - Shona 🇿🇼
- **sd** - Sindhi 🇵🇰
- **si** - Sinhala 🇱🇰
- **sk** - Slovak 🇸🇰
- **sl** - Slovenian 🇸🇮
- **so** - Somali 🇸🇴
- **es** - Spanish 🇪🇸
- **su** - Sundanese 🇲🇨
- **sw** - Swahili 🇰🇪
- **sv** - Swedish 🇸🇪
- **tg** - Tajik 🇹🇯
- **ta** - Tamil 🇮🇳
- **te** - Telugu 🇮🇳
- **th** - Thai 🇹🇭
- **tr** - Turkish 🇹🇷
- **uk** - Ukrainian 🇺🇦
- **ur** - Urdu 🇵🇰
- **ug** - Uyghur 🇨🇳
- **uz** - Uzbek 🇺🇿
- **vi** - Vietnamese 🇻🇳
- **cy** - Welsh 🇬🇧
- **xh** - Xhosa 🇿🇦
- **yi** - Yiddish 🇮🇱
- **yo** - Yoruba 🇳🇬
- **zu** - Zulu 🇿🇦
        
Lưu ý : khi sử dụng kí hiệu ngôn ngữ nhớ bỏ 4 dấu * ở 2 bên đi
➤ Ví dụ : muốn dịch từ tiếng việt sang tiếng anh thì nhập kí hiệu là vi en không nhập **vi** **en**.</b>""", parse_mode='HTML')
    elif call.data == "lsdich":
        see_translation_history(call.message)        
    elif call.data == "text":
        bot.send_message(call.message.chat.id, "<b>Vui lòng nhập theo mẫu\n➤ /text [dấu cách] kí hiệu ngôn ngữ [dấu cách] văn bản cần dịch</b>", parse_mode='HTML')
    elif call.data == "sound":
        bot.send_message(call.message.chat.id, "<b>Vui lòng nhập theo mẫu\n➤ /sound [dấu cách] kí hiệu ngôn ngữ gốc [dấu cách] kí hiệu ngôn ngữ dịch [dấu cách] văn bản cần dịch</b>", parse_mode='HTML')


# Rút gọn văn bản khi dài hơn 3 chữ
# Lưu vào lịch sử dịch
def rut_gon_van_ban(van_ban, max_tu=3):
    tu = van_ban.split()
    if len(tu) > max_tu:
        return f"{tu[0]} {tu[1]} ... {tu[-2]} {tu[-1]}"
    return van_ban


# TEXT 
@bot.message_handler(commands=['text'])
def translate(message):
    User_id = str(message.chat.id)
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(message.chat.id, "<b>❌ Yêu cầu không đúng định dạng. Vui lòng nhập theo mẫu: /text [dấu cách] kí hiệu ngôn ngữ [dấu cách] văn bản cần dịch</b>", parse_mode='HTML')
        return
    ki_tu_ngon_ngu = parts[1]
    van_ban_can_dich = " ".join(parts[2:]) if len(parts) > 2 else ""
    ki_tu_ngon_ngu_hop_le = ["af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca", "ceb", "ny", "zh-CN", "zh-TW", "co", "hr", "cs", "da", "nl", "en", "eo", "et", "tl", "fi", "fr", "fy", "gl", "ka", "de", "el", "gu", "ht", "ha", "haw", "iw", "he", "hi", "hmn", "hu", "is", "ig", "id", "ga", "it", "ja", "jw", "kn", "kk", "km", "ko", "ku", "ky", "lo", "la", "lv", "lt", "lb", "mk", "mg", "ms", "ml", "mt", "mi", "mr", "mn", "my", "ne", "no", "or", "ps", "fa", "pl", "pt", "pa", "ro", "ru", "sm", "gd", "sr", "st", "sn", "sd", "si", "sk", "sl", "so", "es", "su", "sw", "sv", "tg", "ta", "te", "th", "tr", "uk", "ur", "ug", "uz", "vi", "cy", "xh", "yi", "yo", "zu"]
    if ki_tu_ngon_ngu not in ki_tu_ngon_ngu_hop_le:
        huong_dan_ki_tu_ngon_ngu = telebot.types.InlineKeyboardButton("Kí Tự Ngôn Ngữ 🌐", callback_data="ki_tu_ngon_ngu")
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(huong_dan_ki_tu_ngon_ngu)
        bot.send_message(message.chat.id, f"<b>❌ Sai kí tự. Vui lòng xem lại !</b>", parse_mode='HTML',reply_markup=keyboard)
        return
    try:
        thoi_gian_dich = thoigian + " " + ngay
        van_ban_duoc_dich = GoogleTranslator(source='auto', target=ki_tu_ngon_ngu).translate(van_ban_can_dich)
        bot.send_message(message.chat.id, f"<b>📜 Văn bản dịch: {van_ban_duoc_dich}</b>", parse_mode='HTML')
        van_ban_can_dich_rut_gon = rut_gon_van_ban(van_ban_can_dich)
        van_ban_duoc_dich_rut_gon = rut_gon_van_ban(van_ban_duoc_dich)
        user_lsdich[User_id].append({
            'thoi_gian_dich' : thoi_gian_dich,
            'lich_su_tu_can_dich': van_ban_can_dich_rut_gon,
            'lich_su_tu_duoc_dich': van_ban_duoc_dich_rut_gon 
        })    
        cap_nhat_lich_su_dich(User_id, thoi_gian_dich, van_ban_can_dich_rut_gon, van_ban_duoc_dich_rut_gon)
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>❌ Đã xảy ra lỗi khi dịch. Vui lòng thử lại sau. Chi tiết lỗi: {e}</b>", parse_mode='HTML')
        
        
# SOUND        
@bot.message_handler(commands=['sound'])
def translate(message):
    User_id = str(message.chat.id)
    parts = message.text.split(maxsplit=4)
    if len(parts) < 4:
        bot.send_message(message.chat.id, "<b>❌ Yêu cầu không đúng định dạng. Vui lòng nhập theo mẫu: /sound [dấu cách] kí hiệu ngôn ngữ gốc [dấu cách] kí hiệu ngôn ngữ dịch [dấu cách] văn bản cần dịch</b>", parse_mode='HTML')
        return
    van_ban_can_dich = " ".join(parts[3:]) if len(parts) > 3 else ""
    ki_tu_ngon_ngu_hop_le = ["af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca", "ceb", "ny", "zh-CN", "zh-TW", "co", "hr", "cs", "da", "nl", "en", "eo", "et", "tl", "fi", "fr", "fy", "gl", "ka", "de", "el", "gu", "ht", "ha", "haw", "iw", "he", "hi", "hmn", "hu", "is", "ig", "id", "ga", "it", "ja", "jw", "kn", "kk", "km", "ko", "ku", "ky", "lo", "la", "lv", "lt", "lb", "mk", "mg", "ms", "ml", "mt", "mi", "mr", "mn", "my", "ne", "no", "or", "ps", "fa", "pl", "pt", "pa", "ro", "ru", "sm", "gd", "sr", "st", "sn", "sd", "si", "sk", "sl", "so", "es", "su", "sw", "sv", "tg", "ta", "te", "th", "tr", "uk", "ur", "ug", "uz", "vi", "cy", "xh", "yi", "yo", "zu"]
    ki_tu_ngon_ngu_goc = parts[1]
    if ki_tu_ngon_ngu_goc not in ki_tu_ngon_ngu_hop_le:
        huong_dan_ki_tu_ngon_ngu = telebot.types.InlineKeyboardButton("Kí Tự Ngôn Ngữ 🌐", callback_data="ki_tu_ngon_ngu")
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(huong_dan_ki_tu_ngon_ngu)
        bot.send_message(message.chat.id, f"<b>❌ Sai kí tự. Vui lòng xem lại !</b>", parse_mode='HTML',reply_markup=keyboard)
        return    
    ki_tu_ngon_ngu_dich = parts[2]
    if ki_tu_ngon_ngu_dich not in ki_tu_ngon_ngu_hop_le:
        huong_dan_ki_tu_ngon_ngu = telebot.types.InlineKeyboardButton("Kí Tự Ngôn Ngữ 🌐", callback_data="ki_tu_ngon_ngu")
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(huong_dan_ki_tu_ngon_ngu)
        bot.send_message(message.chat.id, f"<b>❌ Sai kí tự. Vui lòng xem lại !</b>", parse_mode='HTML',reply_markup=keyboard)
        return    
    try:
        thoi_gian_dich = thoigian + " " + ngay
        van_ban_duoc_dich = GoogleTranslator(source=ki_tu_ngon_ngu_goc, target=ki_tu_ngon_ngu_dich).translate(van_ban_can_dich)
        bot.send_message(message.chat.id, f"<b>📜 Văn bản dịch: {van_ban_duoc_dich}</b>", parse_mode='HTML')
        van_ban_can_dich_rut_gon = rut_gon_van_ban(van_ban_can_dich)
        van_ban_duoc_dich_rut_gon = rut_gon_van_ban(van_ban_duoc_dich)
        user_lsdich[User_id].append({
            'thoi_gian_dich' : thoi_gian_dich,
            'lich_su_tu_can_dich': van_ban_can_dich_rut_gon,
            'lich_su_tu_duoc_dich': van_ban_duoc_dich_rut_gon 
        })
        tts_nguon = gTTS(van_ban_can_dich, lang=ki_tu_ngon_ngu_goc) 
        tts_dich = gTTS(van_ban_duoc_dich, lang=ki_tu_ngon_ngu_dich)
        tts_nguon.save("goc.mp3")
        tts_dich.save("dich.mp3")
        file_am_thanh_goc = bot.send_audio(message.chat.id, audio=open("goc.mp3", 'rb'), caption="Âm thanh văn bản gốc")
        file_am_thanh_dich = bot.send_audio(message.chat.id, audio=open("dich.mp3", 'rb'), caption="Âm thanh văn bản được dịch")
        os.remove("goc.mp3")
        os.remove("dich.mp3")
        cap_nhat_lich_su_dich(User_id, thoi_gian_dich, van_ban_can_dich_rut_gon, van_ban_duoc_dich_rut_gon)
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>❌ Đã xảy ra lỗi khi dịch. Vui lòng thử lại sau. Chi tiết lỗi: {e}</b>", parse_mode='HTML')


# Hàm trả lời ngoại lệ     
@bot.message_handler(func=lambda message: True)
@bot.message_handler(content_types=['sticker','photo','video','document'])    
def answer_exception(message):
    huong_dan_ki_tu_ngon_ngu = telebot.types.InlineKeyboardButton("Kí Tự Ngôn Ngữ 🌐", callback_data="ki_tu_ngon_ngu")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(huong_dan_ki_tu_ngon_ngu)
    bot.send_message(message.chat.id, f"<b>❌ Sai kí tự. Vui lòng xem lại !</b>", parse_mode='HTML',reply_markup=keyboard)        
        
        
bot.infinity_polling()            
