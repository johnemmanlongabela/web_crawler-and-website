import scrapy
from datetime import date
from dateutil import parser
from scrapy.http import HtmlResponse
from knightcrawler.items import KnightcrawlerItem


class Knightcrawler(scrapy.Spider):
    name = "knightcrawler"

    allowed_domains = [
        "pna.gov.ph",
        "inquirer.net",
        "pco.gov.ph",
    ]

    start_urls = [
        "https://www.pna.gov.ph/",
        "https://www.inquirer.net/",
        "https://pco.gov.ph/",
    ]

    government_keywords = [
        "government",
        "president",
        "malacañang",
        "senate",
        "congress",
        "department of national defense",
        "executive",
        "cabinet",
        "philippine government",
        "foreign policy",
        "administration",
        "china",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_links = set()

    def parse(self, response):

        if not isinstance(response, HtmlResponse):
            return

        self.logger.info(f"Crawling homepage: {response.url}")

        links = response.css("a::attr(href)").getall()

        for href in links:

            if not href:
                continue

            url = response.urljoin(href)

            if url in self.seen_links:
                continue

            self.seen_links.add(url)

            lower = url.lower()

            # Skip non-html files
            if lower.endswith((
                ".pdf",
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".svg",
                ".zip",
                ".doc",
                ".docx",
                ".xls",
                ".xlsx",
                ".ppt",
                ".pptx",
            )):
                continue

            # Only follow links inside allowed domains
            if any(domain in url for domain in self.allowed_domains):
                yield response.follow(
                    url,
                    callback=self.parse_article,
                    errback=self.handle_error
                )

        # Follow pagination
        next_page = response.css(
            "a.next::attr(href), a[rel='next']::attr(href)"
        ).get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):

        if not isinstance(response, HtmlResponse):
            return

        title = (
                response.css("h1::text").get()
                or response.css("meta[property='og:title']::attr(content)").get()
                or ""
        ).strip()

        if not title:
            return

        # ==========================
        # Get publication date
        # ==========================
        published = (
                response.css("time::attr(datetime)").get()
                or response.css(
            "meta[property='article:published_time']::attr(content)"
        ).get()
                or response.css("time::text").get()
        )

        # Only scrape today's news
        if published:
            try:
                article_date = parser.parse(published).date()

                if article_date != date.today():
                    return

            except (ValueError, TypeError):
                # Skip articles with invalid dates
                return
        else:
            # Skip articles with no publication date
            return

        # ==========================
        # Extract article content
        # ==========================
        paragraphs = response.css("""
            article p::text,
            .article-body p::text,
            .entry-content p::text,
            .story-body p::text,
            .content p::text,
            p::text
        """).getall()

        summary = " ".join(
            p.strip()
            for p in paragraphs
            if p.strip()
        )

        if not summary:
            return

        # ==========================
        # Government keyword filter
        # ==========================
        text = (title + " " + summary).lower()

        if not any(
                keyword in text
                for keyword in self.government_keywords
        ):
            return

        # ==========================
        # Create item
        # ==========================
        item = KnightcrawlerItem()

        item["title"] = title
        item["link"] = response.url
        item["source"] = response.url.split("/")[2]
        item["date"] = published
        item["summary"] = summary

        self.logger.info(f"Scraped: {title}")

        yield item

    def handle_error(self, failure):
        self.logger.error(f"Failed request: {failure.request.url}")