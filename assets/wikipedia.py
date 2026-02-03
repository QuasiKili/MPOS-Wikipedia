import lvgl as lv
from mpos import Activity, Intent, DisplayMetrics, MposKeyboard
import requests
import json
import logging
import re

log = logging.getLogger("WikipediaApp")

def normalize_text(text):
    """
    Normalize Unicode characters in Wikipedia text to ASCII equivalents.
    
    This function handles various special characters that may appear in Wikipedia
    articles and replaces them with ASCII-compatible alternatives for better
    display compatibility.
    
    Args:
        text: The text string to normalize
        
    Returns:
        The normalized text string
    """
    # Dictionary mapping Unicode characters to their ASCII equivalents
    unicode_map = {
        # Dashes and hyphens
        '\u2013': ' - ',      # en-dash
        '\u2014': ' - ',      # em-dash
        '\u2011': '-',        # non-breaking hyphen
        '\u2010': '-',        # hyphen
        
        # Quotes
        '\u2018': "'",        # left single quotation mark
        '\u2019': "'",        # right single quotation mark
        '\u201c': '"',        # left double quotation mark
        '\u201d': '"',        # right double quotation mark
        '\u2032': "'",        # prime (often used as apostrophe)
        '\u2033': '"',        # double prime
        
        # Spaces
        '\u00a0': ' ',        # non-breaking space
        '\u2009': ' ',        # thin space
        '\u200a': ' ',        # hair space
        
        # Latin characters with diacritics (common in Wikipedia)
        '\u00e0': 'a',        # à
        '\u00e1': 'a',        # á
        '\u00e2': 'a',        # â
        '\u00e3': 'a',        # ã
        '\u00e4': 'a',        # ä
        '\u00e5': 'a',        # å
        '\u00e6': 'ae',       # æ
        '\u00e7': 'c',        # ç
        '\u00e8': 'e',        # è
        '\u00e9': 'e',        # é
        '\u00ea': 'e',        # ê
        '\u00eb': 'e',        # ë
        '\u00ec': 'i',        # ì
        '\u00ed': 'i',        # í
        '\u00ee': 'i',        # î
        '\u00ef': 'i',        # ï
        '\u00f0': 'd',        # ð
        '\u00f1': 'n',        # ñ
        '\u00f2': 'o',        # ò
        '\u00f3': 'o',        # ó
        '\u00f4': 'o',        # ô
        '\u00f5': 'o',        # õ
        '\u00f6': 'o',        # ö
        '\u00f8': 'o',        # ø
        '\u00f9': 'u',        # ù
        '\u00fa': 'u',        # ú
        '\u00fb': 'u',        # û
        '\u00fc': 'u',        # ü
        '\u00fd': 'y',        # ý
        '\u00fe': 'th',       # þ
        '\u00ff': 'y',        # ÿ
        '\u0101': 'a',        # ā (a with macron)
        '\u0113': 'e',        # ē (e with macron)
        '\u012b': 'i',        # ī (i with macron)
        '\u014d': 'o',        # ō (o with macron)
        '\u016b': 'u',        # ū (u with macron)
        
        # Uppercase variants
        '\u00c0': 'A',        # À
        '\u00c1': 'A',        # Á
        '\u00c2': 'A',        # Â
        '\u00c3': 'A',        # Ã
        '\u00c4': 'A',        # Ä
        '\u00c5': 'A',        # Å
        '\u00c6': 'AE',       # Æ
        '\u00c7': 'C',        # Ç
        '\u00c8': 'E',        # È
        '\u00c9': 'E',        # É
        '\u00ca': 'E',        # Ê
        '\u00cb': 'E',        # Ë
        '\u00cc': 'I',        # Ì
        '\u00cd': 'I',        # Í
        '\u00ce': 'I',        # Î
        '\u00cf': 'I',        # Ï
        '\u00d0': 'D',        # Ð
        '\u00d1': 'N',        # Ñ
        '\u00d2': 'O',        # Ò
        '\u00d3': 'O',        # Ó
        '\u00d4': 'O',        # Ô
        '\u00d5': 'O',        # Õ
        '\u00d6': 'O',        # Ö
        '\u00d8': 'O',        # Ø
        '\u00d9': 'U',        # Ù
        '\u00da': 'U',        # Ú
        '\u00db': 'U',        # Û
        '\u00dc': 'U',        # Ü
        '\u00dd': 'Y',        # Ý
        '\u00de': 'TH',       # Þ
        '\u0100': 'A',        # Ā (A with macron)
        '\u0112': 'E',        # Ē (E with macron)
        '\u012a': 'I',        # Ī (I with macron)
        '\u014c': 'O',        # Ō (O with macron)
        '\u016a': 'U',        # Ū (U with macron)
        
        # Other common symbols
        '\u2022': '*',        # bullet
        '\u2026': '...',      # ellipsis
        '\u00b0': ' deg',     # degree symbol
        '\u00d7': 'x',        # multiplication sign
        '\u00f7': '/',        # division sign
        '\xa5': 'yen',          # yen symbol
    }
    
    # Apply all replacements
    for unicode_char, replacement in unicode_map.items():
        text = text.replace(unicode_char, replacement)
    
    return text

def url_encode(text):
    """
    URL encode a string for use in query parameters.
    Handles spaces, parentheses, and other special characters.
    
    This is a MicroPython-compatible implementation since urllib is not available.
    """
    # Characters that need encoding and their encoded values
    encoding_map = {
        ' ': '%20',
        '!': '%21',
        '"': '%22',
        '#': '%23',
        '$': '%24',
        '%': '%25',
        '&': '%26',
        "'": '%27',
        '(': '%28',
        ')': '%29',
        '*': '%2A',
        '+': '%2B',
        ',': '%2C',
        '/': '%2F',
        ':': '%3A',
        ';': '%3B',
        '=': '%3D',
        '?': '%3F',
        '@': '%40',
        '[': '%5B',
        '\\': '%5C',
        ']': '%5D',
        '^': '%5E',
        '`': '%60',
        '{': '%7B',
        '|': '%7C',
        '}': '%7D',
        '~': '%7E',
        '<': '%3C',
        '>': '%3E',
    }
    
    result = text
    # Encode % first to avoid double-encoding
    if '%' in result:
        result = result.replace('%', '%25')
    
    # Then encode all other characters
    for char, encoded in encoding_map.items():
        if char != '%':  # Skip % since we already handled it
            result = result.replace(char, encoded)
    
    return result

class WikipediaApp(Activity):
    def onCreate(self):
        logging.basicConfig(level=logging.INFO)
        self.name = "Wikipedia"
        log.info("WikipediaApp initialized")
        log.info("WikipediaApp.onCreate started")

        self.screen = lv.obj()
        # Background color removed to allow theme adaptation

        # Create a search bar
        self.search_bar = lv.textarea(self.screen)
        self.search_bar.set_pos(10, 10)
        self.search_bar.set_size(DisplayMetrics.width() - 80, 40)
        self.search_bar.set_placeholder_text("Search Wikipedia...")
        self.search_bar.set_one_line(True)

        # Create keyboard for search bar
        self.keyboard = MposKeyboard(self.screen)
        self.keyboard.set_textarea(self.search_bar)
        self.keyboard.remove_flag(lv.obj.FLAG.HIDDEN)  # Show keyboard on search screen

        # Create a search button
        self.search_btn = lv.button(self.screen)
        self.search_btn.set_pos(DisplayMetrics.width() - 60, 10)
        self.search_btn.set_size(50, 40)
        label = lv.label(self.search_btn)
        label.set_text("Go")
        label.center()
        self.search_btn.add_event_cb(self.search_event_handler, lv.EVENT.CLICKED, None)

        # Create a container for the article content
        # Initially hidden on search screen
        self.article_container = lv.obj(self.screen)
        self.article_container.set_pos(10, 10)
        self.article_container.set_size(DisplayMetrics.width() - 20, DisplayMetrics.height() - 20)
        self.article_container.set_style_border_width(0, 0)
        self.article_container.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self.article_container.add_flag(lv.obj.FLAG.HIDDEN)  # Hidden initially

        # Create a label for the article title (initially hidden)
        self.title_label = lv.label(self.article_container)
        self.title_label.set_long_mode(lv.label.LONG_MODE.WRAP)
        self.title_label.set_width(DisplayMetrics.width() - 40)
        self.title_label.set_style_text_font(lv.font_montserrat_24, lv.PART.MAIN)
        primary_color = lv.theme_get_color_primary(None)
        self.title_label.set_style_text_color(primary_color, lv.PART.MAIN)
        self.title_label.set_text("")

        # Create a label for the article content
        self.article_label = lv.label(self.article_container)
        self.article_label.set_long_mode(lv.label.LONG_MODE.WRAP)
        self.article_label.set_recolor(True)
        self.article_label.set_width(DisplayMetrics.width() - 40)
        self.article_label.set_text("")
        self.article_label.align_to(self.title_label, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 10)

        # Create a floating back button (similar to settings button in appstore.py)
        self.back_btn = lv.button(self.screen)
        margin = 15
        btn_size = 50
        self.back_btn.set_size(btn_size, btn_size)
        self.back_btn.align(lv.ALIGN.TOP_RIGHT, -margin, 10)
        self.back_btn.add_event_cb(self.back_button_handler, lv.EVENT.CLICKED, None)
        self.back_btn.add_flag(lv.obj.FLAG.HIDDEN)  # Hidden initially
        back_label = lv.label(self.back_btn)
        back_label.set_text(lv.SYMBOL.KEYBOARD)
        back_label.set_style_text_font(lv.font_montserrat_18, lv.PART.MAIN)
        back_label.center()

        self.setContentView(self.screen)
        log.info("WikipediaApp.onCreate finished")

    def show_search_screen(self):
        """Switch to search screen view"""
        # Show search elements
        self.search_bar.remove_flag(lv.obj.FLAG.HIDDEN)
        self.search_btn.remove_flag(lv.obj.FLAG.HIDDEN)
        self.keyboard.remove_flag(lv.obj.FLAG.HIDDEN)
        
        # Hide reading elements
        self.article_container.add_flag(lv.obj.FLAG.HIDDEN)
        self.back_btn.add_flag(lv.obj.FLAG.HIDDEN)
        
        log.info("Switched to search screen")

    def show_reading_screen(self):
        """Switch to reading screen view"""
        # Hide search elements
        self.search_bar.add_flag(lv.obj.FLAG.HIDDEN)
        self.search_btn.add_flag(lv.obj.FLAG.HIDDEN)
        self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)
        
        # Show reading elements
        self.article_container.remove_flag(lv.obj.FLAG.HIDDEN)
        self.back_btn.remove_flag(lv.obj.FLAG.HIDDEN)
        
        log.info("Switched to reading screen")

    def back_button_handler(self, event):
        """Handle back button click to return to search screen"""
        self.show_search_screen()

    def search_event_handler(self, event):
        query = self.search_bar.get_text()
        if not query:
            return

        self.article_label.set_text(f"Searching for '{query}'...")
        lv.refr_now(None)
        log.info(f"Searching for: {query}")

        response = None
        try:
            url = (
                "https://en.wikipedia.org/w/api.php"
                "?action=query"
                "&format=json"
                "&redirects=1"
                "&prop=extracts|pageprops|links"
                "&explaintext=true"
                "&pllimit=60"
                f"&titles={url_encode(query)}"
            )

            headers = {
                "User-Agent": "MPOS-WikipediaApp/1.0 (https://github.com/quasikili/MPOS-Wikipedia; kili@quasikili.com)"
            }

            response = requests.get(url, headers=headers)
            data = response.json()

            pages = data["query"]["pages"]
            page_id = next(iter(pages))

            if page_id == "-1":
                self.article_label.set_text(f"Article '{query}' not found.")
                return

            page = pages[page_id]
            
            # Get article title
            article_title = page.get("title", query)

            # ---------- DISAMBIGUATION HANDLING ----------
            if "pageprops" in page and "disambiguation" in page["pageprops"]:
                links = page.get("links", [])
                titles = []

                for link in links:
                    # ns == 0 → real articles only
                    if link.get("ns") == 0:
                        title = link.get("title")
                        if title:
                            titles.append(title)

                if not titles:
                    self.article_label.set_text(
                        f"'{query}' is a disambiguation page, but no articles were found."
                    )
                    return

                log.info(f"Disambiguation titles: {titles}")
                self.create_disambiguation_popup(query, titles)
                return
            # -------------------------------------------

            extract = page.get("extract", "NO EXTRACT FOUND")
            extract = normalize_text(extract)

            # Get primary theme color for headings
            primary_color = lv.theme_get_color_primary(None)
            # Convert LVGL color to hex string for recolor syntax
            color_hex = f"{primary_color.red:02x}{primary_color.green:02x}{primary_color.blue:02x}"
            
            # Style headings with theme color and visual hierarchy
            # # Use negative lookahead/lookbehind to avoid matching nested patterns
            # # Level 3 headings (smaller) - keep === markers visible in theme color
            # extract = re.sub(r'(?<!=)=== (.*?) ===(?!=)', rf'#{color_hex} === \1 ===#', extract)
            # # Level 2 headings (larger) - keep == markers visible in theme color
            # extract = re.sub(r'(?<!=)== (.*?) ==(?!=)', rf'#{color_hex} == \1 ==#', extract)

            # Level 3 headings first
            # extract = re.sub(
            #     r'=== ([^=]+) ===',
            #     r'#%s === \1 ===#' % color_hex,
            #     extract
            # )

            # # Level 2 headings second
            # extract = re.sub(
            #     r'== ([^=]+) ==',
            #     r'#%s == \1 ==#' % color_hex,
            #     extract
            # )

            # extract = extract.strip()

            lines = extract.split('\n')
            styled_lines = []

            for line in lines:
                line = line.rstrip()

                # Level 3 heading
                if line.startswith('=== ') and line.endswith(' ==='):
                    title = line[4:-4]
                    styled_lines.append(f'#{color_hex} === {title} ===#')
                    continue

                # Level 2 heading
                if line.startswith('== ') and line.endswith(' =='):
                    title = line[3:-3]
                    styled_lines.append(f'#{color_hex} == {title} ==#')
                    continue

                styled_lines.append(line)

            extract = '\n'.join(styled_lines).strip()

            print(f"this is the edited extract: {extract}")

            # Display article title
            self.title_label.set_text(article_title)
            
            self.article_label.set_text(extract)
            print(f"THIS CASE {page}")
            
            # Switch to reading screen after successfully loading article
            self.show_reading_screen()

        except Exception as e:
            log.error(f"An error occurred: {e} (type: {type(e)})")
            if response is not None and hasattr(response, "text"):
                log.error(f"Response text was: {response.text}")
            self.article_label.set_text(f"Error: {e}")


    def create_disambiguation_popup(self, query, titles):
        intent = Intent(activity_class=DisambiguationActivity)
        intent.putExtra("query", query)
        intent.putExtra("titles", titles)
        self.startActivityForResult(intent, self.disambiguation_result_callback)

    def disambiguation_result_callback(self, result):
        if result.get("result_code") is True:
            data = result.get("data")
            if data:
                selected_title = data.get("selected_title")
                if selected_title:
                    self.search_bar.set_text(selected_title)
                    self.search_event_handler(None)


class DisambiguationActivity(Activity):
    """
    Activity for selecting a disambiguation option from Wikipedia.
    """
    
    def onCreate(self):
        query = self.getIntent().extras.get("query")
        titles = self.getIntent().extras.get("titles", [])
        
        screen = lv.obj()
        screen.set_style_pad_all(15, lv.PART.MAIN)
        
        # Title label
        title_label = lv.label(screen)
        title_label.set_text(f"'{query}' is ambiguous")
        title_label.set_width(lv.pct(100))
        title_label.align(lv.ALIGN.TOP_MID, 0, 0)
        
        # Subtitle label
        subtitle_label = lv.label(screen)
        subtitle_label.set_text("Which article did you mean?")
        subtitle_label.set_width(lv.pct(100))
        subtitle_label.align(lv.ALIGN.TOP_MID, 0, 30)
        
        # Create a list for the disambiguation options
        options_list = lv.list(screen)
        options_list.set_size(lv.pct(100), DisplayMetrics.height() - 120)
        options_list.align(lv.ALIGN.TOP_MID, 0, 60)
        
        # Add each title as a button in the list
        for title in titles:
            if title:  # Skip empty titles
                button = options_list.add_button(None, title)
                button.add_event_cb(lambda e, t=title: self.select_title(t), lv.EVENT.CLICKED, None)
        
        # Cancel button
        cancel_button = lv.button(screen)
        cancel_button.set_size(lv.SIZE_CONTENT, 40)
        cancel_button.align(lv.ALIGN.BOTTOM_MID, 0, 0)
        cancel_button.add_event_cb(lambda e: self.finish(), lv.EVENT.CLICKED, None)
        cancel_label = lv.label(cancel_button)
        cancel_label.set_text("Cancel")
        cancel_label.center()
        
        self.setContentView(screen)
    
    def select_title(self, title):
        self.setResult(True, {"selected_title": title})
        self.finish()
