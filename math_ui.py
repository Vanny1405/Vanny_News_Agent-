import streamlit as st
import time
from math_trainer import difficulty_settings, generate_math_task, start_sprint, reset_math_game
import streamlit.components.v1 as components

def render_math_setup():
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h1 style='color: #4f46e5;'>🧠 Executive Math Sprint</h1><p>Professional Brain Training</p></div>", unsafe_allow_html=True)

    if st.session_state.math_best_es > 0:
        st.markdown(f"<p style='text-align: center; font-weight: bold; color: #166534;'>🏆 Historischer Best-Score (ES): {int(st.session_state.math_best_es)}</p>", unsafe_allow_html=True)

    st.info("Rechne die Aufgaben wie in deinem Heft. Trage jede Ziffer in ein eigenes Kästchen ein. Das System fokussiert automatisch das nächste Feld.")

    total_time = st.number_input("Gesamtzeit für das Training (in Minuten):", min_value=2, max_value=120, value=st.session_state.math_total_time, step=2)
    st.session_state.math_total_time = total_time
    sprint_duration = total_time // 2

    col1, col2 = st.columns(2)
    with col1:
        diff = st.radio("Wähle dein Level:", options=list(difficulty_settings.keys()), format_func=lambda x: f"{difficulty_settings[x]['label']} ({difficulty_settings[x]['desc']})")
        st.session_state.math_difficulty = diff

        if diff == 'custom':
            d1 = st.slider("Stellen Zahl 1", min_value=1, max_value=10, value=st.session_state.math_custom_digits_1)
            d2 = st.slider("Stellen Zahl 2", min_value=1, max_value=10, value=st.session_state.math_custom_digits_2)
            st.session_state.math_custom_digits_1 = d1
            st.session_state.math_custom_digits_2 = d2

    with col2:
        modes = st.multiselect("Operationsmodus:", options=['Multiplikation', 'Division', 'Überschlagsrechnen'], default=st.session_state.math_operation_modes)
        st.session_state.math_operation_modes = modes

        if 'Division' in modes:
            div_rest = st.checkbox("Division mit Rest", value=st.session_state.math_div_rest)
            st.session_state.math_div_rest = div_rest

    if st.button(f"🚀 SPRINT 1 STARTEN ({sprint_duration} Min)", use_container_width=True):
        if 'Überschlagsrechnen' in modes:
            st.session_state.math_game_state = 'theory'
        else:
            start_sprint()
        st.rerun()

def render_math_theory():
    st.components.v1.html("""
    <style>body { font-family: sans-serif; }</style>

    <div style='text-align: center; margin-bottom: 20px;'>
        <h1 style='color: #4f46e5;'>🧠 Theorie: Überschlagsrechnen</h1>
        <p style='font-size: 1.2rem;'>So rundest du richtig!</p>
    </div>

    <div style='background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 20px;'>
        <h3>Rundungs-Regeln (Grundschule)</h3>
        <p>Bevor du einen Überschlag machst, musst du die Zahlen runden, damit sie leichter zu rechnen sind. Schau dir immer die Stelle an, auf die du runden willst. Schau dann auf den <strong>rechten Nachbarn</strong>:</p>

        <ul style='font-size: 1.1rem; list-style-type: none; padding-left: 0;'>
            <li style='margin-bottom: 10px;'>⬇️ <strong>Abrunden bei:</strong> <span style='background-color: #fee2e2; padding: 2px 8px; border-radius: 4px; font-weight: bold;'>0, 1, 2, 3, 4</span> -> Die Zahl bleibt gleich, der Rest wird zu Nullen.</li>
            <li>⬆️ <strong>Aufrunden bei:</strong> <span style='background-color: #dcfce3; padding: 2px 8px; border-radius: 4px; font-weight: bold;'>5, 6, 7, 8, 9</span> -> Die Zahl wird um 1 größer, der Rest wird zu Nullen.</li>
        </ul>

        <div style='background-color: #e0e7ff; padding: 15px; border-radius: 8px; margin-top: 15px;'>
            <strong>Beispiel:</strong><br>
            Du sollst rechnen: 382 &times; 7<br>
            Wir runden 382 auf den Hunderter. Der Nachbar von 3 ist die 8. Also runden wir auf!<br>
            Aus 382 wird also <strong>400</strong>.<br><br>
            Der einfache Überschlag ist dann: 400 &times; 7 = 2.800.
        </div>
    </div>

    """, height=500)

    if st.button("✅ Verstanden – Sprint starten!", use_container_width=True, type="primary"):
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
            min-width: 1.5rem !important;
            padding: 0 2px !important;
        }
        /* Ersetze das bisherige Merkzahlen-Styling durch diesen spezifischen Block */
        div[data-testid="stTextInput"] > div > div > input[aria-label^="merk_"] {
            background-color: #334155 !important; /* Dunkles Grau-Blau für garantierten Kontrast */
            color: #ffffff !important;           /* Weißer Text */
            border: 1px solid #6366f1 !important; /* Indigo Rahmen */
            -webkit-text-fill-color: #ffffff !important;
            opacity: 1 !important;
            width: 60% !important;
            height: 1.5rem !important;
            font-size: 0.8rem !important;
            margin: 0 auto !important;
        }

        /* Bento Card Styling for Estimation */
        .bento-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            border: 1px solid #e2e8f0;
            margin-bottom: 20px;
            text-align: center;
        }
        .task-text {
            font-size: 3rem;
            font-weight: bold;
            color: #1e293b;
            font-family: 'Roboto Mono', monospace;
            letter-spacing: 2px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Store layout direction for JS
    js_direction = 'rtl' if task_type == 'mul' else 'ltr'

    game_id = st.session_state.math_game_id

    with st.container():
        st.markdown("<div class='math-container'>", unsafe_allow_html=True)

        if task_type == 'est':
            st.markdown(f"""
                <div class='bento-card'>
                    <p style='color: #64748b; font-size: 1.1rem; margin-bottom: 10px;'>Überschlage im Kopf:</p>
                    <div class='task-text'>{n1_str} × {n2_str}</div>
                </div>
            """, unsafe_allow_html=True)

            # Simple text input for estimation instead of grid
            st.text_input("Dein Überschlag:", key=f"est_result_{game_id}", placeholder="Hier eintragen...")
            return # Skip rendering the rest of the JS/grid logic

        elif task_type == 'mul':
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
                        st.text_input(f"merk_{step}_{i}_{game_id}", key=f"merk_{step}_{i}_{game_id}", max_chars=1, label_visibility="collapsed", help="Merkzahl")

                # The actual intermediate calculation step
                cols_step = st.columns(max_cols)
                for i in range(max_cols):
                    with cols_step[i]:
                        st.text_input(f"step_{step}_{i}_{game_id}", key=f"step{step}_{i}_{game_id}", max_chars=1, label_visibility="collapsed")

            if num_steps > 1:
                # Add a final carry row for the addition phase before the result
                st.markdown("<p style='font-size: 8px; color: #cbd5e1; margin: 0 0 -5px 0; text-align: right;'>Additions-Überträge</p>", unsafe_allow_html=True)
                cols_add_merk = st.columns(max_cols)
                for i in range(max_cols):
                    with cols_add_merk[i]:
                        st.text_input(f"merk_add_{i}_{game_id}", key=f"merk_add_{i}_{game_id}", max_chars=1, label_visibility="collapsed", help="Übertrag für Addition")
                st.markdown("<div class='hr-line'></div>", unsafe_allow_html=True)

            # Result row
            st.markdown("<p style='font-size: 10px; color: #a0aec0; margin:0;'>Endergebnis (Rechts nach Links eintragen):</p>", unsafe_allow_html=True)
            cols_res = st.columns(max_cols)
            offset = max_cols - ans_digits
            for i in range(max_cols):
                with cols_res[i]:
                    if i >= offset:
                        res_idx = i - offset
                        st.text_input(f"res_{res_idx}_{game_id}", key=f"result_{res_idx}_{game_id}", max_chars=1, label_visibility="collapsed")
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
                    st.text_input(f"res_{i}_{game_id}", key=f"result_{i}_{game_id}", max_chars=1, label_visibility="collapsed")

            if st.session_state.math_div_rest:
                st.markdown("<p style='font-size: 12px; color: #64748b; margin-top: 5px; margin-bottom: 0;'>Rest (R):</p>", unsafe_allow_html=True)
                # Determine max digits for remainder (could be up to len(n2) but realistically small)
                rem_digits = len(n2_str)
                rem_cols = st.columns([max_cols + 2] + [1]*rem_digits)
                for i in range(rem_digits):
                    with rem_cols[i+1]:
                        st.text_input(f"rem_{i}_{game_id}", key=f"result_rem_{i}_{game_id}", max_chars=1, label_visibility="collapsed")

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
                        st.text_input(f"step_{step}_{i}_{game_id}", key=f"step{step}_{i}_{game_id}", max_chars=1, label_visibility="collapsed")
                # Add line after subtractions
                if step % 2 == 1 and step < num_steps - 1:
                    st.markdown("<div class='hr-line' style='width: 60%; margin-left: 0;'></div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Inject JavaScript for Operation-Specific Focus Flow
    js_code = f"""
    <script>
    setTimeout(() => {{
        const inputs = Array.from(window.parent.document.querySelectorAll('input[type="text"]:not([data-testid="stChatInput"])'));

        function jumpToNext(input, direction) {{
        // We only care about jumping logic for step and merk fields if needed
        // For standard "res_" fields at the bottom or basic inputs, use normal directional hopping
        const label = input.getAttribute('aria-label') || "";

        let targetLabel = "";

        if (direction === 'rtl') {{
            // Multiplication RTL Focus Flow:
            // Hauptfeld (H) -> Merkzahl (M) darüber & EINE SPALTE LINKS -> Hauptfeld (H) links
            // step_X_Y -> merk_X_(Y-1) -> step_X_(Y-1)
            if (label.startsWith("step_")) {{
                let parts = label.split("_");
                // parts = ["step", step_idx, col_idx, game_id]
                let targetCol = parseInt(parts[2]) - 1;
                targetLabel = `merk_${{parts[1]}}_${{targetCol}}_${{parts[3]}}`;
            }} else if (label.startsWith("merk_add_")) {{
                // Fallback for additions if used
                let parts = label.split("_");
                targetLabel = `merk_add_${{parseInt(parts[2]) - 1}}_${{parts[3]}}`;
            }} else if (label.startsWith("merk_")) {{
                let parts = label.split("_");
                // parts = ["merk", step_idx, col_idx, game_id]
                // From Merkzahl (Y-1), we jump down to Step (Y-1)
                targetLabel = `step_${{parts[1]}}_${{parts[2]}}_${{parts[3]}}`;
            }} else if (label.startsWith("res_")) {{
                let parts = label.split("_");
                targetLabel = `res_${{parseInt(parts[1]) - 1}}_${{parts[2]}}`;
            }}
        }} else {{
            // Division: step_X_Y -> merk_X_Y -> step_X_(Y+1) (Note: div has no merk currently, so just LTR)
            let currentIndex = inputs.indexOf(input);
            if (currentIndex >= 0 && currentIndex + 1 < inputs.length) {{
                let nextInput = inputs[currentIndex + 1];
                if (nextInput) nextInput.focus();
                return;
            }}
        }}

        if (targetLabel) {{
            let nextInput = inputs.find(i => i.getAttribute('aria-label') === targetLabel);
            if (nextInput) {{
                nextInput.focus();
            }} else {{
                // Fallback to strict RTL index based jump if target not found (e.g. at edges)
                let currentIndex = inputs.indexOf(input);
                if (currentIndex - 1 >= 0) {{
                    inputs[currentIndex - 1].focus();
                }}
            }}
        }}
    }}

    inputs.forEach((input) => {{
        if (!input.dataset.listenerAttached) {{
            input.dataset.listenerAttached = 'true';

            // Auto jump on type (if character entered)
            input.addEventListener('input', function(e) {{
                if (this.value.length >= 1) {{
                    jumpToNext(this, '{js_direction}');
                }}
            }});

            // Jump on Enter key (to skip optional Merkzahl)
            input.addEventListener('keydown', function(e) {{
                if (e.key === 'Enter') {{
                    // Only prevent default if we actually have somewhere to jump to (not the very last field)
                    // If it's the last result field, let it submit
                    if (!this.getAttribute('aria-label').startsWith('res_0')) {{
                       e.preventDefault();
                       jumpToNext(this, '{js_direction}');
                    }}
                }}
            }});
        }}
    }});
    }}, 100);
    </script>
    """
    components.html(js_code, height=0, key=f"focus_js_{game_id}")


def render_math_sprint():
    sprint_duration_minutes = st.session_state.math_total_time // 2
    elapsed = time.time() - st.session_state.math_sprint_start_time
    remaining = max(0, sprint_duration_minutes * 60 - elapsed)

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
    task_type = current_task.get('type', 'mul')
    game_id = st.session_state.math_game_id

    if task_type == 'est':
        user_val = st.session_state.get(f"est_result_{game_id}", "")
        try:
            user_ans = int(user_val.strip())
            ideal = current_task['correct']
            lower_bound = ideal * 0.85
            upper_bound = ideal * 1.15

            st.session_state.math_total_digits_count += len(str(ideal)) # Weight roughly

            if lower_bound <= user_ans <= upper_bound:
                st.session_state.math_total_score += len(str(ideal))
                st.session_state.math_correct_digits_count += len(str(ideal))
                st.session_state.math_last_check_failed = False
                st.toast(f"✅ Klasse! (Ideal: {ideal})")
                time.sleep(0.5)
                generate_math_task()
                st.rerun()
            else:
                st.error(f"❌ Zu weit weg. Idealer Überschlag war: {ideal}")
                st.session_state.math_last_check_failed = True
        except ValueError:
            st.toast("Bitte gib eine gültige Zahl ein!", icon="⚠️")
        return

    ans_digits = len(str(current_task['correct']))
    ans_str_correct = str(current_task['correct'])

    # Build answer string from individual input fields
    answer_parts = []
    has_empty = False
    wrong_indices = []

    import re
    for i in range(ans_digits):
        val = st.session_state.get(f"result_{i}_{game_id}", "")
        val = re.sub(r'[^\d]', '', val)

        if val:
            answer_parts.append(val)
            if val != ans_str_correct[i]:
                wrong_indices.append(i)
        else:
            has_empty = True
            wrong_indices.append(i)

    answer_str = "".join(answer_parts)

    # Check remainder if applicable
    rem_correct = True
    rem_wrong_indices = []
    if task_type == 'div' and st.session_state.get('math_div_rest', False):
        rem_str_correct = str(current_task.get('correct_rem', 0))
        rem_digits = len(str(current_task['n2'])) # Same logic as UI

        rem_parts = []
        # Pad correct remainder string with leading zeros to match fields
        padded_rem_correct = rem_str_correct.zfill(rem_digits)

        for i in range(rem_digits):
            val = st.session_state.get(f"result_rem_{i}_{game_id}", "")
            val = re.sub(r'[^\d]', '', val)
            if val:
                rem_parts.append(val)
                if val != padded_rem_correct[i]:
                    rem_wrong_indices.append(i)
                    rem_correct = False
            else:
                rem_wrong_indices.append(i)
                rem_correct = False
                if padded_rem_correct[i] != '0': # Empty is only ok if the expected padded digit is 0
                    has_empty = True
                else:
                    # Treat empty as 0 if expected is 0
                    rem_parts.append('0')
                    rem_wrong_indices.remove(i)
                    rem_correct = True # temp fix for this digit

    if has_empty:
        st.toast("Bitte trage ein Ergebnis (und ggf. Rest) ein!", icon="⚠️")
        return

    user_ans = -1
    try:
        user_ans = int(answer_str)
    except ValueError:
        pass

    st.session_state.math_total_digits_count += len(str(current_task['correct']))
    if task_type == 'div' and st.session_state.get('math_div_rest', False):
         st.session_state.math_total_digits_count += 1 # extra point for remainder

    if len(wrong_indices) == 0 and user_ans == current_task['correct'] and rem_correct:
        st.session_state.math_total_score += len(str(current_task['correct']))
        st.session_state.math_correct_digits_count += len(str(current_task['correct']))
        st.session_state.math_last_check_failed = False
        st.toast("Korrekt! Nächste Aufgabe...", icon="✅")
        time.sleep(0.5) # Short pause for feedback
        generate_math_task()
        st.rerun()
    else:
        err_msg = f"Falsch! Das korrekte Ergebnis wäre: {current_task['correct']}"
        if task_type == 'div' and st.session_state.get('math_div_rest', False):
             err_msg += f" Rest {current_task.get('correct_rem', 0)}"
        st.error(err_msg)
        st.session_state.math_last_check_failed = True

        # Inject JS to visually mark ONLY wrong result input fields
        wrong_indices_js = str(wrong_indices)
        rem_wrong_indices_js = str(rem_wrong_indices) if task_type == 'div' else "[]"
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

            // Mark remainder inputs if any
            const remInputs = window.parent.document.querySelectorAll('input[type="text"][aria-label^="rem_"]');
            const remWrongIndices = {rem_wrong_indices_js};
            remInputs.forEach((input, index) => {{
                const ariaLabel = input.getAttribute('aria-label');
                if (ariaLabel) {{
                    const idxStr = ariaLabel.split('_')[1];
                    const idx = parseInt(idxStr);
                    if (remWrongIndices.includes(idx)) {{
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
    sprint_duration_minutes = st.session_state.math_total_time // 2
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

    if st.button(f"🚀 SPRINT 2 STARTEN ({sprint_duration_minutes} Min)", use_container_width=True, type="primary"):
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
    elif state == 'theory':
        render_math_theory()
    elif state in ['sprint_1', 'sprint_2']:
        render_math_sprint()
    elif state == 'break':
        render_math_break()
    elif state == 'results':
        render_math_results()
