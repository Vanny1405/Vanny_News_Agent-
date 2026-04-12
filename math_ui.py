import streamlit as st
import time
from math_trainer import difficulty_settings, generate_math_task, start_sprint, reset_math_game
import streamlit.components.v1 as components

def render_math_setup():
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h1 style='color: #4f46e5;'>🧠 Executive Math Sprint</h1><p>Professional Brain Training</p></div>", unsafe_allow_html=True)

    if st.session_state.math_best_es > 0:
        st.markdown(f"<p style='text-align: center; font-weight: bold; color: #166534;'>🏆 Historischer Best-Score (ES): {int(st.session_state.math_best_es)}</p>", unsafe_allow_html=True)

    st.info("Rechne die Aufgaben wie in deinem Heft. Trage jede Ziffer in ein eigenes Kästchen ein. Das System fokussiert automatisch das nächste Feld.")

    col1, col2 = st.columns(2)
    with col1:
        diff = st.radio("Wähle dein Level:", options=list(difficulty_settings.keys()), format_func=lambda x: f"{difficulty_settings[x]['label']} ({difficulty_settings[x]['desc']})")
        st.session_state.math_difficulty = diff
    with col2:
        op = st.radio("Operationsmodus:", options=['Gemischt', 'Multiplikation', 'Division'])
        st.session_state.math_operation_mode = op

    if st.button("🚀 SPRINT 1 STARTEN (8 Min)", use_container_width=True):
        start_sprint()
        st.rerun()

def render_math_grid():
    current_task = st.session_state.math_tasks[0]
    ans_digits = len(str(current_task['correct']))
    task_type = current_task['type']

    n1_str = str(current_task['n1'])
    n2_str = str(current_task['n2'])
    ans_str = str(current_task['correct'])

    # CSS for the grid inputs
    st.markdown("""
        <style>
        .stTextInput input {
            text-align: center !important;
            font-family: 'Roboto Mono', monospace !important;
            font-size: 1.5rem !important;
            padding: 0 !important;
            height: 3rem !important;
        }
        .math-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border: 2px solid #e2e8f0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .task-text {
            font-family: 'Roboto Mono', monospace;
            font-size: 2rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 3rem;
            margin-bottom: 10px;
        }
        .hr-line {
            border-top: 2px solid #2d3748;
            margin: 5px 0;
            width: 100%;
        }
        /* Make columns tight for the grid */
        div[data-testid="column"] {
            min-width: 3rem !important;
            padding: 0 4px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Store layout direction for JS
    js_direction = 'rtl' if task_type == 'mul' else 'ltr'

    with st.container():
        st.markdown("<div class='math-container'>", unsafe_allow_html=True)

        if task_type == 'mul':
            max_cols = max(len(n1_str) + len(n2_str) + 1, len(ans_str) + 1)

            st.markdown(f"<div class='task-text'>{n1_str} × {n2_str}</div>", unsafe_allow_html=True)
            st.markdown("<div class='hr-line'></div>", unsafe_allow_html=True)

            # Intermediate rows (each preceded by its own smart carries / Merkzahlen row)
            num_steps = len(n2_str)
            for step in range(num_steps):
                # Smart carries for this intermediate step
                st.markdown("<p style='font-size: 8px; color: #cbd5e1; margin: 0 0 -5px 0; text-align: right;'>Merkzahlen</p>", unsafe_allow_html=True)
                cols_merk = st.columns(max_cols)
                for i in range(max_cols):
                    with cols_merk[i]:
                        st.text_input(f"merk_{step}_{i}", key=f"merk_{step}_{i}", max_chars=1, label_visibility="collapsed", help="Merkzahl")

                # The actual intermediate calculation step
                cols_step = st.columns(max_cols)
                for i in range(max_cols):
                    with cols_step[i]:
                        st.text_input(f"step_{step}_{i}", key=f"step{step}_{i}", max_chars=1, label_visibility="collapsed")

            if num_steps > 1:
                # Add a final carry row for the addition phase before the result
                st.markdown("<p style='font-size: 8px; color: #cbd5e1; margin: 0 0 -5px 0; text-align: right;'>Additions-Überträge</p>", unsafe_allow_html=True)
                cols_add_merk = st.columns(max_cols)
                for i in range(max_cols):
                    with cols_add_merk[i]:
                        st.text_input(f"merk_add_{i}", key=f"merk_add_{i}", max_chars=1, label_visibility="collapsed", help="Übertrag für Addition")
                st.markdown("<div class='hr-line'></div>", unsafe_allow_html=True)

            # Result row
            st.markdown("<p style='font-size: 10px; color: #a0aec0; margin:0;'>Endergebnis (Rechts nach Links eintragen):</p>", unsafe_allow_html=True)
            cols_res = st.columns(max_cols)
            offset = max_cols - ans_digits
            for i in range(max_cols):
                with cols_res[i]:
                    if i >= offset:
                        res_idx = i - offset
                        st.text_input(f"res_{res_idx}", key=f"result_{res_idx}", max_chars=1, label_visibility="collapsed")
                    else:
                        st.empty()

        else: # Division
            max_cols = len(n1_str)

            # Top Row: Task and Result Inputs
            top_cols = st.columns([max_cols + 2] + [1]*ans_digits)
            with top_cols[0]:
                st.markdown(f"<div class='task-text' style='justify-content: flex-start;'>{n1_str} ÷ {n2_str} =</div>", unsafe_allow_html=True)
            for i in range(ans_digits):
                with top_cols[i+1]:
                    st.text_input(f"res_{i}", key=f"result_{i}", max_chars=1, label_visibility="collapsed")

            # Scratchpad (Treppenform)
            num_steps = len(n1_str) * 2
            st.markdown("<div style='width: 100%; max-width: " + str(max_cols * 4) + "rem; align-self: flex-start; margin-top: 10px;'>", unsafe_allow_html=True)

            for step in range(num_steps):
                # The staircase involves subtracting every 2nd step
                # Let's add an extra tiny column for the minus sign for odd steps (subtraction steps)
                cols_step = st.columns([0.5] + [1] * max_cols)

                with cols_step[0]:
                    if step % 2 == 1:
                        st.markdown("<div style='font-family: monospace; font-size: 1.5rem; display: flex; align-items: center; justify-content: center; height: 3rem;'>-</div>", unsafe_allow_html=True)
                    else:
                        st.empty()

                for i in range(max_cols):
                    with cols_step[i+1]:
                        st.text_input(f"step_{step}_{i}", key=f"step{step}_{i}", max_chars=1, label_visibility="collapsed")
                # Add line after subtractions
                if step % 2 == 1 and step < num_steps - 1:
                    st.markdown("<div class='hr-line' style='width: 60%; margin-left: 0;'></div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Inject JavaScript for Auto-Focus
    js_code = f"""
    <script>
    const inputs = window.parent.document.querySelectorAll('input[type="text"]:not([data-testid="stChatInput"])');

    inputs.forEach((input, index) => {{
        if (!input.dataset.listenerAttached) {{
            input.dataset.listenerAttached = 'true';
            input.addEventListener('input', function(e) {{
                if (this.value.length >= 1) {{
                    let nextIndex = '{js_direction}' === 'rtl' ? index - 1 : index + 1;

                    if (nextIndex >= 0 && nextIndex < inputs.length) {{
                        let nextInput = window.parent.document.querySelectorAll('input[type="text"]:not([data-testid="stChatInput"])')[nextIndex];
                        if (nextInput) {{
                            nextInput.focus();
                        }}
                    }}
                }}
            }});
        }}
    }});
    </script>
    """
    components.html(js_code, height=0)


def render_math_sprint():
    elapsed = time.time() - st.session_state.math_sprint_start_time
    remaining = max(0, 8 * 60 - elapsed)

    mins, secs = divmod(int(remaining), 60)
    st.markdown(f"<div style='text-align: right; font-family: monospace; font-size: 1.2rem; color: #4a5568;'>⏳ {mins:02d}:{secs:02d}</div>", unsafe_allow_html=True)

    if remaining == 0:
        if st.session_state.math_sprint_num == 1:
            st.session_state.math_game_state = 'break'
        else:
            st.session_state.math_game_state = 'results'
        st.rerun()

    # Store check state in session to render skip button without nested execution block issues
    if 'math_last_check_failed' not in st.session_state:
        st.session_state.math_last_check_failed = False

    # Use a form so Enter submits
    with st.form(key="math_form", clear_on_submit=False):
        render_math_grid()

        st.markdown("""
        <style>
        .stButton > button {
            background-color: #7c3aed !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
            padding: 0.75rem 1rem !important;
            border-radius: 0.5rem !important;
        }
        .stButton > button:hover {
            background-color: #6d28d9 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])

        with col1:
            submit_btn = st.form_submit_button("PRÜFEN ➔", use_container_width=True)

        with col2:
            if st.session_state.math_last_check_failed:
                skip_btn = st.form_submit_button("Überspringen", use_container_width=True)
            else:
                skip_btn = False

        st.markdown("<p style='text-align: center; font-size: 10px; color: #a0aec0; margin-top: 10px;'>Tipp: Leerlassen oder Falsche Eingaben werden rot markiert.</p>", unsafe_allow_html=True)

    if submit_btn:
        check_answer()
    if skip_btn:
        st.session_state.math_last_check_failed = False
        generate_math_task()
        st.rerun()


def check_answer():
    current_task = st.session_state.math_tasks[0]
    ans_digits = len(str(current_task['correct']))

    ans_str_correct = str(current_task['correct'])

    # Build answer string from individual input fields
    # Make sure we don't accidentally pull empty strings out and concatenate
    answer_parts = []
    has_empty = False
    wrong_indices = []

    for i in range(ans_digits):
        val = st.session_state.get(f"result_{i}", "")
        # Remove non-digits just in case
        import re
        val = re.sub(r'[^\d]', '', val)

        if val:
            answer_parts.append(val)
            if val != ans_str_correct[i]:
                wrong_indices.append(i)
        else:
            has_empty = True
            wrong_indices.append(i)

    answer_str = "".join(answer_parts)

    if has_empty:
        st.toast("Bitte trage ein Ergebnis ein!", icon="⚠️")
        return

    user_ans = -1
    try:
        user_ans = int(answer_str)
    except ValueError:
        pass

    # Calculate score metrics
    st.session_state.math_total_digits_count += len(str(current_task['correct']))

    if len(wrong_indices) == 0 and user_ans == current_task['correct']:
        st.session_state.math_total_score += len(str(current_task['correct']))
        st.session_state.math_correct_digits_count += len(str(current_task['correct']))
        st.session_state.math_last_check_failed = False
        st.toast("Korrekt! Nächste Aufgabe...", icon="✅")
        time.sleep(0.5) # Short pause for feedback
        generate_math_task()
        st.rerun()
    else:
        st.error(f"Falsch! Das korrekte Ergebnis wäre: {current_task['correct']}")
        st.session_state.math_last_check_failed = True

        # Inject JS to visually mark ONLY wrong result input fields
        wrong_indices_js = str(wrong_indices)
        error_js = f"""
        <script>
            const inputs = window.parent.document.querySelectorAll('input[type="text"][aria-label^="res_"]');
            const wrongIndices = {wrong_indices_js};
            inputs.forEach((input, index) => {{
                // Extract original index from aria-label which matches "res_i"
                const ariaLabel = input.getAttribute('aria-label');
                if (ariaLabel) {{
                    const idxStr = ariaLabel.split('_')[1];
                    const idx = parseInt(idxStr);
                    if (wrongIndices.includes(idx)) {{
                        input.style.backgroundColor = '#fee2e2';
                        input.style.borderColor = '#ef4444';
                        input.style.color = '#991b1b';
                    }} else {{
                        input.style.backgroundColor = '#f0fdf4';
                        input.style.borderColor = '#22c55e';
                        input.style.color = '#166534';
                    }}
                }}
            }});
        </script>
        """
        components.html(error_js, height=0)

def render_math_break():
    st.markdown("<div class='math-container' style='text-align: center; padding: 40px;'>", unsafe_allow_html=True)
    import random
    quotes = [
        "\"Recalibrating synapses... Phase 1 complete.\"",
        "\"Synergy between logic and speed. Take a breath, the board expects your return.\"",
        "\"Mental liquidity secured. Prepare for exponential growth in Phase 2.\""
    ]
    st.markdown("<h2 style='color: #4f46e5; margin-bottom: 20px;'>Phase 1 Complete</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 1.2rem; font-style: italic; color: #4a5568;'>{random.choice(quotes)}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚀 SPRINT 2 STARTEN (8 Min)", use_container_width=True, type="primary"):
        st.session_state.math_sprint_num = 2
        start_sprint()
        st.rerun()

def render_math_results():
    st.markdown("<div class='math-container' style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("<h2>Executive Ranking</h2>", unsafe_allow_html=True)

    # Calculate Executive Score (ES)
    # ES = (Summe aller Stellen gelöster Aufgaben) * (Genauigkeit in Prozent)^3
    acc_ratio = st.session_state.math_correct_digits_count / max(1, st.session_state.math_total_digits_count)
    accuracy_pct = acc_ratio * 100

    es = st.session_state.math_total_score * (acc_ratio ** 3)

    if es > st.session_state.math_best_es:
        st.session_state.math_best_es = es
        st.balloons()
        st.markdown(f"<h3 style='color: #ea580c;'>🎉 Neuer Rekord! 🎉</h3>", unsafe_allow_html=True)

    st.markdown(f"<h1 style='color: #4f46e5; font-size: 4rem; margin: 20px 0;'>ES: {int(es)}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p>Genauigkeit: {accuracy_pct:.1f}%</p>", unsafe_allow_html=True)

    if es < 100:
        msg = "Junior Analyst: The foundation is laid. Now, scale your mental ROI."
    elif es < 250:
        msg = "Senior Associate: Advancing in the hierarchy. Precision is increasing."
    elif es < 450:
        msg = "VP of Algebra: Leading with logic. Your calculation speed is a competitive advantage."
    elif es < 700:
        msg = "CFO: Financial integrity confirmed. You own the numbers."
    elif es <= 1000 or (es > 1000 and accuracy_pct < 100):
        msg = "Math CEO: Market disruption through mathematical precision. Excellent execution."
    else:
        msg = "Emeritus Professor: Absolute Mastery. The numbers don't just speak to you – they obey."

    st.markdown(f"<div style='background: #f0fdf4; border: 1px solid #bbf7d0; padding: 20px; border-radius: 10px; margin-top: 20px;'><h3 style='color: #166534;'>{msg}</h3></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔄 NEUER TEST", use_container_width=True):
        reset_math_game()
        st.rerun()

def render_brain_training():
    from math_trainer import init_math_state
    init_math_state()

    state = st.session_state.math_game_state

    if state == 'setup':
        render_math_setup()
    elif state in ['sprint_1', 'sprint_2']:
        render_math_sprint()
    elif state == 'break':
        render_math_break()
    elif state == 'results':
        render_math_results()
