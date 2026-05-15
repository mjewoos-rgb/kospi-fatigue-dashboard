import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pykrx import stock
from datetime import datetime, timedelta

st.set_page_config(page_title="KOSPI Fatigue Dashboard", layout="wide")

st.markdown("""
    <style>
    @import url('https://rsms.me/inter/inter.css');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    div[data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
    }
    div[data-testid="stMetricValue"] { color: #38bdf8; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)


# ── 데이터 로드 ──────────────────────────────────────────
@st.cache_data(ttl=1800)
def get_raw_data():
    now        = datetime.now()
    # end_date: 어제 기준 (오늘 데이터는 당일 오후 늦게 반영되므로)
    end_dt     = now - timedelta(days=1)
    start_dt   = now - timedelta(days=25)
    start_date = start_dt.strftime("%Y%m%d")
    end_date   = end_dt.strftime("%Y%m%d")

    df = stock.get_market_trading_value_by_date(
        start_date, end_date, "KOSPI",
        etf=False, etn=False, elw=False
    )
    return df  # 원본 그대로 반환


def process(df_raw):
    if df_raw is None or df_raw.empty:
        return pd.DataFrame()

    # 실제 컬럼 확인
    actual = set(df_raw.columns.tolist())
    needed = {"개인", "외국인", "기관합계"}
    if not needed.issubset(actual):
        st.error(f"컬럼 누락: {needed - actual}\n실제 컬럼 목록: {sorted(actual)}")
        return pd.DataFrame()

    df = df_raw[["개인", "외국인", "기관합계"]].copy()
    df = df / 1e8  # 원 → 억원

    df.index = pd.to_datetime(df.index).strftime("%m-%d")
    df = df.reset_index()
    df.columns = ["date", "individual", "foreign", "institution"]
    return df.tail(10).reset_index(drop=True)


# ── 피로지수 계산 ────────────────────────────────────────
def calc_fatigue(individual, foreign):
    score = 100.0
    indiv_penalty   = min(40, (1500 - individual) / 30) if individual < 1500  else 0
    foreign_penalty = min(40, (-1500 - foreign)   / 40) if foreign    < -1500 else 0
    return int(max(0, min(100, score - indiv_penalty - foreign_penalty)))


# ── 메인 ─────────────────────────────────────────────────
st.title("📉 KOSPI 개인 방어 피로지수")

try:
    with st.spinner("KRX 데이터 불러오는 중..."):
        df_raw = get_raw_data()

    # ── 디버그 패널 (문제 파악용, 정상 작동 확인 후 삭제 가능) ──
    with st.expander("🔧 디버그 정보 (문제 해결용)"):
        st.write("**df_raw.empty:**", df_raw.empty)
        st.write("**df_raw.shape:**", df_raw.shape)
        st.write("**컬럼 목록:**", df_raw.columns.tolist())
        if not df_raw.empty:
            st.write("**최근 3행:**")
            st.dataframe(df_raw.tail(3))

    df = process(df_raw)

    if df.empty:
        st.warning("데이터를 처리하지 못했습니다. 위 디버그 정보를 확인해주세요.")
        st.stop()

    df["fatigue"] = df.apply(
        lambda r: calc_fatigue(r["individual"], r["foreign"]), axis=1
    )

    latest = df.iloc[-1]
    prev   = df.iloc[-2] if len(df) > 1 else latest

    st.markdown(
        f"<p style='color:#94a3b8;'>pykrx 실시간 연동 | 기준일: {latest['date']}</p>",
        unsafe_allow_html=True
    )

    # ── KPI ──────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("피로지수",      f"{latest['fatigue']}점",
              f"{int(latest['fatigue'] - prev['fatigue']):+d}점")
    c2.metric("개인 순매수",   f"{latest['individual']:+,.0f}억",
              f"{latest['individual'] - prev['individual']:+,.0f}억")
    c3.metric("외국인 순매수", f"{latest['foreign']:+,.0f}억",
              f"{latest['foreign'] - prev['foreign']:+,.0f}억",
              delta_color="inverse")

    # ── 상태 배너 ─────────────────────────────────────────
    score = int(latest["fatigue"])
    if score < 60:
        st.error(f"🚨 **위험 ({score}점)** — 개인 방어 한계치 도달")
    elif score < 78:
        st.warning(f"⚠️ **주의 ({score}점)** — 외국인 매도세 증가")
    else:
        st.success(f"✅ **안전 ({score}점)** — 수급 방어 체력 충분")

    st.progress(score / 100)

    # ── 차트 ──────────────────────────────────────────────
    tab1, tab2 = st.tabs(["📈 피로지수 추이", "💹 투자자 수급"])

    with tab1:
        fig = go.Figure()
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
            height=300, margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("점선: 주황=주의(78), 빨강=위험(60)")

    with tab2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="개인",   x=df["date"], y=df["individual"],  marker_color="#38bdf8"))
        fig2.add_trace(go.Bar(name="외국인", x=df["date"], y=df["foreign"],     marker_color="#f87171"))
        fig2.add_trace(go.Bar(name="기관",   x=df["date"], y=df["institution"], marker_color="#a78bfa"))
        fig2.update_layout(
            template="plotly_dark", barmode="group",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=300, margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── 테이블 ────────────────────────────────────────────
    st.subheader("📋 최근 수급 상세 (단위: 억원)")
    display = df[["date", "individual", "foreign", "institution", "fatigue"]].copy()
    display.columns = ["날짜", "개인(억)", "외국인(억)", "기관합계(억)", "피로지수"]
    display = display.iloc[::-1].reset_index(drop=True)

    st.dataframe(
        display.style
            .format({"개인(억)": "{:+,.0f}", "외국인(억)": "{:+,.0f}",
                     "기관합계(억)": "{:+,.0f}", "피로지수": "{:.0f}"})
            .background_gradient(cmap="RdYlGn", subset=["피로지수"], vmin=0, vmax=100),
        use_container_width=True, hide_index=True
    )

    st.divider()
    st.caption("데이터: pykrx `get_market_trading_value_by_date` | 캐싱 30분")

except Exception as e:
    st.error(f"오류 발생: {e}")
    st.code(str(e))
    st.info("`pip install pykrx plotly` 확인 후 재실행")
