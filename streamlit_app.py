import streamlit as st
import google.generativeai as genai
import feedparser

# UI Setup
st.set_page_config(page_title="KI News Agent", page_icon="📰", layout="wide")

# API Key sicher laden
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("🤖 Dein persönlicher News-Agent")

def get_news():
    # Wir ziehen die neuesten Google News (Deutsch)
    feed = feedparser.parse("https://news.google.com/rss?hl=de&gl=DE&ceid=DE:de")
    return [f"Titel: {e.title} | Link: {e.link}" for e in feed.entries[:20]]

if st.button("News-Update jetzt generieren"):
    with st.spinner('Analysiere Weltlage...'):
        headlines = get_news()
        prompt = f"""
        Du bist ein News-Agent. Hier sind aktuelle Schlagzeilen: {headlines}
        
        Erstelle eine visuell ansprechende Zusammenfassung:
        1. **Welt-News**: Die 3 wichtigsten globalen Ereignisse.
        2. **Fokus-Themen**: Analysiere spezifisch [KI, Tech, Wirtschaft].
        
        Nutze für jeden News-Punkt folgendes Format:
        ### [Titel des Themas]
        - **Zusammenfassung**: Ein prägnanter Satz.
        - [👉 Mehr erfahren](Link aus den Daten einfügen)
        ---
        """
        response = model.generate_content(prompt)
        st.markdown(response.text)
