import sqlite3
from pathlib import Path
import streamlit as st

# Pfad zur SQLite-Datenbank festlegen
DB_PATH = Path(__file__).parent / "news.db"

# Seiteneinstellungen für Streamlit festlegen
st.set_page_config(page_title="Tech-News AI Summarizer", layout="wide")
st.title("Tech-News AI Summarizer")
st.write("Automatisiert analysierte Hacker-News mit Gemini KI.")

# Prüfen, ob die Datenbank existiert
if not DB_PATH.exists():
    st.warning("Keine Datenbank 'news.db' gefunden. Führe zuerst main.py aus.")
else:
    # Daten aus SQLite auslesen
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, link, category, rating, summary, created_at 
            FROM articles 
            ORDER BY id DESC
        """)
        articles = cursor.fetchall()

    if not articles:
        st.info("Noch keine Artikel in der Datenbank vorhanden.")
    else:
        # Filter-Steuerung in der linken Seitenleiste
        st.sidebar.header("Filter")
        min_rating = st.sidebar.slider("Mindest-Rating (1-10)", 1, 10, 5)
        
        categories = ["Alle"] + sorted(list(set(art[2] for art in articles if art[2])))
        selected_category = st.sidebar.selectbox("Kategorie auswählen", categories)

        # Artikel filtern und darstellen
        displayed_count = 0
        for title, link, category, rating, summary, created_at in articles:
            # Filterprüfung
            if rating >= min_rating and (selected_category == "Alle" or category == selected_category):
                displayed_count += 1
                
                # Einzelnen Artikel anzeigen
                st.subheader(f"[{title}]({link})")
                st.caption(f"Kategorie: {category} | Rating: {rating}/10 | Erfasst am: {created_at}")
                st.write(summary)
                st.divider()

        if displayed_count == 0:
            st.warning("Keine Artikel entsprechen den ausgewählten Filtern.")