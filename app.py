import streamlit as st
from faker import Faker
import pycountry

# Функция для поиска страны по коду
def get_country_info(iban):
    code = iban[:2].upper()
    try:
        country = pycountry.countries.get(alpha_2=code)
        return country.name, code
    except:
        return None, None

st.set_page_config(page_title="IBAN Helper", page_icon="🏦")

st.title("🏦 IBAN Address Generator")
st.write("Enter an IBAN to get a country-specific address.")

# Поле ввода
iban_input = st.text_input("Paste IBAN:", "").strip()

if iban_input:
    if len(iban_input) >= 2:
        country_name, code = get_country_info(iban_input)
        
        if country_name:
            # Настраиваем Faker под страну
            try:
                fake = Faker(f"{code.lower()}_{code.upper()}")
            except:
                fake = Faker()

            # Генерируем данные
            city = fake.city()
            raw_address = fake.street_address()

            # Логика очистки адреса: оставляем только улицу и номер дома
            # Большинство локалей Faker возвращают "Street Name 123, Flat 1" или "Street, 123..."
            # Берем часть до второй запятой (если она есть)
            address_parts = raw_address.split(',')
            if len(address_parts) > 1:
                # Оставляем только "Улица, Номер"
                clean_address = f"{address_parts[0].strip()}, {address_parts[1].strip()}"
            else:
                clean_address = raw_address

            st.success(f"Country: **{country_name}**")
            
            # Поле для копирования АДРЕСА
            st.write("**Address**")
            st.code(clean_address, language="text")
            
            # Поле для копирования ГОРОДА (сделал таким же блоком)
            st.write("**City**")
            st.code(city, language="text")
            
            st.caption("Click to copy any field above")

        else:
            st.error("Could not recognize the country code.")
    else:
        st.warning("IBAN is too short.")