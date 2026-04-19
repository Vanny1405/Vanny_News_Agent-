import time
import streamlit as st
import random

def render_theory():
    st.markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h1 style='color: #4f46e5;'>🧠 Theorie: Überschlagsrechnen</h1>
        <p style='font-size: 1.2rem;'>So rundest du richtig!</p>
    </div>

    <div style='background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 20px;'>
        <h3>Rundungs-Regeln (4. Klasse)</h3>
        <p>Bevor du einen Überschlag machst, musst du die Zahlen runden, damit sie leichter zu rechnen sind. Schau dir immer die Stelle an, die <strong>rechts</strong> neben der Zahl steht, auf die du runden willst.</p>

        <ul style='font-size: 1.1rem; list-style-type: none; padding-left: 0;'>
            <li style='margin-bottom: 10px;'>⬇️ <strong>Abrunden bei:</strong> <span style='background-color: #fee2e2; padding: 2px 8px; border-radius: 4px; font-weight: bold;'>0, 1, 2, 3, 4</span> -> Die Zahl bleibt gleich, der Rest wird zu Nullen.</li>
            <li>⬆️ <strong>Aufrunden bei:</strong> <span style='background-color: #dcfce3; padding: 2px 8px; border-radius: 4px; font-weight: bold;'>5, 6, 7, 8, 9</span> -> Die Zahl wird um 1 größer, der Rest wird zu Nullen.</li>
        </ul>

        <div style='background-color: #e0e7ff; padding: 15px; border-radius: 8px; margin-top: 15px;'>
            <strong>Beispiel:</strong><br>
            Du sollst rechnen: $587 \\times 4$<br>
            Du rundest die erste Zahl auf Hunderter. Die Zahl daneben ist eine 8. Bei 8 wird <strong>aufgerundet</strong>!<br>
            Aus 587 wird also <strong>600</strong>.<br><br>
            Der einfache Überschlag ist dann: $600 \\times 4 = 2.400$.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✅ Verstanden – Sprint starten!", use_container_width=True, type="primary"):
        st.session_state.estimation_state = 'sprint'
        st.session_state.math_sprint_start_time = time.time()
        # Ensure tasks are cleared/ready for generation in the sprint view
        if 'est_task' in st.session_state:
            del st.session_state.est_task
        st.rerun()


def generate_estimation_task():
    # Generate numbers like 314 * 5 -> expected around 300 * 5 = 1500
    # Range based roughly on "medium" difficulty style, focusing on rounding
    n1 = random.randint(111, 999)
    n2 = random.randint(3, 9)
    exact = n1 * n2

    # Simple automatic rounding to nearest hundred for n1 to determine the "ideal" estimation
    # 314 -> 300. 380 -> 400.
    n1_rounded = round(n1, -2)
    if n1_rounded == 0:
        n1_rounded = 100

    ideal_estimation = n1_rounded * n2

    st.session_state.est_task = {
        'n1': n1,
        'n2': n2,
        'exact': exact,
        'ideal_est': ideal_estimation
    }
    st.session_state.est_input = "" # Clear input

def render_estimation_sprint():
    if 'est_task' not in st.session_state or 'n1' not in st.session_state.get('est_task', {}):
        generate_estimation_task()

    task = st.session_state.est_task

    # CSS injection for Bento layout and inputs (specifically including the merk_ fix requested for safety/consistency)
    st.markdown("""
        <style>
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

        /* Merkzahlen visibility fix from previous task (applied globally to this module for safety) */
        div[data-testid="stTextInput"] > div > div > input[aria-label^="merk_"] {
            background-color: #1e293b !important;
            color: #ffffff !important;
            border: 1px solid #6366f1 !important;
            -webkit-text-fill-color: #ffffff !important;
            opacity: 1 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class='bento-card'>
            <p style='color: #64748b; font-size: 1.1rem; margin-bottom: 10px;'>Überschlage im Kopf:</p>
            <div class='task-text'>{task['n1']} × {task['n2']}</div>
        </div>
    """, unsafe_allow_html=True)

    # Use a form to capture enter key
    with st.form(key="est_form", clear_on_submit=True):
        user_val = st.text_input("Dein Überschlag:", key="est_input_field")
        col1, col2 = st.columns([3, 1])
        with col1:
            submit_btn = st.form_submit_button("PRÜFEN ➔", use_container_width=True)
        with col2:
            skip_btn = st.form_submit_button("Überspringen", use_container_width=True)

    if submit_btn:
        try:
            user_num = int(user_val.strip())

            ideal = task['ideal_est']
            # Allow +- 15% deviation for estimations
            lower_bound = ideal * 0.85
            upper_bound = ideal * 1.15

            if lower_bound <= user_num <= upper_bound:
                st.toast(f"✅ Klasse! (Idealer Überschlag: {ideal})")

                if 'est_score' not in st.session_state:
                    st.session_state.est_score = 0
                st.session_state.est_score += 1

                time.sleep(0.5)
                generate_estimation_task()
                st.rerun()
            else:
                st.error(f"❌ Zu weit weg. Idealer Überschlag war: {ideal}")
        except ValueError:
            st.error("Bitte gib eine gültige Zahl ein.")

    if skip_btn:
        generate_estimation_task()
        st.rerun()

    if st.button("🏁 Beenden & Ergebnisse", type="secondary"):
        st.session_state.estimation_state = 'results'
        st.rerun()

def render_estimation_results():
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("<h2>Ergebnisse: Überschlagsrechnen</h2>", unsafe_allow_html=True)

    score = st.session_state.get('est_score', 0)
    st.markdown(f"<h1 style='color: #4f46e5; font-size: 4rem; margin: 20px 0;'>{score} Richtig!</h1>", unsafe_allow_html=True)

    if score > 5:
        st.balloons()
        st.success("Hervorragend! Du hast ein super Gefühl für Zahlen entwickelt.")
    elif score > 0:
        st.info("Guter Anfang! Mit etwas mehr Übung wirst du noch schneller.")
    else:
        st.warning("Das war vielleicht noch etwas schwer. Probier es gleich nochmal!")

    if st.button("🔄 Neues Training starten", use_container_width=True):
        st.session_state.estimation_state = 'setup'
        st.session_state.est_score = 0
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_estimation_setup():
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h1 style='color: #4f46e5;'>📈 Überschlagsrechnen</h1><p>Trainiere dein Zahlengefühl</p></div>", unsafe_allow_html=True)

    st.info("Beim Überschlagsrechnen geht es nicht um das exakte Ergebnis! Du rundest die Zahlen, um im Kopf blitzschnell zu prüfen, in welcher Größenordnung das Ergebnis liegt.")

    if st.button("📖 Theorie lesen & Starten", use_container_width=True, type="primary"):
        st.session_state.estimation_state = 'theory'
        st.rerun()

def render_estimation_training():
    state = st.session_state.get('estimation_state', 'setup')

    if state == 'setup':
        render_estimation_setup()
    elif state == 'theory':
        render_theory()
    elif state == 'sprint':
        render_estimation_sprint()
    elif state == 'results':
        render_estimation_results()
