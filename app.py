import sqlite3
from pathlib import Path
import streamlit as st

# Absoluten Pfad zur news.db ermitteln (funktioniert auch auf Streamlit Cloud verlässlich)
DB_PATH = Path(__file__).resolve().parent / "news.db"

st.set_page_config(page_title="Tech-News AI Summarizer", layout="wide")
st.title("Tech-News AI Summarizer")
st.write("Automatisiert analysierte Hacker-News mit Gemini KI.")

if not DB_PATH.exists():
    st.error(f"Datenbank-Datei 'news.db' wurde unter dem Pfad `{DB_PATH}` nicht gefunden.")
else:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT title, link, category, rating, summary, created_at 
                FROM articles 
                ORDER BY id DESC
            """)
            articles = cursor.fetchall()
        except sqlite3.OperationalError as e:
            st.error(f"Fehler beim Auslesen der Tabelle 'articles': {e}")
            articles = []

    if not articles:
        st.info("Die Datenbank existiert auf GitHub, enthält aber aktuell noch 0 Artikel.")
    else:
        # Seitenleiste: Standard-Filter auf 1 setzen, damit initial ALLE Artikel angezeigt werden
        st.sidebar.header("Filter")
        min_rating = st.sidebar.slider("Mindest-Rating (1-10)", 1, 10, 1)
        
        categories = ["Alle"] + sorted(list(set(art[2] for art in articles if art[2])))
        selected_category = st.sidebar.selectbox("Kategorie auswählen", categories)

        displayed_count = 0
        for title, link, category, rating, summary, created_at in articles:
            if rating >= min_rating and (selected_category == "Alle" or category == selected_category):
                displayed_count += 1
                st.subheader(f"[{title}]({link})")
                st.caption(f"Kategorie: {category} | Rating: {rating}/10 | Erfasst am: {created_at}")
                st.write(summary)
                st.divider()

        if displayed_count == 0:
            st.warning("Keine Artikel entsprechen den ausgewählten Filtern.")