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

def draw_current_ecosystem(nodes, edges, title):
    """현재 구성된 먹이 관계를 시각화합니다."""
    
    if not nodes:
        st.info("🎨 모형을 만들기 위해 아래에서 생물을 추가해주세요.")
        return

    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    # --- [수정] 그래프 크기 줄이기 (10, 8) -> (5, 4) ---
    fig, ax = plt.subplots(figsize=(5, 4))
    pos = nx.spring_layout(G, seed=42, k=0.5) 
    
    # 노드 색상: 영양 단계별로 다르게 설정
    color_map = {"생산자": 'lightgreen', "1차 소비자": 'yellow', "2차 소비자": 'orange', "3차 소비자": 'salmon', "최종 소비자": 'red'}
    colors = [color_map.get(ECO_DATA.get(node, {}).get('tl'), 'skyblue') for node in nodes]
    
    # 노드 라벨: 이모지 + 이름
    labels = {node: f"{ECO_DATA[node]['emoji']} {node}" for node in nodes if node in ECO_DATA}

    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=2000, alpha=0.9) # 노드 크기 줄임
    nx.draw_networkx_edges(G, pos, edge_color="gray", arrowsize=20, width=1.5) # 화살표/선 크기 줄임
    
    # 서버측 이미지 렌더링에서 한글을 보이게 하기 위해 로컬 TTF를 FontProperties로 직접 사용
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts", "NanumGothic.ttf"))
    
    fp = None 
    
    if os.path.exists(font_path):
        fp = font_manager.FontProperties(fname=font_path)
        for n, label in labels.items():
            x, y = pos[n]
            ax.text(x, y, label, fontproperties=fp, fontsize=8, ha='center', va='center') # 폰트 크기 줄임
    else:
        nx.draw_networkx_labels(G, pos, labels, font_size=8) # 폰트 크기 줄임
        if 'fp_warned_p1' not in st.session_state: # 경고 중복 방지
            st.warning("경고: 폰트 파일(NanumGothic.ttf)을 찾을 수 없습니다. 그래프의 한글이 깨질 수 있습니다.")
            st.session_state.fp_warned_p1 = True

    ax.set_title(title, fontsize=12, fontproperties=fp) # 제목 폰트 크기 줄임
    
    ax.axis('off')
    st.pyplot(fig)


def check_for_full_chain(G):
    """생산자 -> 1차 -> 2차 -> 최종 소비자의 완전한 체인이 있는지 확인합니다."""
    
    # 1. 각 영양 단계의 노드 그룹화
    tl_nodes = {tl: [] for tl in TL_ORDER}
    for node in G.nodes:
        if node in ECO_DATA:
            tl = ECO_DATA[node]['tl']
            if tl in tl_nodes:
                tl_nodes[tl].append(node)
                
    # 2. 필수 영양 단계가 모두 존재하는지 확인 (생산자, 1차, 2차, 최종)
    if not (tl_nodes["생산자"] and tl_nodes["1차 소비자"] and tl_nodes["2차 소비자"] and tl_nodes["최종 소비자"]):
        return False

    # 3. NetworkX를 이용해 경로 탐색 (BFS/DFS)
    for p_node in tl_nodes["생산자"]:
        for c1_node in tl_nodes["1차 소비자"]:
            if G.has_edge(p_node, c1_node): # P -> 1C
                for c2_node in tl_nodes["2차 소비자"]:
                    if G.has_edge(c1_node, c2_node): # 1C -> 2C
                        for fc_node in tl_nodes["최종 소비자"]:
                            if G.has_edge(c2_node, fc_node): # 2C -> FC
                                return True # 완전한 체인 발견!
    return False

# --- 4. Streamlit 페이지 구성 ---

st.title("🧱 1. 먹이 관계 모형 만들기 (연결 체험)")
st.header("생물 카드를 골라 먹이 관계를 연결해 봐요!")
st.caption("초식동물(1차)은 식물(생산자)을, 육식동물(2차 이상)은 다른 동물을 먹는답니다.")

st.markdown("---")

# 리셋 버튼
if st.button("🔄 모형 초기화 (다시 하기)"):
    reset_model()
    st.rerun() # 초기화 후 페이지를 새로고침하여 상태를 반영

# --- 1단계: 생물 (노드) 추가 (영양 단계별 도식화) ---
st.subheader("1단계: 🐾 생물 친구들 추가하기 (영양 단계별)")

cols_tl = st.columns(5)
tl_selection_map = {}

for i, tl in enumerate(TL_ORDER):
    with cols_tl[i]:
        st.markdown(f"**{TL_MAP_KOR[tl]}**")
        
        # 현재 단계에 해당하는 생물 목록 생성
        available_in_tl = [
            f"{ECO_DATA[name]['emoji']} {name}" for name in st.session_state.available_species
            if name in ECO_DATA and ECO_DATA[name]['tl'] == tl
        ]
        
        # 이미 추가된 생물 목록 (색상으로 표시)
        added_in_tl = [
            f"✅ {ECO_DATA[name]['emoji']} {name}" for name in st.session_state.user_nodes
            if name in ECO_DATA and ECO_DATA[name]['tl'] == tl
        ]
        
        # 추가된 생물이 있다면 표시
        if added_in_tl:
            st.markdown("\n".join(added_in_tl))
        else:
            st.markdown("_추가된 생물 없음_")
            
        # 선택 박스 (추가할 생물만)
        if available_in_tl:
            tl_selection_map[tl] = st.selectbox(
                f"추가할 {tl} 선택:",
                options=['선택 안함'] + available_in_tl,
                key=f"select_tl_{i}"
            )
        else:
            st.markdown("_이 단계의 생물 모두 추가 완료_")


if st.button("➕ 선택한 생물들 생태계에 추가하기", key="add_selected_species"):
    newly_added_count = 0
    for tl, selection in tl_selection_map.items():
        if selection and selection != '선택 안함':
            # '도토리'처럼 이름에 공백이 없는 경우 [1] 인덱스가 오류나므로 수정
            clean_name = " ".join(selection.split(' ')[1:])
            
            if clean_name not in st.session_state.user_nodes:
                st.session_state.user_nodes.append(clean_name)
                st.session_state.user_pop[clean_name] = INITIAL_POP
                if clean_name in st.session_state.available_species:
                    st.session_state.available_species.remove(clean_name)
                newly_added_count += 1
                
    if newly_added_count > 0:
        st.success(f"카드 {newly_added_count}개 추가 완료! 이제 연결해 보세요.")
    else:
        st.info("새로 추가된 생물이 없거나 '선택 안함'으로 설정되었습니다.")

st.markdown("---")

# --- 2단계: 먹이 관계 (화살표) 연결 ---
st.subheader("2단계: 🔗 먹이 관계 연결하기")
st.caption("**먹이가 되는 생물** → **먹는 생물** 순서로 화살표를 이어주세요! (화살표는 먹는 방향으로!)")

col_prey, col_predator, col_button = st.columns([1, 1, 0.5])

# 현재 노드 목록 (순수 이름)
node_options = st.session_state.user_nodes or ["생물을 먼저 추가하세요"]

with col_prey:
    prey = st.selectbox("🍚 먹이 (화살표 꼬리):", options=node_options, key="select_prey")
with col_predator:
    predator = st.selectbox("🍽️ 포식자 (화살표 머리):", options=node_options, key="select_predator")

with col_button:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➡️ 연결하기"):
        if len(node_options) < 2:
            st.error("생물이 두 종류 이상 있어야 연결할 수 있어요!")
        elif prey == predator:
            st.error("같은 생물을 먹을 수는 없어요! 다시 골라봐.")
        elif (prey, predator) in st.session_state.user_edges:
            st.warning("이미 연결된 관계입니다.")
        elif prey in st.session_state.user_nodes and predator in st.session_state.user_nodes:
            st.session_state.user_edges.append((prey, predator))
            st.success(f"**'{prey}'** → **'{predator}'** 관계 완성! 👍")
            
            # 완전한 체인 검사 및 풍선 효과 발동
            if not st.session_state.is_chain_completed:
                G_temp = nx.DiGraph()
                G_temp.add_nodes_from(st.session_state.user_nodes) # (수정) 노드 추가
                G_temp.add_edges_from(st.session_state.user_edges)
                if check_for_full_chain(G_temp):
                    st.session_state.is_chain_completed = True
                    st.balloons()
                    st.success("🎉 축하해요! 생산자부터 최종 소비자까지 이어지는 완전한 **먹이사슬**을 처음 완성했어요!")
        else:
            st.error("생물을 먼저 추가하거나 올바른 생물을 선택해주세요.")

st.markdown("---")

# --- 3단계: 모형 시각화 ---
st.header("👀 내가 만든 먹이 모형")
draw_current_ecosystem(st.session_state.user_nodes, st.session_state.user_edges, "모형 시각화 (색깔은 영양 단계를 나타냅니다)")

# --- 4단계: 설명글 추가 ---
st.markdown("---")
st.header("📝 먹이그물이란 무엇일까요?")
st.markdown("""
먹이그물은 **여러 개의 먹이사슬이 복잡하게 얽혀서 그물 모양**을 이루고 있는 것을 말해요. 

우리가 만든 모형처럼, 하나의 생물(예: 토끼)을 여러 포식자(예: 뱀, 여우)가 먹거나, 하나의 포식자(예: 매)가 여러 먹이(예: 뱀, 직박구리)를 먹을 때 먹이사슬이 겹치면서 복잡한 먹이그물이 탄생해요.

**먹이그물이 복잡할수록 생태계는 더 튼튼하고 안정적이랍니다!**
""")


if st.session_state.user_edges:
    st.markdown("---")
    st.info("✅ 먹이 모형 구성 완료! 이제 **[2. 생태계 안정성 실험]** 페이지로 가서 실험해 봅시다!")

# (여기서부터 시작된 모든 추가 코드를 삭제했습니다.)