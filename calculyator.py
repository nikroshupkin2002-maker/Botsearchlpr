import streamlit as st

# Настройка страницы
st.set_page_config(page_title="Smart Restaurant Calc", layout="wide")

# Кастомный CSS для имитации вашего React-дизайна
st.markdown("""
    <style>
    /* Основной фон как в вашем React приложении */
    .stApp { background-color: #f8fafc; }
    
    /* Контейнеры блоков */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white;
        border-radius: 24px;
        padding: 10px;
    }

    /* Стилизация заголовков */
    h1 { color: #111827; font-weight: 800 !important; }
    h2 { color: #111827; font-size: 1.2rem !important; font-weight: 700 !important; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; }

    /* Инфо-плашка */
    .info-badge {
        background-color: #eff6ff;
        color: #1d4ed8;
        padding: 12px 20px;
        border-radius: 12px;
        border: 1px solid #dbeafe;
        font-weight: 600;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }

    /* Карточки результатов (Правая колонка) */
    .res-card-white {
        background-color: white;
        border-radius: 32px;
        padding: 30px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        border: 1px solid #f1f5f9;
        text-align: center;
    }
    
    .now-profit-val {
        background-color: #f8fafc;
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid #f1f5f9;
    }

    .smart-profit-card {
        background: linear-gradient(135deg, #1fcc59 0%, #0cb055 100%);
        color: white;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 10px 20px rgba(31, 204, 89, 0.2);
    }

    .benefit-card {
        background-color: rgba(31, 204, 89, 0.1);
        border: 2px solid rgba(31, 204, 89, 0.3);
        color: #0cb055;
        border-radius: 16px;
        padding: 20px;
        margin-top: 20px;
        font-weight: 900;
        font-size: 1.5rem;
    }
    
    /* Инпуты */
    .stNumberInput input {
        background-color: #f8fafc !important;
        border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def format_money(val):
    return f"{int(round(val)):,}".replace(",", " ")

# --- ИНИЦИАЛИЗАЦИЯ ИНТЕРФЕЙСА ---
col_main, col_sidebar = st.columns([0.65, 0.35], gap="large")

with col_main:
    st.markdown("<h1>Smart Restaurant Calc</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div class="info-badge">
            ℹ️ Расчет ведется на 40% проникновения продукта
        </div>
    """, unsafe_allow_html=True)

    # 1. Основные параметры
    st.markdown("## 1. Основные параметры")
    c1, c2, c3, c4 = st.columns(4)
    with c1: loc = st.number_input("Локаций", value=1, min_value=1)
    with c2: chd = st.number_input("Чеков/день", value=100, min_value=0)
    with c3: avg = st.number_input("Ср. чек (₸)", value=5000, min_value=0)
    with c4: marg_val = st.number_input("Маржа (%)", value=70, min_value=0, max_value=100)
    
    # 2. Дополнительные параметры
    st.markdown("## 2. Дополнительные параметры")
    c5, c6 = st.columns(2)
    with c5: aggr_val = st.number_input("Комиссия агрегатора (%)", value=30, min_value=0, max_value=100)
    with c6: disc_val = st.number_input("Скидка на услуги (%)", value=0, min_value=0, max_value=100)

    # 3. Продукты
    st.markdown("## 3. Продукты")
    p_col1, p_col2 = st.columns(2)
    
    with p_col1:
        p1 = st.checkbox("Без кассира (84 000 ₸ / лок)")
        p3 = st.checkbox("SR Delivery (60 000 ₸ / лок)")
        p5 = st.checkbox("Лояльность (60 000 ₸)")
        p7 = st.checkbox("Автоподтягивание счета (60 000 ₸ / лок)")

    with p_col2:
        p2 = st.checkbox("Без официанта (120 000 ₸ / лок)")
        p4 = st.checkbox("Приложение (Настраиваемая цена)")
        app_price, app_loc = 0, 0
        if p4:
            ci1, ci2 = st.columns(2)
            app_price = ci1.number_input("Цена прилож. (₸)", value=420000)
            app_loc = ci2.number_input("Локаций прилож.", value=5)
            
        p6 = st.checkbox("AppClip (35 000 ₸ / лок)")
        p8 = st.checkbox("Киоск (60 000 ₸ / ед)")
        kiosk_count = 1
        if p8:
            kiosk_count = st.number_input("Кол-во киосков", value=1, min_value=1)

# --- ЛОГИКА РАСЧЕТОВ ---
marg = marg_val / 100
aggr = aggr_val / 100
days = 30
delivery_share = 0.3
impact = 0.4

total_checks = chd * days * loc
base_revenue = total_checks * avg
now_profit = (base_revenue * marg) - (base_revenue * delivery_share * aggr)

cost = 0
if p1: cost += 84000 * loc
if p2: cost += 120000 * loc
if p3: cost += 60000 * loc
if p4: cost += app_price
if p5: cost += 60000
if p6: cost += 35000 * loc
if p7: cost += 60000 * loc
if p8: cost += 60000 * kiosk_count

has_boost = any([p1, p2, p3, p4, p8])
has_speed = p2
has_loyalty = p5
has_return = any([p1, p2, p3, p4, p5, p7, p8])

n_avg = (avg * (1 - impact)) + (avg * 1.16 * impact) if has_boost else avg
n_ch = (total_checks * (1 - impact)) + (total_checks * 1.25 * impact) if has_speed else total_checks
ret_rev = (n_ch * 0.2 * n_avg) if has_return else 0
loy_rev = (n_ch * 0.2 * n_avg * 0.3) if has_loyalty else 0

smart_rev = (n_ch * n_avg) + ret_rev + loy_rev
final_cost = cost * (1 - disc_val / 100)

smart_profit = (smart_rev * marg) - final_cost
if not p3:
    smart_profit -= (smart_rev * delivery_share * aggr)

diff = smart_profit - now_profit

# --- ВЫВОД РЕЗУЛЬТАТОВ (ПРАВАЯ ПАНЕЛЬ) ---
with col_sidebar:
    st.write("## ") # Отступ
    st.markdown(f"""
        <div class="res-card-white">
            <h3 style="margin-bottom: 25px;">Итоговый расчет за 30 дней</h3>
            
            <div class="now-profit-val">
                <span style="font-size: 0.75rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.1em;">Прибыль сейчас</span><br>
                <span style="font-size: 1.8rem; font-weight: 800; color: #1e293b;">{format_money(now_profit)} ₸</span>
            </div>
            
            <div style="color: #cbd5e1; margin: 10px 0;">▼</div>
            
            <div class="smart-profit-card">
                <span style="font-size: 0.75rem; font-weight: 700; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.1em;">С Smart Restaurant</span><br>
                <span style="font-size: 2.2rem; font-weight: 800;">{format_money(smart_profit)} ₸</span>
                {f'<div style="font-size: 0.7rem; margin-top: 10px; background: rgba(255,255,255,0.2); padding: 5px; border-radius: 20px;">Затраты: -{format_money(final_cost)} ₸</div>' if final_cost > 0 else ''}
            </div>
            
            <div class="benefit-card">
                <span style="font-size: 0.7rem; text-transform: uppercase; display: block; margin-bottom: 5px;">Выгода от внедрения</span>
                {"+" if diff > 0 else ""}{format_money(diff)} ₸
            </div>
        </div>
    """, unsafe_allow_html=True)
