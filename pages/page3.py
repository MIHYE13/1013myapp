import streamlit as st
from utils.fonts import inject_nanum_font

# 웹 폰트 주입 (브라우저 렌더링용)
inject_nanum_font()
import networkx as nx
import matplotlib.pyplot as plt

# 페이지 1과 동일한 이모지 및 시각화 함수 사용
SPECIES_EMOJI = {
    "풀/나무": "🌳", "도토리": "🌰", "애벌레": "🐛", "토끼": "🐇", 
    "다람쥐": "🐿️", "개구리": "🐸", "직박구리": "🐦", "뱀": "🐍", 
    "족제비": "🦦", "매": "🦅"
}

def draw_final_ecosystem(nodes, edges, title):
    if not nodes:
        return

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42, k=0.5) 
    
    colors = ['green' if any(s in node for s in ["풀", "도토리"]) else 'skyblue' for node in nodes]

    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=4000, alpha=0.9)
    nx.draw_networkx_edges(G, pos, edge_color="gray", arrowsize=30, width=2)
    
    labels = {node: f"{SPECIES_EMOJI.get(node, '?')} {node}" for node in nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=12, font_family="NanumGothic")

    ax.set_title(title, fontsize=15)
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
    
    if stability_score > 1.5:
         st.balloons()
         st.success(f"🥳 축하해요! 연결이 많은 **복잡한 먹이그물**이에요! (복잡도 점수: {stability_score:.2f})")
    elif stability_score < 1.0:
         st.error(f"⚠️ 연결이 적은 **단순한 먹이사슬**에 가까워요. (복잡도 점수: {stability_score:.2f})")
    else:
         st.warning(f"🤔 중간 복잡도입니다. (복잡도 점수: {stability_score:.2f})")
    
    st.markdown("---")
    st.header("🧠 핵심 개념 퀴즈!")
    
    # --- 퀴즈 1: 먹이사슬 vs 먹이그물 ---
    q1 = st.radio(
        "**문제 1:** 하나의 생물이 사라졌을 때, 다른 먹이를 찾아 덜 위험한 것은 무엇인가요?",
        ["1. 먹이사슬", "2. 먹이그물"],
        key="quiz1"
    )
    if st.button("문제 1 정답 확인"):
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
    if st.button("문제 2 정답 확인"):
        if q2 == "2. 복잡하게 얽혀 있어야 한다.":
            st.success("정답! 🌟 복잡할수록 튼튼하답니다!")
        else:
            st.error("다시 한번 생각해봐요. 복잡한 관계가 충격에 더 강해요!")

    st.markdown("---")
    st.info("🎉 모든 학습을 마쳤어요! **'먹이그물이 복잡할수록 생태계는 안정적이다'**라는 점을 꼭 기억하세요!")
    
else:
    st.warning("⚠️ 페이지 1에서 '먹이 관계 모형 만들기'를 먼저 진행하고 오세요!")
