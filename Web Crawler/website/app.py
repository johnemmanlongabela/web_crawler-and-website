from flask import Flask, render_template, request
from database import (
    get_articles,
    count_articles,
    get_dashboard_stats
)

app = Flask(__name__)

@app.route("/")
def home():

    search = request.args.get("search", "")
    date = request.args.get("date", "")

    page = request.args.get("page", 1, type=int)

    per_page = 10

    articles = get_articles(search, date, page, per_page)

    dashboard_total, today_articles, total_sources = get_dashboard_stats()

    total_articles = count_articles(search, date)

    total_pages = (total_articles + per_page - 1) // per_page

    return render_template(
        "index.html",
        articles=articles,
        search=search,
        date=date,
        total_articles=dashboard_total,
        today_articles=today_articles,
        total_sources=total_sources,
        page=page,
        total_pages=total_pages
    )

if __name__ == "__main__":
    app.run(debug=True)