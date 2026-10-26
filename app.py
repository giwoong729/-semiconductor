import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. 화면 제목 및 안내
st.title("📱 스마트폰 모바일 AP 온도 관리 시뮬레이터")
st.write("사용할 앱의 종류와 주변 환경을 입력하면, 스마트폰 반도체의 예상 온도 변화와 성능 저하(쓰로틀링) 시점을 예측해 줍니다.")

# 2. 사용자 입력 (UI 및 예외 처리를 위한 제약 조건 설정)
st.sidebar.header("환경 설정")
# min_value, max_value를 통해 비정상적인 값 입력을 1차적으로 방지 (예외 처리)
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
    temp_history = [current_temp] # 시간별 온도 데이터를 담을 리스트
    throttling_time = -1 # 쓰로틀링 발생 시간을 저장할 변수 (-1은 발생 안 함을 의미)
    
    # 런타임 에러 방지를 위한 예외 처리 (try-except)
    try:
        # 사용 시간만큼 반복하며 1분 단위 온도 계산
        for minute in range(1, int(time_usage) + 1):
            # 온도가 무한정 오르지 않도록 주변 온도와의 차이에 따른 자연 냉각 효과를 살짝 반영 (보다 현실적인 시뮬레이션)
            cooling_effect = (current_temp - temp_env) * 0.05
            current_temp = current_temp + temp_increase - cooling_effect
            
            temp_history.append(current_temp)
            
            # 성능 저하 한계점(45도) 초과 여부 검사
            if current_temp >= 45.0 and throttling_time == -1:
                throttling_time = minute
                
        # 4. 시각화 및 결과 출력
        st.subheader("📈 시간에 따른 반도체 온도 변화 추이")
        
        # 데이터를 데이터프레임으로 변환
        df = pd.DataFrame({
            "시간(분)": range(int(time_usage) + 1),
            "온도(℃)": temp_history
        })
        df.set_index("시간(분)", inplace=True)
        
        # 스트림릿 내장 그래프 함수로 꺾은선 그래프 출력
        st.line_chart(df)
        
        # 경고 메시지 출력
        if throttling_time != -1:
            st.error(f"⚠️ **성능 저하 주의!**\n\n사용 시작 **{throttling_time}분 후** 스마트폰 온도가 45℃를 초과하여 쓰로틀링이 발생할 것으로 예상됩니다. 잠시 기기 사용을 멈추고 열을 식혀주세요.")
        else:
            st.success("✅ 안전 범위입니다. 해당 사용 시간 동안은 성능 저하 없이 원활하게 사용할 수 있습니다.")
            
    except Exception as e:
        # 예기치 못한 에러 발생 시 프로그램 종료를 막고 에러 메시지 출력
        st.error("데이터 처리 중 알 수 없는 오류가 발생했습니다. 입력값을 다시 확인해 주세요.")
