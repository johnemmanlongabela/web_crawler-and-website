import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess
import threading
import webbrowser
import os
import sys


class KnightCrawlerGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Government News Search System")
        self.root.geometry("1200x750")

        # =========================
        # Color Palette Definition
        # =========================
        self.BG_MAIN = "#1E1E2E"  # Main window background
        self.BG_PANEL = "#252538"  # Frame background
        self.BG_INPUT = "#313244"  # Entry & Text box background
        self.FG_TEXT = "#CDD6F4"  # Primary text color
        self.FG_MUTED = "#A6ADC8"  # Secondary/Muted text
        self.FG_HEADER = "#89B4FA"  # Title text color
        self.BG_HEADER_TBL = "#45475A"  # Table heading background
        self.FG_HEADER_TBL = "#F5E0DC"  # Table heading foreground
        self.BG_SELECT = "#585B70"  # Table row selection background
        self.FG_SELECT = "#FFFFFF"  # Table row selection foreground
        self.STATUS_BG = "#181825"  # Bottom status bar background

        self.root.configure(bg=self.BG_MAIN)

        # =========================
        # Styles
        # =========================
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        # Treeview Styles
        style.configure(
            "Treeview",
            background=self.BG_INPUT,
            foreground=self.FG_TEXT,
            fieldbackground=self.BG_INPUT,
            rowheight=30,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background=self.BG_HEADER_TBL,
            foreground=self.FG_HEADER_TBL,
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", self.BG_SELECT)],
            foreground=[("selected", self.FG_SELECT)]
        )

        # Entry Style
        style.configure(
            "Custom.TEntry",
            fieldbackground=self.BG_INPUT,
            foreground=self.FG_TEXT,
            insertcolor=self.FG_TEXT
        )

        # =========================
        # Main Layout Frames
        # =========================
        header_frame = tk.Frame(root, bg=self.BG_MAIN)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        content_frame = tk.Frame(root, bg=self.BG_MAIN)
        content_frame.pack(fill="both", expand=True, padx=20, pady=5)

        summary_frame = tk.Frame(root, bg=self.BG_MAIN)
        summary_frame.pack(fill="x", padx=20, pady=(5, 10))

        # =========================
        # Title & Article Counter
        # =========================
        title_frame = tk.Frame(header_frame, bg=self.BG_MAIN)
        title_frame.pack(side="left")

        title = tk.Label(
            title_frame,
            text="Government News Search",
            bg=self.BG_MAIN,
            fg=self.FG_HEADER,
            font=("Segoe UI", 20, "bold")
        )
        title.pack(anchor="w")

        # Article Count Display Badge
        self.count_label = tk.Label(
            title_frame,
            text="Total in DB: 0 articles | Showing: 0",
            bg=self.BG_MAIN,
            fg=self.FG_MUTED,
            font=("Segoe UI", 9, "italic")
        )
        self.count_label.pack(anchor="w")

        # =========================
        # Buttons & Search (Top Right)
        # =========================
        controls_frame = tk.Frame(header_frame, bg=self.BG_MAIN)
        controls_frame.pack(side="right", fill="y")

        tk.Label(
            controls_frame,
            text="Date (YYYY-MM-DD):",
            bg=self.BG_MAIN,
            fg=self.FG_TEXT,
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, padx=(0, 5))

        self.date_entry = ttk.Entry(
            controls_frame,
            width=15,
            font=("Segoe UI", 10),
            style="Custom.TEntry"
        )
        self.date_entry.grid(row=0, column=1, padx=(0, 15))

        self.search_btn = ttk.Button(
            controls_frame,
            text="Search",
            command=self.search,
            width=10
        )
        self.search_btn.grid(row=0, column=2, padx=(0, 10))

        self.update_btn = ttk.Button(
            controls_frame,
            text="↻ Update News",
            command=self.start_crawler,
            width=15
        )
        self.update_btn.grid(row=0, column=3)

        # =========================
        # Table
        # =========================
        columns = ("Title", "Source", "Date", "Link")

        scrollbar = ttk.Scrollbar(content_frame)
        self.table = ttk.Treeview(
            content_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.table.yview)
        scrollbar.pack(side="right", fill="y")

        self.table.heading("Title", text="Title")
        self.table.column("Title", width=400, stretch=True)

        self.table.heading("Source", text="Source")
        self.table.column("Source", width=150, stretch=False, anchor="center")

        self.table.heading("Date", text="Date")
        self.table.column("Date", width=120, stretch=False, anchor="center")

        self.table.heading("Link", text="Link")
        self.table.column("Link", width=250, stretch=True)

        self.table.pack(fill="both", expand=True)

        # =========================
        # AI Summary
        # =========================
        tk.Label(
            summary_frame,
            text="AI Summary",
            bg=self.BG_MAIN,
            fg=self.FG_HEADER,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.summary_box = tk.Text(
            summary_frame,
            height=6,
            bg=self.BG_INPUT,
            fg=self.FG_TEXT,
            insertbackground=self.FG_TEXT,
            wrap="word",
            font=("Segoe UI", 10),
            relief="flat",
            borderwidth=1,
            state="disabled"
        )
        self.summary_box.pack(fill="x")

        # =========================
        # Status Bar
        # =========================
        self.status = tk.Label(
            root,
            text=" Ready",
            bg=self.STATUS_BG,
            fg=self.FG_MUTED,
            font=("Segoe UI", 9),
            anchor="w",
            relief="flat"
        )
        self.status.pack(side="bottom", fill="x")

        # Event Bindings
        self.table.bind("<<TreeviewSelect>>", self.show_summary)
        self.table.bind("<Double-1>", self.open_link)

        # Load initial article count and default search list
        self.search()

    # =========================
    # Article Counter Helper
    # =========================
    def get_total_db_count(self):
        """Fetches the grand total count of articles saved in the SQLite database."""
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            DB_PATH = os.path.join(BASE_DIR, "knightcrawler", "news.db")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM news")
            total = cursor.fetchone()[0]
            conn.close()
            return total
        except Exception:
            return 0

    def update_article_counter(self, showing_count):
        total_in_db = self.get_total_db_count()
        self.count_label.config(
            text=f"Total in Database: {total_in_db:,} articles  |  Showing: {showing_count:,}"
        )

    # =========================
    # Search
    # =========================
    def search(self):
        search_date = self.date_entry.get().strip()

        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            DB_PATH = os.path.join(BASE_DIR, "knightcrawler", "news.db")

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            if search_date:
                cursor.execute("""
                    SELECT title, source, date, link
                    FROM news
                    WHERE date LIKE ?
                    ORDER BY date DESC
                """, (search_date + "%",))
            else:
                cursor.execute("""
                    SELECT title, source, date, link
                    FROM news
                    ORDER BY date DESC
                """)

            results = cursor.fetchall()
            self.table.delete(*self.table.get_children())

            for row in results:
                self.table.insert("", tk.END, values=row)

            conn.close()

            showing_count = len(results)
            self.update_article_counter(showing_count)
            self.status.config(text=f" ✓ {showing_count} article(s) displayed.", fg="#A6E3A1")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.status.config(text=" ⚠ Database Error", fg="#F38BA8")

    # =========================
    # Update News
    # =========================
    def start_crawler(self):
        self.update_btn.state(["disabled"])
        self.status.config(text=" ↻ Updating news... Please wait.", fg=self.FG_TEXT)
        threading.Thread(target=self.run_spider, daemon=True).start()

    def run_spider(self):
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "knightcrawler"))

        try:
            result = subprocess.run(
                [sys.executable, "-m", "scrapy", "crawl", "knightcrawler"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            if result.returncode == 0:
                self.root.after(0, lambda: self.finish_update(True))
            else:
                error_message = result.stderr
                self.root.after(0, lambda msg=error_message: self.finish_update(False, msg))

        except Exception as e:
            error_message = str(e)
            self.root.after(0, lambda msg=error_message: self.finish_update(False, msg))

    def finish_update(self, success, error=None):
        self.update_btn.state(["!disabled"])

        if success:
            self.status.config(text=" ✓ News updated successfully.", fg="#A6E3A1")
            messagebox.showinfo("Success", "News updated successfully!")
            self.search()
        else:
            self.status.config(text=" ⚠ Crawler failed.", fg="#F38BA8")
            messagebox.showerror("Crawler Error", error if error else "Failed to update news.")

    # =========================
    # Show Summary
    # =========================
    def show_summary(self, event=None):
        selected = self.table.focus()
        if not selected:
            return

        values = self.table.item(selected)["values"]
        if len(values) < 4:
            return

        link = values[3]

        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            DB_PATH = os.path.join(BASE_DIR, "knightcrawler", "news.db")

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT summary FROM news WHERE link=?", (link,))
            row = cursor.fetchone()
            conn.close()

            self.summary_box.config(state="normal")
            self.summary_box.delete("1.0", tk.END)

            if row and row[0]:
                self.summary_box.insert(tk.END, row[0])
            else:
                self.summary_box.insert(tk.END, "No AI summary available for this article.")

            self.summary_box.config(state="disabled")

        except Exception as e:
            self.summary_box.config(state="normal")
            self.summary_box.delete("1.0", tk.END)
            self.summary_box.insert(tk.END, f"Error loading summary: {str(e)}")
            self.summary_box.config(state="disabled")

    # =========================
    # Open Link
    # =========================
    def open_link(self, event):
        selected = self.table.focus()
        if selected:
            values = self.table.item(selected)["values"]
            if len(values) >= 4:
                webbrowser.open(values[3])


if __name__ == "__main__":
    root = tk.Tk()
    app = KnightCrawlerGUI(root)
    root.mainloop()