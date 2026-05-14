import streamlit as st
from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(page_title="개인 방어 피로지수", layout="wide", initial_sidebar_state="collapsed")
st.title("📊 개인 방어 피로지수 대시보드")
st.caption("🔥 pykrx 완전 자동 • 시장 마감 후에도 최근 거래일 데이터 자동 표시")

# 최근 10일 범위로 데이터 한 번에 가져오기 (빈 날짜 자동 스킵)
end_date = datetime.now() - timedelta(days=1)
start_date = end_date - timedelta(days=12)
start_str = start_date.strftime("%Y%m%d")
end_str = end_date.strftime("%Y%m%d")

st.subheader(f"📅 최근 거래일 투자자 순매수 추이 (억원)")

try:
    df_raw = stock.get_market_net_purchases_of_equities(start_str, end_str, "KOSPI")
    
    if df_raw.empty:
        st.warning("⚠️ 아직 KRX 데이터가 업데이트되지 않았어요. 내일 아침 다시 확인해주세요!")
    else:
        # 날짜별로 정리
        df = df_raw.reset_index()
        df['날짜'] = pd.to_datetime(df['날짜']).dt.strftime('%Y-%m-%d')
        df = df.sort_values('날짜', ascending=False).head(8)  # 최근 8개 거래일 (안전하게)
        
        # 피로지수 계산
        df['피로지수'] = 100
        df.loc[df['개인'] < 15000, '피로지수'] -= 35
        df.loc[df['외국인'] < -15000, '피로지수'] -= 30
        df.loc[df['개인'] > 25000, '피로지수'] += 10
        df['피로지수'] = df['피로지수'].clip(0, 100)
        
        # 테이블 (최근 5일)
        display_df = df.head(5).copy()
        st.dataframe(
            display_df.style.format({"개인": "{:,.0f}", "외국인": "{:,.0f}", "피로지수": "{:.0f}"})
                     .background_gradient(cmap="RdYlGn_r", subset=["피로지수"]),
            use_container_width=True,
            hide_index=True
        )
        
        # 그래프
        st.subheader("📈 피로지수 5일 추이")
        chart_data = display_df.set_index("날짜")[["피로지수"]]
        st.line_chart(chart_data, use_container_width=True, height=320)
        
        # 오늘(가장 최근) 피로지수 강조
        latest = display_df.iloc[0]
        fatigue = int(latest["피로지수"])
        col1, col2 = st.columns([3, 1])
        with col1:
            st.metric(
                "최근 거래일 피로지수",
                f"{fatigue}점",
                delta="위험 🔥" if fatigue < 70 else "주의 ⚠️" if fatigue < 85 else "안전 ✅",
                delta_color="inverse"
            )
        with col2:
            color = "🔴" if fatigue < 70 else "🟠" if fatigue < 85 else "🟢"
            st.markdown(f"### {color} {fatigue}점")
        
        st.progress(fatigue / 100)
        
        if fatigue < 70:
            st.error("🚨 피로 누적 강함! 곱버스 정리 고려할 때")
        elif fatigue < 85:
            st.warning("⚠️ 주의 단계 — 신용잔고 계속 지켜봐")
        else:
            st.success("✅ 아직 안전 구간")

        st.success("✅ 데이터 불러오기 성공! (최근 거래일 기준)")

except Exception as e:
    st.error(f"데이터 불러오는 중... ({e})")
    st.info("내일 아침 시장 열리면 자동으로 최신 데이터가 나와요.")

st.divider()
st.caption("🚀 다음 업데이트: 신용잔고 완전 자동 + 푸시 알림")
