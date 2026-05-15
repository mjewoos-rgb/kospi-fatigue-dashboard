import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pykrx import stock
from datetime import datetime, timedelta

# ── 페이지 설정 ──────────────────────────────────────────
st.set_page_config(page_title="KOSPI Fatigue Dashboard", layout="wide")

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
    }
    div[data-testid="stMetricValue"] { color: #38bdf8; font-weight: 800; }
    .stDataFrame { border: 1px solid #334155; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)


# ── 데이터 로드 ──────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_real_data():
    now = datetime.now()
    start_date = (now - timedelta(days=20)).strftime("%Y%m%d")
    end_date   = now.strftime("%Y%m%d")

    # ✅ 수정된 함수: 날짜별 투자자 순매수 거래대금
    # 반환 컬럼: 금융투자, 보험, 투신, 사모, 은행, 기타금융, 연기금,
    #            기관합계, 기타법인, 개인, 외국인, 기타외국인, 전체
    df = stock.get_market_trading_value_by_date(
        start_date, end_date, "KOSPI",
        etf=False, etn=False, elw=False
    )

    if df.empty:
        return pd.DataFrame()

    df = df[["개인", "외국인", "기관합계"]].copy()
    df = df / 1e8  # 원 → 억원

    # 인덱스(날짜) → 컬럼, 이름 통일
    df.index = pd.to_datetime(df.index).strftime("%m-%d")
    df = df.reset_index()
    df.columns = ["date", "individual", "foreign", "institution"]

    return df.tail(10).reset_index(drop=True)


# ── 피로지수 계산 ────────────────────────────────────────
def calc_fatigue(individual, foreign):
    score = 100.0
    indiv_penalty   = min(40, (1500 - individual) / 30)  if individual < 1500  else 0
    foreign_penalty = min(40, (-1500 - foreign)   / 40)  if foreign    < -1500 else 0
    return int(max(0, min(100, score - indiv_penalty - foreign_penalty)))


# ── 메인 ─────────────────────────────────────────────────
st.title("📉 KOSPI 개인 방어 피로지수")

try:
    with st.spinner("KRX 데이터 불러오는 중..."):
        df = get_real_data()

    if df.empty:
        st.warning("KRX 데이터가 아직 업데이트되지 않았습니다. 장 마감(오후 6시) 이후 다시 시도해주세요.")
        st.stop()

    df["fatigue"] = df.apply(
        lambda r: calc_fatigue(r["individual"], r["foreign"]), axis=1
    )

    latest = df.iloc[-1]
    prev   = df.iloc[-2] if len(df) > 1 else latest

    st.markdown(
        f"<p style='color:#94a3b8;'>실시간 pykrx 데이터 연동됨 (기준일: {latest['date']})</p>",
        unsafe_allow_html=True
    )

    # ── KPI ──────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "피로지수",
        f"{latest['fatigue']}점",
        f"{int(latest['fatigue'] - prev['fatigue']):+d}점"
    )
    c2.metric(
        "개인 순매수",
        f"{latest['individual']:+,.0f}억",
        f"{latest['individual'] - prev['individual']:+,.0f}억"
    )
    c3.metric(
        "외국인 순매수",
        f"{latest['foreign']:+,.0f}억",
        f"{latest['foreign'] - prev['foreign']:+,.0f}억",
        delta_color="inverse"
    )

    # ── 상태 배너 ─────────────────────────────────────────
    score = int(latest["fatigue"])
    if score < 60:
        st.error(f"🚨 **위험 단계 ({score}점)** — 개인 방어 한계치 도달. 보수적 접근 필요.")
    elif score < 78:
        st.warning(f"⚠️ **주의 단계 ({score}점)** — 외국인 매도세 증가 및 방어력 약화.")
    else:
        st.success(f"✅ **안전 단계 ({score}점)** — 현재 수급 방어 체력 충분.")

    st.progress(score / 100)

    # ── 차트 ──────────────────────────────────────────────
    tab1, tab2 = st.tabs(["📈 피로지수 추이", "💹 투자자 수급"])

    with tab1:
        fig = go.Figure()
        # 기준선
        fig.add_shape(type="line", x0=df["date"].iloc[0], x1=df["date"].iloc[-1],
                      y0=78, y1=78, line=dict(color="#f59e0b", dash="dash", width=1))
        fig.add_shape(type="line", x0=df["date"].iloc[0], x1=df["date"].iloc[-1],
                      y0=60, y1=60, line=dict(color="#ef4444", dash="dash", width=1))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["fatigue"],
            mode="lines+markers",
            line=dict(color="#38bdf8", width=3),
            fill="tozeroy", fillcolor="rgba(56,189,248,0.08)",
            marker=dict(size=7)
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, 105]),
            height=300,
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("점선: 주황=주의(78점), 빨강=위험(60점)")

    with tab2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="개인",   x=df["date"], y=df["individual"],  marker_color="#38bdf8"))
        fig2.add_trace(go.Bar(name="외국인", x=df["date"], y=df["foreign"],     marker_color="#f87171"))
        fig2.add_trace(go.Bar(name="기관",   x=df["date"], y=df["institution"], marker_color="#a78bfa"))
        fig2.update_layout(
            template="plotly_dark",
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── 데이터 테이블 ─────────────────────────────────────
    st.subheader("📋 최근 수급 상세 (단위: 억원)")
    display = df[["date", "individual", "foreign", "institution", "fatigue"]].copy()
    display.columns = ["날짜", "개인(억)", "외국인(억)", "기관합계(억)", "피로지수"]
    display = display.iloc[::-1].reset_index(drop=True)

    st.dataframe(
        display.style
            .format({
                "개인(억)":    "{:+,.0f}",
                "외국인(억)":  "{:+,.0f}",
                "기관합계(억)": "{:+,.0f}",
                "피로지수":    "{:.0f}"
            })
            .background_gradient(cmap="RdYlGn", subset=["피로지수"], vmin=0, vmax=100),
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.caption("데이터 출처: KRX → pykrx `get_market_trading_value_by_date` | 캐싱: 1시간")

except Exception as e:
    st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
    st.info("터미널에서 `pip install pykrx plotly` 후 재실행해주세요.")
