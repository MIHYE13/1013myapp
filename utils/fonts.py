import streamlit as st
import os
import base64


def inject_nanum_font():
    """로컬 `fonts/NanumGothic.ttf` 파일을 base64로 임베드해 @font-face로 등록합니다.
    파일이 없으면 Google Fonts를 사용하도록 폴백합니다.
    이 함수를 페이지 최상단에서 호출하면 Streamlit 앱의 모든 텍스트(브라우저 렌더링 영역 포함)에 적용됩니다.
    """
    # 로컬 폰트 경로 (프로젝트 루트의 fonts 디렉토리)
    local_font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts", "NanumGothic.ttf")

    if os.path.exists(local_font_path):
        try:
            with open(local_font_path, "rb") as f:
                font_data = f.read()
            b64_font = base64.b64encode(font_data).decode()
            css = f"""
            <style>
            @font-face {{
                font-family: 'NanumGothicLocal';
                src: url(data:font/ttf;base64,{b64_font}) format('truetype');
                font-weight: 400 700;
                font-style: normal;
                font-display: swap;
            }}
            html, body, [data-testid="stAppViewContainer"] {{
                font-family: 'NanumGothicLocal', 'Nanum Gothic', sans-serif !important;
            }}
            /* 위젯 및 입력 요소 커버 */
            .stText, .stMarkdown, .streamlit-expanderHeader, .stMarkdown p, .stButton button,
            button, label, input, select, option, textarea, .stSelectbox, .stFileUploader,
            .css-1d391kg, .css-1ps3b9p {{
                font-family: 'NanumGothicLocal', 'Nanum Gothic', sans-serif !important;
            }}
            </style>
            """
            st.markdown(css, unsafe_allow_html=True)
            return
        except Exception as e:
            # 실패하면 폴백으로 Google Fonts 사용
            print(f"로컬 폰트 임베드 실패: {e}")

    # Google Fonts 폴백
    css = """
    <link href="https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700&display=swap" rel="stylesheet">
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Nanum Gothic', 'NanumGothic', sans-serif !important;
    }
    .stText, .stMarkdown, .streamlit-expanderHeader, .stMarkdown p, .stButton button,
    button, label, input, select, option, textarea, .stSelectbox, .stFileUploader,
    .css-1d391kg, .css-1ps3b9p {
        font-family: 'Nanum Gothic', 'NanumGothic', sans-serif !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
