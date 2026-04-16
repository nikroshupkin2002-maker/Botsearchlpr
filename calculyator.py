import streamlit as st

# 1. Настройка стиля под твой HTML-файл
st.set_page_config(page_title="Smart Restaurant Calc", layout="centered")

st.markdown("""
    <style>
    /* Темно-зеленый фон страницы */
    .stApp { background-color: #004d40; }
    
    /* Контейнер для центровки контента */
    .block-container { max-width: 800px !important; padding-top: 1rem !important; }

    /* Карточки (как в твоем HTML) */
    .custom-card {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }

    /* Светло-зеленые элементы внутри */
    div[data-testid="stMetric"], .stCheckbox, .stNumberInput, div.stSlider, .stMarkdown {
        background-color: #e8f5e9 !important;
        border-radius: 12px;
        border: 1px solid #c8e6c9;
    }

    /* Черный текст для всего */
    h1, h2, h3, p, label, .stMetricValue, span, div { color: #000000 !important; }

    /* Центровка начального заголовка */
    .start-title { text-align: center; color: #ffffff !important; margin-bottom: 40px; font-size: 2.5rem; }

    /* Кнопка запуска */
    div.stButton > button {
        display: block; margin: 0 auto;
        background-color: #c8e6c9; color: black;
        border: 2px solid #2e7d32; font-size: 20px; padding: 10px 30px; border-radius: 12px;
    }

    /* Итоговые блоки */
    .comp-block {
        padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 10px;
    }
    .now-block { background-color: #f1f2f6; border: 1px solid #ddd; }
    .choco-block { background-color: #ffffff; border: 2px solid #81c784; }
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГИКА ЭКРАНОВ ---
if 'started' not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.write("# ") 
    st.markdown("<h1 class='start-title'>Добро пожаловать в<br>Smart Restaurant Calc.</h1>", unsafe_allow_html=True)
    if st.button("ОТКРЫТЬ КАЛЬКУЛЯТОР"):
        st.session_state.started = True
        st.rerun()
else:
    if st.button("⬅ Назад"):
        st.session_state.started = False
        st.rerun()

    # --- ОСНОВНАЯ КАРТОЧКА (ВЕРХ И ЦЕНТР) ---
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("Smart Restaurant Calc")
    st.caption("ℹ️ Расчет ведется на 40% проникновения продукта")

    # 1. Параметры (Сетка как в HTML)
    col1, col2, col3 = st.columns(3)
    with col1: loc = st.number_input("Локаций", value=1, step=1)
    with col2: chd = st.number_input("Чеков/день", value=100)
    with col3: avg = st.number_input("Ср. чек (₸)", value=5000)
    
    col4, col5 = st.columns(2)
    with col4: marg = st.number_input("Маржа (%)", value=70) / 100
    with col5: aggr = st.number_input("Комиссия агр.(%)", value=30) / 100

    st.markdown("---")
    st.subheader("Продукты:")
    
    # 2. Продукты плиткой (2 колонки)
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        p1 = st.checkbox("Без кассира (84к)")
        p2 = st.checkbox("Без официанта (120к)")
        p3 = st.checkbox("SR Delivery (60к)")
        p4 = st.checkbox("Приложение")
        if p4:
            p4_p = st.number_input("Цена прилож.", value=420000)
            p4_l = st.number_input("Локаций прилож.", value=5)
        else: p4_p, p4_l = 0, 0

    with p_col2:
        p5 = st.checkbox("Лояльность (60к)")
        p6 = st.checkbox("AppClip (35к)")
        p7 = st.checkbox("Автоподтягивание счета (60к)")
        p8 = st.checkbox("Киоск (60к/ед)")
        if p8: p8_c = st.number_input("Кол-во киосков", value=1, min_value=1)
        else: p8_c = 0

    st.markdown('</div>', unsafe_allow_html=True)

    # --- ЛОГИКА РАСЧЕТОВ ---
    days = 30
    total_checks = chd * days * loc
    base_revenue = total_checks * avg
    delivery_share = 0.3
    now_profit = (base_revenue * marg) - (base_revenue * delivery_share * aggr)

    cost = 0
    has_boost = any([p1, p2, p3, p4, p8])
    has_speed = p2
    has_loyalty = p5
    has_return = any([p1, p2, p3, p4, p5, p7, p8])

    if p1: cost += 84000 * loc
    if p2: cost += 120000 * loc
    if p3: cost += 60000 * loc
    if p4: cost += p4_p
    if p5: cost += 60000
    if p6: cost += 35000 * loc
    if p7: cost += 60000 * loc
    if p8: cost += 60000 * p8_c

    impact = 0.4
    n_avg = (avg * (1 - impact)) + (avg * 1.16 * impact) if has_boost else avg
    n_ch = (total_checks * (1 - impact)) + (total_checks * 1.25 * impact) if has_speed else total_checks
    ret_rev = (n_ch * 0.2 * n_avg) if has_return else 0
    loy_rev = (n_ch * 0.2 * n_avg * 0.3) if has_loyalty else 0

    choco_rev = (n_ch * n_avg) + ret_rev + loy_rev
    
    # Скидка
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    discount = st.number_input("Скидка на услуги (%)", 0, 100, 0)
    final_cost = cost * (1 - discount / 100)
    
    choco_profit = (choco_rev * marg) - final_cost
    if not p3: choco_profit -= (choco_rev * delivery_share * aggr)

    # --- 3. ИТОГИ (ДВЕ КАРТОЧКИ В РЯД) ---
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.markdown(f"""
            <div class="comp-block now-block">
                <p style="margin:0; font-size:0.8rem; font-weight:bold;">СЕЙЧАС</p>
                <h2 style="margin:0;">{int(now_profit):,} ₸</h2>
            </div>
        """, unsafe_allow_html=True)

    with res_col2:
        st.markdown(f"""
            <div class="comp-block choco-block">
                <p style="margin:0; font-size:0.8rem; font-weight:bold;">ПРИБЫЛЬ С НАШИМ ПРОДУКТОМ</p>
                <h2 style="margin:0; color:#2e7d32 !important;">{int(choco_profit):,} ₸</h2>
            </div>
        """, unsafe_allow_html=True)
        
        diff = choco_profit - now_profit
        st.metric("Чистая выгода", f"{int(diff):,} ₸".replace(",", " "), delta=f"{int(diff):,} ₸")
    st.markdown('</div>', unsafe_allow_html=True)
