from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time


def get_clean_html(url: str, max_retries: int = 2) -> str:
    last_error = None
    for attempt in range(max_retries):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=20000, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                html_content = page.content()
                browser.close()

            soup = BeautifulSoup(html_content, "html.parser")
            for tag in soup(["script", "style", "svg", "meta", "link", "noscript"]):
                tag.decompose()

            body = soup.find("body")
            return str(body) if body else str(soup)

        except Exception as e:
            last_error = e
            print(f"[HTML fetch attempt {attempt + 1}/{max_retries} failed: {e}]")
            if attempt < max_retries - 1:
                time.sleep(5)

    return f"[HTML_FETCH_FAILED after {max_retries} attempts: {last_error}]"