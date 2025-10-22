import streamlit as st
import base64
from pathlib import Path

# --- 1. 페이지 기본 설정 ---
# 이 설정은 앱의 모든 페이지에 적용됩니다. (가장 먼저 호출되어야 함)
st.set_page_config(
    page_title="인터랙티브 생태계 교실",
    page_icon="🌳",
    layout="wide",
)

# --- 2. 전역 한글 폰트 적용 함수 ---
# CSS를 주입하여 Streamlit의 모든 UI 요소(제목, 텍스트, 버튼 등)에
# 나눔고딕 폰트를 적용합니다.
# (Matplotlib 그래프 폰트와는 별개로 UI 자체의 폰트를 설정합니다.)

def inject_nanum_font():
    """
    로컬 fonts/NanumGothic.ttf를 base64로 인라인 임베드하여
    Streamlit 페이지의 모든 텍스트에 적용합니다.
    """
    # 폰트 경로 설정 (main_app.py는 fonts 폴더와 같은 레벨에 있다고 가정)
    font_path = Path(__file__).parent / "fonts" / "NanumGothic.ttf"
    
    if not font_path.exists():
        st.warning(f"폰트 파일을 찾을 수 없습니다: {font_path}")
        st.warning("UI의 한글 폰트가 깨져 보일 수 있습니다.")
        return

    try:
        # 폰트 파일을 base64로 인코딩
        b64 = base64.b64encode(font_path.read_bytes()).decode("utf-8")
        
        # CSS 스타일 정의
        css = f"""
        <style>
        @font-face {{
            font-family: 'NanumGothicLocal';
            src: url('data:font/ttf;base64,{b64}') format('truetype');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
        }}
        
        /* Streamlit의 모든 UI 요소에 폰트 적용 */
        html, body, .stApp, [class*="css"] {{
            font-family: 'NanumGothicLocal', 'NanumGothic', sans-serif !important;
        }}
        
        /* 헤더, 마크다운 텍스트 등에도 명시적으로 적용 */
        h1, h2, h3, h4, h5, h6, .stMarkdown {{
            font-family: 'NanumGothicLocal', 'NanumGothic', sans-serif !important;
        }}
        </style>
        """
        # CSS 주입
        st.markdown(css, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"폰트 주입 중 오류 발생: {e}")

# --- 3. 메인 페이지 UI ---

def main_home_page():
    
    # 1. 폰트 주입 실행
    inject_nanum_font()

    # 2. 메인 타이틀 및 소개
    st.title("🌳 살아있는 생태계 학습 교실 👩‍🔬")
    st.markdown("---")
    
    st.header("이 웹앱은 생태계의 구성 요소와 안정성을 체험하며 배우는 인터랙티브 학습 도구입니다.")
    
    st.info(
        """
        **👈 왼쪽 사이드바에서 학습할 페이지를 선택하세요!**
        
        1.  **[1. 먹이 관계 모형 만들기]**: 직접 생물 카드를 골라 나만의 먹이그물을 만들어봅니다.
        2.  **[2. 생태계 안정성 실험]**: 만든 먹이그물에 충격을 주어 생태 피라미드가 어떻게 변하는지 실험합니다.
        3.  **[3. 모형 완성 확인 및 퀴즈]**: 완성된 모형의 복잡도를 확인하고, 핵심 개념 퀴즈를 풀어봅니다.
        """
    )
    
    st.markdown("---")

    # 3. 앱 구조 안내
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 학습 목표")
        st.markdown(
            """
            - 생물과 비생물 요소를 구분하고, 생태계 구성 요소를 이해합니다.
            - 먹이사슬과 먹이그물의 관계를 파악합니다.
            - 생태 피라미드의 개념을 이해합니다.
            - **먹이그물이 복잡할수록 생태계가 안정적으로 유지됨**을 실험을 통해 깨닫습니다.
            """
        )

    with col2:
        st.subheader("📂 앱 파일 구조 (권장)")
        st.code(
            """
(프로젝트 폴더)/
├── 🏠 streamlit_app.py
│
├── 📁 pages/
│   ├── 📄 1_먹이관계_모형.py (page 1 코드)
│   ├── 📄 2_생태계_안정성_실험.py (page 2 코드)
│   └── 📄 3_개념_퀴즈.py (page 3 코드)
│
└── 📁 fonts/
    └── 📄 NanumGothic.ttf (한글 폰트 파일)
            """,
            language="bash"
        )
        st.caption("※ `pages` 폴더 안의 파일 이름이 사이드바에 표시됩니다.")

# --- 4. 앱 실행 ---
if __name__ == "__main__":
    main_home_page()