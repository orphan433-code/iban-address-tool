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
            # Настраиваем Faker под страну (локаль)
            # Например, для PL будет pl_PL
            try:
                fake = Faker(f"{code.lower()}_{code.upper()}")
            except:
                fake = Faker() # Если локали нет, используем стандартную

            # Генерируем данные
            city = fake.city()
            address = fake.street_address()

            # Выводим результат
            st.success(f"Country: **{country_name}**")
            
            # Блок с результатом для копирования
            full_address = f"{address}, {city}, {country_name}"
            st.code(full_address, language="text")
            st.caption("Copy the address above")
            
            # Доп инфо
            col1, col2 = st.columns(2)
            col1.metric("City", city)
            col2.metric("ISO Code", code)
        else:
            st.error("Could not recognize the country code.")
    else:
        st.warning("IBAN is too short.")