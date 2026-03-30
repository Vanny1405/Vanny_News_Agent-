import streamlit as st
import google.generativeai as genai

# UI Setup
st.set_page_config(page_title="KI News Agent Diagnose", page_icon="🕵️", layout="wide")

# API Key laden
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

st.title("🤖 Modell-Diagnose & News-Agent")

# --- DIAGNOSE SEKTION ---
with st.expander("Modell-Liste anzeigen (Klicke hier, falls Fehler auftreten)"):
    try:
        available_models = [m.name.replace('models/', '') for m in genai.list_models() 
                            if 'generateContent' in m.supported_generation_methods]
        st.write("Diese Namen akzeptiert dein API-Key aktuell:")
        st.code(available_models)
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Liste: {e}")

# --- AGENT SEKTION ---
# Wähle hier einen Namen aus der Liste oben aus. 
# Wir probieren jetzt mal den ganz schlichten Namen:
model_id = 'gemini-1.5-flash' 

try:
    model = genai.GenerativeModel(
        model_name=model_id,
        tools=[{'google_search_retrieval': {}}]
    )
    st.success(f"Aktuell konfiguriert: {model_id}")
except Exception as e:
    st.error(f"Fehler bei Initialisierung: {e}")

fokus = st.text_input("Dein Schwerpunkt:", "KI & Technologie")

if st.button("Echtzeit-Update generieren"):
    with st.spinner('Suche läuft...'):
        try:
            prompt = f"Suche nach Top-News zu {fokus} der letzten 12 Stunden. Zusammenfassung mit Links."
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"API-Fehler: {e}")
            st.info("Falls oben '404' steht, kopiere einen Namen aus der Liste oben in den Code (Zeile 24).")
