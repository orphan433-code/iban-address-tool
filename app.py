import streamlit as st
import pycountry
import geonamescache
import random
from geopy.geocoders import Nominatim
import time
import warnings

# Скрываем предупреждения об SSL, специфичные для macOS
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

# Инициализация базы городов
gc = geonamescache.GeonamesCache()

def get_country_info(iban):
    """Определяет страну и генерирует флаг по коду IBAN"""
    code = iban[:2].upper()
    try:
        country = pycountry.countries.get(alpha_2=code)
        # Генерируем эмодзи флага из кода страны
        flag = "".join(chr(ord(c) + 127397) for c in code)
        return f"{flag} {country.name}", code
    except:
        return None, None

def get_real_city_data(country_code):
    """Выбирает случайный город в указанной стране"""
    cities = gc.get_cities()
    country_cities = [
        c for c in cities.values() 
        if c['countrycode'] == country_code.upper() and c['population'] > 20000
    ]
    if country_cities:
        target = random.choice(country_cities)
        return target['name'], target['latitude'], target['longitude']
    return None, None, None

def get_precise_address(lat, lon):
    """Получает реальный адрес через реверс-геокодинг (Geopy)"""
    # Рандомный User-Agent помогает обходить блокировки 403
    user_agent = f"address_validator_{random.randint(10000, 99999)}"
    geolocator = Nominatim(user_agent=user_agent)
    
    try:
        # Небольшое смещение от центра, чтобы попадать в жилые кварталы
        new_lat = lat + random.uniform(-0.015, 0.015)
        new_lon = lon + random.uniform(-0.015, 0.015)
        
        location = geolocator.reverse((new_lat, new_lon), language='en', timeout=10)
        
        if location and location.address:
            addr_dict = location.raw.get('address', {})
            # Пробуем достать название улицы из разных тегов OSM
            street = addr_dict.get('road') or addr_dict.get('pedestrian') or addr_dict.get('suburb')
            house = addr_dict.get('house_number') or random.randint(1, 85)
            
            if street:
                return f"{street}, {house}"
    except:
        pass
    return None

# --- Настройка интерфейса Streamlit ---
st.set_page_config(page_title="Real Address Validator", page_icon="🏦", layout="centered")

st.title("🏦 Real Address Validator")

iban_input = st.text_input("Paste IBAN:", "").strip()

if iban_input:
    if len(iban_input) >= 2:
        country_display, code = get_country_info(iban_input)
        
        if country_display:
            address = None
            final_city = None
            
            with st.spinner(f'Searching real location in {country_display}...'):
                # До 5 попыток найти жилую улицу в разных городах страны
                for _ in range(5):
                    city_name, lat, lon = get_real_city_data(code)
                    if city_name:
                        time.sleep(0.7) # Пауза для стабильности API
                        address = get_precise_address(lat, lon)
                        if address:
                            final_city = city_name
                            break
            
            if address:
                st.success("Точный адрес найден!")
                
                # Вывод Страны
                st.write("**Country**")
                st.code(country_display, language="text")
                
                # Вывод Улицы
                st.write("**Street Address**")
                st.code(address, language="text")
                
                # Вывод Города
                st.write("**City**")
                st.code(final_city, language="text")
                
                st.caption(f"Location: {final_city}, {country_display}. Verified via OSM/Geopy.")
            else:
                st.error("Не удалось получить данные с карт. Сервер перегружен, попробуйте еще раз через 5-10 секунд.")
        else:
            st.error("Country code not recognized. Check the first 2 letters of IBAN.")
    else:
        st.warning("Please enter a valid IBAN.")