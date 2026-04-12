import time
from datetime import datetime
import google.generativeai as genai
import streamlit as st
import feedparser

# 1. UI SETUP & DESIGN
st.set_page_config(
    page_title="Executive News Monitor",
    page_icon="📈",
    layout="wide"
)

# Custom CSS für den Executive Bento-Box Look
st.markdown("""
    <style>
    /* Generelle Schriftart und Hintergrund */
    html, body, [class*="css"]  {
        font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    .main {
        background-color: #f0f2f5;
    }

    /* Bento-Box Karten Styling */
    .bento-card {
        background-color: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        height: 100%;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        margin-bottom: 20px;
    }
    .bento-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }

    /* Modernere Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        opacity: 0.9;
    }

    /* Überschriften */
    .cluster-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 12px;
        border-bottom: 2px solid #edf2f7;
        padding-bottom: 8px;
    }
    .cluster-content {
        color: #4a5568;
        font-size: 0.95rem;
        margin-bottom: 20px;
        min-height: 80px;
    }

    /* Header Area */
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 20px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 30px;
    }
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #2d3748;
        margin: 0;
    }
    .live-time {
        font-size: 1.1rem;
        color: #718096;
        font-weight: 500;
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

# 3. RSS FEED DEFINITION & ABFRAGE
NEWS_CLUSTERS = {
    "Weltnews (Global & Top DE)": {
        "description": "Wichtige globale Ereignisse.",
        "feeds": [
            "https://www.tagesschau.de/infosprecher/index~rss2.xml",
            "https://www.zdf.de/rss/zdf/nachrichten",
            "http://feeds.bbci.co.uk/news/world/rss.xml"
        ],
        "icon": "🌍"
    },
    "KI-Giganten (Google, OpenAI, MSFT)": {
        "description": "Die neuesten Entwicklungen in der KI.",
        "feeds": [
            "https://www.heise.de/rss/heise-atom.xml",
            "https://openai.com/news/rss.xml",
            "https://blog.google/technology/ai/rss/",
            "https://techcrunch.com/category/artificial-intelligence/feed/"
        ],
        "icon": "🤖"
    },
    "Wirtschaft & Spiegel der Weltpresse": {
        "description": "Wirtschaftsnachrichten und internationale Perspektiven.",
        "feeds": [
            "https://www.spiegel.de/wirtschaft/index.rss",
            "https://www.manager-magazin.de/index.rss",
            "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/europe/rss.xml"
        ],
        "icon": "🇩🇪"
    },
    "BW-Lokal, Raumfahrt & E-Mobilität": {
        "description": "Lokalnachrichten aus BW, Weltraumforschung und Elektromobilität.",
        "feeds": [
            "https://www.swr.de/swraktuell/baden-wuerttemberg/index~rss2.xml",
            "https://www.esa.int/rssfeed/Our_Missions",
            "https://electrek.co/feed/"
        ],
        "icon": "🏭"
    }
}

@st.cache_data(ttl=900)
def fetch_aggregated_rss_data(feeds, limit_per_feed=3):
    """Holt Schlagzeilen aus mehreren RSS Feeds und fasst sie als Liste von dicts zusammen."""
    aggregated_entries = []
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            # Begrenze die Anzahl der Einträge pro Feed, um eine bunte Mischung zu erhalten (z.B. max 3)
            # Insgesamt streben wir 5-8 Einträge pro Cluster an.
            for entry in feed.entries[:limit_per_feed]:
                title = entry.get('title', 'Ohne Titel')
                link = entry.get('link', '#')
                aggregated_entries.append({"title": title, "link": link})
        except Exception:
            pass # Fehlerhafte Feeds überspringen

    return aggregated_entries

# Verfügbare Text Modelle
VERFUEGBARE_MODELLE = [
    'gemini-3.1-flash-lite', # Default laut Auftrag
    'gemini-3-flash-preview',
    'gemini-2.5-flash',
    'gemini-2.0-flash'
]

# State für Detail-Ansicht
if 'active_cluster' not in st.session_state:
    st.session_state.active_cluster = None
if 'last_analysis_result' not in st.session_state:
    st.session_state.last_analysis_result = None

# 4. SIDEBAR (NAVIGATION & KONFIGURATION)
with st.sidebar:
    st.title("🧭 Navigator")    
    app_mode = st.radio("Wähle ein Modul:", ["📰 News-Monitor", "🧠 Brain Training"])

    st.divider()
    
    if app_mode == "📰 News-Monitor":
        st.title("⚙️ Einstellungen")
        st.info("Wähle deine Modelle für die KI-Zusammenfassung.")

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

        eigenes_thema = st.text_area(
            "Eigenes Thema überwachen:",
            help="Gib ein Thema ein, um es zu analysieren. (z.B. Bitcoin, Tesla...)"
        )
        if st.button("Thema analysieren"):
            if eigenes_thema:
                st.session_state.active_cluster = f"Eigene Suche: {eigenes_thema}"
                st.session_state.last_analysis_result = None # Force re-fetch for new topic

        st.divider()
        st.caption("Status: Verbunden mit Gemini API")

        # Diagnose-Option (falls du mal die Modell-Liste brauchst)
        with st.expander("System-Diagnose"):
            if st.button("Verfügbare Modelle auflisten"):
                models = [m.name for m in genai.list_models()]
                st.code(models)
    else:
        primaeres_modell = VERFUEGBARE_MODELLE[0]
        fallback_modell = VERFUEGBARE_MODELLE[1]

# 5. HAUPTBEREICH & GRID DASHBOARD
if app_mode == "📰 News-Monitor":
    st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="dashboard-title">📈 Executive News Monitor</h1>
        <div class="live-time">Status: LIVE • {datetime.now().strftime('%H:%M')} Uhr</div>
    </div>
""", unsafe_allow_html=True)

    # Grid Layout: 2 Spalten
    col1, col2 = st.columns(2)

@st.cache_data(ttl=900)
def generate_cluster_summary(cluster_name, rss_data, model_name):
    """
    Nutzt Gemini um die reinen RSS Daten ins Deutsche zu übersetzen
    und 5 prägnante Bulletpoints zu generieren.
    """
    if not rss_data:
        return "Keine aktuellen Nachrichten verfügbar."

    rss_text = "\n".join([f"- {item['title']} (URL: {item['link']})" for item in rss_data])

    prompt = f"""
    Du bist ein erstklassiger Executive Assistant. Deine Aufgabe ist es, die folgenden internationalen und nationalen Schlagzeilen für das Dashboard-Modul '{cluster_name}' zusammenzufassen.

    AUFGABE:
    1. Übersetze alle englischsprachigen oder fremdsprachigen Schlagzeilen in professionelles Deutsch.
    2. Erstelle exakt 5 prägnante, aussagekräftige Bullet Points, die die wichtigsten Entwicklungen aus den Rohdaten zusammenfassen.
    3. Verwende HTML-Listen (`<ul><li>...</li></ul>`), damit die Ausgabe sauber im Dashboard formatiert ist.
    4. KEINE Links in den Bulletpoints! Links werden später in der Detailansicht angezeigt.
    5. Schreibe keinen Einleitungssatz, sondern starte direkt mit der HTML-Liste.

    ROHDATEN (RSS-Schlagzeilen):
    {rss_text}
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(model_name=model_name) # KEIN google_search_retrieval Tool hier!
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                if attempt < max_retries - 1:
                    time.sleep((2 ** attempt) * 5)
                else:
                    return f"API-Limit ({model_name}) nach Retries erreicht. Fallback benötigt."
            else:
                 return f"Fehler bei der KI-Analyse: {str(e)}"

# Funktion um Bento Cards zu rendern
def render_bento_card(cluster_name, cluster_data, col, primary_model, fallback_model):
    with col:
        # 1. Fetch RAW RSS Data
        rss_data = fetch_aggregated_rss_data(cluster_data["feeds"])

        # 2. Generiere KI Zusammenfassung (Caches über @st.cache_data in der Funktion)
        summary_html = generate_cluster_summary(cluster_name, rss_data, primary_model)

        # Basic Fallback check inside the card generator if primary fails with 429
        if "Fallback benötigt" in summary_html and primary_model != fallback_model:
            summary_html = generate_cluster_summary(cluster_name, rss_data, fallback_model)

        # Rendere die Bento-Box als zusammenhängendes HTML-Block
        bento_html = f"""
        <div class="bento-card">
            <div class="cluster-title">{cluster_data["icon"]} {cluster_name}</div>
            <div class="cluster-content">{summary_html}</div>
        </div>
        """
        st.markdown(bento_html, unsafe_allow_html=True)

        # Deep Dive Button sitzt regulär darunter, damit er klickbar bleibt
        if st.button(f"🔍 Details", key=f"btn_{cluster_name}"):
            if st.session_state.active_cluster != cluster_name:
                st.session_state.active_cluster = cluster_name
                st.session_state.last_analysis_result = None

if app_mode == "📰 News-Monitor":
    # Rendern der 4 Cluster-Karten
    clusters_list = list(NEWS_CLUSTERS.items())
    with st.spinner('Führe KI-Analyse für das Dashboard aus (Modelle übersetzen & aggregieren RSS-Feeds)...'):
        render_bento_card(clusters_list[0][0], clusters_list[0][1], col1, primaeres_modell, fallback_modell)
        render_bento_card(clusters_list[1][0], clusters_list[1][1], col2, primaeres_modell, fallback_modell)
        render_bento_card(clusters_list[2][0], clusters_list[2][1], col1, primaeres_modell, fallback_modell)
        render_bento_card(clusters_list[3][0], clusters_list[3][1], col2, primaeres_modell, fallback_modell)

    st.divider()

    # Platzhalter für die Detail-Ansicht oder den alten Button
    st.subheader("📰 Deep Dive & Original-Quellen")
    if not st.session_state.active_cluster:
        st.info("Klicke auf 'Details' in einem der Cluster oben, um die Original-Schlagzeilen und Quell-Links einzusehen.")

    if st.session_state.active_cluster:
        active_topic = st.session_state.active_cluster
        st.markdown(f"#### Rohdaten für: **{active_topic}**")

        if "Eigene Suche" in active_topic:
             st.warning("Die Detailansicht für die Eigene Suche ist noch in Entwicklung. Bitte wähle ein vorgefertigtes Cluster für Deep Dives.")
        else:
            # Finde das ausgewählte Cluster
            selected_cluster_data = NEWS_CLUSTERS.get(active_topic)
            if selected_cluster_data:
                # Hole die (bereits gecacheten) RSS Daten nochmal
                rss_data = fetch_aggregated_rss_data(selected_cluster_data["feeds"], limit_per_feed=5)

                if rss_data:
                    for item in rss_data:
                        # Clean up the output using Streamlit elements
                        st.markdown(f"🔗 **[{item['title']}]({item['link']})**")
                else:
                    st.info("Keine Rohdaten für dieses Cluster gefunden.")

    st.divider()
    st.caption("Powered by Gemini Models & Streamlit Cloud • 2026")

elif app_mode == "🧠 Brain Training":
    from math_ui import render_brain_training
    render_brain_training()
