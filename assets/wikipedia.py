import lvgl as lv
from mpos import Activity, DisplayMetrics
import requests
import json
import logging
import re

log = logging.getLogger("WikipediaApp")

class WikipediaApp(Activity):
    def onCreate(self):
        logging.basicConfig(level=logging.INFO)
        self.name = "Wikipedia"
        log.info("WikipediaApp initialized")
        log.info("WikipediaApp.onCreate started")

        self.screen = lv.obj()
        self.screen.set_style_bg_color(lv.color_hex(0xFFFFFF), lv.PART.MAIN)

        # Create a search bar
        self.search_bar = lv.textarea(self.screen)
        self.search_bar.set_pos(10, 10)
        self.search_bar.set_size(DisplayMetrics.width() - 80, 40)
        self.search_bar.set_placeholder_text("Search Wikipedia...")
        self.search_bar.set_one_line(True)

        # Create a search button
        self.search_btn = lv.button(self.screen)
        self.search_btn.set_pos(DisplayMetrics.width() - 60, 10)
        self.search_btn.set_size(50, 40)
        label = lv.label(self.search_btn)
        label.set_text("Go")
        label.center()
        self.search_btn.add_event_cb(self.search_event_handler, lv.EVENT.CLICKED, None)

        # Create a text area for the article
        self.article_area = lv.textarea(self.screen)
        self.article_area.set_pos(10, 60)
        self.article_area.set_size(DisplayMetrics.width() - 20, DisplayMetrics.height() - 70)
        self.article_area.set_text("Wikipedia article will be displayed here.")

        self.setContentView(self.screen)
        log.info("WikipediaApp.onCreate finished")

    def search_event_handler(self, event):
        query = self.search_bar.get_text()
        if query:
            self.article_area.set_text("Searching...")
            log.info(f"Searching for: {query}")
            response = None
            try:
                url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&explaintext=true&titles={query}"
                headers = { "User-Agent": "MPOS-WikipediaApp/1.0 (https://github.com/quasikili/MPOS-Wikipedia; kili@quasikili.com)" }
                response = requests.get(url, headers=headers)

                data = response.json()
                pages = data["query"]["pages"]
                page_id = next(iter(pages))
                extract = pages[page_id].get("extract", "NO EXTRACT FOUND")

                # Clean the extract
                extract = re.sub(r'==.*?==', '', extract)
                extract = extract.strip()

                self.article_area.set_text(extract)

            except Exception as e:
                log.error(f"An error occurred: {e} (type: {type(e)})")
                if response is not None and hasattr(response, 'text'):
                    log.error(f"Response text was: {response.text}")
                self.article_area.set_text(f"Error: {e}")
