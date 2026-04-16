import streamlit as st

# 1. Настройка страницы и стилей
st.set_page_config(page_title="Smart Restaurant Calc", layout="centered")

st.markdown("""
    <style>
    /* Фон приложения */
    .stApp { background-color: #004d40; }
    
    /* Основной контейнер */
    .block-container { max-width: 850px !important; padding-top: 1.5rem !important; }

    /* Светло-зеленые ячейки (карточки) */
    div[data-testid="stMetric"], .stCheckbox, .stNumberInput, div.stSlider, .stMarkdown, .product-item {
        background-color: #e8f5e9 !important;
        padding: 8px 12px !important;
        border-radius: 10px;
        border: 1px solid #c8e6c9;
        margin-bottom: 6px;
    }

    /* Текст и цифры */
    h1, h2, h3, p, label, .stMetricValue, span, div { color: #000000 !important; }

    /* Центровка заголовков */
    .header-text { text-align: center; color: #ffffff !important; margin-bottom: 5px; }
    .info-badge { 
        text-align: center; background-color: #e8f5e9; padding: 5px; 
        border-radius: 8px; font-size: 0.8rem; margin-bottom: 25px;
    }

    /* Кнопка запуска */
    div.stButton > button {
        display: block; margin: 0 auto;
        background-color: #c8e6c9; color: black;
        border: 2px solid #2e7d32; font-size: 18px; padding: 10px 30px; border-radius: 12px;
    }

    /* Кастомные блоки итогов */
    .res-card { padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px; border: 1px solid #000; }
    .res-now { background-color: #f1f2f6; min-height: 120px; display: flex; flex-direction: column; justify-content: center; }
    .res-choco { background-color: #ffffff; border: 2px solid #81c784; }
    .res-benefit { background-color: #e8f5e9; border: 1px dashed #2e7d32; padding: 5px; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГИКА СТАРТОВОГО ЭКРАНА ---
if 'started' not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.write("# ") 
    st.markdown("<h1 class='header-text'>Smart Restaurant Calc.</h1>", unsafe_allow_html=True)
    if st.button("ОТКРЫТЬ КАЛЬКУЛЯТОР"):
        st.session_state.started = True
        st.rerun()
else:
    if st.button("⬅ Назад"):
        st.session_state.started = False
        st.rerun()

    st.markdown("<h2 class='header-text'>Smart Restaurant Calc</h2>", unsafe_allow_html=True)
    st.markdown("<div class='info-badge'>ℹ️ Расчет ведется на 40% проникновения продукта</div>", unsafe_allow_html=True)

    # --- 1. ПАРАМЕТРЫ (РЯД 1: 4 КОЛОНКИ, РЯД 2: 1 КОЛОНКА) ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: loc = st.number_input("Локаций", value=1)
    with c2: chd = st.number_input("Чеков/день", value=100)
    with c3: avg = st.number_input("Ср. чек (₸)", value=5000)
    with c4: marg = st.number_input("Маржа (%)", value=70) / 100
    
    c5_1, c5_2, c5_3, c5_4 = st.columns(4)
    with c5_1: aggr = st.number_input("Комиссия агр.(%)", value=30) / 100

    # --- 2. ПРОДУКТЫ (ДВЕ КОЛОНКИ) ---
    st.markdown("### Продукты:")
    p_left, p_right = st.columns(2)
    
    with p_left:
        p1 = st.checkbox("Без кассира (84к)")
        p3 = st.checkbox("SR Delivery (60к)")
        p5 = st.checkbox("Лояльность (60к)")
        p7 = st.checkbox("Автоподтягивание счета (60к)")

    with p_right:
        p2 = st.checkbox("Без официанта (120к)")
        p4 = st.checkbox("Приложение")
        if p4:
            p4_p = st.number_input("Цена прилож.", value=420000)
            p4_l = st.number_input("Локаций", value=5)
        else: p4_p, p4_l = 0, 0
        
        p6 = st.checkbox("AppClip (35к)")
        p8 = st.checkbox("Киоск (60к/ед)")
        if p8: p8_c = st.number_input("Кол-во киосков", value=1, min_value=1)
        else: p8_c = 0

    # --- РАСЧЕТЫ ---
    days, delivery_share, impact = 30, 0.3, 0.4
    total_checks = chd * days * loc
    base_revenue = total_checks * avg
    now_profit = (base_revenue * marg) - (base_revenue * delivery_share * aggr)

    cost = 0
    if p1: cost += 84000 * loc
    if p2: cost += 120000 * loc
    if p3: cost += 60000 * loc
    if p4: cost += p4_p
    if p5: cost += 60000
    if p6: cost += 35000 * loc
    if p7: cost += 60000 * loc
    if p8: cost += 60000 * p8_c

    has_boost = any([p1, p2, p3, p4, p8])
    has_speed, has_loyalty = p2, p5
    has_return = any([p1, p2, p3, p4, p5, p7, p8])

    n_avg = (avg * (1-impact)) + (avg * 1.16 * impact) if has_boost else avg
    n_ch = (total_checks * (1-impact)) + (total_checks * 1.25 * impact) if has_speed else total_checks
    ret_rev = (n_ch * 0.2 * n_avg) if has_return else 0
    loy_rev = (n_ch * 0.2 * n_avg * 0.3) if has_loyalty else 0
    
    choco_rev = (n_ch * n_avg) + ret_rev + loy_rev
    
    st.markdown("---")
    discount = st.number_input("Скидка на услуги (%)", 0, 100, 0)
    final_cost = cost * (1 - discount/100)
    
    choco_profit = (choco_rev * marg) - final_cost
    if not p3: choco_profit -= (choco_rev * delivery_share * aggr)

    # --- 3. ИТОГИ (ПО МАКЕТУ) ---
    res_left, res_right = st.columns([1.5, 1])
    
    with res_left:
        st.markdown(f"""
            <div class="res-card res-now">
                <p style="margin:0; font-size:0.9rem; font-weight:bold;">СЕЙЧАС</p>
                <h2 style="margin:0;">{int(now_profit):,} ₸</h2>
            </div>
        """, unsafe_allow_html=True)

    with res_right:
        st.markdown(f"""
            <div class="res-card res-choco">
                <p style="margin:0; font-size:0.8rem; font-weight:bold;">С CHOCO</p>
                <h3 style="margin:0; color:#2e7d32 !important;">{int(choco_profit):,} ₸</h3>
            </div>
        """, unsafe_allow_html=True)
        
        diff = choco_profit - now_profit
        st.markdown(f"""
            <div class="res-card res-benefit">
                <p style="margin:0; font-weight:bold;">ВЫГОДА: +{int(diff):,} ₸</p>
            </div>
        """, unsafe_allow_html=True)
