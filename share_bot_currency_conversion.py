import time, telebot, requests
from telebot import types

bot = telebot.TeleBot("Thay API BOT")
API_KEY = 'API KEY Twelve'  

dang_theo_doi = {}
don_vi_dang_theo_doi = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.username
    if not user_name :
        full_name = message.from_user.first_name + " " + message.from_user.last_name
    else:    
        full_name = user_name
    bot.send_message(message.chat.id, f"Chào mừng {full_name} đến với bot thay đổi tiền tệ\nNhập lệnh /[don vi tien muon doi]\nVí dụ: /usd (đổi tiền đô sang việt)")

def api_ty_gia_tien_te(don_vi_tien_te):
    url = f"https://api.twelvedata.com/price?symbol={don_vi_tien_te}/VND&apikey={API_KEY}"
    response = requests.get(url).json()
    if 'price' in response:
        return float(response['price'])
    else:
        raise Exception(response.get('message', 'Không lấy được giá từ Twelve Data'))


# Đơn vị tiền tệ hợp lệ
don_vi_tien_te_hop_le = [
    "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN",
    "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BRL",
    "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHF", "CLP", "CNY",
    "COP", "CRC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP",
    "ERN", "ETB", "EUR", "FJD", "FKP", "FOK", "GBP", "GEL", "GGP", "GHS",
    "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF",
    "IDR", "ILS", "IMP", "INR", "IQD", "IRR", "ISK", "JEP", "JMD", "JOD",
    "JPY", "KES", "KGS", "KHR", "KID", "KMF", "KRW", "KWD", "KYD", "KZT",
    "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD",
    "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MYR", "MZN",
    "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK",
    "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR",
    "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD",
    "SSP", "STN", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY",
    "TTD", "TVD", "TWD", "TZS", "UAH", "UGX", "USD", "UYU", "UZS", "VES",
    "VND", "VUV", "WST", "XAF", "XCD", "XOF", "XPF", "YER", "ZAR", "ZMW", "ZWL"
]

@bot.message_handler(func=lambda message: message.text.startswith('/'))
def thay_doi_tien_te(message):
    user_id = message.from_user.id
    try:
        don_vi_tien_te = message.text[1:].upper()
        if don_vi_tien_te == "STOP":
            dang_theo_doi[user_id] = False
            don_vi = don_vi_dang_theo_doi.get(user_id)
            if don_vi:
                bot.send_message(message.chat.id, f"Đã dừng theo dõi {don_vi}")
            else:
                bot.send_message(message.chat.id, "Hiện không theo dõi đồng nào")
            return
        if don_vi_tien_te not in don_vi_tien_te_hop_le:
            nut_don_vi_tien_hop_le = types.InlineKeyboardButton("📜 Danh sách đơn vị hợp lệ", callback_data="dvhl")
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(nut_don_vi_tien_hop_le)
            bot.send_message(message.chat.id, "❌ Đơn vị tiền không hợp lệ", reply_markup=keyboard)
            return
        dang_theo_doi[user_id] = True
        don_vi_dang_theo_doi[user_id] = don_vi_tien_te
        gia_luc_dau = api_ty_gia_tien_te(don_vi_tien_te)
        tin_nhan_ban_dau = bot.send_message(message.chat.id, f"1 {don_vi_tien_te} = {gia_luc_dau} VNĐ")
        while dang_theo_doi.get(user_id):
            try:
                gia_hien_tai = api_ty_gia_tien_te(don_vi_tien_te)
                if gia_hien_tai != gia_luc_dau:  
                    bot.edit_message_text(
                        chat_id=tin_nhan_ban_dau.chat.id,
                        message_id=tin_nhan_ban_dau.message_id,
                        text=f"1 {don_vi_tien_te} = {gia_hien_tai} VND"
                    )
                    gia_luc_dau = gia_hien_tai
                time.sleep(8)      
            except Exception as e:
                bot.send_message(message.chat.id, f"Lỗi: {e}")
                break
    except Exception as e:
        bot.send_message(message.chat.id, f"Lỗi: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
