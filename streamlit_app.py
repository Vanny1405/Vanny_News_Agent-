import time
import google.generativeai as genai
import streamlit as st

# 1. UI SETUP & DESIGN
st.set_page_config(
    page_title="Vanny's News Agent", 
    page_icon="🗞️", 
    layout="wide"
)

# Custom CSS für einen moderneren Look
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. API KONFIGURATION
# Wir nutzen deinen Key aus den Streamlit Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("API Key nicht gefunden! Bitte in den Streamlit-Settings unter 'Secrets' hinterlegen.")
    st.stop()

# Verfügbare Text/Search Modelle (gefiltert aus deiner Liste)
VERFUEGBARE_MODELLE = [
    'gemini-3-flash-preview',
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    'gemini-2.0-flash'
]

# 3. SIDEBAR (KONFIGURATION)
with st.sidebar:
    st.title("⚙️ Einstellungen")
    st.info("Wähle deine Modelle mit Echtzeit-Websuche.")

    primaeres_modell = st.selectbox(
        "Primäres Modell:",
        VERFUEGBARE_MODELLE,
        index=0,
        help="Wird zuerst versucht."
    )

    fallback_modell = st.selectbox(
        "Fallback Modell (bei Limit-Fehler):",
        VERFUEGBARE_MODELLE,
        index=1,
        help="Wird genutzt, wenn das primäre Modell keine Quote mehr hat."
    )

    st.divider()
    
    fokus_themen = st.text_area(
        "Spezifische Schwerpunkte:", 
        "KI-Trends, Raumfahrt & E-Mobilität",
        help="Trenne Themen mit Kommas."
    )
    
    st.divider()
    st.caption("Status: Verbunden mit Gemini API")
    
    # Diagnose-Option (falls du mal die Modell-Liste brauchst)
    with st.expander("System-Diagnose"):
        if st.button("Verfügbare Modelle auflisten"):
            models = [m.name for m in genai.list_models()]
            st.code(models)

# 4. HAUPTBEREICH
st.title("🤖 Dein persönlicher News-Agent")
st.write("Klicke auf den Button, um die Weltlage der letzten 8-12 Stunden zu analysieren.")

if st.button("🚀 News-Update jetzt generieren"):
    progress_bar = st.progress(0, text='Durchsuche das Internet...')

    # Retry-Logik gegen den 429-Fehler (Quota exceeded)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Der Prompt für Gemini
            prompt = f"""
            Suche im Internet nach den wichtigsten Nachrichten der letzten 8-12 Stunden.
            Erstelle einen übersichtlichen Bericht in Deutsch mit folgenden Sektionen:

            1. 🌍 **Globales Weltgeschehen**: Die 3 kritischsten Schlagzeilen.
            2. 🔍 **Deep Dive Schwerpunkte**: Analysiere detailliert: {fokus_themen}.

            Formatierung:
            - Nutze für jedes Thema eine ### Überschrift.
            - Schreibe eine prägnante Zusammenfassung (2-3 Sätze).
            - Füge am Ende jeder News einen Link zur Quelle ein: [👉 Mehr lesen](URL).
            - Trenne die Sektionen mit --- Linien.
            """

            # 1. Versuche das Primäre Modell
            aktuelles_modell = primaeres_modell
            model = genai.GenerativeModel(
                model_name=aktuelles_modell,
                tools=[{'google_search_retrieval': {}}]
            )

            progress_bar.progress(50, text=f'Generiere Antwort mit {aktuelles_modell}...')
            response = model.generate_content(prompt)

            # Wenn wir hier ankommen, war es erfolgreich
            st.markdown(response.text)
            st.success(f"Update abgeschlossen um {time.strftime('%H:%M:%S')} Uhr. Verwendetes Modell: **{aktuelles_modell}**")
            progress_bar.progress(100, text='Abgeschlossen!')
            break # Schleife beenden

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5
                    st.warning(f"Limit beim {aktuelles_modell} erreicht. Warte {wait_time}s... (Versuch {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    st.error(f"Limit beim {aktuelles_modell} komplett ausgeschöpft.")

                    # 2. Aktiviere den Fallback!
                    if primaeres_modell != fallback_modell:
                        st.info(f"Wechsle jetzt zum Fallback-Modell: {fallback_modell}...")
                        try:
                            aktuelles_modell = fallback_modell
                            fallback_agent = genai.GenerativeModel(
                                model_name=aktuelles_modell,
                                tools=[{'google_search_retrieval': {}}]
                            )
                            response = fallback_agent.generate_content(prompt)

                            st.markdown(response.text)
                            st.success(f"Update abgeschlossen um {time.strftime('%H:%M:%S')} Uhr über Fallback. Verwendetes Modell: **{aktuelles_modell}**")
                            progress_bar.progress(100, text='Abgeschlossen mit Fallback!')
                            break # Den gesamten Block erfolgreich beenden

                        except Exception as fallback_e:
                             st.error(f"Leider hat auch das Fallback-Modell ({fallback_modell}) einen Fehler geworfen: {fallback_e}")
                             break
                    else:
                        st.error("Es wurde kein alternatives Fallback-Modell konfiguriert. Bitte probiere es später noch einmal.")
                        break
            else:
                st.error(f"Ein Fehler ist aufgetreten: {e}")
                break

st.divider()
st.caption("Powered by Gemini Models & Streamlit Cloud • 2026")
