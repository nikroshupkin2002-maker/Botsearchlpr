import streamlit as st

# Настройка страницы
st.set_page_config(page_title="Choco Smart Calc", layout="wide")

# Стилизация под ваш дизайн
st.markdown("""
    <style>
    .main { background-color: #FFF0F6; }
    .stNumberInput, .stCheckbox { background: white; border-radius: 10px; }
    h1, h2, h3 { color: #FF4D94 !important; }
    .result-card {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        background: white;
        border: 2px solid #FF4D94;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Choco Smart Calc")
st.info("ℹ️ Расчет ведется на 40% проникновения продукта")

# Основные входные данные
with st.container():
    st.subheader("Основные параметры")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1: loc = st.number_input("Локаций", value=1, min_value=1)
    with col2: chd = st.number_input("Чеков/день", value=100)
    with col3: avg = st.number_input("Ср. чек (₸)", value=5000)
    with col4: marg = st.number_input("Маржа (%)", value=70) / 100
    with col5: aggr = st.number_input("Комиссия агр.(%)", value=30) / 100

# Выбор продуктов
st.subheader("Выберите продукты")
p_cols = st.columns(2)

products = {}
with p_cols[0]:
    products['p1'] = st.checkbox("Без кассира (84к)")
    products['p2'] = st.checkbox("Без официанта (120к)")
    products['p3'] = st.checkbox("SR Delivery (60к)")
    products['p4'] = st.checkbox("Приложение")
    if products['p4']:
        p4_price = st.number_input("Цена приложения", value=420000)
        p4_locs = st.number_input("Локаций для приложения", value=5)

with p_cols[1]:
    products['p5'] = st.checkbox("Лояльность (60к)")
    products['p6'] = st.checkbox("AppClip (35к)")
    products['p7'] = st.checkbox("Автосчет (60к)")
    products['p8'] = st.checkbox("Киоск (60к/ед)")
    if products['p8']:
        p8_count = st.number_input("Количество киосков", value=1)

# ЛОГИКА РАСЧЕТА
days = 30
total_checks = chd * days * loc
base_revenue = total_checks * avg

# --- СЕЙЧАС ---
delivery_share = 0.3
now_profit = (base_revenue * marg) - (base_revenue * delivery_share * aggr)

# --- С CHOCO ---
cost = 0
has_boost = any([products['p1'], products['p2'], products['p3'], products['p4'], products['p8']])
has_speed = products['p2']
has_loyalty = products['p5']
has_return = any([products['p1'], products['p2'], products['p3'], products['p4'], products['p5'], products['p7'], products['p8']])

if products['p1']: cost += 84000 * loc
if products['p2']: cost += 120000 * loc
if products['p3']: cost += 60000 * loc
if products['p4']: cost += p4_price
if products['p5']: cost += 60000
if products['p6']: cost += 35000 * loc
if products['p7']: cost += 60000 * loc
if products['p8']: cost += 60000 * p8_count

impact_rate = 0.4
new_avg = (avg * (1 - impact_rate)) + (avg * 1.16 * impact_rate) if has_boost else avg
new_total_checks = (total_checks * (1 - impact_rate)) + (total_checks * 1.25 * impact_rate) if has_speed else total_checks

extra_return_rev = (new_total_checks * 0.2) * new_avg if has_return else 0
loyalty_rev = (new_total_checks * 0.2) * (new_avg * 0.3) if has_loyalty else 0

choco_rev = (new_total_checks * new_avg) + extra_return_rev + loyalty_rev
choco_profit = (choco_rev * marg) - cost

if not products['p3']:
    choco_profit -= (choco_rev * delivery_share * aggr)

# ВЫВОД РЕЗУЛЬТАТОВ
st.markdown("---")
res_col1, res_col2 = st.columns(2)

with res_col1:
    st.metric("СЕЙЧАС (Прибыль)", f"{int(now_profit):,} ₸".replace(",", " "))

with res_col2:
    diff = choco_profit - now_profit
    st.metric("С CHOCO (Прибыль)", f"{int(choco_profit):,} ₸".replace(",", " "), delta=f"{int(diff):,} ₸")

if diff > 0:
    st.success(f"Выгода с Choco составляет {int(diff):,} ₸ в месяц")
