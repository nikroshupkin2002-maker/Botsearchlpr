import streamlit as st

# 1. Настройка стиля (Темно-зеленый фон, светло-зеленые ячейки, черный текст)
st.set_page_config(page_title="Choco Smart Calc", layout="wide")

st.markdown("""
    <style>
    /* Темно-зеленый фон всего приложения */
    .stApp {
        background-color: #004d40; 
    }
    
    /* Светло-зеленые ячейки (карточки) */
    div[data-testid="stMetric"], .stCheckbox, .stNumberInput, div.stSlider, .stMarkdown, .product-container {
        background-color: #e8f5e9 !important;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #c8e6c9;
    }

    /* Весь текст и цифры — черные */
    h1, h2, h3, p, label, .stMetricValue, span, div {
        color: #000000 !important;
    }

    /* Кнопка запуска */
    .stButton>button {
        background-color: #c8e6c9;
        color: black;
        border: 2px solid #2e7d32;
        font-size: 20px;
        padding: 10px 24px;
        border-radius: 10px;
    }
    
    /* Блок итоговой прибыли */
    .res-block {
        padding: 25px;
        border-radius: 20px;
        background-color: #81c784; /* Ярко-зеленый акцент для итога */
        color: black;
        text-align: center;
        border: 2px solid #000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГИКА КНОПКИ ПРИ ВХОДЕ ---
if 'started' not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    # Экран с кнопкой
    st.write("# ") # Отступ
    col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 2, 1])
    with col_btn_2:
        st.title("Добро пожаловать в Choco Smart Calc")
        if st.button("ОТКРЫТЬ КАЛЬКУЛЯТОР"):
            st.session_state.started = True
            st.rerun()
else:
    # --- САМ КАЛЬКУЛЯТОР (показывается после нажатия) ---
    if st.button("⬅ Назад"):
        st.session_state.started = False
        st.rerun()

    st.title("📊 Choco Smart Calc")
    st.info("ℹ️ Расчет ведется на 40% проникновения продукта")

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

    now_profit = (base_revenue * marg) - (base_revenue * delivery_share * aggr)

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

    with col_res:
        st.subheader("3. Итоги")
        
        discount = st.number_input("Скидка на услуги (%)", 0, 100, 0)
        if discount > 0:
            choco_profit += (cost * (discount / 100))

        st.metric("Текущая прибыль", f"{int(now_profit):,} ₸".replace(",", " "))
        
        st.markdown(f"""
            <div class="res-block">
                <p style="margin:0; font-size:1.1rem; font-weight:bold;">Прибыль с Нашим Продуктом</p>
                <h1 style="margin:0; color:black !important;">{int(choco_profit):,} ₸</h1>
            </div>
        """, unsafe_allow_html=True)
        
        diff = choco_profit - now_profit
        st.metric("Чистая выгода", f"{int(diff):,} ₸".replace(",", " "), delta=f"{int(diff):,} ₸")
