import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="AP 온도 시뮬레이터", page_icon="📱", layout="centered")

# 은은한 파스텔 배경색 및 커스텀 CSS 적용 (조절 바 색상 강제 지정은 제거)
st.markdown("""
    <style>
    /* 전체 메인 화면 배경색 (은은한 쿨 그레이/파스텔 슬레이트) */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* 사이드바 배경색 */
    [data-testid="stSidebar"] {
        background-color: #F1F5F9;
    }

    /* 메인 타이틀 그라데이션 */
    .main-header {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4338CA 0%, #6366F1 100%);
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
    .sidebar-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #334155;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    
    /* 은은한 흰색 메트릭 카드 (배경과 대비감 확보) */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #6366F1;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
    }
    .metric-label {
        color: #64748B;
        font-size: 0.82rem;
        margin: 0;
        font-weight: 600;
    }
    .metric-value {
        color: #1E293B;
        font-size: 1.45rem;
        margin: 4px 0 0 0;
        font-weight: 800;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📱 모바일 AP 온도 시뮬레이터</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">기기 종류, 충전 상태, 사용 조건에 따른 실시간 발열 분석 대시보드</p>', unsafe_allow_html=True)

# 2. 사이드바 구성 (기기 선택, 앱 종류, 환경 조건)
with st.sidebar:
    st.header("⚙️ 기기 및 환경 설정")
    st.divider()
    
    device_type = st.radio("기기 종류", ["스마트폰 📱", "태블릿 / 패드 📱"])
    
    st.markdown('<p class="sidebar-title">🌡️ 주변 환경 및 사용 시간</p>', unsafe_allow_html=True)
    temp_env = st.slider("현재 주변 온도 (℃)", min_value=-10.0, max_value=40.0, value=25.0, step=1.0)
    time_usage = st.slider("예상 사용 시간 (분)", min_value=10, max_value=300, value=60, step=10)
    
    st.markdown('<p class="sidebar-title">⚡ 세부 사용 조건</p>', unsafe_allow_html=True)
    app_type = st.radio("실행할 앱 종류", ["메신저 / SNS 💬", "단순 웹서핑 🌐", "고화질 동영상 시청 🎬", "3D 고사양 게임 🎮"])
    brightness = st.slider("화면 밝기 (%)", min_value=10, max_value=100, value=70, step=10)
    charge_type = st.selectbox("충전 상태", ["미충전 🔋", "일반 충전 🔌", "고속 충전 ⚡"])

    st.divider()
    st.caption("💡 설정을 변경하면 오른쪽 결과가 실시간으로 업데이트됩니다.")

# 3. 시뮬레이션 알고리즘 가중치 설정
if "태블릿" in device_type:
    device_mult = 0.75  # 태블릿은 넓은 방열 면적으로 발열 감소
    cooling_factor = 0.10
else:
    device_mult = 1.00
    cooling_factor = 0.075

if "메신저" in app_type:
    base_increase = 0.4
elif "웹서핑" in app_type:
    base_increase = 0.7
elif "동영상" in app_type:
    base_increase = 1.3
else:
    base_increase = 2.3

brightness_increase = (brightness / 100.0) * 0.5

if "고속" in charge_type:
    charge_increase = 1.1
elif "일반" in charge_type:
    charge_increase = 0.4
else:
    charge_increase = 0.0

total_increase = (base_increase + brightness_increase + charge_increase) * device_mult

# 4. 실시간 온도로직 시뮬레이션
current_temp = temp_env
temp_history = [current_temp]
throttling_time = -1

try:
    for minute in range(1, int(time_usage) + 1):
        if current_temp >= 45.0:
            effective_increase = total_increase * 0.45
            if throttling_time == -1:
                throttling_time = minute
        else:
            effective_increase = total_increase

        cooling_effect = (current_temp - temp_env) * cooling_factor
        current_temp = current_temp + effective_increase - cooling_effect
        
        if current_temp > 62.0:
            current_temp = 62.0
            
        temp_history.append(current_temp)

    # 5. 결과 대시보드 출력
    st.divider()
    st.subheader("📊 시뮬레이션 분석 대시보드")
    
    max_t = str(round(max(temp_history), 1))
    final_t = str(round(temp_history[-1], 1))
    th_t = str(throttling_time) + " 분" if throttling_time != -1 else "안전 (미발생)"

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'<div class="metric-card"><p class="metric-label">최고 도달 온도</p><p class="metric-value">{max_t} ℃</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><p class="metric-label">사용 후 최종 온도</p><p class="metric-value">{final_t} ℃</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><p class="metric-label">쓰로틀링 시작</p><p class="metric-value">{th_t}</p></div>', unsafe_allow_html=True)
    
    # 꺾은선 그래프
    df = pd.DataFrame({
        "시간(분)": range(int(time_usage) + 1),
        "예상 온도(℃)": temp_history,
        "위험 기준선(45℃)": [45.0] * (int(time_usage) + 1)
    })
    df.set_index("시간(분)", inplace=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.line_chart(df, color=["#6366F1", "#F87171"])
    
    # 6. 경고 메시지 및 쿨링 가이드
    if throttling_time != -1:
        warning_msg = f"🚨 **경고!** 사용 시작 **{throttling_time}분** 후 {device_type.split()[0]} 온도가 45℃를 초과하여 쓰로틀링(성능 제한)이 시작됩니다."
        st.error(warning_msg)
        
        with st.expander("❄️ 조건별 맞춤형 쿨링 가이드 보기", expanded=True):
            if "태블릿" in device_type:
                st.write("• **📱 태블릿/패드 방열:** 거치대를 사용해 후면 전체에 공기가 통하도록 띄워주면 방열 효과가 극대화됩니다.")
            else:
                st.write("• **📱 스마트폰 방열:** 열 방출을 막는 밀착형 파우치나 두꺼운 범퍼 케이스를 벗겨주세요.")

            if "메신저" in app_type:
                st.write("• **💬 메신저/SNS:** 미디어 자동 다운로드 옵션을 끄고 백그라운드 동영상 자동 재생을 제한하세요.")
            elif "웹서핑" in app_type:
                st.write("• **🌐 웹서핑:** 브라우저 백그라운드 탭을 정리하고 다크 모드를 설정하세요.")
            elif "동영상" in app_type:
                st.write("• **🎬 동영상:** 스트리밍 해상도를 한 단계 낮추고 화면 밝기를 조절하세요.")
            else:
                st.write("• **🎮 3D 게임:** 게임 옵션에서 그래픽 품질 및 프레임(FPS)을 하향 조정하세요.")
            
            if brightness >= 70:
                st.write(f"• **☀️ 화면 밝기 ({brightness}%):** 디스플레이 면적이 넓을수록 발열이 커집니다. 밝기를 낮춰주세요.")
            if "충전" in charge_type and "미충전" not in charge_type:
                st.write("• **🔌 충전 중 사용:** 고사양 작업이나 영상 시청 시 충전 케이블을 분리하는 것이 기기 수명과 발열 제어에 좋습니다.")

            st.caption("⚠️ **주의:** 급격히 식히기 위해 냉장고에 넣으면 내부 결로 현상으로 부품이 부식될 수 있습니다.")
    else:
        st.success("✨ **안정적인 상태입니다.** 현재 설정한 기기 조건에서는 성능 저하 없이 원활하게 구동 가능합니다.")

except Exception as e:
    st.error("데이터 처리 중 오류가 발생했습니다. 환경 설정 값을 다시 확인해 주세요.")
