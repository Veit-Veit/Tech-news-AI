import os
import time
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
import feedparser
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- 1. KONFIGURATION ---
DB_PATH = Path(__file__).parent / "news.db"

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- 2. DATENSTRUKTUR ---
class NewsAnalysis(BaseModel):
    summary: str = Field(description="Eine praegnante Zusammenfassung des Artikels in genau 2 Saetzen auf Deutsch.")
    rating: int = Field(description="Eine Wichtigkeitsbewertung von 1 bis 10 fuer IT-Entwickler.")
    category: str = Field(description="Kategorie des Themas, z. B. AI, Cloud, Security, Python oder DevOps.")

# --- 3. DATENBANK-FUNKTIONEN ---
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                link TEXT UNIQUE,
                category TEXT,
                rating INTEGER,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def article_exists(link: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM articles WHERE link = ?", (link,))
        return cursor.fetchone() is not None

def save_article(title: str, link: str, analysis: NewsAnalysis):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO articles (title, link, category, rating, summary)
            VALUES (?, ?, ?, ?, ?)
        """, (title, link, analysis.category, analysis.rating, analysis.summary))
        conn.commit()

# --- 4. KI-FUNKTION ---
def analyze_article(title: str, link: str, retries: int = 3) -> NewsAnalysis:
    prompt = f"Analysiere diesen Artikel:\nTitel: {title}\nLink: {link}"
    
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=NewsAnalysis,
                ),
            )
            return NewsAnalysis.model_validate_json(response.text)
        except APIError as e:
            if ("503" in str(e) or "429" in str(e)) and attempt < retries - 1:
                print(f"Limit/Server-Problem ({e.code}). Warte 15 Sekunden... ({attempt + 1}/{retries})")
                time.sleep(15)
            else:
                raise e

# --- 5. HAUPTPROGRAMM ---
def main():
    init_db()
    print("Hole die neuesten News von Hacker News...\n")
    
    feed = feedparser.parse("https://news.ycombinator.com/rss")
    
    for entry in feed.entries[:5]:
        print(f"Titel: {entry.title}")
        
        if article_exists(entry.link):
            print("Artikel bereits in DB vorhanden. Ueberspringe...")
            print("-" * 50)
            continue
        
        try:
            analysis = analyze_article(entry.title, entry.link)
            
            print(f"Top-Kategorie: {analysis.category}")
            print(f"Relevanz-Rating: {analysis.rating}/10")
            print(f"Zusammenfassung: {analysis.summary}")
            
            save_article(entry.title, entry.link, analysis)
            print("In SQLite gespeichert!")
            
            time.sleep(12)
            
        except Exception as err:
            print(f"Fehler bei der Analyse: {err}")
            
        print("-" * 50)

# --- 6. SKRIPT-START ---
if __name__ == "__main__":
    main()