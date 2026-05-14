import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 페이지 설정 ---
st.set_page_config(page_title="KOSPI 피로지수 대시보드", layout="wide")

# --- 커스텀 CSS (리액트의 다크 테마 감성 재현) ---
st.markdown("""
    <style>
    .main { background-color: #080f1a; color: #e2e8f0; }
    .stMetric { background-color: #0d1929; border: 1px solid #1e293b; padding: 15px; border-radius: 10px; }
    div[data-testid="stMetricValue"] { color: #38bdf8; font-family: 'IBM Plex Mono'; }
    .status-banner { padding: 12px; border-radius: 8px; margin-bottom: 20px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 준비 (Mock Data) ---
data = [
    {"date": "05-06", "individual": 18200, "foreign": -12300, "institution": -5900},
    {"date": "05-07", "individual": 22100, "foreign": -19800, "institution": -2300},
    {"date": "05-08", "individual": 11500, "foreign": -23100, "institution": 11600},
    {"date": "05-09", "individual": 28700, "foreign": -8400,  "institution": -20300},
    {"date": "05-12", "individual": 9800,  "foreign": -31200, "institution": 21400},
    {"date": "05-13", "individual": 16400, "foreign": -17600, "institution": 1200},
    {"date": "05-14", "individual": 13200, "foreign": -22800, "institution": 9600},
]
df = pd.DataFrame(data)

# --- 피로지수 계산 로직 ---
def calc_fatigue(individual, foreign):
    score = 100
    indiv_penalty = min(40, (15000 - individual) / 300) if individual < 15000 else 0
    foreign_penalty = min(40, (-15000 - foreign) / 400) if foreign < -15000 else 0
    both_weak_bonus = 5 if individual > 25000 else 0
    score = score - indiv_penalty - foreign_penalty + both_weak_bonus
    return int(max(0, min(100, score)))

df['fatigue'] = df.apply(lambda x: calc_fatigue(x['individual'], x['foreign']), axis=1)

# --- 상태 추출 ---
latest = df.iloc[-1]
prev = df.iloc[-2]
delta_fatigue = int(latest['fatigue'] - prev['fatigue'])

def get_status(score):
    if score < 60: return "위험", "#ef4444", "2a0d0d"
    if score < 78: return "주의", "#f59e0b", "2a1f0d"
    return "안전", "#10b981", "0d2a1a"

status_label, status_color, status_bg = get_status(latest['fatigue'])

# --- Header ---
st.title("📊 개인 방어 피로지수")
st.caption(f"KOSPI 투자자 동향 분석 (최근 거래일: {latest['date']}) · 단위: 억원")

# --- KPI Metrics ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("피로지수", f"{latest['fatigue']}점", delta=f"{delta_fatigue}점")
with col2:
    st.metric("개인 순매수", f"{latest['individual']//100}억", 
              delta="방어 충분" if latest['individual'] >= 15000 else "방어 미약")
with col3:
    st.metric("외국인 순매수", f"{latest['foreign']//100}억", 
              delta="매도 압력" if latest['foreign'] < -15000 else "정상", delta_color="inverse")

# --- Status Banner ---
st.markdown(f"""
    <div class="status-banner" style="background-color: #{status_bg}; border: 1px solid {status_color}; color: {status_color};">
        ● {status_label} 단계 ({latest['fatigue']}점) — 
        {"곱버스 포지션 재검토 신호" if status_label == "위험" else "신용잔고 모니터링 필요" if status_label == "주의" else "현재 방어 수요 유지 중"}
    </div>
    """, unsafe_allow_html=True)

# --- Charts ---
tab1, tab2 = st.tabs(["📈 피로지수 추이", "📉 투자자 수급"])

with tab1:
    fig_fatigue = go.Figure()
    fig_fatigue.add_trace(go.Scatter(
        x=df['date'], y=df['fatigue'], 
        mode='lines+markers', fill='tozeroy',
        line=dict(color='#38bdf8', width=3),
        fillcolor='rgba(56, 189, 248, 0.1)'
    ))
    # 기준선 추가
    fig_fatigue.add_hline(y=78, line_dash="dash", line_color="#f59e0b", annotation_text="주의")
    fig_fatigue.add_hline(y=60, line_dash="dash", line_color="#ef4444", annotation_text="위험")
    
    fig_fatigue.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20), height=350,
        font=dict(color="#64748b"),
        xaxis=dict(showgrid=False), yaxis=dict(range=[0, 100], gridcolor="#1e293b")
    )
    st.plotly_chart(fig_fatigue, use_container_width=True)

with tab2:
    fig_flow = go.Figure()
    fig_flow.add_trace(go.Bar(name='개인', x=df['date'], y=df['individual'], marker_color='#38bdf8'))
    fig_flow.add_trace(go.Bar(name='외국인', x=df['date'], y=df['foreign'], marker_color='#fb923c'))
    
    fig_flow.update_layout(
        barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20), height=350,
        font=dict(color="#64748b"),
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="#1e293b")
    )
    st.plotly_chart(fig_flow, use_container_width=True)

# --- Data Table ---
st.write("### 원본 데이터 (최근 7거래일)")
display_df = df.copy()
display_df['individual'] = display_df['individual'].apply(lambda x: f"{x/100:+.0f}억")
display_df['foreign'] = display_df['foreign'].apply(lambda x: f"{x/100:+.0f}억")
display_df['institution'] = display_df['institution'].apply(lambda x: f"{x/100:+.0f}억")
st.dataframe(display_df.iloc[::-1], use_container_width=True)

