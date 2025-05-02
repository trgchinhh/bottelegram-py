# ! py
# Bot body
# Copyright by @Truongchinh304

import os, telebot
from telebot import types 
from fpdf import FPDF
from decimal import Decimal, ROUND_HALF_UP    
from PIL import Image, ImageDraw, ImageFont
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup    


API_KEY_BOT = "THAY_API_BOT"
bot = telebot.TeleBot(API_KEY_BOT)
file_path_inforbody = "/sdcard/download/codingpython/body.txt" # File txt lưu thông tin người dùng


@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.username
    if not user_name :
        full_name = message.from_user.first_name + " " + message.from_user.last_name
    else:    
        full_name = user_name
    keyboard = InlineKeyboardMarkup()
    button_dslenh = InlineKeyboardButton(text="📜 Danh sách lệnh", callback_data = "xem_danh_sach_lenh")
    keyboard.row(button_dslenh)
    bot.send_message(message.chat.id, f"<b>Chào mừng {full_name} đến với bot tính chỉ số cơ thể\n\nNhấn nút 👇 để xem danh sách lệnh</b>", parse_mode = "HTML", reply_markup=keyboard)    
    
    
@bot.message_handler(commands=['nhapthongtin'])
def nhap_thong_tin(message):
    thong_tin = message.text.split(maxsplit=5)
    User_id = message.from_user.id
    
    if len(thong_tin) < 6:
        bot.send_message(message.chat.id, "<b>Vui lòng nhập đúng mẫu: /nhapthongtin [cân nặng (kg)] [chiều cao (m)] [tuổi] [giới tính (m/w)] [chỉ số R]</b>", parse_mode = "HTML")
        return 
    try:
        can_nang = float(thong_tin[1])
        chieu_cao = float(thong_tin[2])
        tuoi = int(thong_tin[3])
        gioi_tinh = thong_tin[4]
        chi_so_R = int(thong_tin[5])
        
        # Kiểm tra thông tin nhập vào  
        if not (10 <= can_nang <= 150):
            bot.send_message(message.chat.id, "<b>Cân nặng nằm trong khoảng 10 - 150 kg</b>", parse_mode="HTML")
            return
        if not (0.4 <= chieu_cao <= 2.5):
            bot.send_message(message.chat.id, "<b>Chiều cao nằm trong khoảng 0.4 - 2.5 m</b>", parse_mode="HTML")
            return
        if not (10 <= tuoi <= 80):
            bot.send_message(message.chat.id, "<b>Tuổi nằm trong khoảng 10 - 80</b>", parse_mode="HTML")
            return
        if gioi_tinh not in ["m","w","M","W"]:
            bot.send_message(message.chat.id, "<b>Nhập [m hoặc M] nếu bạn là đàn ông\nNhập [w hoặc W] nếu bạn là phụ nữ</b>", parse_mode="HTML")
            return
        if chi_so_R not in [1, 2, 3, 4, 5]:
            bot.send_message(message.chat.id, "<b>Chỉ số vận động (R) thuộc khoảng [1, 2, 3, 4, 5]</b>", parse_mode="HTML")
            return
        
        lines = []
        if os.path.exists(file_path_inforbody):
            with open(file_path_inforbody, "r", encoding="utf-8") as file:
                lines = file.readlines()
        
        # Kiểm tra và xử lý ghi đè hoặc thêm mới thông tin
        found = False
        with open(file_path_inforbody, "w", encoding="utf-8") as file:
            for line in lines:
                if str(User_id) in line:
                    # Nếu user_id tồn tại, ghi đè thông tin mới lên
                    file.write(f"{User_id} - {can_nang} - {chieu_cao} - {tuoi} - {gioi_tinh} - {chi_so_R}\n")
                    found = True
                else:
                    file.write(line)
                    
        with open(file_path_inforbody, "w", encoding = "utf-8") as file:
            file.write(f"{User_id} - {can_nang} - {chieu_cao} - {tuoi} - {gioi_tinh} - {chi_so_R}\n")
       
        bot.send_message(message.chat.id, "<b>Thông tin của bạn đã được lưu thành công!</b>", parse_mode="HTML")
    except Exception as error:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi: {error}!</b>", parse_mode="HTML")    


@bot.message_handler(commands=['pdf'])
def generate_pdf(message):
    User_id = message.from_user.id
    user_name = message.from_user.username
    if not user_name:
        full_name = message.from_user.first_name + " " + message.from_user.last_name
    else:
        full_name = user_name
    
    try:
        if os.path.exists(file_path_inforbody):
            with open(file_path_inforbody, "r", encoding="utf-8") as file:
                found = False
                for line in file:
                    if str(User_id) in line:
                        found = True
                        _, can_nang, chieu_cao, tuoi, gioi_tinh, hoat_dong = line.split(" - ")
                        can_nang = float(can_nang)
                        chieu_cao = float(chieu_cao)
                        tuoi = int(tuoi)
                        gioi_tinh = gioi_tinh.strip()
                        chi_so_R = float(hoat_dong.strip())
                        break
                
                if not found:
                    bot.send_message(message.chat.id, "<b>Không tìm thấy thông tin của bạn. Vui lòng nhập thông tin với lệnh /nhapthongtin</b>", parse_mode="HTML")
                    return
        else:
            bot.send_message(message.chat.id, "<b>Không tìm thấy tệp lưu trữ thông tin</b>", parse_mode="HTML")
            return
        
        # Tính BMI, BMR, TDEE
        tinh_chi_so_bmi = Decimal(can_nang) / Decimal(chieu_cao * chieu_cao)
        tinh_chi_so_bmi = tinh_chi_so_bmi.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
        if gioi_tinh in ["m","M"]:
            tinh_chi_so_bmr = Decimal(655) + (Decimal(9.6) * Decimal(can_nang)) + (Decimal(1.8) * Decimal(chieu_cao)) - (Decimal(4.7) * Decimal(tuoi))
        else:
            tinh_chi_so_bmr = Decimal(66) + (Decimal(13.7) * Decimal(can_nang)) + (Decimal(5) * Decimal(chieu_cao)) - (Decimal(6.8) * Decimal(tuoi))
        tinh_chi_so_bmr = tinh_chi_so_bmr.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)    
        he_so_hoat_dong = {
            1: 1.2,
            2: 1.375,
            3: 1.55,
            4: 1.725,
            5: 1.9
        }
        bac_he_so_hoat_dong = {
            1: "Không vận động", 
            2: "Vận động nhẹ",
            3: "Vận động vừa",
            4: "Vận động nhiều",
            5: "Vận động rất nhiều"
        }    
        if chi_so_R in he_so_hoat_dong:
            tinh_chi_so_tdee = tinh_chi_so_bmr * Decimal(he_so_hoat_dong[chi_so_R])
            tinh_chi_so_tdee = tinh_chi_so_tdee.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
        else:
            bot.send_message(message.chat.id, "<b>Vui lòng nhập đúng chỉ số hoạt động</b>", parse_mode = "HTML")    
            return 
        
        # Khởi tạo file PDF, định dạng phông chữ unicode không bị lỗi
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('DejaVu', '', '/sdcard/download/dejavu-sans/DejaVuSans.ttf', uni=True) # Đường dẫn đến file DejaVuSans.ttf
        pdf.set_font('DejaVu', '', 14) # Font DejaVu cỡ chữ 12
        
        pdf.multi_cell(200, 15, txt=f"CHỈ SỐ CƠ THỂ CỦA {full_name.upper()}", align='C')
        pdf.multi_cell(200, 15, txt=f"➤ Cân nặng: {can_nang} kg")
        pdf.multi_cell(200, 15, txt=f"➤ Chiều cao: {chieu_cao} m")
        pdf.multi_cell(200, 15, txt=f"➤ Tuổi: {tuoi}")
        pdf.multi_cell(200, 15, txt=f"➤ Giới tính: {'Nam' if gioi_tinh == 'm' else 'Nữ'}")
        pdf.multi_cell(200, 15, txt=f"➤ Chỉ số hoạt động (R): {he_so_hoat_dong[chi_so_R]} - {bac_he_so_hoat_dong[chi_so_R]}")
        pdf.multi_cell(200, 15, txt=f"➤ Chỉ số BMI: {tinh_chi_so_bmi} kg/m²")
        pdf.multi_cell(200, 15, txt=f"➤ Chỉ số BMR (cần): {tinh_chi_so_bmr} calo/ngày")
        pdf.multi_cell(200, 15, txt=f"➤ Chỉ số TDEE (tiêu thụ): {tinh_chi_so_tdee} calo/ngày")
        
        # In ra lời khuyên sau cùng
        nhung_truong_hop = {
            1: f"➤ Cơ thể của {full_name.lower()} đang thiếu cân\n>> Lời khuyên: Hãy ăn và tập thể dục nhiều lên",
            2: f"➤ Cơ thể của {full_name.lower()} cân đối\n>> Lời khuyên: Giữ dáng vậy hoài nhá",
            3: f"➤ Cơ thể của {full_name.lower()} thừa cân\n>> Lời khuyên: Tập thể dục ngay thôi",
            4: f"➤ Cơ thể của {full_name.lower()} béo phì\n>> Lời khuyên: Ăn ít đồ mỡ lại đi",
            5: f"➤ Cơ thể của {full_name.lower()} béo phì nguy hiểm\n>> Lời khuyên: Đi khám ngay đi",
        }
        
        if tinh_chi_so_bmi < 18.5:
            pdf.multi_cell(200, 15, txt=nhung_truong_hop[1])
        elif 18.5 <= tinh_chi_so_bmi <= 24.9:
            pdf.multi_cell(200, 15, txt=nhung_truong_hop[2])
        elif 25 <= tinh_chi_so_bmi <= 29.9:
            pdf.multi_cell(200, 15, txt=nhung_truong_hop[3])
        elif 30 <= tinh_chi_so_bmi <= 34.9:
            pdf.multi_cell(200, 15, txt=nhung_truong_hop[4])
        else:
            pdf.multi_cell(200, 15, txt=nhung_truong_hop[5])
        
        # Xuất và gửi file     
        pdf_file_path = f"/sdcard/download/codingpython/Chi_so_co_the_{User_id}.pdf"
        pdf.output(pdf_file_path)
        with open(pdf_file_path, "rb") as file:
            bot.send_document(message.chat.id, file)
        bot.send_message(message.chat.id, "<b>Hoàn thành gửi file chỉ số cơ thể !</b>", parse_mode = "HTML")
        os.remove(pdf_file_path) # Xoá file sau khi gửi 
        
    except Exception as error:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi: {error}!</b>", parse_mode="HTML")
        
        
def xem_danh_sach_lenh(message):
    danh_sach_lenh = (
        "<b>/nhapthongtin: lệnh dùng nhập thông tin hoặc sửa thông tin trước khi tính chỉ số\n"
        "/pdf: lệnh dùng ghi chỉ số BMI, BMR, TDEE rồi gửi file cho người dùng\n"
        "Chỉ số R (chỉ số vận động)\n"
        "+ 1: Không vận động\n" 
        "+ 2: Vận động nhẹ\n"
        "+ 3: Vận động vừa\n"
        "+ 4: Vận động nhiều\n"
        "+ 5: Vận động rất nhiều"
        "Lưu ý: Khi nhập xem kỹ đơn vị để tránh sai sót khi tính kết quả !</b>"
    )   
    bot.send_message(message.chat.id, danh_sach_lenh, parse_mode = "HTML")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query_game(call):
    if call.data == "xem_danh_sach_lenh":
        xem_danh_sach_lenh(call.message)
        
        
@bot.message_handler(func=lambda message: True)
@bot.message_handler(content_types=['sticker','photo','video','document'])    
def tra_loi_ngoai_le(message):
    keyboard = InlineKeyboardMarkup()
    button_dslenh = InlineKeyboardButton(text="📜 Danh sách lệnh", callback_data = "xem_danh_sach_lenh")
    keyboard.row(button_dslenh)
    bot.send_message(message.chat.id, "<b>Sai cú pháp. Nhấn nút 👇 để xem danh sách lệnh</b>", parse_mode = "HTML", reply_markup=keyboard)
        
        
bot.infinity_polling()
             
    
    
