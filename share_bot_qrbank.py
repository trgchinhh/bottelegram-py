# ! py
# Bot qrbank
# Copyright by @Truongchinh304

# https://qr.sepay.vn/img?acc=SO_TAI_KHOAN&bank=NGAN_HANG&amount=SO_TIEN&des=NOI_DUNG&template=TEMPLATE&download=DOWNLOAD

import requests, telebot, os
from telebot import types

API_TOKEN_BOT = "THAY_API_BOT"
bot = telebot.TeleBot(API_TOKEN_BOT)
filename ="D:\\Python\\QR_LINK_CODE.png"

def qrlink(so_tai_khoan, ten_ngan_hang, so_tien, noi_dung, download):
    qrlink = f"https://qr.sepay.vn/img?acc={so_tai_khoan}&bank={ten_ngan_hang}&amount={so_tien}&des={noi_dung}&template=compact&download={download}"
    return qrlink

def download_qr_image(url, noi_dung,  message):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as file:
            file.write(response.content)
        with open(filename, "rb") as file:    
            bot.send_photo(message.chat.id, file, caption = noi_dung, parse_mode = "HTML")
        os.remove(filename)    
        print(f"QR code đã được tải xuống thành công: {filename}")
    else:
        print("Không thể tải QR code. Vui lòng kiểm tra lại URL")

# Các ngân hàng khả dụng 
bank_list = [
    "mbbank", "dongabank", "viettinbank", "vietcombank", "techcombank", 
    "bidv", "acb", "sacombank", "vpbank", "agribank",
    "hdbank", "tpbank", "shb", "eximbank", "ocb",
    "seabank", "bacabank", "pvcombank", "scb", "vib",
    "namabank", "abbank", "lpbank", "vietabank", "msb",
    "nvbank", "pgbank", "publicbank", "cimbbank", "uob"
]

@bot.message_handler(commands=["qrbank"])
def lay_thong_tin(message):
    User_id = str(message.chat.id)
    try:
        # donate admin nếu thấy hay =))))))))
        '''so_tai_khoan: "00230042006" 
        ten_ngan_hang: mbbank'''
        parts = message.text.split(maxsplit=4)
        if len(parts) != 5:
            bot.send_message(message.chat.id, "<b>Nhập theo định dạng /qrbank [STK] [Mã bank] [Số tiền]</b>", parse_mode = "HTML")
            return 
        so_tai_khoan = parts[1]
        if(len(so_tai_khoan) < 7 or len(so_tai_khoan) > 14):
            bot.send_message(message.chat.id, "<b>Vui lòng nhập số tài khoản hợp lệ</b>", parse_mode = "HTML")
            return
        ma_ngan_hang = parts[2].lower()
        if(ma_ngan_hang not in bank_list):
            bot.send_message(message.chat.id, "<b>Mã ngân hàng không hợp lệ</b>", parse_mode = "HTML")
            return
        so_tien = int(parts[3])
        if not (so_tien, int):
            bot.send_message(message.chat.id, "<b>Tiền phải là số nguyên, nếu không muốn để số tiền thì nhập 0</b>", parse_mode = "HTML")
            return
        noi_dung = " ".join(parts[4:]) if len(parts) > 4 else ""
        link = qrlink(so_tai_khoan, ma_ngan_hang, so_tien, noi_dung, "true")
        dinh_dang_so_tien = f"{so_tien:.0f}"
        noi_dung_thong_tin = (
            f"<b>➤ THÔNG TIN QRCODE !!!\n" 
            f"┏━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            f"┣➤ 🏦 Ngân Hàng: {ma_ngan_hang.upper()}\n"
            f"┣➤ 💳 Số TK: <code>{so_tai_khoan}</code>\n"
            f"┣➤ 💵 Số tiền: {dinh_dang_so_tien} VNĐ\n"
            f"┣➤ 📋 Nội dung: <code>{noi_dung}</code>\n"
            f"┗━━━━━━━━━━━━━━━━━━━━━━━┛</b>\n"
        )
        download_qr_image(link, noi_dung_thong_tin, message)
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>Đã xảy ra lỗi: {e}</b>", parse_mode = "HTML")    

def alway_run_qrbot():
    if (qrlink("00230042006", "mbbbank", "50000", "", "false")):
        print("Kết nối Sepay thành công !")
    else:
        print("Kết nối Sepay không thành công")
        return      
    bot.infinity_polling()  

if __name__ == "__main__":
    alway_run_qrbot()  
