import random
import time
import streamlit as st

def init_math_state():
    if 'math_game_state' not in st.session_state:
        st.session_state.math_game_state = 'setup' # 'setup', 'sprint_1', 'break', 'sprint_2', 'results'
    if 'math_difficulty' not in st.session_state:
        st.session_state.math_difficulty = 'easy'
    if 'math_operation_mode' not in st.session_state:
        st.session_state.math_operation_mode = 'Gemischt' # 'Multiplikation', 'Division', 'Gemischt'
    if 'math_tasks' not in st.session_state:
        st.session_state.math_tasks = []
    if 'math_current_index' not in st.session_state:
        st.session_state.math_current_index = 0
    if 'math_results' not in st.session_state:
        st.session_state.math_results = []
    if 'math_sprint_start_time' not in st.session_state:
        st.session_state.math_sprint_start_time = 0
    if 'math_sprint_num' not in st.session_state:
        st.session_state.math_sprint_num = 1
    if 'math_total_score' not in st.session_state:
        st.session_state.math_total_score = 0
    if 'math_correct_digits_count' not in st.session_state:
        st.session_state.math_correct_digits_count = 0
    if 'math_total_digits_count' not in st.session_state:
        st.session_state.math_total_digits_count = 0
    if 'math_grid_values' not in st.session_state:
        st.session_state.math_grid_values = {}
    if 'math_current_task_type' not in st.session_state:
        st.session_state.math_current_task_type = 'mul'
    if 'math_best_es' not in st.session_state:
        st.session_state.math_best_es = 0

difficulty_settings = {
    'easy': {'label': 'Leicht', 'desc': '3-stellig × 1-stellig | Div: 3-stellig ÷ 1-stellig', 'range1': [100, 500], 'range2': [2, 5]},
    'medium': {'label': 'Mittel', 'desc': '3-stellig × 2-stellig | Div: 4-stellig ÷ 1-stellig', 'range1': [200, 999], 'range2': [11, 99]},
    'hard': {'label': 'Meister', 'desc': '4-stellig × 2-stellig | Div: 5-stellig ÷ 2-stellig', 'range1': [1000, 9999], 'range2': [11, 99]},
    'expert': {'label': 'Executive', 'desc': '5-stellig × 2-stellig | Div: 5-stellig ÷ 3-stellig', 'range1': [10000, 99999], 'range2': [11, 99]}
}

def generate_math_task():
    settings = difficulty_settings[st.session_state.math_difficulty]

    op_mode = st.session_state.math_operation_mode
    if op_mode == 'Gemischt':
        task_type = random.choice(['mul', 'div'])
    elif op_mode == 'Multiplikation':
        task_type = 'mul'
    else:
        task_type = 'div'

    st.session_state.math_current_task_type = task_type
    st.session_state.math_current_index += 1

    if task_type == 'mul':
        n1 = random.randint(settings['range1'][0], settings['range1'][1])
        n2 = random.randint(settings['range2'][0], settings['range2'][1])
        st.session_state.math_tasks = [{'n1': n1, 'n2': n2, 'correct': n1 * n2, 'type': 'mul'}]
    else:
        # Division logic setup based on difficulty mapping
        if st.session_state.math_difficulty == 'easy':
            n2 = random.randint(2, 9)
            correct = random.randint(100, 333)
            n1 = n2 * correct
        elif st.session_state.math_difficulty == 'medium':
            n2 = random.randint(2, 9)
            correct = random.randint(334, 1111)
            n1 = n2 * correct
        elif st.session_state.math_difficulty == 'hard':
            n2 = random.randint(11, 99)
            correct = random.randint(100, 999)
            n1 = n2 * correct
        else: # expert
            n2 = random.randint(100, 999)
            correct = random.randint(100, 999)
            n1 = n2 * correct

        st.session_state.math_tasks = [{'n1': n1, 'n2': n2, 'correct': correct, 'type': 'div'}]

    st.session_state.math_grid_values = {}

    # We must explicitly clear Streamlit session state keys associated with the grid inputs
    # otherwise they persist across task generation
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith('carry_') or k.startswith('step') or k.startswith('result_')]
    for k in keys_to_clear:
        del st.session_state[k]

def start_sprint():
    st.session_state.math_game_state = f'sprint_{st.session_state.math_sprint_num}'
    st.session_state.math_sprint_start_time = time.time()
    st.session_state.math_results = []
    # Only reset index on Sprint 1 start
    if st.session_state.math_sprint_num == 1:
        st.session_state.math_current_index = 0
    generate_math_task()

def reset_math_game():
    st.session_state.math_game_state = 'setup'
    st.session_state.math_sprint_num = 1
    st.session_state.math_total_score = 0
    st.session_state.math_correct_digits_count = 0
    st.session_state.math_total_digits_count = 0
