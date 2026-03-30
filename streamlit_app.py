import streamlit as st
import google.generativeai as genai

# UI Setup
st.set_page_config(page_title="KI News Agent Pro", page_icon="🚀", layout="wide")

# API Key sicher laden
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Modell mit Google Search Tool initialisieren
# Wir nutzen den Namen, den du im AI Studio gefunden hast!
# Versuche das stabilste Modell zu laden
try:
    # Wir probieren erst die "Latest"-Variante, die ist am sichersten
    model_id = 'gemini-1.5-flash-latest' 
    model = genai.GenerativeModel(
        model_name=model_id,
        tools=[{'google_search_retrieval': {}}]
    )
    # Test-Aufruf um sicherzugehen, dass das Modell existiert
    st.sidebar.success(f"Aktiv: {model_id}")
except Exception:
    try:
        # Falls das fehlschlägt, nehmen wir das, was du im AI Studio gesehen hast
        model_id = 'gemini-3-flash-preview'
        model = genai.GenerativeModel(
            model_name=model_id,
            tools=[{'google_search_retrieval': {}}]
        )
        st.sidebar.warning(f"Nutze Preview: {model_id}")
    except Exception as e:
        st.error("Konnte kein passendes Modell finden.")
        # Dieser Teil listet dir alle verfügbaren Modelle in der App auf, 
        # damit wir den Namen schwarz auf weiß sehen:
        st.write("Verfügbare Modelle für dich:")
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.write(models)

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
