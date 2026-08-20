import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "webcrawling",
    "knightcrawler",
    "news.db"
)

DB_PATH = os.path.abspath(DB_PATH)


def get_articles(search="", date="", page=1, per_page=10):

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    conditions = []
    parameters = []

    if search:
        conditions.append("(title LIKE ? OR summary LIKE ? OR source LIKE ?)")
        parameters.extend([
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ])

    if date:
        conditions.append("date LIKE ?")
        parameters.append(f"{date}%")

    query = """
    SELECT title, source, date, summary, link
    FROM news
    """

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY date DESC"

    offset = (page - 1) * per_page

    query += " LIMIT ? OFFSET ?"

    parameters.extend([per_page, offset])

    cursor.execute(query, parameters)

    articles = cursor.fetchall()

    conn.close()

    return articles

def count_articles(search="", date=""):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    conditions = []
    parameters = []

    if search:
        conditions.append("(title LIKE ? OR summary LIKE ? OR source LIKE ?)")
        parameters.extend([
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ])

    if date:
        conditions.append("date LIKE ?")
        parameters.append(f"{date}%")

    query = "SELECT COUNT(*) FROM news"

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    cursor.execute(query, parameters)

    total = cursor.fetchone()[0]

    conn.close()

    return total

def get_dashboard_stats():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total articles
    cursor.execute("SELECT COUNT(*) FROM news")
    total_articles = cursor.fetchone()[0]

    # Today's articles
    cursor.execute("""
        SELECT COUNT(*)
        FROM news
        WHERE date LIKE date('now') || '%'
    """)
    today_articles = cursor.fetchone()[0]

    # Number of unique sources
    cursor.execute("SELECT COUNT(DISTINCT source) FROM news")
    total_sources = cursor.fetchone()[0]

    conn.close()

    return total_articles, today_articles, total_sources

