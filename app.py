import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정 및 모던 UI CSS 정의
st.set_page_config(page_title="AP 온도 시뮬레이터", page_icon="📱", layout="centered")

st.markdown("""
    <style>
    /* 1. 전체 배경: 눈이 편안한 연한 슬레이트 블루-그레이 */
    [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* 2. 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    
    /* 3. 상단 히어로 헤더 배너 */
    .hero-banner {
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
        border: 1px solid #C7D2FE;
        border-radius: 16px;
        padding: 24px 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.05);
    }
    .hero-tag {
        display: inline-block;
        background-color: #6366F1;
        color: #FFFFFF;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 12px;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #1E1B4B;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero-sub {
        font-size: 0.9rem;
        color: #4338CA;
        margin-top: 6px;
        margin-bottom: 0;
        font-weight: 500;
    }

    /* 4. 입체감 있는 결과 분석 지표 카드 */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #6366F1;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease-in-out;
    }
    .metric-label {
        color: #64748B;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    .metric-value {
        color: #0F172A;
        font-size: 1.55rem;
        font-weight: 800;
        margin: 6px 0 0 0;
        letter-spacing: -0.02em;
    }
    
    /* 5. 사이드바 그룹 섹션 바 */
    .sidebar-label {
        display: inline-block;
        background-color: #F1F5F9;
        color: #475569;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 6px;
        margin-top: 14px;
        margin-bottom: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# 헤더 히어로 배너 출력
st.markdown("""
    <div class="hero-banner">
        <span class="hero-tag">REAL-TIME SIMULATOR</span>
        <h1 class="hero-title">📱 모바일 AP 온도 시뮬레이터</h1>
        <p class="hero-sub">기기 특성, 충전 조건, 화면 밝기에 따른 반도체 발열과 성능 제한 예측</p>
    </div>
""", unsafe_allow_html=True)

# 2. 사이드바 컨트롤 구성
with st.sidebar:
    st.header("⚙️ 시뮬레이션 환경 설정")
    st.divider()
    
    st.markdown('<span class="sidebar-label">기기 유형</span>', unsafe_allow_html=True)
    device_type = st.radio("기기 종류", ["스마트폰 📱", "태블릿 / 패드 📱"], label_visibility="collapsed")
    
    st.markdown('<span class="sidebar-label">주변 환경 & 사용 시간</span>', unsafe_allow_html=True)
    temp_env = st.slider("현재 주변 온도 (℃)", min_value=-10.0, max_value=40.0, value=25.0, step=1.0)
    time_usage = st.slider("예상 사용 시간 (분)", min_value=10, max_value=300, value=60, step=10)
    
    st.markdown('<span class="sidebar-label">앱 실행 & 충전 상태</span>', unsafe_allow_html=True)
    app_type = st.radio("실행할 앱 종류", ["메신저 / SNS 💬", "단순 웹서핑 🌐", "고화질 동영상 시청 🎬", "3D 고사양 게임 🎮"])
    brightness = st.slider("화면 밝기 (%)", min_value=10, max_value=100, value=70, step=10)
    charge_type = st.selectbox("충전 상태", ["미충전 🔋", "일반 충전 🔌", "고속 충전 ⚡"])

    st.divider()
    st.caption("💡 옵션을 조작하면 오른쪽 대시보드가 실시간으로 업데이트됩니다.")

# 3. 발열 모델링 연산 알고리즘
if "태블릿" in device_type:
    device_mult = 0.75     # 넓은 방열 면적으로 온도 상승 완화
    cooling_factor = 0.10  # 대형 방열판 효과
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

# 4. 시뮬레이션 계산 진행
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

    # 5. 대시보드 결과 리포트
    st.subheader("📊 시뮬레이션 분석 결과")
    
    max_t = f"{max(temp_history):.1f}"
    final_t = f"{temp_history[-1]:.1f}"
    th_t = f"{throttling_time} 분" if throttling_time != -1 else "안전 (미발생)"

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
            <div class="metric-card">
                <p class="metric-label">최고 도달 온도</p>
                <p class="metric-value">{max_t} ℃</p>
            </div>
        ''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''
            <div class="metric-card">
                <p class="metric-label">최종 상태 온도</p>
                <p class="metric-value">{final_t} ℃</p>
            </div>
        ''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''
            <div class="metric-card">
                <p class="metric-label">쓰로틀링 시작</p>
                <p class="metric-value">{th_t}</p>
            </div>
        ''', unsafe_allow_html=True)
    
    # 온도 추이 꺾은선 그래프
    df = pd.DataFrame({
        "시간(분)": range(int(time_usage) + 1),
        "예상 온도(℃)": temp_history,
        "위험 기준선(45℃)": [45.0] * (int(time_usage) + 1)
    })
    df.set_index("시간(분)", inplace=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.line_chart(df, color=["#6366F1", "#F87171"])
    
    # 6. 알림 메시지 및 스마트 쿨링 가이드
    if throttling_time != -1:
        st.error(f"🚨 **경고!** 사용 시작 **{throttling_time}분** 후 {device_type.split()[0]} 온도가 45℃를 초과하여 쓰로틀링(성능 제한)이 작동합니다.")
        
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
    st.error("데이터 처리 중 오류가 발생했습니다. 환경 설정 값을 확인해 주세요.")
