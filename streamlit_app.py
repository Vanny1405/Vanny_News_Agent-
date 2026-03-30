import streamlit as st
import google.generativeai as genai
import feedparser

# UI Setup
st.set_page_config(page_title="KI News Agent", page_icon="📰", layout="wide")

# API Key sicher laden
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3-flash-preview')

st.title("🤖 Dein persönlicher News-Agent")

def get_news():
    # Wir ziehen die neuesten Google News (Deutsch)
    feed = feedparser.parse("https://news.google.com/rss?hl=de&gl=DE&ceid=DE:de")
    return [f"Titel: {e.title} | Link: {e.link}" for e in feed.entries[:20]]

if st.button("News-Update jetzt generieren"):
    with st.spinner('Analysiere Weltlage...'):
        headlines = get_news()
        
        if not headlines:
            st.error("Konnte keine News abrufen. Versuche es in ein paar Minuten noch einmal.")
        else:
            prompt = f"""
            Analysiere diese Schlagzeilen: {headlines}
            Erstelle eine visuelle Zusammenfassung mit Welt-News und Schwerpunkten (KI, Tech, Wirtschaft).
            Nutze Markdown-Überschriften und Emojis.
            """
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Fehler bei der KI-Generierung: {e}")
