import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import os
from matplotlib import font_manager

# --- matplotlib 한글 폰트 설정 ---
# 시스템에 맑은 고딕(Malgun Gothic)이 있는 경우 사용하거나, 
# 없다면 기본 sans-serif 폰트 중 한글을 지원하는 폰트를 사용하도록 설정
try:
    # 윈도우 사용자에게 가장 흔한 폰트
    plt.rcParams['font.family'] = 'Malgun Gothic'
except:
    # 맑은 고딕이 없는 경우 (예: 리눅스/맥 환경) 대비
    plt.rcParams['font.family'] = 'sans-serif'
    
plt.rcParams['axes.unicode_minus'] = False # 마이너스 폰트 깨짐 방지
# ---------------------------------

# --- 1. 공통 데이터 및 초기화 ---

# 14종의 생물 데이터 (생물, 이모지, 영양 단계)
ECO_DATA = {
    "풀/나무": {"emoji": "🌳", "tl": "생산자"}, "도토리": {"emoji": "🌰", "tl": "생산자"},
    "산수유": {"emoji": "🍒", "tl": "생산자"}, "메뚜기": {"emoji": "🦗", "tl": "1차 소비자"},
    "토끼": {"emoji": "🐇", "tl": "1차 소비자"}, "애벌레": {"emoji": "🐛", "tl": "1차 소비자"},
    "다람쥐": {"emoji": "🐿️", "tl": "1차 소비자"}, "오리": {"emoji": "🦆", "tl": "2차 소비자"}, 
    "개구리": {"emoji": "🐸", "tl": "2차 소비자"}, "직박구리": {"emoji": "🐦", "tl": "2차 소비자"},
    "뱀": {"emoji": "🐍", "tl": "3차 소비자"}, "족제비": {"emoji": "🦦", "tl": "3차 소비자"}, 
    "여우": {"emoji": "🦊", "tl": "3차 소비자"}, "매": {"emoji": "🦅", "tl": "최종 소비자"}
}

TL_ORDER = ["생산자", "1차 소비자", "2차 소비자", "3차 소비자", "최종 소비자"]
TL_MAP_KOR = {
    "생산자": "🌿 생산자", "1차 소비자": "🥕 1차 소비자", 
    "2차 소비자": "🐸 2차 소비자", "3차 소비자": "🐍 3차 소비자", 
    "최종 소비자": "👑 최종 소비자"
}
INITIAL_POP = 50 

# --- 2. 상태 초기화 및 리셋 함수 ---

def reset_model():
    """모형 구성을 초기화합니다."""
    st.session_state.user_nodes = [] 
    st.session_state.user_edges = []
    st.session_state.user_pop = {}
    st.session_state.is_chain_completed = False # 풍선 플래그 리셋
    st.session_state.available_species = list(ECO_DATA.keys())

if 'user_nodes' not in st.session_state:
    # 초기화 시 메시지를 표시하기 위해 초기화 함수 대신 직접 로직 실행
    st.session_state.user_nodes = [] 
    st.session_state.user_edges = []
    st.session_state.user_pop = {}
    st.session_state.is_chain_completed = False 
    st.session_state.available_species = list(ECO_DATA.keys())

# --- 3. 시각화 및 검증 로직 ---

def draw_current_