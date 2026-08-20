# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from knightcrawler.ai import summarize_article
import os
import sqlite3
from itemadapter import ItemAdapter


class KnightcrawlerPipeline:

    def open_spider(self, spider):

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.abspath(
            os.path.join(BASE_DIR, "..", "news.db")
        )

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS news
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                title
                                TEXT,
                                link
                                TEXT
                                UNIQUE,
                                source
                                TEXT,
                                date
                                TEXT,
                                summary
                                TEXT
                            )
                            """)

        self.conn.commit()

    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        # Clean title
        if adapter.get("title"):
            adapter["title"] = " ".join(adapter["title"].split())

        # Clean article text
        if adapter.get("summary"):
            adapter["summary"] = " ".join(adapter["summary"].split())

        # Convert relative links to absolute
        if adapter.get("link") and not adapter["link"].startswith("http"):
            adapter["link"] = spider.start_urls[0] + adapter["link"]

        # ==========================
        # AI Summarization
        # ==========================
        if adapter.get("summary"):
            try:
                ai_summary = summarize_article(adapter["summary"])
                adapter["summary"] = ai_summary
            except Exception as e:
                spider.logger.error(f"Gemini Error: {e}")

        # Save to database
        self.cursor.execute("""
            INSERT OR IGNORE INTO news
            (title, link, source, date, summary)
            VALUES (?, ?, ?, ?, ?)
        """, (
            adapter.get("title"),
            adapter.get("link"),
            adapter.get("source"),
            adapter.get("date"),
            adapter.get("summary")
        ))

        self.conn.commit()

        return item

    def close_spider(self, spider):
        self.conn.close()