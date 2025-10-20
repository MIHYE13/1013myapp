import streamlit as st
from utils.fonts import inject_nanum_font

# 웹 폰트 주입 (브라우저 렌더링용)
inject_nanum_font()
import networkx as nx
import matplotlib.pyplot as plt

# --- 공통 데이터 및 초기화 ---
# 초등학생 눈높이에 맞춰 이모지 사용
SPECIES_EMOJI = {
    "풀/나무": "🌳", "도토리": "🌰", "애벌레": "🐛", "토끼": "🐇", 
    "다람쥐": "🐿️", "개구리": "🐸", "직박구리": "🐦", "뱀": "🐍", 
    "족제비": "🦦", "매": "🦅"
}
# 이모지 + 이름 형식으로 사용자에게 보여줄 목록
ALL_SPECIES_DISPLAY = [
    "🌳 풀/나무 (생산자)", "🌰 도토리 (생산자)", "🐛 애벌레", "🐇 토끼", 
    "🐿️ 다람쥐", "🐸 개구리", "🐦 직박구리", "🐍 뱀", 
    "🦦 족제비", "🦅 매"
]
INITIAL_POP = 50 

if 'user_nodes' not in st.session_state:
    st.session_state.user_nodes = [] # ['토끼', '뱀'] 순수 이름 저장
    st.session_state.user_edges = [] # [('토끼', '뱀')] 순수 이름 저장
    st.session_state.user_pop = {}
    st.session_state.available_species_display = ALL_SPECIES_DISPLAY.copy()

# --- 그래프 시각화 함수 ---
def draw_current_ecosystem(nodes, edges, title):
    """현재 구성된 먹이 관계를 시각화합니다."""
    
    if not nodes:
        st.info("🎨 모형을 만들기 위해 아래에서 생물을 추가해주세요.")
        return

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42, k=0.5) 
    
    # 노드 색상: 생산자(green)와 소비자(skyblue) 구분
    colors = ['green' if any(s in node for s in ["풀", "도토리"]) else 'skyblue' for node in nodes]
    
    # 노드 라벨: 이모지 + 이름
    labels = {node: f"{SPECIES_EMOJI.get(node, '?')} {node}" for node in nodes}

    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=4000, alpha=0.9)
    nx.draw_networkx_edges(G, pos, edge_color="gray", arrowsize=30, width=2)
    nx.draw_networkx_labels(G, pos, labels, font_size=12, font_family="Malgun Gothic")

    ax.set_title(title, fontsize=15)
    ax.axis('off')
    st.pyplot(fig)


# --- Streamlit 페이지 구성 ---
st.title("🧱 1. 먹이 관계 모형 만들기 (Drag & Drop 체험)")
st.header("생물 카드를 골라 먹이 관계를 연결해 봐요!")

st.markdown("---")

col_add, col_connect = st.columns(2)

# --- 1단계: 생물 (노드) 추가 ---
with col_add:
    st.subheader("1단계: 🐾 생물 친구들 추가하기")
    st.caption("아래 목록에서 생물을 골라 '추가' 버튼을 눌러주세요.")
    
    species_to_add_display = st.selectbox(
        "✨ 추가할 생물 카드 선택:",
        options=st.session_state.available_species_display,
        key="select_node_add"
    )
    
    if st.button("➕ 생태계에 추가하기"):
        if species_to_add_display:
            clean_name = species_to_add_display.split(' ')[1] # 예: 토끼
            if clean_name.startswith('('): # (생산자) 태그 제거
                clean_name = clean_name.split('(')[0].strip()
            
            if clean_name not in st.session_state.user_nodes:
                st.session_state.user_nodes.append(clean_name)
                st.session_state.user_pop[clean_name] = INITIAL_POP
                st.session_state.available_species_display.remove(species_to_add_display)
                st.balloons()
                st.success(f"'{clean_name}' 카드 추가 완료! 이제 연결해 볼까요?")
            else:
                st.warning("이미 이 생물은 추가되었어요! 다른 생물을 골라봐.")

# --- 2단계: 먹이 관계 (화살표) 연결 ---
with col_connect:
    st.subheader("2단계: 🔗 먹이 관계 연결하기")
    st.caption("먹이가 되는 생물 → 먹는 생물 순서로 화살표를 이어주세요!")
    
    # 현재 노드 목록 (순수 이름)
    node_options = st.session_state.user_nodes or ["생물을 먼저 추가하세요"]

    prey = st.selectbox("🍚 먹이 (화살표 꼬리):", options=node_options, key="select_prey")
    predator = st.selectbox("🍽️ 포식자 (화살표 머리):", options=node_options, key="select_predator")

    if st.button("➡️ 화살표 연결 (관계 만들기)"):
        if len(node_options) < 2:
            st.error("생물이 두 종류 이상 있어야 연결할 수 있어요!")
        elif prey == predator:
            st.error("같은 생물을 먹을 수는 없어요! 다시 골라봐.")
        elif (prey, predator) in st.session_state.user_edges:
            st.warning("이미 연결된 관계입니다.")
        elif prey in st.session_state.user_nodes and predator in st.session_state.user_nodes:
            st.session_state.user_edges.append((prey, predator))
            st.success(f"**'{prey}'** → **'{predator}'** 관계 완성! 👍")
        else:
            st.error("생물을 먼저 추가하거나 올바른 생물을 선택해주세요.")

st.markdown("---")
st.header("👀 내가 만든 먹이 모형")
col_chart, col_list = st.columns([2, 1])

with col_chart:
    draw_current_ecosystem(st.session_state.user_nodes, st.session_state.user_edges, "모형 시각화")

with col_list:
    st.subheader("📋 현재 생물 목록")
    if st.session_state.user_nodes:
        node_data = [{"생물": node, "초기 개체 수": st.session_state.user_pop.get(node)} for node in st.session_state.user_nodes]
        st.dataframe(node_data, hide_index=True)

    st.subheader("🔗 현재 관계 목록")
    if st.session_state.user_edges:
        edge_data = [{"먹이 (꼬리)": edge[0], "포식자 (머리)": edge[1]} for edge in st.session_state.user_edges]
        st.dataframe(edge_data, hide_index=True)
    else:
        st.info("생물 친구들을 추가하고 화살표로 연결해보세요!")


if st.session_state.user_edges:
    st.markdown("---")
    st.success("✅ 먹이 모형 구성 완료! **[2. 생태계 안정성 실험]** 페이지로 가서 실험해 봅시다!")
