import streamlit as st
from utils.fonts import inject_nanum_font

# 웹 폰트 주입 (브라우저 렌더링용)
inject_nanum_font()
import networkx as nx
import matplotlib.pyplot as plt

# --- 1. 기본 데이터 (페이지 1의 데이터를 사용하므로 기본 데이터는 참고용으로만 남김) ---
SIMPLE_ECO = {
    "name": "단순한 먹이사슬",
    "nodes": ["토끼", "뱀"],
    "edges": [("토끼", "뱀")],
    "initial_population": {"토끼": 50, "뱀": 20},
    "removal_factor": 0.5 
}
SPECIES_EMOJI = {
    "풀/나무": "🌳", "도토리": "🌰", "애벌레": "🐛", "토끼": "🐇", 
    "다람쥐": "🐿️", "개구리": "🐸", "직박구리": "🐦", "뱀": "🐍", 
    "족제비": "🦦", "매": "🦅"
}

# --- 2. 시뮬레이션 핵심 로직 ---

def run_simulation_step_by_step(ecosystem_data, change_target, change_type, change_value):
    """특정 생물의 개체 수 변화에 따른 생태계 반응을 시뮬레이션합니다."""
    
    G = nx.DiGraph()
    G.add_nodes_from(ecosystem_data["nodes"])
    G.add_edges_from(ecosystem_data["edges"])
    population = ecosystem_data["initial_population"].copy()
    removal_factor = ecosystem_data.get("removal_factor", 0.4) 

    initial_pop_copy = population.copy() # 초기 개체수 저장
    simulation_log = [] # 단계별 로그 기록

    # 1. 초기 충격 적용
    original_pop = population[change_target]
    pop_change_amount = 0
    
    if change_type == "제거":
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

    
    # 2. 연쇄 반응 시뮬레이션 (포식자와 피식자에게 영향 전파)
    
    # 2-1. 포식자에게 미치는 영향 (먹이 감소/멸종)
    for predator in G.successors(change_target):
        if pop_change_amount < 0: # 타겟 생물이 감소 또는 제거되었을 때
            decrease_factor = removal_factor if population[change_target] == 0 else 0.5
            pop_decrease = int(population[predator] * decrease_factor)
            population[predator] -= min(pop_decrease, population[predator])
            
            log_msg = f"📉 **{change_target}**의 먹이 감소로 **{predator}**의 개체수가 **-{pop_decrease} 감소**했어요."
            simulation_log.append(log_msg)
            
    # 2-2. 피식자에게 미치는 영향 (포식자 감소/멸종)
    for prey in G.predecessors(change_target):
        if pop_change_amount < 0: # 타겟 생물이 감소 또는 제거되었을 때
            increase_factor = removal_factor * 1.5 if population[change_target] == 0 else 0.5
            pop_increase = int(population[prey] * increase_factor)
            population[prey] += pop_increase
            
            log_msg = f"📈 **{change_target}** 포식자 감소로 **{prey}**의 개체수가 **+{pop_increase} 증가**했어요!"
            simulation_log.append(log_msg)

    return population, G, initial_pop_copy, simulation_log

# --- 3. 그래프 시각화 함수 ---
def draw_ecosystem(G, population, title, initial_pop):
    """먹이그물을 시각화하고 개체 수 변화를 색상으로 표현합니다."""
    
    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42, k=0.5) 

    colors = []
    
    for node in G.nodes:
        if node in initial_pop:
            change = population.get(node, 0) - initial_pop[node]
            if change > 0:
                colors.append('lightgreen') # 증가
            elif change < 0:
                colors.append('red') # 감소
            else:
                colors.append('skyblue') # 변화 없음
        else:
            colors.append('skyblue')

    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=4000, alpha=0.9)
    nx.draw_networkx_edges(G, pos, edge_color="gray", arrowsize=30, width=2)
    
    labels = {node: f"{SPECIES_EMOJI.get(node, '?')} {node}\n({population.get(node, '?')})" for node in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_family="Malgun Gothic")

    ax.set_title(title, fontsize=15)
    ax.axis('off')
    st.pyplot(fig)
    
# --- 4. Streamlit 페이지 구성 ---

def main_simulation_page():
    st.title("🧪 2. 생태계 안정성 실험")
    st.header("특정 생물이 사라지면 생태계는 어떻게 될까요?")

    # 데이터 로드 및 유효성 검사
    user_nodes = st.session_state.get('user_nodes', [])
    user_edges = st.session_state.get('user_edges', [])

    if not user_edges:
        st.error("⚠️ 먼저 **[1. 먹이 관계 모형 만들기]** 페이지에서 생물들을 연결해야 실험을 할 수 있어요!.")
        
        # 임시로 단순 먹이사슬 모델을 보여줌
        selected_eco = SIMPLE_ECO
        st.session_state.current_ecosystem = selected_eco
    else:
        st.success(f"✨ 내가 만든 모형 ({len(user_nodes)}종)으로 실험을 시작합니다! **{len(user_edges)}개의 화살표**가 생태계를 지키고 있어요.")
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

    # 세션 상태 초기화 (시뮬레이션 결과 저장)
    if 'simulated_pop' not in st.session_state:
        st.session_state.simulated_pop = initial_pop_data
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
        st.session_state.initial_pop_at_sim = initial_pop_copy # 실험 시점의 초기값 저장
        st.session_state.is_simulated = True
        st.session_state.simulation_log = log
        G_result.graph['initial_pop'] = initial_pop_copy
        st.success("실험 결과가 나왔어요! 아래를 확인해 보세요.")


    st.markdown("---")
    
    # --- 결과 시각화 및 비교 ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1️⃣ 실험 전 (초기 상태)")
        draw_ecosystem(G_initial, initial_pop_data, "실험 전 모형", initial_pop_data)

    with col2:
        st.subheader("2️⃣ 실험 후 (변화 상태)")
        if st.session_state.is_simulated:
            draw_ecosystem(G_initial, st.session_state.simulated_pop, "실험 후 모형", st.session_state.initial_pop_at_sim)
        else:
            st.info("좌측에서 충격을 설정하고 '실험 시작!' 버튼을 눌러주세요.")
            draw_ecosystem(G_initial, initial_pop_data, "실험 대기 중", initial_pop_data)

    st.markdown("---")
    
    # --- 변화 상세 로그 및 메트릭 ---
    if st.session_state.is_simulated:
        st.header("🔍 상세 분석: 어떤 생물이 변했을까요?")
        
        # 1. 시뮬레이션 과정 로그
        with st.expander("📝 충격이 전파되는 과정 (로그 보기)"):
            for step in st.session_state.simulation_log:
                st.markdown(f"- {step}")

        # 2. 메트릭으로 변화량 표시
        cols = st.columns(len(selected_eco["nodes"]))
        
        for i, node in enumerate(selected_eco["nodes"]):
            initial = st.session_state.initial_pop_at_sim.get(node, 0)
            current = st.session_state.simulated_pop.get(node, 0)
            
            delta_val = current - initial
            delta_str = f"{'+' if delta_val > 0 else ''}{delta_val}"
            
            with cols[i]:
                st.metric(
                    label=f"{SPECIES_EMOJI.get(node, '?')} {node}",
                    value=f"{current} 마리",
                    delta=delta_str,
                    delta_color="off" if delta_val == 0 else ("inverse" if delta_val < 0 else "normal")
                )
        
        st.info("✅ **핵심 발견:** 화살표 연결이 많을수록 (복잡할수록) 한 생물의 충격에 다른 생물들이 덜 피해를 입고 살아남을 수 있어요! 이것이 **안정성**이랍니다.")

if __name__ == "__main__":
    main_simulation_page()
