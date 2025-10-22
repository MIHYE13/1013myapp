import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import os  # (수정) 폰트 경로 탐색을 위해 os import 추가
from matplotlib import font_manager  # (수정) 폰트 관리를 위해 font_manager import 추가

# --- matplotlib 한글 폰트 설정 ---
try:
    plt.rcParams['font.family'] = 'Malgun Gothic'
except:
    plt.rcParams['font.family'] = 'sans-serif'
    
plt.rcParams['axes.unicode_minus'] = False # 마이너스 폰트 깨짐 방지
# ---------------------------------

# 페이지 1과 동일한 이모지 및 시각화 함수 사용
SPECIES_EMOJI = {
    "풀/나무": "🌳", "도토리": "🌰", "산수유": "🍒", "메뚜기": "🦗", 
    "토끼": "🐇", "애벌레": "🐛", "다람쥐": "🐿️", "오리": "🦆", 
    "개구리": "🐸", "직박구리": "🐦", "뱀": "🐍", "족제비": "🦦", 
    "여우": "🦊", "매": "🦅"
}

# 페이지 1의 데이터 재정의 (폰트 설정에 필요)
ECO_DATA = {
    "풀/나무": {"emoji": "🌳", "tl": "생산자"}, "도토리": {"emoji": "🌰", "tl": "생산자"},
    "산수유": {"emoji": "🍒", "tl": "생산자"}, "메뚜기": {"emoji": "🦗", "tl": "1차 소비자"},
    "토끼": {"emoji": "🐇", "tl": "1차 소비자"}, "애벌레": {"emoji": "🐛", "tl": "1차 소비자"},
    "다람쥐": {"emoji": "🐿️", "tl": "1차 소비자"}, "오리": {"emoji": "🦆", "tl": "2차 소비자"}, 
    "개구리": {"emoji": "🐸", "tl": "2차 소비자"}, "직박구리": {"emoji": "🐦", "tl": "2차 소비자"},
    "뱀": {"emoji": "🐍", "tl": "3차 소비자"}, "족제비": {"emoji": "🦦", "tl": "3차 소비자"}, 
    "여우": {"emoji": "🦊", "tl": "3차 소비자"}, "매": {"emoji": "🦅", "tl": "최종 소비자"}
}

def draw_final_ecosystem(nodes, edges, title):
    if not nodes:
        return

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42, k=0.5) 
    
    # 노드 색상: 영양 단계별로 다르게 설정
    color_map = {"생산자": 'lightgreen', "1차 소비자": 'yellow', "2차 소비자": 'orange', "3차 소비자": 'salmon', "최종 소비자": 'red'}
    colors = [color_map.get(ECO_DATA.get(node, {}).get('tl'), 'skyblue') for node in nodes]

    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=4000, alpha=0.9)
    nx.draw_networkx_edges(G, pos, edge_color="gray", arrowsize=30, width=2)
    
    labels = {node: f"{SPECIES_EMOJI.get(node, '?')} {node}" for node in nodes if node in ECO_DATA}

    # --- (수정 1) 폰트 경로 및 fp 초기화 ---
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts", "NanumGothic.ttf"))
    fp = None
    
    if os.path.exists(font_path):
        fp = font_manager.FontProperties(fname=font_path)
        for n, label in labels.items():
            x, y = pos[n]
            # --- (수정 2) 라벨을 ax.text로 직접 그리기 (기존 nx.draw_networkx_labels 대체) ---
            ax.text(x, y, label, fontproperties=fp, fontsize=12, ha='center', va='center')
    else:
        # 폰트가 없을 경우 기본 라벨 함수 사용
        nx.draw_networkx_labels(G, pos, labels, font_size=12)
        if 'fp_warned_p3' not in st.session_state: # 3페이지 경고 중복 방지
             st.warning("경고: 폰트 파일(NanumGothic.ttf)을 찾을 수 없습니다. 그래프의 한글이 깨질 수 있습니다.")
             st.session_state.fp_warned_p3 = True

    # --- (수정 3) 제목에도 폰트 속성 적용 ---
    ax.set_title(title, fontsize=15, fontproperties=fp)
    
    ax.axis('off')
    st.pyplot(fig)

# --- Streamlit 페이지 구성 ---
st.title("💯 3. 모형 완성 확인 및 개념 퀴즈")
st.header("내가 만든 생태계가 얼마나 튼튼할까요?")

# 사용자 정의 모형 로드
user_nodes = st.session_state.get('user_nodes', [])
user_edges = st.session_state.get('user_edges', [])

if user_edges:
    st.subheader(f"✨ 내가 만든 최종 모형 ({len(user_nodes)} 종, {len(user_edges)} 관계)")
    draw_final_ecosystem(user_nodes, user_edges, "최종 사용자 정의 먹이그물 모형")
    
    # 복잡도 계산
    stability_score = len(user_edges) / len(user_nodes) if len(user_nodes) > 0 else 0
    
    st.markdown("---")
    st.subheader("📊 모형 복잡도 점수")
    
    # 복잡도 게이지 시각화 (간단한 bar chart 사용)
    score_level = max(0, min(2, stability_score))
    st.progress(score_level / 2.0, text=f"복잡도 점수: {stability_score:.2f}")

    if stability_score > 1.5:
        st.success(f"🥳 아주 좋아요! 연결이 많은 **복잡한 먹이그물**이에요! 생태계가 튼튼해요.")
    elif stability_score < 1.0:
        st.error(f"⚠️ 연결이 적은 **단순한 먹이사슬**에 가까워요. 충격에 약할 수 있어요.")
    else:
        st.warning(f"🤔 중간 복잡도입니다. 연결을 더 늘려볼까요?")
    
    st.markdown("---")
    st.header("🧠 핵심 개념 퀴즈!")
    
    # --- 퀴즈 1: 먹이사슬 vs 먹이그물 ---
    q1 = st.radio(
        "**문제 1:** 하나의 생물이 사라졌을 때, 다른 먹이를 찾아 덜 위험한 것은 무엇인가요?",
        ["1. 먹이사슬", "2. 먹이그물"],
        key="quiz1"
    )
    if st.button("문제 1 정답 확인", key="check1"):
        if q1 == "2. 먹이그물":
            st.success("딩동댕! 🎶 먹이그물은 복잡하게 연결되어 충격에 강해요!")
        else:
            st.error("앗! 먹이 사슬은 연결이 끊어지기 쉬워요. 먹이그물이 정답!")

    # --- 퀴즈 2: 안정성 원리 ---
    q2 = st.radio(
        "**문제 2:** 생태계가 안정적으로 유지되기 위해서는 먹이 관계가 어떻게 되어야 할까요?",
        ["1. 단순하게 연결되어야 한다.", "2. 복잡하게 얽혀 있어야 한다."],
        key="quiz2"
    )
    if st.button("문제 2 정답 확인", key="check2"):
        if q2 == "2. 복잡하게 얽혀 있어야 한다.":
            st.success("정답! 🌟 복잡할수록 튼튼하답니다!")
        else:
            st.error("다시 한번 생각해봐요. 복잡한 관계가 충격에 더 강해요!")

    st.markdown("---")
    st.info("🎉 모든 학습을 마쳤어요! **'먹이그물이 복잡할수록 생태계는 안정적이다'**라는 점을 꼭 기억하세요!")
    
else:
    st.warning("⚠️ 페이지 1에서 '먹이 관계 모형 만들기'를 먼저 진행하고 오세요!")