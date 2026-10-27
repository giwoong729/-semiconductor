import streamlit as st
import pandas as pd

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
st.markdown('<p class="sub-header">스마트폰 사용 환경에 따른 반도체 발열과 성능 저하 시점을 실시간으로 예측합니다.</p>', unsafe_allow_html=True)

# 2. 사이드바 디자인 (값 변경 시 즉시 반영)
with st.sidebar:
    st.header("⚙️ 환경 설정")
    st.divider()
    temp_env = st.slider("현재 주변 온도 (℃)", min_value=-10.0, max_value=40.0, value=25.0, step=1.0)
    time_usage = st.slider("예상 사용 시간 (분)", min_value=10, max_value=300, value=60, step=10)
    app_type = st.radio("실행할 앱 종류", ["단순 웹서핑 🌐", "고화질 동영상 시청 🎬", "3D 고사양 게임 🎮"])
    
    st.divider()
    st.info("💡 사이드바의 설정을 변경하면 오른쪽 결과 그래프가 실시간으로 업데이트됩니다.")

# 앱 종류에 따른 기본 발열량 설정
if "웹서핑" in app_type:
    base_increase = 0.9
elif "동영상" in app_type:
    base_increase = 1.5
else:
    base_increase = 2.5

# 3. 실시간 알고리즘 시뮬레이션 (버튼 없이 즉시 실행)
current_temp = temp_env
temp_history = [current_temp]
throttling_time = -1

try:
    for minute in range(1, int(time_usage) + 1):
        # 45도 이상 달성 시 AP 쓰로틀링(발열 제어) 작동으로 발열량 급감 메커니즘 반영
        if current_temp >= 45.0:
            effective_increase = base_increase * 0.4  # 발열량 60% 감소
            if throttling_time == -1:
                throttling_time = minute
        else:
            effective_increase = base_increase

        # 자연 냉각 효과 (온도가 높아질수록 방열량 증가)
        cooling_effect = (current_temp - temp_env) * 0.08
        current_temp = current_temp + effective_increase - cooling_effect
        
        # 실제 모바일 AP의 물리적 한계 온도 캡 적용 (최대 약 58도)
        if current_temp > 58.0:
            current_temp = 58.0
            
        temp_history.append(current_temp)

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
    st.line_chart(df, color=["#3B82F6", "#EF4444"])
    
    # 경고 메시지 및 앱별 맞춤형 쿨링 가이드
    if throttling_time != -1:
        warning_msg = "🚨 **경고!** 사용 시작 **" + str(throttling_time) + "분** 후 스마트폰 온도가 45℃를 초과하여 쓰로틀링(성능 제한)이 시작됩니다."
        st.error(warning_msg)
        
        with st.expander("❄️ 앱별 맞춤형 쿨링 및 발열 관리 가이드", expanded=True):
            if "웹서핑" in app_type:
                st.markdown("""
                **🌐 웹서핑 맞춤형 발열 대처법:**
                * **백그라운드 탭 정리:** 브라우저에 열려 있는 수많은 탭을 닫아 메모리(RAM) 및 AP 연산 부하를 줄입니다.
                * **다크 모드 활성화:** 디스플레이 전력 소모를 줄여 추가적인 내부 발열을 예방합니다.
                * **광고 차단 기능 사용:** 웹 페이지의 과도한 리소스 소모 및 동영상 광고 로딩을 원천 차단합니다.
                """)
            elif "동영상" in app_type:
                st.markdown("""
                **🎬 동영상 시청 맞춤형 발열 대처법:**
                * **재생 해상도 조절:** 4K 고해상도 대신 1080p(FHD) 이하로 변경하여 디코딩 반도체의 부담을 낮춥니다.
                * **다운로드 후 감상:** 고화질 스트리밍 시 통신 모뎀 칩셋 발열이 심해지므로 미리 받아서 재생합니다.
                * **화면 밝기 조절:** 화면 디스플레이 발열 비중이 매우 크므로 자동 밝기를 켜거나 수동으로 조절합니다.
                """)
            else: # 3D 게임
                st.markdown("""
                **🎮 3D 고사양 게임 맞춤형 발열 대처법:**
                * **프레임 제한 설정:** 게임 내 옵션에서 60fps/120fps 대신 30fps로 낮춰 GPU 연산 부하를 크게 줄입니다.
                * **충전 중 게임 절대 금지:** 충전 IC 부품 발열과 AP 발열이 중첩되므로 충전기를 뺀 상태로 플레이합니다.
                * **스마트폰 쿨러 활용:** 기기 뒷면에 붙이는 펠티어 외장 쿨러나 쿨링 팬을 활용해 물리적으로 열을 빼냅니다.
                * **케이스 탈거:** 방열을 방해하는 두꺼운 케이스를 벗겨줍니다.
                """)
            st.caption("⚠️ **공통 주의사항:** 급격히 식히기 위해 냉장고나 얼음팩에 두면 기기 내부 결로 현상으로 부품이 부식되어 고장 납니다.")
    else:
        st.success("✨ **안정적인 상태입니다.** 설정하신 시간 동안 성능 저하 없이 쾌적하게 기기를 사용할 수 있습니다.")

except Exception as e:
    st.error("데이터 처리 중 오류가 발생했습니다. 환경 설정 값을 다시 확인해 주세요.")
