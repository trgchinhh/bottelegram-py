# ! py
# Bot telebank 
# Copyright by @Truongchinh304

import telebot, os, hashlib
from telebot import types
from datetime import datetime 

API_KEY = "THAY API BOT VÀO ĐÂY"
bot = telebot.TeleBot(API_KEY)

path_luu_tien = "D:\\Python\\so_du.txt" # lưu số dư cho mọi user
path_luu_bill_nap = "D:\\Python\\bill_nap.txt" # lưu bill nạp của admin cho user
path_luu_bill_chuyen = "D:\\Python\\bill_chuyen.txt" # lưu bill chuyển tiền cho mọi user
path_luu_bill_nhan = "D:\\Python\\bill_nhan.txt" # lưu bill nhận tiền cho mọi user

ID_ADMIN = "THAY ID ADMIN"

def thoi_gian_hien_tai():
    return datetime.now().strftime('%H:%M:%S ngày %d/%m/%Y')

# lệnh nút inline 
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "nap_tien":
        bot.send_message(call.message.chat.id, "<b>Vui lòng sử dụng lệnh /naptien [ID] [Số tiền]</b>", parse_mode='HTML')
    elif call.data == "chuyen_tien":
        bot.send_message(call.message.chat.id, "<b>Vui lòng sử dụng lệnh /chuyentien [ID] [Số tiền] [Ghi chú]</b>", parse_mode='HTML')    
    elif call.data == "menu":
        help(call.message)

def handle_button(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button0 = types.KeyboardButton(text="📋 Hướng dẫn")
    button1 = types.KeyboardButton(text="👤 Tài khoản")
    keyboard.add(button0, button1)
    bot.send_message(message.chat.id, "<b>Chọn 1 trong 2 nút bên dưới 👇</b>", reply_markup=keyboard, parse_mode='HTML')    

@bot.message_handler(commands=['start'])  
def start(message):
    khong_tim_thay_so_tien = False
    User_id = str(message.chat.id)
    is_bot_ans = "True" if message.from_user.is_bot else "False"
    user_first_name = message.from_user.first_name
    user_last_name = message.from_user.last_name
    user_language = message.from_user.language_code
    user_name = message.from_user.username
    full_name = f"{user_first_name} {user_last_name}"
    try:
        User_id = str(message.chat.id)
        if os.path.exists(path_luu_tien):
            with open(path_luu_tien, "r") as file:
                nhung_so_tien = file.readlines()
                for so_tien in nhung_so_tien:
                    if so_tien.startswith(User_id):
                        so_tien_nguoi_dung = int(so_tien[len(User_id):].strip())
                        so_tien_nguoi_dung_dinh_dang = f"{so_tien_nguoi_dung:,.0f}".replace(',','.')
                        Nap_tien_button = telebot.types.InlineKeyboardButton("💳 Nạp tiền", callback_data="nap_tien")
                        Chuyen_tien_button = telebot.types.InlineKeyboardButton("💳 Chuyển tiền", callback_data="chuyen_tien")
                        keyboard = telebot.types.InlineKeyboardMarkup()
                        keyboard.row(Nap_tien_button)
                        keyboard.row(Chuyen_tien_button)
                        bot.send_message(message.chat.id, f"<b>💳Số dư tài khoản: {so_tien_nguoi_dung_dinh_dang} VNĐ</b>", parse_mode="HTML")
                        break
                else:
                    #bot.send_message(message.chat.id, f"<b>Không tìm thấy số dư ID: {User_id}</b>", parse_mode="HTML")
                    khong_tim_thay_so_tien = True
                    so_tien_nguoi_dung = 0
                    so_tien_nguoi_dung_dinh_dang = 0
                    infor_user = (
                        f"<b>TELEBANK BOT XIN CHÀO {full_name.upper()}</b>\n\n"
                        f"━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
                        f"👤 <b>Thông tin bạn:</b>\n"
                        f"<b>├ID:</b> {User_id}\n"
                        f"<b>├ Là bot:</b> {is_bot_ans}\n"
                        f"<b>├ Tên đầu:</b> {user_first_name}\n"
                        f"<b>├ Tên cuối:</b> {user_last_name}\n"
                        f"<b>├ Tên người dùng:</b> {user_name}\n"
                        f"<b>├ Tên đầy đủ:</b> {full_name}\n"
                        f"<b>└ Mã ngôn ngữ:</b> {user_language} (-)\n\n"
                        f"<b>💳 Số dư tài khoản:</b> {so_tien_nguoi_dung_dinh_dang} VNĐ\n"
                        f"<b>━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━</b>\n"
                        f"<b>➤ Nhấp vào nút hướng dẫn để xem cách sử dụng telebank</b>"
                    )
                    Nap_tien_button = telebot.types.InlineKeyboardButton("💳 Nạp tiền", callback_data="nap_tien")
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    keyboard.row(Nap_tien_button)
                    bot.send_message(message.chat.id, infor_user, parse_mode="HTML", reply_markup = keyboard)
            if khong_tim_thay_so_tien:
                with open(path_luu_tien, "a", encoding="utf-8") as file:
                    file.write(f"{User_id}{so_tien_nguoi_dung}\n")
        else:
            bot.send_message(message.chat.id, f"<b>Không tìm thấy đường dẫn {path_luu_tien}</b>", parse_mode="HTML")       
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi {e}</b>", parse_mode="HTML")

# Hàm yêu cầu nạp tiền cho user
@bot.message_handler(commands=['wload'])
def wload(message):    
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) != 3:
            bot.send_message(message.chat.id, "<b>Nhập theo mẫu /wload [User id] [Số tiền]</b>", parse_mode="HTML")
            return 
        id_muon_nap = parts[1]    
        so_tien_muon_nap = int(parts[2])
        so_tien_muon_nap_dinh_dang = f"{so_tien_muon_nap:,.0f}".replace(',','.')
        if not isinstance(so_tien_muon_nap, int):
            bot.send_message(message.chat.id, "<b>Số tiền phải là số nguyên</b>", parse_mode="HTML")
            return
        with open(path_luu_tien, "r") as file:
            nhung_so_tien = file.readlines()
            for so_tien in nhung_so_tien:
                if so_tien.startswith(id_muon_nap):
                    so_tien_nguoi_dung = int(so_tien[len(id_muon_nap):].strip())
                    so_tien_nguoi_dung_dinh_dang = f"{so_tien_nguoi_dung:,.0f}".replace(',', '.')
                    thong_tin_muon_nap = (
                        f"<pre>━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
                        f"Thực Hiện : Muốn Nạp\n"
                        f"ID : {id_muon_nap}\n"
                        f"Số tiền muốn nạp : {so_tien_muon_nap_dinh_dang} VNĐ\n"
                        f"Số dư tài khoản : {so_tien_nguoi_dung_dinh_dang} VNĐ\n"
                        f"Trạng thái : Đang chờ xử lý\n"
                        f"Thời gian : {thoi_gian_hien_tai()}\n"
                        f"━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━</pre>"
                    )     
                    bot.send_message(message.chat.id, thong_tin_muon_nap, parse_mode="HTML")
                    break  
                else:
                    bot.send_message(message.chat.id, f"<b>Không tìm thấy {id_muon_nap} trong file</b>", parse_mode="HTML")  
            else:
                bot.send_message(message.chat.id, f"<b>Không tìm thấy {User_id} trong file</b>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi {e}</b>", parse_mode="HTML")

# Hàm nạp tiền cho user [admin]
@bot.message_handler(commands=['load'])
def load(message):        
    try:
        User_id = str(message.chat.id)
        parts = message.text.split(maxsplit=2)
        if User_id != ID_ADMIN:
            bot.send_message(message.chat.id, "<b>Bạn không có quyền dùng lệnh này !</b>", parse_mode='HTML')
            return
        if len(parts) != 3:
            bot.send_message(message.chat.id, "<b>Nhập theo mẫu /load [User id] [Số tiền]</b>", parse_mode="HTML")
            return
        id_nap = parts[1]    
        so_tien_nap = int(parts[2])
        so_tien_nap_dinh_dang = f"{so_tien_nap:,.0f}".replace(',','.')
        if not isinstance(so_tien_nap, int):
            bot.send_message(message.chat.id, "<b>Số tiền phải là số nguyên</b>", parse_mode="HTML")
            return    
        with open(path_luu_tien, "r") as file:
            nhung_so_tien = file.readlines()
        cap_nhat = False
        for i, line in enumerate(nhung_so_tien):
            if line.startswith(id_nap):
                so_du_nguoi_dung = int(line[len(id_nap):])
                so_du_moi = so_du_nguoi_dung + so_tien_nap
                nhung_so_tien[i] = f"{id_nap}{so_du_moi}\n"
                so_du_nguoi_dung = so_du_moi
                so_du_nguoi_dung_dinh_dang = f"{so_du_nguoi_dung:,.0f}".replace(',','.')
                cap_nhat = True
                break
        if not cap_nhat:
            bot.send_message(message.chat.id, f"<b>Không tìm thấy {id_nap} trong file</b>", parse_mode="HTML")
        with open(path_luu_tien, "w") as file:
            file.writelines(nhung_so_tien)
        che_user_id_nguoi_nap = str(message.chat.id)[:-3] + "***"
        che_user_id_nguoi_nhan = id_nap[:-3] + "***"   
        chuoi_giao_dich = (str(so_tien_nap) + str(so_du_nguoi_dung) + str(ID_ADMIN) + str(id_nap) + str(thoi_gian_hien_tai()))
        chuoi_giao_dich_hash = hashlib.sha256(chuoi_giao_dich.encode()).hexdigest()
        ma_giao_dich_rut_gon = (''.join(filter(str.isdigit, chuoi_giao_dich_hash))[:15]) 
        thong_tin_nap_tien = (
            f"    <b>GIAO DỊCH THÀNH CÔNG</b>    \n\n"
            f"<b>━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━</b>\n"
            f"<pre>Thực Hiện : NẠP\n"
            f"Số tiền : {so_tien_nap_dinh_dang} VNĐ\n"
            f"Trạng thái : Thành công\n"
            f"Số dư mới : {so_du_nguoi_dung_dinh_dang} VNĐ\n"
            f"ID Người Gửi : Admin - {che_user_id_nguoi_nap}\n"
            f"ID Người Nhận : Bạn - {che_user_id_nguoi_nhan}\n" 
            f"Mã giao dịch : {ma_giao_dich_rut_gon}\n"
            f"Thời gian : {thoi_gian_hien_tai()}</pre>\n"
            f"<b>━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━</b>" 
        )
        thong_tin_nap_tien_ghi_file = thong_tin_nap_tien.replace("<b>", "").replace("</b>", "").replace("<pre>", "").replace("</pre>", "").replace("GIAO DỊCH THÀNH CÔNG","")
        with open(path_luu_bill_nap, "a", encoding = "utf-8") as file:
            file.write(thong_tin_nap_tien_ghi_file + "\n")
        bot.send_message(message.chat.id, thong_tin_nap_tien, parse_mode="HTML")
        bot.send_message(id_nap, thong_tin_nap_tien, parse_mode="HTML")
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi {e}</b>", parse_mode="HTML")  

# hàm chuyển tiền cho user         
@bot.message_handler(commands=['transfer'])
def transfer(message):
    try:
        User_id = str(message.chat.id)
        parts = message.text.split(maxsplit=3)
        if len(parts) != 4:
            bot.send_message(message.chat.id, "<b>Nhập theo mẫu /transfer [User id chuyển] [User id nhận] [Số tiền]</b>", parse_mode="HTML")
            return
        user_chuyen_tien = parts[1]
        user_nhan_tien = parts[2]
        so_tien_chuyen = int(parts[3])
        so_tien_chuyen_dinh_dang = f"{so_tien_chuyen:,.0f}".replace(',','.')
        if not isinstance(so_tien_chuyen, int):
            bot.send_message(message.chat.id, "<b>Số tiền chuyển phải là số nguyên</b>", parse_mode="HTML")
            return
        with open(path_luu_tien, "r") as file:
            id_nguoi_dung = file.readlines()
            id_chuyen_hop_le = False
            id_nhan_hop_le = False
            for line in id_nguoi_dung:
                if line.startswith(user_chuyen_tien):
                    id_chuyen_hop_le = True
                if line.startswith(user_nhan_tien):
                    id_nhan_hop_le = True
            if not id_chuyen_hop_le:
                bot.send_message(message.chat.id, "<b>ID người chuyển không hợp lệ</b>", parse_mode="HTML")
                return
            if not id_nhan_hop_le:
                bot.send_message(message.chat.id, "<b>ID người nhận không hợp lệ</b>", parse_mode="HTML")
                return
        with open(path_luu_tien, "r") as file:
            nhung_so_tien = file.readlines()
        cap_nhat_chuyen = False
        cap_nhat_nhan = False
        so_du_nguoi_chuyen = 0
        so_du_nguoi_nhan = 0
        for i, line in enumerate(nhung_so_tien):
            if line.startswith(user_chuyen_tien):
                so_du_nguoi_chuyen = int(line[len(user_chuyen_tien):])
                if so_tien_chuyen > so_du_nguoi_chuyen:
                    bot.send_message(message.chat.id, "<b>Số dư không đủ để chuyển</b>", parse_mode="HTML")
                    return
                so_du_moi_chuyen = so_du_nguoi_chuyen - so_tien_chuyen
                so_du_moi_chuyen_dinh_dang =  f"{so_du_moi_chuyen:,.0f}".replace(',','.')
                nhung_so_tien[i] = f"{user_chuyen_tien}{so_du_moi_chuyen}\n"
                cap_nhat_chuyen = True
            elif line.startswith(user_nhan_tien):
                so_du_nguoi_nhan = int(line[len(user_nhan_tien):])
                so_du_moi_nhan = so_du_nguoi_nhan + so_tien_chuyen
                so_du_moi_nhan_dinh_dang =  f"{so_du_moi_nhan:,.0f}".replace(',','.')
                nhung_so_tien[i] = f"{user_nhan_tien}{so_du_moi_nhan}\n"
                cap_nhat_nhan = True
        if not cap_nhat_chuyen:
            so_du_moi_chuyen = -so_tien_chuyen
            so_du_moi_chuyen_dinh_dang =  f"{so_du_moi_chuyen:,.0f}".replace(',','.')
            nhung_so_tien.append(f"{user_chuyen_tien}{so_du_moi_chuyen}\n")
        if not cap_nhat_nhan:
            so_du_moi_nhan = so_tien_chuyen
            so_du_moi_nhan_dinh_dang =  f"{so_du_moi_nhan:,.0f}".replace(',','.')
            nhung_so_tien.append(f"{user_nhan_tien}{so_du_moi_nhan}\n")
        with open(path_luu_tien, "w") as file:
            file.writelines(nhung_so_tien)  
        che_user_id_nguoi_chuyen = str(user_chuyen_tien)[:-3] + "***"
        che_user_id_nguoi_nhan = user_nhan_tien[:-3] + "***"   
        chuoi_giao_dich = (str(so_tien_chuyen) + str(so_du_moi_chuyen) + str(so_du_moi_nhan) + str(user_chuyen_tien) + str(user_nhan_tien) + str(thoi_gian_hien_tai()))
        chuoi_giao_dich_hash = hashlib.sha256(chuoi_giao_dich.encode()).hexdigest()
        ma_giao_dich_rut_gon = (''.join(filter(str.isdigit, chuoi_giao_dich_hash))[:15])      
        thong_tin_chuyen_tien = (
            f"    <b>GIAO DỊCH THÀNH CÔNG</b>    \n\n"
            f"<b>━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━</b>\n"
            f"<pre>Thực Hiện : CHUYỂN\n"
            f"Số tiền : {so_tien_chuyen_dinh_dang} VNĐ\n"
            f"Trạng thái : Thành công\n"
            f"Số dư mới : {so_du_moi_chuyen_dinh_dang} VNĐ\n"
            f"ID Người Gửi : {che_user_id_nguoi_chuyen}\n"
            f"ID Người Nhận : {che_user_id_nguoi_nhan}\n" 
            f"Mã giao dịch : {ma_giao_dich_rut_gon}\n"
            f"Thời gian : {thoi_gian_hien_tai()}</pre>\n"
            f"<b>━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━</b>" 
        )
        thong_tin_nhan_tien = (
            f"    <b>GIAO DỊCH THÀNH CÔNG</b>    \n\n"
            f"<b>━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━</b>\n"
            f"<pre>Thực Hiện : NHẬN\n"
            f"Số tiền : {so_tien_chuyen_dinh_dang} VNĐ\n"
            f"Trạng thái : Thành công\n"
            f"Số dư mới : {so_du_moi_nhan_dinh_dang} VNĐ\n"
            f"ID Người Gửi : {che_user_id_nguoi_chuyen}\n"
            f"ID Người Nhận : {che_user_id_nguoi_nhan}\n" 
            f"Mã giao dịch : {ma_giao_dich_rut_gon}\n"
            f"Thời gian : {thoi_gian_hien_tai()}</pre>\n"
            f"<b>━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━</b>" 
        )
        thong_tin_chuyen_tien_ghi_file = thong_tin_chuyen_tien.replace("<b>", "").replace("</b>", "").replace("<pre>", "").replace("</pre>", "").replace("GIAO DỊCH THÀNH CÔNG","")
        with open(path_luu_bill_chuyen, "a", encoding = "utf-8") as file:
            file.write(thong_tin_chuyen_tien_ghi_file + "\n")
        thong_tin_nhan_tien_ghi_file = thong_tin_nhan_tien.replace("<b>", "").replace("</b>", "").replace("<pre>", "").replace("</pre>", "").replace("GIAO DỊCH THÀNH CÔNG","")
        with open(path_luu_bill_nhan, "a", encoding = "utf-8") as file:
            file.write(thong_tin_nhan_tien_ghi_file + "\n")    
        bot.send_message(user_chuyen_tien, thong_tin_chuyen_tien, parse_mode="HTML")
        bot.send_message(user_nhan_tien, thong_tin_nhan_tien, parse_mode="HTML")        
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi {e}</b>", parse_mode="HTML")          

# lệnh khả thi
@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda message: message.text == "📋 Hướng dẫn")
def help(message):
    help_text = (
        "<b>Các lệnh khả dụng\n\n"
        "━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━\n"
        "➤ /start - Khởi động bot\n"
        "➤ /load - Nạp tiền vào tài khoản (admin)\n"
        "➤ /wload - Yêu cầu nạp tiền\n"
        "➤ /transfer - Chuyển tiền cho người dùng khác\n"
        "➤ /mgd - Xem bill có mã giao dịch\n"
        "➤ /account - Xem số dư tài khoản\n"
        "➤ /help - Hiển thị các lệnh hướng dẫn\n"
        "━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━</b>"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

# xem tài khoản và số dư
@bot.message_handler(commands=['account']) 
@bot.message_handler(func=lambda message: message.text == "👤 Tài khoản")
def account(message):
    User_id = str(message.chat.id)
    try:
        user_first_name = message.from_user.first_name
        user_last_name = message.from_user.last_name
        user_name = message.from_user.username
        full_name = f"{user_first_name} {user_last_name}"
        with open(path_luu_tien, "r") as file:
            nhung_so_tien = file.readlines()
            for so_tien in nhung_so_tien:
                if so_tien.startswith(User_id):
                    so_tien_nguoi_dung = int(so_tien[len(User_id):].strip())
                    so_tien_nguoi_dung_dinh_dang = f"{so_tien_nguoi_dung:,.0f}".replace(',','.')
                    break
        thong_tin_account = (
            f"👤 <b>Thông tin account:</b>\n"
            f"<b>├ ID:</b> {User_id}\n"
            f"<b>├ Tên người dùng:</b> {user_name}\n"
            f"<b>├ Tên đầy đủ:</b> {full_name}\n"
            f"<b>└ 💳 Số dư tài khoản:</b> {so_tien_nguoi_dung_dinh_dang} VNĐ\n"
        )
        bot.send_message(message.chat.id, thong_tin_account, parse_mode="HTML")
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi {e}</b>", parse_mode="HTML")

# hàm lấy tất cả bill chuyển và nhận của User id
@bot.message_handler(commands=['getbill'])
def get_bill(message):
    try:    
        User_id = str(message.chat.id)
        bills = []
        with open(path_luu_bill_chuyen, "r") as file_chuyen:
            bill_data = ""
            for line in file_chuyen:
                if "━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━" in line and bill_data:
                    if user_id in bill_data:
                        bills.append(bill_data) 
                    bill_data = ""  
                bill_data += line
            if user_id in bill_data:
                bills.append(bill_data)
        with open(path_luu_bill_nhan, "r") as file_nhan:
            bill_data = ""
            for line in file_nhan:
                if "━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━" in line and bill_data:
                    if user_id in bill_data:
                        bills.append(bill_data)
                    bill_data = ""
                bill_data += line
            if user_id in bill_data:
                bills.append(bill_data)
        if not bills:
            bot.send_message(message.chat.id, "<b>Không có giao dịch nào được tìm thấy cho tài khoản này</b>", parse_mode ="HTML")
            return
        temp_file_path = f"D:\\Python\\tong_hop_giao_dich_{User_id}.txt"
        with open(temp_file_path, "w", encoding = "utf-8") as temp_file:
            for bill in bills:
                temp_file.write(bill + "\n")
        with open(temp_file_path, "rb") as temp_file:
            bot.send_document(message.chat.id, temp_file)
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi {e}</b>", parse_mode="HTML")

# hàm lấy bill giao dịch theo mã giao dịch
@bot.message_handler(commands=['mgd'])
def mgd(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) != 2:
            bot.send_message(message.chat.id, "<b>Nhập theo mẫu /mgd [Mã giao dịch]</b>", parse_mode="HTML")
            return 
        ma_giao_dich = parts[1]
        found_bill = False
        paths = [path_luu_bill_nap, path_luu_bill_chuyen, path_luu_bill_nhan]
        for path in paths:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as file:
                    bills = file.read().split("━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━")
                    for bill in bills:
                        if ma_giao_dich in bill:
                            bot.send_message(message.chat.id, f"<pre>{bill}</pre>", parse_mode="HTML")
                            found_bill = True
                            break
            else:
                bot.send_message(message.chat.id, f"<b>Không tìm thấy file {path}</b>", parse_mode="HTML")
        if not found_bill:
            bot.send_message(message.chat.id, "<b>Không tìm thấy mã giao dịch</b>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi {e}</b>", parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
@bot.message_handler(content_types=['sticker','photo','video','document'])    
def answer_exception(message):
    menu_button = telebot.types.InlineKeyboardButton("Menu lệnh", callback_data="menu")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(menu_button)
    bot.send_message(message.chat.id, f"<b>❌ Sai lệnh . Vui lòng xem lại !</b>", parse_mode='HTML',reply_markup=keyboard)        

if __name__ == "__main__":
    print("\nBot đang hoạt động ...\n")
    bot.infinity_polling()  
