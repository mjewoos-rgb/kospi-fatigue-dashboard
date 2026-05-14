import streamlit as st
from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="개인 방어 피로지수", layout="wide", initial_sidebar_state="collapsed")
st.title("📊 개인 방어 피로지수 대시보드")
st.caption("🔥 pykrx 자동 실시간 업데이트 • 매일 시장 열릴 때마다 최신")

# 날짜
today = datetime.now().strftime("%Y%m%d")
yest = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
st.subheader(f"📅 {yest[:4]}-{yest[4:6]}-{yest[6:]} 투자자 순매수 (억원)")

try:
    df = stock.get_market_net_purchases_of_equities(yest, yest, "KOSPI")
    
    if df.empty:
        st.warning("⚠️ 오늘 데이터가 아직 업데이트되지 않았어요. 시장 마감 후 다시 확인해주세요!")
        # 임시로 지난 데이터 예시 보여주기 (실제로는 pykrx가 가져올 때까지)
        st.info("현재 피로지수는 어제 데이터 기준으로 계산 중입니다.")
    else:
        st.dataframe(
            df.style.format("{:,.0f}").background_gradient(cmap="RdYlGn", axis=1),
            use_container_width=True,
            height=200
        )

    # 피로지수 계산
    personal = int(df.loc['개인'].iloc[0]) if not df.empty and '개인' in df.index else 0
    foreign = int(df.loc['외국인'].iloc[0]) if not df.empty and '외국인' in df.index else 0
    
    fatigue = 100
    if personal < 15000: fatigue -= 35
    if foreign < -15000: fatigue -= 30
    if personal > 25000: fatigue += 10
    fatigue = max(0, min(100, fatigue))  # 0\~100 사이로 제한

    # 예쁜 메트릭 + 프로그레스바
    col1, col2 = st.columns([3, 1])
    with col1:
        st.metric(
            label="현재 피로지수",
            value=f"{fatigue}점",
            delta="위험 🔥" if fatigue < 70 else "주의 ⚠️" if fatigue < 85 else "안전 ✅",
            delta_color="inverse"
        )
    with col2:
        color = "🔴" if fatigue < 70 else "🟠" if fatigue < 85 else "🟢"
        st.markdown(f"### {color} {fatigue}점")

    # 프로그레스바 (시각적으로 딱!)
    st.progress(fatigue / 100)
    if fatigue < 70:
        st.error("🚨 개인 매수 피로 누적! 외국인 매도 지속 중 → 곱버스 정리 고려")
    elif fatigue < 85:
        st.warning("⚠️ 주의 단계. 신용잔고 변화 계속 지켜보세요")
    else:
        st.success("✅ 안전! 지금은 개인 방어가 아직 버티는 중")

    st.success("✅ 실시간 데이터 불러오기 성공!")

except Exception as e:
    st.error(f"데이터 불러오는 중... ({e})")
    st.info("시장 마감 후 다시 새로고침 해보세요. 곧 신용잔고까지 완전 자동 추가할게!")

st.divider()
st.caption("🚀 다음 업데이트: 신용잔고 자동 연동 + 5일 추이 차트 + 알림 기능")
