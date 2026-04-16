import streamlit as st

# 1. Настройка стиля под фото
st.set_page_config(page_title="Choco Smart Calc", layout="wide")

st.markdown("""
    <style>
    /* Основной фон и шрифты */
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #FF4D94 !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Контейнеры для ввода */
    div[data-testid="stMetric"] {
        background-color: #FFF0F6;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #FFE0ED;
    }
    
    /* Кнопки и чекбоксы */
    .stCheckbox > label { font-weight: 600; color: #2D3436; }
    
    /* Плашка результата */
    .res-block {
        padding: 20px;
        border-radius: 20px;
        background-color: #FF4D94;
        color: white;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Choco Smart Calc")

# --- ЛЕВАЯ КОЛОНКА: ВВОДНЫЕ ДАННЫЕ ---
col_in, col_res = st.columns([2, 1])

with col_in:
    st.subheader("1. Параметры заведения")
    c1, c2, c3 = st.columns(3)
    with c1: loc = st.number_input("Локаций", value=1, step=1)
    with c2: chd = st.number_input("Чеков в день", value=100)
    with c3: avg = st.number_input("Средний чек (₸)", value=5000)
    
    c4, c5 = st.columns(2)
    with c4: marg = st.slider("Маржа (%)", 0, 100, 70) / 100
    with c5: aggr = st.slider("Комиссия агрегаторов (%)", 0, 100, 30) / 100

    st.subheader("2. Выбор продуктов и настройка цен")
    
    # Список продуктов с возможностью менять цену
    def prod_row(label, default_price, key):
        cols = st.columns([3, 2])
        is_active = cols[0].checkbox(label, key=f"check_{key}")
        price = cols[1].number_input(f"Цена {key} (₸)", value=default_price, key=f"price_{key}", label_visibility="collapsed")
        return is_active, price

    p1_act, p1_pr = prod_row("Без кассира", 84000, "p1")
    p2_act, p2_pr = prod_row("Без официанта", 120000, "p2")
    p3_act, p3_pr = prod_row("SR Delivery", 60000, "p3")
    p5_act, p5_pr = prod_row("Лояльность", 60000, "p5")
    p7_act, p7_pr = prod_row("Автосчет", 60000, "p7")
    
    # Особые продукты с доп. множителями
    st.markdown("---")
    p8_act = st.checkbox("Киоски Самообслуживания")
    if p8_act:
        c8_1, c8_2 = st.columns(2)
        p8_count = c8_1.number_input("Кол-во киосков", value=1, min_value=1)
        p8_single_pr = c8_2.number_input("Цена за 1 киоск (₸)", value=60000)
        p8_pr = p8_single_pr * p8_count
    else: p8_pr = 0

# --- ЛОГИКА РАСЧЕТОВ ---
days = 30
total_checks = chd * days * loc
base_revenue = total_checks * avg
delivery_share = 0.3

# Сейчас
now_profit = (base_revenue * marg) - (base_revenue * delivery_share * aggr)

# С Choco
cost = 0
if p1_act: cost += p1_pr * loc
if p2_act: cost += p2_pr * loc
if p3_act: cost += p3_pr * loc
if p5_act: cost += p5_pr
if p7_act: cost += p7_pr * loc
if p8_act: cost += p8_pr

has_boost = any([p1_act, p2_act, p3_act, p8_act])
has_speed = p2_act
has_return = any([p1_act, p2_act, p3_act, p5_act, p7_act, p8_act])

impact = 0.4
n_avg = (avg * (1-impact)) + (avg * 1.16 * impact) if has_boost else avg
n_ch = (total_checks * (1-impact)) + (total_checks * 1.25 * impact) if has_speed else total_checks
ret_rev = (n_ch * 0.2 * n_avg) if has_return else 0

choco_profit = ((n_ch * n_avg) + ret_rev) * marg - cost
if not p3_act:
    choco_profit -= (n_ch * n_avg * delivery_share * aggr)

# --- ПРАВАЯ КОЛОНКА: ИТОГИ ---
with col_res:
    st.subheader("3. Итоги")
    
    # Скидка
    discount = st.number_input("Скидка на услуги (%)", 0, 100, 0)
    if discount > 0:
        choco_profit += (cost * (discount / 100)) # Уменьшаем затраты = увеличиваем прибыль

    st.metric("Текущая прибыль", f"{int(now_profit):,} ₸".replace(",", " "))
    
    st.markdown(f"""
        <div class="res-block">
            <p style="margin:0; font-size:1rem;">Прибыль с Нашим Продуктом</p>
            <h1 style="margin:0; color:white !important;">{int(choco_profit):,} ₸</h1>
        </div>
    """, unsafe_allow_html=True)
    
    diff = choco_profit - now_profit
    st.metric("Чистая выгода", f"{int(diff):,} ₸".replace(",", " "), delta=f"{int(diff):,} ₸")
