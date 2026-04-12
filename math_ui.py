import streamlit as st
import time
from math_trainer import difficulty_settings, generate_math_task, start_sprint, reset_math_game
import streamlit.components.v1 as components

def render_math_setup():
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h1 style='color: #4f46e5;'>🧠 Executive Math Sprint</h1><p>Professional Brain Training</p></div>", unsafe_allow_html=True)

    st.info("Rechne die Aufgaben wie in deinem Heft. Trage jede Ziffer in ein eigenes Kästchen ein. Das System fokussiert automatisch das nächste Feld.")

    diff = st.radio("Wähle dein Level:", options=list(difficulty_settings.keys()), format_func=lambda x: difficulty_settings[x]['label'])
    st.session_state.math_difficulty = diff

    if st.button("🚀 SPRINT 1 STARTEN (8 Min)", use_container_width=True):
        start_sprint()
        st.rerun()

def render_math_grid():
    current_task = st.session_state.math_tasks[0]
    digits = difficulty_settings[st.session_state.math_difficulty]['digits']
    task_type = current_task['type']

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
        .carry-input input {
            font-size: 0.8rem !important;
            height: 1.5rem !important;
            color: #718096 !important;
        }
        .math-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border: 2px solid #e2e8f0;
        }
        .wrong-input input {
            background-color: #fee2e2 !important;
            border-color: #ef4444 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='math-container'>", unsafe_allow_html=True)

        # Display Task
        operator_sym = '×' if task_type == 'mul' else '÷'
        st.markdown(f"<h2 style='text-align: center; font-family: \"Roboto Mono\", monospace; letter-spacing: 0.2em; font-size: 2.5rem; margin-bottom: 30px;'>{current_task['n1']} <span style='color: #4f46e5;'>{operator_sym}</span> {current_task['n2']}</h2>", unsafe_allow_html=True)

        cols = st.columns(digits)

        # Store layout direction for JS
        js_direction = 'rtl' if task_type == 'mul' else 'ltr'

        if task_type == 'mul':
            # Carry row
            for i in range(digits):
                with cols[i]:
                    st.text_input("", key=f"carry_{i}", max_chars=1, label_visibility="collapsed", args=("carry-input math-cell",))

            # Intermediate rows for Hard mode (3x2)
            if st.session_state.math_difficulty == 'hard':
                st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
                cols_step1 = st.columns(digits)
                for i in range(digits):
                    with cols_step1[i]:
                        st.text_input("", key=f"step1_{i}", max_chars=1, label_visibility="collapsed", args=("math-cell",))

                cols_step2 = st.columns(digits)
                for i in range(digits):
                    with cols_step2[i]:
                        st.text_input("", key=f"step2_{i}", max_chars=1, label_visibility="collapsed", args=("math-cell",))

            st.markdown("<hr style='border-top: 2px solid #2d3748; margin: 15px 0;'>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; font-size: 10px; font-weight: bold; color: #a0aec0; text-transform: uppercase;'>Dein Endergebnis:</p>", unsafe_allow_html=True)

            cols_result = st.columns(digits)
            for i in range(digits):
                with cols_result[i]:
                    val = st.text_input("", key=f"result_{i}", max_chars=1, label_visibility="collapsed", args=("math-cell result-cell",))
                    st.session_state.math_grid_values[f"result_{i}"] = val

        else: # Division
            st.markdown("<p style='text-align: center; font-size: 10px; font-weight: bold; color: #a0aec0; text-transform: uppercase;'>Dein Endergebnis (Links nach Rechts):</p>", unsafe_allow_html=True)
            cols_result = st.columns(digits)
            for i in range(digits):
                with cols_result[i]:
                    val = st.text_input("", key=f"result_{i}", max_chars=1, label_visibility="collapsed", args=("math-cell result-cell",))
                    st.session_state.math_grid_values[f"result_{i}"] = val

        st.markdown("</div>", unsafe_allow_html=True)

    # Inject JavaScript for Auto-Focus
    js_code = f"""
    <script>
    const inputs = window.parent.document.querySelectorAll('input[type="text"]:not([data-testid="stChatInput"])');

    // Sort inputs based on direction to map logical flow
    let sortedInputs = Array.from(inputs);

    // Simplistic approach for now: just add event listeners to all text inputs
    // We rely on the user tabbing or the script finding the next logical input

    inputs.forEach((input, index) => {{
        // Remove old listeners to prevent duplicates on rerun
        const new_input = input.cloneNode(true);
        input.parentNode.replaceChild(new_input, input);

        new_input.addEventListener('input', function(e) {{
            if (this.value.length >= 1) {{
                let nextIndex = '{js_direction}' === 'rtl' ? index - 1 : index + 1;

                // For RTL (multiplication), the result row visually is left-to-right in the DOM
                // but conceptually we fill it right-to-left.
                // A better approach is to rely on data-attributes, but since we can't easily set them
                // on Streamlit inputs, we do a basic DOM traversal

                if (nextIndex >= 0 && nextIndex < inputs.length) {{
                    // Try to find next input in parent document
                    let nextInput = window.parent.document.querySelectorAll('input[type="text"]:not([data-testid="stChatInput"])')[nextIndex];
                    if (nextInput) {{
                        nextInput.focus();
                    }}
                }}
            }}
        }});
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

    render_math_grid()

    if st.button("PRÜFEN ➔", use_container_width=True, type="primary"):
        check_answer()

    st.markdown("<p style='text-align: center; font-size: 10px; color: #a0aec0; margin-top: 10px;'>Tipp: Leerlassen oder Falsche Eingaben werden rot markiert.</p>", unsafe_allow_html=True)


def check_answer():
    current_task = st.session_state.math_tasks[0]
    digits = difficulty_settings[st.session_state.math_difficulty]['digits']

    answer_str = ""
    for i in range(digits):
        val = st.session_state.get(f"result_{i}", "")
        if not val:
            val = st.session_state.math_grid_values.get(f"result_{i}", "")
        if val and val.isdigit():
            answer_str += val

    if not answer_str:
        st.toast("Bitte trage ein Ergebnis ein!", icon="⚠️")
        return

    user_ans = int(answer_str)

    # Calculate score metrics
    st.session_state.math_total_digits_count += len(str(current_task['correct']))

    if user_ans == current_task['correct']:
        st.session_state.math_total_score += len(str(current_task['correct']))
        st.session_state.math_correct_digits_count += len(str(current_task['correct']))
        st.toast("Korrekt! Nächste Aufgabe...", icon="✅")
        time.sleep(0.5) # Short pause for feedback
        generate_math_task()
        st.rerun()
    else:
        st.error(f"Falsch! Das korrekte Ergebnis wäre: {current_task['correct']}")

        # Inject JS to visually mark input fields as wrong
        error_js = """
        <script>
            const inputs = window.parent.document.querySelectorAll('input[type="text"]:not([data-testid="stChatInput"])');
            inputs.forEach(input => {
                input.style.backgroundColor = '#fee2e2';
                input.style.borderColor = '#ef4444';
            });
        </script>
        """
        components.html(error_js, height=0)

        if st.button("Überspringen"):
            generate_math_task()
            st.rerun()

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
    elif es < 1000:
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
