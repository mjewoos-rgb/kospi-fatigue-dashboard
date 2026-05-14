import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pykrx import stock
from datetime import datetime, timedelta

# --- 페이지 설정 및 스타일 ---
st.set_page_config(page_title="KOSPI Fatigue Dashboard", layout="wide")

# UI 디자인 고도화 (Tailwind 스타일 색상 반영)
st.markdown("""
    <style>
    @import url('https://rsms.me/inter/inter.css');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0f172a; }
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    div[data-testid="stMetricValue"] { color: #38bdf8; font-weight: 800; }
    .status-card {
        padding: 16px;
        border-radius: 10px;
        margin: 20px 0;
        border: 1px solid opacity 0.2;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    /* 테이블 다크모드 강제 적용 */
    .stDataFrame { border: 1px solid #334155; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 실시간 데이터 로드 함수 ---
@st.cache_data(ttl=3600) # 1시간마다 캐시 갱신
def get_real_data():
    now = datetime.now()
    # 주말 고려하여 넉넉하게 최근 20일치 조회
    start_date = (now - timedelta(days=20)).strftime("%Y%m%d")
    end_date = now.strftime("%Y%m%d")
    
    # pykrx 데이터 fetch (코스피 투자자별 순매수 합계)
    df = stock.get_market_net_purchases_of_equities(start_date, end_date, "KOSPI")
    
    # 단위 조정 (원 -> 억원) 및 컬럼 정리
    df = df[['개인', '외국인', '기관합계']].tail(7)
    df.columns = ['individual', 'foreign', 'institution']
    df = df / 100000000 
    df.index = df.index.strftime('%m-%d')
    return df.reset_index().rename(columns={'index': 'date'})

# --- 피로지수 계산 로직 ---
def calc_fatigue(individual, foreign):
    score = 100
    # 개인 방어력 미약 시 감점 (1500억 기준)
    indiv_penalty = min(40, (1500 - individual) / 30) if individual < 1500 else 0
    # 외국인 매도 압력 시 감점 (-1500억 기준)
    for_penalty = min(40, (-1500 - foreign) / 40) if foreign < -1500 else 0
    return int(max(0, min(100, score - indiv_penalty - for_penalty)))

try:
    df = get_real_data()
    df['fatigue'] = df.apply(lambda x: calc_fatigue(x['individual'], x['foreign']), axis=1)
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # --- 상단 헤더 ---
    st.title("📉 KOSPI 개인 방어 피로지수")
    st.markdown(f"<p style='color: #94a3b8;'>실시간 pykrx 데이터 연동됨 (기준일: {latest['date']})</p>", unsafe_allow_html=True)

    # --- KPI 지표 ---
    c1, c2, c3 = st.columns(3)
    c1.metric("피로지수", f"{latest['fatigue']}점", f"{latest['fatigue'] - prev['fatigue']}점")
    c2.metric("개인 순매수", f"{latest['individual']:,.0f}억", f"{latest['individual'] - prev['individual']:,.0f}억")
    c3.metric("외국인 순매수", f"{latest['foreign']:,.0f}억", f"{latest['foreign'] - prev['foreign']:,.0f}억")

    # --- 상태 배너 (52093.jpg 디자인 개선) ---
    score = latest['fatigue']
    if score < 60:
        st.error(f"🚨 **위험 단계 ({score}점)** — 개인 방어 한계치 도달. 보수적 접근 필요.")
    elif score < 78:
        st.warning(f"⚠️ **주의 단계 ({score}점)** — 외국인 매도세 증가 및 방어력 약화.")
    else:
        st.success(f"✅ **안전 단계 ({score}점)** — 현재 수급 방어 체력 충분.")

    # --- 차트 영역 ---
    tab1, tab2 = st.tabs(["피로지수 추이", "투자자 수급 상황"])
    
    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['fatigue'], mode='lines+markers', 
                                 line=dict(color='#38bdf8', width=4), fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.1)'))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(name='개인', x=df['date'], y=df['individual'], marker_color='#38bdf8'))
        fig_bar.add_trace(go.Bar(name='외국인', x=df['date'], y=df['foreign'], marker_color='#f87171'))
        fig_bar.update_layout(template="plotly_dark", barmode='group', paper_bgcolor='rgba(0,0,0,0)', height=300)
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- 데이터 테이블 (52095.jpg 개선) ---
    st.subheader("📋 최근 수급 상세 (단위: 억원)")
    formatted_df = df.copy()
    for col in ['individual', 'foreign', 'institution']:
        formatted_df[col] = formatted_df[col].map('{:,.0f}억'.format)
    st.table(formatted_df.iloc[::-1]) # 최신순 정렬

except Exception as e:
    st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
