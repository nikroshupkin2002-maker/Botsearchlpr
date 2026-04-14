import streamlit as st
from duckduckgo_search import DDGS
import pandas as pd

st.set_page_config(page_title="Choco HoReCa Finder", layout="wide")

st.title("🚀 HoReCa Search KZ (No API Edition)")
st.write("Поиск заведений через поисковые системы DuckDuckGo")

# Боковая панель
with st.sidebar:
    city = st.text_input("Город", "Алматы")
    category = st.selectbox("Категория", ["Ресторан", "Кафе", "Фастфуд", "Кофейня", "Бар"])
    search_query = f"{category} {city} Казахстан"
    btn = st.button("Начать поиск")

if btn:
    with st.spinner('Парсим интернет...'):
        results = []
        # Используем DuckDuckGo для поиска сайтов и заведений
        with DDGS() as ddgs:
            # Ищем первые 20 результатов
            search_results = ddgs.text(search_query, region='kz-ru', safesearch='off', timelimit='m')
            
            for r in search_results:
                results.append({
                    "Название": r['title'],
                    "Описание/Адрес": r['body'],
                    "Ссылка": r['href'],
                    "Менеджер": "",
                    "Статус": "Новый"
                })
        
        if results:
            df = pd.DataFrame(results)
            # Интерактивная таблица, где можно менять данные прямо в браузере
            edited_df = st.data_editor(
                df, 
                column_config={
                    "Ссылка": st.column_config.LinkColumn("Сайт/Источник"),
                    "Статус": st.column_config.SelectboxColumn(
                        "Статус",
                        options=["Новый", "В работе", "Отказ", "Договор"]
                    ),
                },
                hide_index=True,
                num_rows="dynamic"
            )
            
            # Кнопка скачивания в Excel
            st.download_button(
                "Скачать базу в Excel",
                df.to_csv(index=False).encode('utf-8-sig'),
                "horeca_base.csv",
                "text/csv"
            )
        else:
            st.error("Ничего не найдено. Попробуйте изменить запрос.")

st.info("💡 Лайфхак: Данные в таблице выше можно редактировать. После завершения работы нажмите кнопку 'Скачать', чтобы сохранить результат.")