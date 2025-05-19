import requests, sys, telebot
from telebot import types 
from datetime import datetime
from deep_translator import GoogleTranslator

API_BOT = telebot.TeleBot("THAY_API_BOT")

def get_data_weather(*,nation: str, lang: str):
    api_key = "THAY_API_KEY_OPEN_WEATHER" # api_key openweather
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": nation,
        "appid": api_key,
        "units": "metric",
        "lang": lang  
    }
    try:
        response = requests.get(base_url, params=params)
        data = response.json()        
        if response.status_code != 200:
            return f"Không tìm thấy thông tin thời tiết cho '{nation}'"
        name = data['name']
        country = data['sys']['country']
        coord = data['coord']
        lat, lon = coord['lat'], coord['lon']
        weather_main = data['weather'][0]['main']
        weather_desc = data['weather'][0]['description']
        icon_code = data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        temp_min = data['main']['temp_min']
        temp_max = data['main']['temp_max']
        pressure = data['main']['pressure']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        wind_deg = data['wind'].get('deg', 'N/A')
        clouds = data['clouds']['all']
        sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S')
        sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S')
        map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        def translate_keyword(keyword):
            return GoogleTranslator(source='auto', target=lang).translate(keyword)
        name = GoogleTranslator(source='auto', target=lang).translate(name)
        country = GoogleTranslator(source='auto', target=lang).translate(country)
        weather_main = GoogleTranslator(source='auto', target=lang).translate(weather_main)
        weather_desc = GoogleTranslator(source='auto', target=lang).translate(weather_desc)
        location_label = translate_keyword("Location")
        coord_label = translate_keyword("Coordinates")
        weather_label = translate_keyword("Weather")
        weather_sky = translate_keyword("Sky")
        temp_label = translate_keyword("Temperature")
        feels_like_label = translate_keyword("Feels like")
        min_temp_label = translate_keyword("Min")
        max_temp_label = translate_keyword("Max")
        humidity_label = translate_keyword("Humidity")
        wind_label = translate_keyword("Wind")
        wind_deg_label = translate_keyword("Wind direction")
        pressure_label = translate_keyword("Pressure")
        clouds_label = translate_keyword("Cloudiness")
        sunrise_label = translate_keyword("Sunrise")
        sunset_label = translate_keyword("Sunset")
        map_label = translate_keyword("Map")
        icon_label = translate_keyword("Weather icon")
        result = (
            f"\n"
            f"┌ {location_label}: {name}, {country}\n"
            f"├ {weather_label}: {weather_main}\n"
            f"├ {weather_sky}: {weather_desc.capitalize()}\n"
            f"├ {temp_label}: {temp}°C\n"
            f"├ {feels_like_label}: {feels_like}°C\n"
            f"├ {min_temp_label}: {temp_min}°C\n"
            f"├ {max_temp_label}: {temp_max}°C\n"
            f"├ {humidity_label}: {humidity}%\n"
            f"├ {wind_label}: {wind_speed} m/s\n"
            f"├ {wind_deg_label}: {wind_deg}°\n"
            f"├ {pressure_label}: {pressure} hPa\n"
            f"├ {clouds_label}: {clouds}%\n"
            f"├ {sunrise_label}: {sunrise}\n"
            f"└ {sunset_label}: {sunset}\n"
        )
        return result
    except Exception as e:
        return e

@bot.message_handler(commands=['vitri'])
def input_weather():
    try:
        parts = message.text[1:].upper()
        if(len(parts) != 3):
            bot.send_message(message.chat.id, "Vui long nhap theo mau /vitri [Quốc gia (Vị trí)] [ngôn ngữ]")
        nation = parts[1]
        lang = parts[2]     
        print(get_data_weather(nation=nation, lang=lang))
    except Exception as e:
        bot.send_message(message.chat.id f"Lỗi {e}")

if __name__ == '__main__':
    bot.infinity_polling()

# print(get_data_weather(nation="Ho Chi Minh", lang="vi"))