import streamlit as st
import pandas as pd
import time

# 1. 페이지 기본 설정 (대시보드 레이아웃)
st.set_page_config(page_title="AP 온도 시뮬레이터", page_icon="📱", layout="centered")

# 커스텀 CSS 적용 (UI 디자인 개선)
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 800; text-align: center; margin-bottom: 0px; }
    .sub-header { font-size: 1rem; color: #6B7280; text-align: center; margin-bottom: 30px; }
    div[data-testid="metric-container"] { background-color: #F9FAFB; padding: 15px; border-radius: 10px; border: 1px solid #E5E7EB; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📱 모바일 AP 온도 시뮬레이터</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">스마트폰 사용 환경에 따른 반도체 발열과 성능 저하 시점을 예측합니다.</p>', unsafe_allow_html=True)

# 2. 사이드바 디자인
with st.sidebar:
    st.header("⚙️ 환경 설정")
    st.divider()
    temp_env = st.slider("현재 주변 온도 (℃)", min_value=-10.0, max_value=40.0, value=25.0, step=1.0)
    time_usage = st.slider("예상 사용 시간 (분)", min_value=10, max_value=300, value=60, step=10)
    app_type = st.radio("실행할 앱 종류", ["단순 웹서핑 🌐", "고화질 동영상 시청 🎬", "3D 고사양 게임 🎮"])
    
    st.divider()
    st.info("💡 사용 시간이 길거나 주변 온도가 높을수록 45℃ 한계점에 빠르게 도달합니다.")

# 앱 부하 수준에 따른 발열량 설정 (웹서핑/동영상도 장시간 시 45도 초과 가능)
if "웹서핑" in app_type:
    temp_increase = 0.8
elif "동영상" in app_type:
    temp_increase = 1.3
else:
    temp_increase = 2.2

# 3. 시뮬레이션 실행 및 결과 화면
if st.button("🚀 시뮬레이션 시작", use_container_width=True):
    with st.spinner("알고리즘을 통해 반도체 온도 변화를 계산 중입니다..."):
        time.sleep(0.5) 
    
    current_temp = temp_env
    temp_history = [current_temp]
    throttling_time = -1
    
    try:
        # 발열 시뮬레이션 알고리즘
        for minute in range(1, int(time_usage) + 1):
            cooling_effect = (current_temp - temp_env) * 0.03
            current_temp = current_temp + temp_increase - cooling_effect
            temp_history.append(current_temp)
            
            if current_temp >= 45.0 and throttling_time == -1:
                throttling_time = minute
                
        # 4. 결과 대시보드 레이아웃
        st.divider()
        st.subheader("📊 시뮬레이션 결과 요약")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("최고 도달 온도", str(round(max(temp_history), 1)) + " ℃")
        col2.metric("사용 후 최종 온도", str(round(temp_history[-1], 1)) + " ℃")
        
        if throttling_time != -1:
            col3.metric("쓰로틀링 시작 시점", str(throttling_time) + " 분")
        else:
            col3.metric("쓰로틀링 시작 시점", "안전 (미발생)")
        
        # 꺾은선 그래프 데이터 작성
        df = pd.DataFrame({
            "시간(분)": range(int(time_usage) + 1),
            "예상 온도(℃)": temp_history,
            "위험 기준선(45℃)": [45.0] * (int(time_usage) + 1)
        })
        df.set_index("시간(분)", inplace=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        # 파란색(예상 온도), 빨간색(위험 기준선)
        st.line_chart(df, color=["#3B82F6", "#EF4444"])
        
        # 경고 메시지 및 쿨링 가이드
        if throttling_time != -1:
            warning_msg = "🚨 **경고!** 사용 시작 **" + str(throttling_time) + "분** 후 스마트폰 온도가 45℃를 초과하여 기기가 느려집니다."
            st.error(warning_msg)
            
            with st.expander("❄️ 올바른 스마트폰 쿨링 방법 보기", expanded=True):
                st.write("""
                * **케이스 분리:** 열 방출을 방해하는 두꺼운 케이스를 벗겨주세요.
                * **화면 밝기 조절:** 디스플레이 발열을 줄이기 위해 밝기를 낮추고 불필요한 백그라운드 앱을 종료하세요.
                * **자연 냉각:** 선풍기 바람을 쐬거나 통풍이 잘 되는 서늘한 곳에 잠시 두세요. 
                * ⚠️ **절대 금지:** 기기를 빨리 식히려고 냉장고나 얼음팩 위에 두면 내부 결로(물방울)로 인해 반도체 기판이 부식되어 고장 납니다.
                """)
        else:
            st.success("✨ **안정적인 상태입니다.** 설정하신 시간 동안 성능 저
