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
    "🌍 Weltnews": {
        "description": "USA, China, Europa.",
        "feed_url": "https://www.tagesschau.de/xml/rss2/",
        "icon": "🌐"
    },
    "🤖 KI-Giganten": {
        "description": "Google, Microsoft, SAP, OpenAI.",
        "feed_url": "https://www.heise.de/rss/heise-atom.xml",
        "icon": "🚀"
    },
    "🇩🇪 DE im Ausland": {
        "description": "Wie berichten andere über DE?",
        "feed_url": "https://news.google.com/rss/search?q=Germany&hl=en-US&gl=US&ceid=US:en",
        "icon": "👁️"
    },
    "🥨 Lokal-Fokus BW": {
        "description": "Wirtschaft & Umwelt in Baden-Württemberg.",
        "feed_url": "https://www.swr.de/~rss/swraktuell/baden-wuerttemberg/swraktuell-bw-100.xml",
        "icon": "🏭"
    }
}

@st.cache_data(ttl=900) # Cache für 15 Minuten um API/Bandbreite zu schonen
def fetch_rss_headlines(feed_url, limit=4):
    """Holt die aktuellsten Schlagzeilen aus einem RSS Feed."""
    try:
        feed = feedparser.parse(feed_url)
        entries = feed.entries[:limit]
        headlines = [f"• {entry.title}" for entry in entries]
        return "\n".join(headlines) if headlines else "Keine aktuellen Meldungen gefunden."
    except Exception as e:
        return f"Fehler beim Laden des Feeds: {str(e)}"

# Verfügbare Text/Search Modelle
VERFUEGBARE_MODELLE = [
    'gemini-2.0-flash', # Default
    'gemini-2.5-flash',
    'gemini-2.5-pro',
    'gemini-3-flash-preview'
]

# State für Detail-Ansicht
if 'active_cluster' not in st.session_state:
    st.session_state.active_cluster = None
if 'last_analysis_result' not in st.session_state:
    st.session_state.last_analysis_result = None

# 4. SIDEBAR (KONFIGURATION)
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

# 5. HAUPTBEREICH & GRID DASHBOARD
st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="dashboard-title">📈 Executive News Monitor</h1>
        <div class="live-time">Status: LIVE • {datetime.now().strftime('%H:%M')} Uhr</div>
    </div>
""", unsafe_allow_html=True)

# Grid Layout: 2 Spalten
col1, col2 = st.columns(2)

# Funktion um Bento Cards zu rendern
def render_bento_card(cluster_name, cluster_data, col):
    with col:
        # Fetch headlines (cached, so it's fast and free)
        headlines_raw = fetch_rss_headlines(cluster_data["feed_url"])
        headlines_html = headlines_raw.replace("\n", "<br>")

        # Rendere die Bento-Box als zusammenhängendes HTML-Block
        bento_html = f"""
        <div class="bento-card">
            <div class="cluster-title">{cluster_data["icon"]} {cluster_name}</div>
            <div class="cluster-content">{headlines_html}</div>
        </div>
        """
        st.markdown(bento_html, unsafe_allow_html=True)

        # Deep Dive Button sitzt regulär darunter, damit er klickbar bleibt
        if st.button(f"🔍 Deep Dive", key=f"btn_{cluster_name}"):
            # Nur resetten, wenn sich das Cluster wirklich ändert, spart API Calls!
            if st.session_state.active_cluster != cluster_name:
                st.session_state.active_cluster = cluster_name
                st.session_state.last_analysis_result = None

# Rendern der 4 Cluster-Karten
clusters_list = list(NEWS_CLUSTERS.items())
render_bento_card(clusters_list[0][0], clusters_list[0][1], col1)
render_bento_card(clusters_list[1][0], clusters_list[1][1], col2)
render_bento_card(clusters_list[2][0], clusters_list[2][1], col1)
render_bento_card(clusters_list[3][0], clusters_list[3][1], col2)

st.divider()

# Platzhalter für die Detail-Ansicht oder den alten Button
st.subheader("Detail-Analyse")
if not st.session_state.active_cluster:
    st.info("Klicke auf 'Deep Dive' in einem der Cluster oben oder suche ein eigenes Thema in der Seitenleiste, um eine KI-gestützte Analyse der aktuellen Themen zu generieren.")

if st.session_state.active_cluster:
    active_topic = st.session_state.active_cluster

    st.markdown(f"### 🤖 Analyse für: **{active_topic}**")

    # Render cached result if available to save API quota on reruns
    if st.session_state.last_analysis_result:
        st.markdown(st.session_state.last_analysis_result["text"])
        st.success(f"Aus dem Cache geladen. Verwendetes Modell: **{st.session_state.last_analysis_result['model']}**")
    else:
        progress_bar = st.progress(0, text='Initialisiere KI Agenten...')

        # Retry-Logik gegen den 429-Fehler (Quota exceeded)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Bereite Kontext für den Prompt vor
                rss_context = ""
                if "Eigene Suche" in active_topic:
                    suchbegriff = active_topic.replace("Eigene Suche: ", "")
                    prompt_topic = f"Spezifische Recherche zum Thema: {suchbegriff}"
                else:
                    prompt_topic = f"Executive Summary für das Themenfeld: {active_topic}"
                    # Hole den spezifischen RSS-Feed für den aktiven Cluster als Kontext
                    for cluster_name, cluster_data in NEWS_CLUSTERS.items():
                        if cluster_name == active_topic:
                            feed_content = fetch_rss_headlines(cluster_data["feed_url"], limit=10)
                            rss_context = f"\n\n**Aktuelle RSS-Schlagzeilen als Basis-Kontext:**\n{feed_content}"
                            break

                prompt = f"""
                Erstelle einen übersichtlichen, professionellen Executive News Report in Deutsch.
                Konzentriere dich auf das folgende Cluster/Thema: {prompt_topic}

                Beziehe dich primär auf diese aktuellen Schlagzeilen (falls vorhanden) und ergänze sie durch dein eigenes Wissen oder Websuchen, um tiefergehende Informationen zu liefern:{rss_context}

                Aufbau:
                1. 📊 **Executive Summary**: 2-3 Sätze, die die generelle Nachrichtenlage in diesem Themenbereich zusammenfassen.
                2. 📰 **Top 3 Schlagzeilen & Deep Dive**:
                   - Nutze für jede Headline eine ### Überschrift.
                   - Schreibe eine prägnante Zusammenfassung (2-3 Sätze) zu jeder der Top 3 Nachrichten.
                   - WICHTIG: Füge am Ende jeder News zwingend einen direkten Link zur Quelle ein: [👉 Quelle](URL).
                3. 💡 **Management Takeaway**: Was bedeutet das konkret für Entscheidungsträger? (1 Satz)

                Trennzeichen:
                - Trenne die 3 Schlagzeilen-Sektionen optisch sauber mit --- Linien.
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

                # Cachen für spätere Streamlit Reruns
                st.session_state.last_analysis_result = {
                    "text": response.text,
                    "model": aktuelles_modell
                }

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

                                # Cachen für spätere Streamlit Reruns
                                st.session_state.last_analysis_result = {
                                    "text": response.text,
                                    "model": aktuelles_modell
                                }

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
