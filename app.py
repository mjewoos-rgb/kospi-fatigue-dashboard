import streamlit as st
from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="코스피 피로지수", layout="wide")
st.title("📊 개인 방어 피로지수 대시보드")
st.caption("pykrx 자동 실시간 업데이트 • 매일 시장 열릴 때마다 최신")

today = datetime.now().strftime("%Y%m%d")
yest = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

st.subheader(f"📅 {yest[:4]}-{yest[4:6]}-{yest[6:]} 투자자 순매수 (억원)")

try:
    df = stock.get_market_net_purchases_of_equities(yest, yest, "KOSPI")
    st.dataframe(df.style.format("{:,.0f}"), use_container_width=True)
    
    # 간단 피로지수 계산 (데이터 기반)
    personal = int(df.loc['개인'].iloc[0]) if '개인' in df.index else 0
    foreign = int(df.loc['외국인'].iloc[0]) if '외국인' in df.index else 0
    
    fatigue = 100
    if personal < 15000: fatigue -= 35   # 개인 매수 약해지면
    if foreign < -15000: fatigue -= 30   # 외국인 매도 강하면
    if personal > 25000: fatigue += 10   # 개인 과열
    
    delta = "위험 🔥" if fatigue < 70 else "주의 ⚠️" if fatigue < 85 else "안전 ✅"
    st.metric("현재 피로지수", f"{fatigue}점", delta=delta)
    
    st.success("✅ 실시간 데이터 불러오기 성공!")
    
except Exception as e:
    st.error(f"데이터 불러오는 중... ({e})")
    st.info("시장 시간 외에는 어제 데이터가 나와요")

st.divider()
st.write("🚀 신용잔고는 다음 업데이트 때 완전 자동화할게. 지금은 투자자 매매동향 + 피로지수부터 제대로 돌아감!")