from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def get_clean_html(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=15000)
        page.wait_for_load_state("networkidle")
        html_content = page.content()
        browser.close()

    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "svg", "meta", "link", "noscript"]):
        tag.decompose()

    body = soup.find("body")
    return str(body) if body else str(soup)