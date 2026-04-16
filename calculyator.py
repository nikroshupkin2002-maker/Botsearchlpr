import streamlit as st

# 1. Настройка стиля (Темно-зеленый фон, светло-зеленые ячейки, черный текст)
st.set_page_config(page_title="Smart Restaurant Calc", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #004d40; }
    
    .block-container {
        max-width: 700px !important;
        padding-top: 2rem !important;
    }

    /* Светло-зеленые ячейки (карточки) */
    div[data-testid="stMetric"], .stCheckbox, .stNumberInput, div.stSlider, .stMarkdown, .product-item {
        background-color: #e8f5e9 !important;
        padding: 10px 15px !important;
        border-radius: 12px;
        border: 1px solid #c8e6c9;
        margin-bottom: 8px;
    }

    h1, h2, h3, p, label, .stMetricValue, span, div { color: #000000 !important; }
    .centered-title { text-align: center; color: #e8f5e9 !important; margin-bottom: 30px; }

    div.stButton > button {
        display: block; margin: 0 auto;
        background-color: #c8e6c9; color: black;
        border: 2px solid #2e7d32; font-size: 20px; padding: 10px 24px; border-radius: 10px;
    }
    
    .res-block-main {
        padding: 15px; border-radius: 15px;
        background-color: #81c784; color: black;
        text-align: center; border: 2px solid #000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- СОСТОЯНИЕ (КНОПКА ПРИ ВХОДЕ) ---
if 'started' not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.write("# ") 
    st.markdown("<h1 class='centered-title'>Добро пожаловать в<br>Smart Restaurant Calc.</h1>", unsafe_allow_html=True)
    if st.button("ОТКРЫТЬ КАЛЬКУЛЯТОР"):
        st.session_state.started = True
        st.rerun()
else:
    if st.button("⬅ Назад"):
        st.session_state.started = False
        st.rerun()

    st.markdown("<h2 style='text-align: center; color: white !important;'>📊 Smart Restaurant Calc</h2>", unsafe_allow_html=True)
    st.info("ℹ️ Расчет ведется на 40% проникновения продукта")

    # --- 1. ПАРАМЕТРЫ ЗАВЕДЕНИЯ ---
    st.subheader("1. Параметры заведения")
    c1, c2, c3 = st.columns(3)
    with c1: loc = st.number_input("Локаций", value=1, step=1)
    with c2: chd = st.number_input("Чеков в день", value=100)
    with c3: avg = st.number_input("Средний чек (₸)", value=5000)
    
    col_s1, col_s2 = st.columns(2)
    with col_s1: marg = st.number_input("Маржа (%)", value=70) / 100
    with col_s2: aggr = st.number_input("Комиссия агр. (%)", value=30) / 100

    # --- 2. ВЫБОР ПРОДУКТОВ ---
    st.markdown("---")
    st.subheader("2. Выбор продуктов и цен")
    
    p1 = st.checkbox("Без кассира (84к)")
    p2 = st.checkbox("Без официанта (120к)")
    p3 = st.checkbox("SR Delivery (60к)")
    
    # ПРИЛОЖЕНИЕ (p4)
    p4 = st.checkbox("Приложение")
    p4_price, p4_locs = 0, 0
    if p4:
        cp4_1, cp4_2 = st.columns(2)
        p4_price = cp4_1.number_input("Цена приложения (₸)", value=420000)
        p4_locs = cp4_2.number_input("Локаций приложения", value=5)

    p5 = st.checkbox("Лояльность (60к)")
    p6 = st.checkbox("AppClip (35к)")
    p7 = st.checkbox("Автоподтягивание счета (60к)")
    
    # КИОСК (p8)
    p8 = st.checkbox("Киоск (60к/ед)")
    p8_count = 0
    if p8:
        p8_count = st.number_input("Количество киосков", value=1, min_value=1)

    # --- ЛОГИКА РАСЧЕТОВ (ИЗ ВАШЕГО HTML) ---
    days = 30
    total_checks = chd * days * loc
    base_revenue = total_checks * avg
    delivery_share = 0.3
    
    # СЕЙЧАС
    now_profit = (base_revenue * marg) - (base_revenue * delivery_share * aggr)

    # С CHOCO
    cost = 0
    has_boost = False
    has_speed = False
    has_loyalty = False
    has_return = False

    if p1: cost += 84000 * loc; has_boost = True; has_return = True
    if p2: cost += 120000 * loc; has_boost = True; has_speed = True; has_return = True
    if p3: cost += 60000 * loc; has_boost = True; has_return = True
    if p4: cost += p4_price; has_boost = True; has_return = True
    if p5: cost += 60000; has_loyalty = True; has_return = True
    if p6: cost += 35000 * loc
    if p7: cost += 60000 * loc; has_return = True
    if p8: cost += 60000 * p8_count; has_boost = True; has_return = True

    impact_rate = 0.4
    # 1. Увеличение ср. чека (+16% на 40% заказов)
    new_avg = (avg * (1 - impact_rate)) + (avg * 1.16 * impact_rate) if has_boost else avg
    # 2. Увеличение кол-ва чеков (+25% на 40% столов)
    new_total_checks = (total_checks * (1 - impact_rate)) + (total_checks * 1.25 * impact_rate) if has_speed else total_checks
    # 3. Возврат гостей (20% дополнительно)
    extra_return_rev = (new_total_checks * 0.2) * new_avg if has_return else 0
    # 4. Буст лояльности (+30% к чеку вернувшихся)
    loyalty_rev = (new_total_checks * 0.2) * (new_avg * 0.3) if has_loyalty else 0

    choco_rev = (new_total_checks * new_avg) + extra_return_rev + loyalty_rev
    
    # --- 3. ИТОГИ ---
    st.markdown("---")
    st.subheader("3. Результаты")
    
    discount_perc = st.number_input("Скидка на услуги (%)", 0, 100, 0)
    final_cost = cost * (1 - discount_perc / 100)
    
    choco_profit = (choco_rev * marg) - final_cost
    if not p3:
        choco_profit -= (choco_rev * delivery_share * aggr)

    res_col_left, res_col_right = st.columns(2)

    with res_col_left:
        st.metric("Текущая прибыль", f"{int(now_profit):,} ₸".replace(",", " "))

    with res_col_right:
        st.markdown(f"""
            <div class="res-block-main">
                <p style="margin:0; font-size:0.9rem; font-weight:bold;">Прибыль с Нашим Продуктом</p>
                <h2 style="margin:0; color:black !important;">{int(choco_profit):,} ₸</h2>
            </div>
        """, unsafe_allow_html=True)
        
        diff = choco_profit - now_profit
        st.metric("Чистая выгода", f"{int(diff):,} ₸".replace(",", " "), delta=f"{int(diff):,} ₸")
