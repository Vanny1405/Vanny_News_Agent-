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

# Das Modell, das wir in deiner Liste gefunden haben (Stand 2026)
MODEL_ID = 'gemini-3-flash-preview'

# Initialisierung des Modells mit Google Search Tool
model = genai.GenerativeModel(
    model_name=MODEL_ID,
    tools=[{'google_search_retrieval': {}}]
)

# 3. SIDEBAR (KONFIGURATION)
with st.sidebar:
    st.title("⚙️ Einstellungen")
    st.info("Dein Agent nutzt Gemini 3 mit Echtzeit-Websuche.")
    
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

            progress_bar.progress(50, text='Generiere Antwort...')
            response = model.generate_content(prompt)

            # Wenn wir hier ankommen, war es erfolgreich
            st.markdown(response.text)
            st.success(f"Update abgeschlossen um {time.strftime('%H:%M:%S')} Uhr.")
            progress_bar.progress(100, text='Abgeschlossen!')
            break # Schleife beenden

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5
                    st.warning(f"Limit erreicht. Ich warte {wait_time} Sekunden und probiere es erneut... (Versuch {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    st.error("Leider ist das API-Limit für heute erschöpft. Bitte probiere es in einer Stunde noch einmal.")
            else:
                st.error(f"Ein Fehler ist aufgetreten: {e}")
                break

st.divider()
st.caption("Powered by Gemini 3 Flash & Streamlit Cloud • 2026")
