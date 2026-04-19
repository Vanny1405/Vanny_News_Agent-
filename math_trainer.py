import random
import time
import streamlit as st

def init_math_state():
    # Estimation State
    if 'estimation_state' not in st.session_state:
        st.session_state.estimation_state = 'setup' # 'setup', 'theory', 'sprint', 'results'

    # Math Sprint State
    if 'math_game_state' not in st.session_state:
        st.session_state.math_game_state = 'setup' # 'setup', 'sprint_1', 'break', 'sprint_2', 'results'
    if 'math_difficulty' not in st.session_state:
        st.session_state.math_difficulty = 'easy'
    if 'math_operation_modes' not in st.session_state:
        st.session_state.math_operation_modes = ['Multiplikation', 'Division']
    if 'math_div_rest' not in st.session_state:
        st.session_state.math_div_rest = False
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
    if 'math_game_id' not in st.session_state:
        st.session_state.math_game_id = 0
    if 'math_total_time' not in st.session_state:
        st.session_state.math_total_time = 16
    if 'math_custom_digits_1' not in st.session_state:
        st.session_state.math_custom_digits_1 = 3
    if 'math_custom_digits_2' not in st.session_state:
        st.session_state.math_custom_digits_2 = 2

difficulty_settings = {
    'easy': {'label': 'Leicht', 'desc': '3-stellig × 1-stellig | Div: 3-stellig ÷ 1-stellig', 'range1': [100, 999], 'range2': [2, 9]},
    'medium': {'label': 'Mittel', 'desc': '4-stellig × 2-stellig | Div: 5-stellig ÷ 1-stellig', 'range1': [1000, 9999], 'range2': [11, 99]},
    'hard': {'label': 'CEO (Meister)', 'desc': '5-stellig × 2-stellig | Div: 5-stellig ÷ 2-stellig', 'range1': [10000, 99999], 'range2': [11, 99]},
    'custom': {'label': 'Custom / Individual', 'desc': 'Frei wählbare Komplexität'}
}

def get_range_for_digits(digits):
    if digits == 1:
        return [2, 9] # Don't allow 0 or 1 for meaningful arithmetic
    return [10**(digits-1), (10**digits) - 1]

def generate_math_task():

    modes = st.session_state.math_operation_modes
    if not modes:
        modes = ['Multiplikation'] # Fallback

    choices = []
    if 'Multiplikation' in modes: choices.append('mul')
    if 'Division' in modes: choices.append('div')
    if 'Überschlagsrechnen' in modes: choices.append('est')

    task_type = random.choice(choices)
    st.session_state.math_current_task_type = task_type
    st.session_state.math_current_index += 1

    if st.session_state.math_difficulty == 'custom':
        range1 = get_range_for_digits(st.session_state.math_custom_digits_1)
        range2 = get_range_for_digits(st.session_state.math_custom_digits_2)
    else:
        settings = difficulty_settings[st.session_state.math_difficulty]
        range1 = settings['range1']
        range2 = settings['range2']

    if task_type == 'mul':
        n1 = random.randint(range1[0], range1[1])
        n2 = random.randint(range2[0], range2[1])
        st.session_state.math_tasks = [{'n1': n1, 'n2': n2, 'correct': n1 * n2, 'type': 'mul'}]
    elif task_type == 'est':
        n1 = random.randint(111, 999)
        n2 = random.randint(3, 9)
        # 314 -> 300. 380 -> 400.
        n1_rounded = round(n1, -2)
        if n1_rounded == 0:
            n1_rounded = 100
        ideal_estimation = n1_rounded * n2
        st.session_state.math_tasks = [{'n1': n1, 'n2': n2, 'correct': ideal_estimation, 'type': 'est'}]
    else:
        # Division logic setup based on difficulty mapping
        if st.session_state.math_difficulty == 'custom':
            # Div: n1-stellig ÷ n2-stellig
            n2 = random.randint(range2[0], range2[1])
            n1 = random.randint(range1[0], range1[1])
            if n2 > n1:
                n1, n2 = n2, n1 # Ensure n1 is always the larger number for division
            if n2 == 0: n2 = 1 # Fallback
            correct = n1 // n2
            if not st.session_state.math_div_rest:
                n1 = n2 * correct
        elif st.session_state.math_difficulty == 'easy':
            n2 = random.randint(2, 9)
            # n1 up to 3 digits (max 999), meaning correct is up to 999/2
            n1 = random.randint(100, 999)
            correct = n1 // n2
            if not st.session_state.math_div_rest:
                n1 = n2 * correct
        elif st.session_state.math_difficulty == 'medium':
            # Div: 5-stellig ÷ 1-stellig
            n2 = random.randint(2, 9)
            n1 = random.randint(10000, 99999)
            correct = n1 // n2
            if not st.session_state.math_div_rest:
                n1 = n2 * correct
        else: # hard / CEO
            # Div: 5-stellig ÷ 2-stellig
            n2 = random.randint(11, 99)
            n1 = random.randint(10000, 99999)
            correct = n1 // n2
            if not st.session_state.math_div_rest:
                n1 = n2 * correct

        remainder = n1 % n2 if st.session_state.math_div_rest else 0
        st.session_state.math_tasks = [{'n1': n1, 'n2': n2, 'correct': correct, 'correct_rem': remainder, 'type': 'div'}]

    st.session_state.math_grid_values = {}

    # Increment game_id to force Streamlit to completely re-render inputs
    # and not carry over old text input values
    st.session_state.math_game_id += 1

    # We also keep the explicit cleanup to avoid accumulating orphaned keys
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith('merk_') or k.startswith('step') or k.startswith('result_') or k == 'math_result_input']
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
