import streamlit as st
import google.generativeai as genai

# UI Setup
st.set_page_config(page_title="KI News Agent Pro", page_icon="🚀", layout="wide")

# API Key sicher laden
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Modell mit Google Search Tool initialisieren
# Wir nutzen den Namen, den du im AI Studio gefunden hast!
model = genai.GenerativeModel(
    model_name='gemini-3-flash-preview',
    tools=[{'google_search_retrieval': {}}]
)

st.title("🤖 Dein Profi News-Agent")
st.subheader("Echtzeit-Analyse powered by Google Search")

# Seitenleiste für Einstellungen
with st.sidebar:
    st.header("Konfiguration")
    fokus = st.text_input("Zusätzliches Schwerpunktthema:", "Raumfahrt & E-Mobilität")
    st.info("Dein Agent sucht jetzt live im Netz, ohne auf starre Feeds angewiesen zu sein.")

if st.button("Echtzeit-Update generieren"):
    with st.spinner('Durchsuche das Internet nach den aktuellsten News...'):
        prompt = f"""
        Suche nach den wichtigsten globalen News der letzten 8 Stunden.
        Erstelle eine strukturierte Zusammenfassung in folgenden Kategorien:
        1. 🌍 **Top Weltgeschehen** (Die 3 wichtigsten Meldungen)
        2. 💻 **Tech & KI Fokus** (Aktuelle Trends)
        3. 🎯 **Dein Schwerpunkt: {fokus}**
        
        Wichtig:
        - Sei prägnant.
        - Füge für jede News einen direkten Quellen-Link ein.
        - Nutze Markdown-Trennlinien zwischen den Sektionen.
        """
        
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            
            st.success("Bericht erfolgreich erstellt!")
        except Exception as e:
            st.error(f"Da ist etwas schiefgelaufen: {e}")

st.divider()
st.caption("Datenquelle: Live Google Search via Gemini 3 API")
