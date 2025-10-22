import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import os
from matplotlib import font_manager

# --- matplotlib 한글 폰트 설정 ---
try:
    plt.rcParams['font.family'] = 'Malgun Gothic'
except:
    plt.rcParams['font.family'] = 'sans-serif'
    
plt.rcParams['axes.unicode_minus'] = False # 마이너스 폰트 깨짐 방지
# ---------------------------------

# --- 1. 기본 데이터 (페이지 1의 데이터) ---
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

SIMPLE_ECO = {
    "name": "단순한 먹이사슬",
    "nodes": ["풀/나무", "토끼", "뱀"],
    "edges": [("풀/나무", "토끼"), ("토끼", "뱀")],
    "initial_population": {"풀/나무": 100, "토끼": 50, "뱀": 20},
    "removal_factor": 0.5 
}
SPECIES_EMOJI = {
    "풀/나무": "🌳", "도토리": "🌰", "산수유": "🍒", "메뚜기": "🦗", 
    "토끼": "🐇", "애벌레": "🐛", "다람쥐": "🐿️", "오리": "🦆", 
    "개구리": "🐸", "직박구리": "🐦", "뱀": "🐍", "족제비": "🦦", 
    "여우": "🦊", "매": "🦅"
}

# --- 2. 시뮬레이션 핵심 로직 ---

def run_simulation_step_by_step(ecosystem_data, change_target, change_type, change_value):
    """특정 생물의 개체 수 변화에 따른 생태계 반응을 시뮬레이션합니다."""
    
    G = nx.DiGraph()
    G.add_nodes_from(ecosystem_data["nodes"])
    G.add_edges_from(ecosystem_data["edges"])
    population = ecosystem_data["initial_population"].copy()
    removal_factor = ecosystem_data.get("removal_factor", 0.4) 

    initial_pop_copy = population.copy() 
    simulation_log = [] 

    # 1. 초기 충격 적용
    original_pop = population.get(change_target, 0)
    pop_change_amount = 0
    
    if original_pop == 0:
        simulation_log.append(f"⚠️ **{change_target}**는 이미 0마리입니다. 충격을 줄 수 없습니다.")
        return population, G, initial_pop_copy, simulation_log
        
    if change_type == "제거 (멸종)":
        pop_change_amount = -original_pop
        population[change_target] = 0
        simulation_log.append(f"🔴 **{change_target}** 카드 **제거**! (개체수: {original_pop} → 0)")
    else:
        pop_change = int(original_pop * (change_value / 100))
        population[change_target] = max(0, population[change_target] + pop_change)
        pop_change_amount = population[change_target] - original_pop
        
        if pop_change_amount > 0:
            simulation_log.append(f"🟢 **{change_target}** 개체수 **증가**! ({original_pop} → {population[change_target]})")
        else:
            simulation_log.append(f"🟠 **{change_target}** 개체수 **감소**! ({original_pop} → {population[change_target]})")

    
    # 2. 연쇄 반응 시뮬레이션
    for predator in G.successors(change_target):
        if pop_change_amount < 0: 
            decrease_factor = removal_factor if population[change_target] == 0 else 0.5
            pop_decrease = int(population[predator] * decrease_factor)
            population[predator] -= min(pop_decrease, population.get(predator, 0))
            log_msg = f"📉 **{change_target}**의 먹이 감소로 **{predator}**의 개체수가 **-{pop_decrease} 감소**했어요."
            simulation_log.append(log_msg)
            
    for prey in G.predecessors(change_target):
        if pop_change_amount < 0: 
            increase_factor = removal_factor * 1.5 if population[change_target] == 0 else 0.5
            pop_increase = int(population[prey] * increase_factor)
            population[prey] += pop_increase
            log_msg = f"📈 **{change_target}** 포식자 감소로 **{prey}**의 개체수가 **+{pop_increase} 증가**했어요!"
            simulation_log.append(log_msg)

    return population, G, initial_pop_copy, simulation_log

# --- 3. 피라미드 데이터 계산 함수 ---
def get_trophic_level_populations(population_data):
    """종별 개체수를 영양 단계별 총 개체수로 합산합니다."""
    tl_pops = {tl: 0 for tl in TL_ORDER}
    
    for species, pop in population_data.items():
        if species in ECO_DATA:
            tl = ECO_DATA[species]['tl']
            if tl in tl_pops:
                tl_pops[tl] += pop
                
    return tl_pops

# --- 4. 그래프 시각화 함수 ---

# 4-1. 네트워크 그래프
def draw_ecosystem(G, population, title, initial_pop, fp=None):
    """먹이그물(네트워크)을 시각화하고 개체 수 변화를 색상으로 표현합니다."""
    
    # --- [수정] 그래프 크기 줄이기 (10, 8) -> (5, 4) ---
    fig, ax = plt.subplots(figsize=(5, 4))
    pos = nx.spring_layout(G, seed=42, k=0.5) 

    colors = []
    
    for node in G.nodes:
        if node in initial_pop:
            change = population.get(node, 0) - initial_pop[node]
            if change > 0: colors.append('lightgreen')
            elif change < 0: colors.append('red')
            else: colors.append('skyblue')
        else: colors.append('skyblue')

    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=2000, alpha=0.9) # 노드 크기도 살짝 줄임
    nx.draw_networkx_edges(G, pos, edge_color="gray", arrowsize=20, width=1.5)
    
    labels = {node: f"{SPECIES_EMOJI.get(node, '?')} {node}\n({population.get(node, '?')})" for node in G.nodes}
    
    if fp:
        for n, label in labels.items():
            x, y = pos[n]
            ax.text(x, y, label, fontproperties=fp, fontsize=8, ha='center', va='center') # 폰트 크기 줄임
    else:
        nx.draw_networkx_labels(G, pos, labels, font_size=8) # 폰트 크기 줄임

    ax.set_title(title, fontsize=12, fontproperties=fp) # 제목 폰트 크기 줄임
    ax.axis('off')
    st.pyplot(fig)

# 4-2. 생태 피라미드 그래프
def draw_pyramid(population_data, title, fp=None):
    """영양 단계별 개체수를 바탕으로 생태 피라미드를 시각화합니다."""
    
    tl_pops = get_trophic_level_populations(population_data)
    
    labels = TL_ORDER
    populations = [tl_pops[tl] for tl in labels]
    colors = ['lightgreen', 'yellow', 'orange', 'salmon', 'red']
    y_pos = range(len(labels))

    # --- [수정] 그래프 크기 줄이기 (10, 6) -> (5, 3) ---
    fig, ax = plt.subplots(figsize=(5, 3)) 
    
    bars = ax.barh(y_pos, populations, color=colors, edgecolor='black', align='center', height=0.7)
    
    ax.set_yticks(y_pos, labels=labels, fontproperties=fp, fontsize=9) # 폰트 크기 줄임
    ax.set_xlabel("개체 수", fontproperties=fp, fontsize=9)
    ax.set_title(title, fontsize=12, fontproperties=fp) # 제목 폰트 크기 줄임
    
    for i, (bar, pop) in enumerate(zip(bars, populations)):
        x_val = bar.get_width()
        ax.text(x_val + 3, i, f"{pop}", va='center', ha='left', fontproperties=fp, fontsize=8) # 폰트 크기 줄임

    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    st.pyplot(fig)

    
# --- 5. Streamlit 페이지 구성 ---

def main_simulation_page():
    st.title("🧪 2. 생태계 안정성 실험")
    st.header("특정 생물이 사라지면 생태계는 어떻게 될까요?")

    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts", "NanumGothic.ttf"))
    fp = None
    if os.path.exists(font_path):
        fp = font_manager.FontProperties(fname=font_path)
    elif 'fp_warned' not in st.session_state:
        st.warning("경고: 폰트 파일(NanumGothic.ttf)을 찾을 수 없습니다. 그래프의 한글이 깨질 수 있습니다.")
        st.session_state.fp_warned = True 

    # 데이터 로드
    user_nodes = st.session_state.get('user_nodes', [])
    user_edges = st.session_state.get('user_edges', [])

    if not user_edges:
        st.error("⚠️ 먼저 **[1. 먹이 관계 모형 만들기]** 페이지에서 생물들을 연결해야 실험을 할 수 있어요! 기본 단순 모형으로 시작합니다.")
        selected_eco = SIMPLE_ECO
    else:
        st.success(f"✨ 내가 만든 모형 ({len(user_nodes)}종)으로 실험을 시작합니다!")
        selected_eco = {
            "name": "내가 만든 모형",
            "nodes": user_nodes,
            "edges": user_edges,
            "initial_population": st.session_state.user_pop,
            "removal_factor": 0.4
        }
    
    initial_pop_data = selected_eco['initial_population'].copy()
    G_initial = nx.DiGraph()
    G_initial.add_nodes_from(selected_eco["nodes"])
    G_initial.add_edges_from(selected_eco["edges"])
    G_initial.graph['initial_pop'] = initial_pop_data

    # 세션 상태 초기화
    if 'simulated_pop' not in st.session_state or st.session_state.simulated_pop is None:
        st.session_state.simulated_pop = initial_pop_data.copy()
        st.session_state.initial_pop_at_sim = initial_pop_data.copy()
        st.session_state.is_simulated = False
        st.session_state.simulation_log = []

    
    # --- 사이드바: 충격 입력 ---
    st.sidebar.header("실험 설정: 💣 생태계에 충격 주기")
    
    target_species = st.sidebar.selectbox(
        "⚡️ 충격을 줄 생물 선택:",
        options=selected_eco["nodes"],
        help="이 생물의 개체 수에 변화를 줍니다."
    )
    
    change_type = st.sidebar.radio(
        "💥 어떤 충격을 줄까요?",
        ("제거 (멸종)", "개체 수 변경"),
        horizontal=True
    )
    
    change_value = 0
    if change_type == "개체 수 변경":
        change_value = st.sidebar.slider(
            "변화율 (%)",
            min_value=-100,
            max_value=100,
            value=-50,
            step=10,
            help="-100은 모두 사라짐, 100은 두 배 증가를 의미해요."
        )

    # --- 시뮬레이션 버튼 ---
    if st.sidebar.button("🔬 실험 시작! (시뮬레이션 실행)"):
        with st.spinner('생태계가 반응하는 중...'):
            new_population, G_result, initial_pop_copy, log = run_simulation_step_by_step(
                selected_eco, target_species, change_type, change_value
            )
        st.session_state.simulated_pop = new_population
        st.session_state.initial_pop_at_sim = initial_pop_copy 
        st.session_state.is_simulated = True
        st.session_state.simulation_log = log
        st.success("실험 결과가 나왔어요! 아래를 확인해 보세요.")


    st.markdown("---")
    
    # --- 결과 시각화 및 비교 (네트워크 + 피라미드) ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1️⃣ 실험 전 (초기 상태)")
        st.markdown("---")
        draw_ecosystem(G_initial, initial_pop_data, "실험 전 (먹이그물)", initial_pop_data, fp=fp)
        st.markdown("---")
        draw_pyramid(initial_pop_data, "실험 전 (생태 피라미드)", fp=fp)


    with col2:
        st.subheader("2️⃣ 실험 후 (변화 상태)")
        st.markdown("---")
        if st.session_state.is_simulated:
            draw_ecosystem(G_initial, st.session_state.simulated_pop, "실험 후 (먹이그물)", st.session_state.initial_pop_at_sim, fp=fp)
            st.markdown("---")
            draw_pyramid(st.session_state.simulated_pop, "실험 후 (생태 피라미드)", fp=fp)
        else:
            st.info("좌측에서 충격을 설정하고 '실험 시작!' 버튼을 눌러주세요.")
            # --- [오류 수정] G_T -> G_initial ---
            draw_ecosystem(G_initial, initial_pop_data, "실험 대기 중", initial_pop_data, fp=fp)
            st.markdown("---")
            draw_pyramid(initial_pop_data, "실험 대기 중", fp=fp)

    st.markdown("---")
    
    # --- 변화 상세 로그 및 메트릭 ---
    if st.session_state.is_simulated:
        st.header("🔍 상세 분석: 어떤 생물이 변했을까요?")
        
        with st.expander("📝 충격이 전파되는 과정 (로그 보기)"):
            for step in st.session_state.simulation_log:
                st.markdown(f"- {step}")

        # 메트릭 스크롤 방지를 위해 컬럼 개수 제한 (5개씩)
        nodes_list = selected_eco["nodes"]
        num_nodes = len(nodes_list)
        cols_per_row = 5
        
        for i in range(0, num_nodes, cols_per_row):
            cols = st.columns(cols_per_row)
            for j, node in enumerate(nodes_list[i:i+cols_per_row]):
                initial = st.session_state.initial_pop_at_sim.get(node, 0)
                current = st.session_state.simulated_pop.get(node, 0)
                delta_val = current - initial
                delta_str = f"{'+' if delta_val > 0 else ''}{delta_val}"
                
                with cols[j]:
                    st.metric(
                        label=f"{SPECIES_EMOJI.get(node, '?')} {node}",
                        value=f"{current} 마리",
                        delta=delta_str,
                        delta_color="off" if delta_val == 0 else ("inverse" if delta_val < 0 else "normal")
                    )
        
        st.info("✅ **핵심 발견:** 화살표 연결이 많을수록 (복잡할수록) 한 생물의 충격에 다른 생물들이 덜 피해를 입고 살아남을 수 있어요! 이것이 **안정성**이랍니다.")

if __name__ == "__main__":
    main_simulation_page()