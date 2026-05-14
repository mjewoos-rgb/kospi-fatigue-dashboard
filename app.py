import streamlit as st
from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="개인 방어 피로지수", layout="wide", initial_sidebar_state="collapsed")
st.title("📊 개인 방어 피로지수 대시보드")
st.caption("🔥 pykrx 완전 자동 • 매일 시장 열릴 때마다 최신")

# 날짜 설정
today = datetime.now().strftime("%Y%m%d")
dates = [(datetime.now() - timedelta(days=i)).strftime("%Y%m%d") for i in range(6)]  # 최근 5일 + 오늘

st.subheader("📅 최근 5일 투자자 순매수 추이 (억원)")

data_list = []
for d in dates[1:]:  # 최근 5일
    try:
        df_day = stock.get_market_net_purchases_of_equities(d, d, "KOSPI")
        if not df_day.empty:
            personal = int(df_day.loc['개인'].iloc[0]) if '개인' in df_day.index else 0
            foreign = int(df_day.loc['외국인'].iloc[0]) if '외국인' in df_day.index else 0
            data_list.append({
                '날짜': d[:4] + '-' + d[4:6] + '-' + d[6:],
                '개인': personal,
                '외국인': foreign,
                '피로지수': 100 - (35 if personal < 15000 else 0) - (30 if foreign < -15000 else 0) + (10 if personal > 25000 else 0)
            })
    except:
        pass

if data_list:
    df = pd.DataFrame(data_list)
    df = df[::-1]  # 최신 날짜가 위로
    
    # 테이블 + 색상
    st.dataframe(
        df.style.format({"개인": "{:,.0f}", "외국인": "{:,.0f}", "피로지수": "{:.0f}"}).background_gradient(cmap="RdYlGn_r", subset=["피로지수"]),
        use_container_width=True,
        hide_index=True
    )
    
    # 피로지수 추이 차트 (한눈에 확!)
    st.subheader("📈 피로지수 5일 추이")
    chart_data = df.set_index("날짜")[["피로지수"]]
    st.line_chart(chart_data, use_container_width=True, height=300)
    
    # 오늘 최신 피로지수
    latest = df.iloc[0]
    fatigue = latest["피로지수"]
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(
            "오늘 피로지수",
            f"{fatigue}점",
            delta="위험 🔥" if fatigue < 70 else "주의 ⚠️" if fatigue < 85 else "안전 ✅",
            delta_color="inverse"
        )
    with col2:
        color = "🔴" if fatigue < 70 else "🟠" if fatigue < 85 else "🟢"
        st.markdown(f"### {color} {fatigue}점")
    
    st.progress(fatigue / 100)
    
    if fatigue < 70:
        st.error("🚨 피로 누적 강함! 곱버스 정리 or 현금 비중 늘릴 타이밍")
    elif fatigue < 85:
        st.warning("⚠️ 주의 단계 — 신용잔고와 외국인 움직임 계속 지켜봐")
    else:
        st.success("✅ 아직 안전! 개인 방어가 잘 버티는 중")

    st.success("✅ 실시간 데이터 불러오기 성공!")
else:
    st.warning("⚠️ 아직 시장 데이터가 업데이트되지 않았어요. 시장 마감 후 다시 확인해주세요.")

st.divider()
st.caption("🚀 다음 업데이트: 신용잔고 완전 자동 + 알림 기능 + 종목별 분석")
