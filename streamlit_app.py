import streamlit as st
import google.generativeai as genai
import feedparser
import time

# 1. UI SETUP & DESIGN
st.set_page_config(
    page_title="Vanny's RSS News Agent", 
    page_icon="🗞️", 
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
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
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("API Key nicht gefunden! Bitte in den Secrets hinterlegen.")
    st.stop()

# Modelle (Hier nutzen wir jetzt die reine Text-Power ohne Search-Tool)
VERFUEGBARE_MODELLE = [
    'gemini-2.0-flash',
    'gemini-2.5-flash',
    'gemini-1.5-flash',
    'gemini-3-flash-preview'
]

# RSS FEEDS DEFINIEREN
RSS_URLS = [
    "https://news.google.com/rss?hl=de&gl=DE&ceid=DE:de", # Google News DE
    "https://www.tagesschau.de/infosprecher/index~rss2.xml" # Tagesschau
]

def fetch_rss_news():
    news_items = []
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]: # Top 10 pro Feed
            news_items.append(f"Titel: {entry.title}\nLink: {entry.link}\n")
    return "\n".join(news_items)

# 3. SIDEBAR
with st.sidebar:
    st.title("⚙️ Einstellungen")
    st.info("Dieser Agent nutzt stabile RSS-Feeds statt der Google-Suche.")

    primaeres_modell = st.selectbox("Primäres Modell:", VERFUEGBARE_MODELLE, index=0)
    fallback_modell = st.selectbox("Fallback Modell:", VERFUEGBARE_MODELLE, index=2)

    st.divider()
    fokus_themen = st.text_area("Spezifische Schwerpunkte:", "KI-Trends, Raumfahrt & E-Mobilität")
    st.caption("Status: RSS-Modus Aktiv (Stabil)")

# 4. HAUPTBEREICH
st.title("🤖 Dein RSS News-Agent")
st.write("Liest aktuelle RSS-Feeds und fasst sie für dich zusammen.")

if st.button("🚀 News-Update jetzt generieren"):
    progress_bar = st.progress(0, text='Lese RSS-Feeds aus...')
    
    # 1. News holen
    raw_news = fetch_rss_news()
    progress_bar.progress(30, text='Nachrichten an Gemini übertragen...')

    # Retry-Logik
    max_retries = 3
    for attempt in range(max_retries):
        try:
            aktuelles_modell = primaeres_modell
            model = genai.GenerativeModel(model_name=aktuelles_modell) # KEINE Tools nötig!

            prompt = f"""
            Hier sind aktuelle Nachrichten-Schlagzeilen aus RSS-Feeds:
            {raw_news}

            Bitte erstelle daraus eine Zusammenfassung auf Deutsch.
            Fokussiere dich besonders auf: {fokus_themen}.
            
            Struktur:
            ### 🌍 Top Weltgeschehen
            (Zusammenfassung der wichtigsten 3 Meldungen)
            
            ### 🔍 Deep Dive: {fokus_themen}
            (Relevante Infos aus den Feeds dazu)

            Wichtig: Füge am Ende jeder Meldung den passenden Link aus den bereitgestellten Daten ein.
            """

            progress_bar.progress(60, text=f'Analysiere mit {aktuelles_modell}...')
            response = model.generate_content(prompt)

            st.markdown(response.text)
            st.success(f"Update fertig! (Modell: {aktuelles_modell})")
            progress_bar.progress(100, text='Abgeschlossen!')
            break

        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                st.warning(f"Limit bei {aktuelles_modell} erreicht. Wechsel zum Fallback...")
                aktuelles_modell = fallback_modell
                time.sleep(5)
            else:
                st.error(f"Fehler: {e}")
                break

st.divider()
st.caption("Datenquelle: Google News & Tagesschau RSS • 2026")
