import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정 및 감각적인 CSS 디자인 적용
st.set_page_config(page_title="AP 온도 시뮬레이터", page_icon="📱", layout="centered")

# 부분적인 색상 포인트 및 스타일링 (과하지 않은 트렌디한 대시보드 스타일)
st.markdown("""
    <style>
    /* 상단 타이틀 그라데이션 포인트 */
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 4px;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 25px;
    }
    
    /* 결과 지표 카드 디자인 (좌측 세로 파란 포인트 선) */
    div[data-testid="metric-container"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #3B82F6;
        border-radius: 12px;
        padding: 12px 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* 사이드바 그룹 소제목 */
    .sidebar-section-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1E293B;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📱 모바일 AP 온도 시뮬레이터</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">충전 상태와 화면 밝기까지 반영한 실시간 스마트폰 발열 예측 시스템</p>', unsafe_allow_html=True)

# 2. 사이드바 구성 (신규 항목 추가: 밝기, 충전 상태)
with st.sidebar:
    st.header("⚙️ 환경 및 기기 설정")
    st.divider()
    
    temp_env = st.slider("현재 주변 온도 (℃)", min_value=-10.0, max_value=40.0, value=25.0, step=1.0)
    time_usage = st.slider("예상 사용 시간 (분)", min_value=10, max_value=300, value=60, step=10)
    
    st.markdown('<p class="sidebar-section-title">📱 세부 사용 조건</p>', unsafe_allow_html=True)
    app_type = st.radio("실행할 앱 종류", ["단순 웹서핑 🌐", "고화질 동영상 시청 🎬", "3D 고사양 게임 🎮"])
    brightness = st.slider("화면 밝기 (%)", min_value=10, max_value=100, value=70, step=10)
    charge_type = st.selectbox("충전 상태", ["미충전 🔋", "일반 충전 🔌", "고속 충전 ⚡"])

    st.divider()
    st.caption("💡 설정을 변경하면 오른쪽 대시보드가 실시간으로 업데이트됩니다.")

# 3. 발열 계산 알고리즘 (앱 부하 + 밝기 발열 + 충전 회로 발열)
# ① 앱 종류 기본 발열
if "웹서핑" in app_type:
    base_increase = 0.7
elif "동영상" in app_type:
    base_increase = 1.3
else:
    base_increase = 2.3

# ② 화면 밝기 추가 발열 (10%~100% -> 0.05 ~ 0.5°C/분 추가)
brightness_increase = (brightness / 100.0) * 0.5

# ③ 충전 상태 추가 발열 (고속 충전은 충전 IC 회로 발열이 매우 큼)
if "고속" in charge_type:
    charge_increase = 1.1
elif "일반" in charge_type:
    charge_increase = 0.4
else:
    charge_increase = 0.0

# 총 발열 수치 합산
total_increase = base_increase + brightness_increase + charge_increase

# 4. 실시간 시뮬레이션 계산
current_temp = temp_env
temp_history = [current_temp]
throttling_time = -1

try:
    for minute in range(1, int(time_usage) + 1):
        # 45도 초과 시 AP 쓰로틀링(전력 및 성능 제어) 작동
        if current_temp >= 45.0:
            effective_increase = total_increase * 0.45
            if throttling_time == -1:
                throttling_time = minute
        else:
            effective_increase = total_increase

        # 자연 방열 계산
        cooling_effect = (current_temp - temp_env) * 0.075
        current_temp = current_temp + effective_increase - cooling_effect
        
        # 하드웨어 최대 제한 온도 설정
        if current_temp > 62.0:
            current_temp = 62.0
            
        temp_history.append(current_temp)

    # 5. 결과 대시보드 출력
    st.divider()
    st.subheader("📊 시뮬레이션 분석 대시보드")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("최고 도달 온도", str(round(max(temp_history), 1)) + " ℃")
    col2.metric("사용 후 최종 온도", str(round(temp_history[-1], 1)) + " ℃")
    
    if throttling_time != -1:
        col3.metric("쓰로틀링 시작 시점", str(throttling_time) + " 분")
    else:
        col3.metric("쓰로틀링 시작 시점", "안전 (미발생)")
    
    # 그래프 데이터 구성
    df = pd.DataFrame({
        "시간(분)": range(int(time_usage) + 1),
        "예상 온도(℃)": temp_history,
        "위험 기준선(45℃)": [45.0] * (int(time_usage) + 1)
    })
    df.set_index("시간(분)", inplace=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    # 파란색 (온도 변화 선), 빨간색 (위험 기준선)
    st.line_chart(df, color=["#2563EB", "#EF4444"])
    
    # 6. 경고 및 동적 맞춤형 쿨링 가이드
    if throttling_time != -1:
        warning_msg = "🚨 **경고!** 사용 시작 **" + str(throttling_time) + "분** 후 스마트폰 온도가 45℃를 초과하여 쓰로틀링(성능 제한)이 작동합니다."
        st.error(warning_msg)
        
        with st.expander("❄️ 조건별 맞춤형 쿨링 가이드 보기", expanded=True):
            # 앱 종류별 가이드
            if "웹서핑" in app_type:
                st.write("• **🌐 웹서핑:** 브라우저 백그라운드 탭을 정리하고 다크 모드를 켜서 AP 연산을 줄이세요.")
            elif "동영상" in app_type:
                st.write("• **🎬 동영상:** 스트리밍 해상도를 1080p 이하로 맞추고 데이터 모뎀 사용을 줄이세요.")
            else:
                st.write("• **🎮 3D 게임:** 게임 내 옵션에서 프레임을 30fps로 변경하고 그래픽 설정을 하향하세요.")
            
            # 밝기 조건 가이드
            if brightness >= 70:
                st.write("• **☀️ 화면 밝기 (" + str(brightness) + "%):** 현재 화면 밝기가 높습니다. 밝기를 50% 이하로 낮추면 디스플레이 발열이 크게 줄어듭니다.")
            
            # 충전 조건 가이드
            if "고속" in charge_type:
                st.write("• **⚡ 고속 충전 중:** 고속 충전 회로의 발열이 매우 심합니다. **고사양 작업 시에는 반드시 충전 케이블을 분리**해 주세요.")
            elif "일반" in charge_type:
                st.write("• **🔌 일반 충전 중:** 충전과 기기 사용이 동시 진행되면 배터리 수명이 줄고 발열이 가중됩니다. 완충 후 사용을 권장합니다.")
            
            st.caption("⚠️ **주의:** 냉장고나 얼음팩을 활용한 급격한 냉각은 내부 결로 현상을 발생시켜 메인보드 고장의 원인이 됩니다.")
    else:
        st.success("✨ **안정적인 상태입니다.** 현재 설정 조건에서는 성능 저하 없이 원활하게 구동 가능합니다.")

except Exception as e:
    st.error("데이터 처리 중 오류가 발생했습니다. 환경 설정 값을 다시 확인해 주세요.")
