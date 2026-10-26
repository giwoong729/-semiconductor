import streamlit as st
import pandas as pd

# 1. 화면 제목 및 안내
st.title("📱 스마트폰 모바일 AP 온도 관리 시뮬레이터")
st.write("사용할 앱의 종류와 주변 환경을 입력하면, 스마트폰 반도체의 예상 온도 변화와 성능 저하(쓰로틀링) 시점을 예측해 줍니다.")

# 2. 사용자 입력 (UI 및 예외 처리를 위한 제약 조건 설정)
st.sidebar.header("환경 설정")
temp_env = st.sidebar.number_input("현재 주변 온도 (℃)", min_value=-20.0, max_value=60.0, value=25.0, step=1.0)
time_usage = st.sidebar.number_input("예상 사용 시간 (분)", min_value=1, max_value=300, value=30, step=10)
app_type = st.sidebar.selectbox("실행할 앱 종류", ["단순 웹서핑", "고화질 동영상 시청", "3D 고사양 게임"])

# 앱 부하 수준에 따른 1분당 발열 증가량 설정
if app_type == "단순 웹서핑":
    temp_increase = 0.2
elif app_type == "고화질 동영상 시청":
    temp_increase = 0.5
else:
    temp_increase = 1.2

# 3. 데이터 처리 및 알고리즘 시뮬레이션
if st.button("시뮬레이션 시작"):
    current_temp = temp_env
    temp_history = [current_temp]
    throttling_time = -1
    
    try:
        # 사용 시간만큼 반복하며 1분 단위 온도 계산
        for minute in range(1, int(time_usage) + 1):
            cooling_effect = (current_temp - temp_env) * 0.05
            current_temp = current_temp + temp_increase - cooling_effect
            
            temp_history.append(current_temp)
            
            # 성능 저하 한계점(45도) 초과 여부 검사
            if current_temp >= 45.0 and throttling_time == -1:
                throttling_time = minute
                
        # 4
