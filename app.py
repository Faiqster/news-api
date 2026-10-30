import os, re, urllib.parse
from collections import Counter
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ====== EDIT THESE ======
REGISTRATION = "SP23-BAI-031"     
NEWS_SOURCE  = "Euronews"
DOMAIN       = "euronews.com"

app = Flask(__name__)


def make_driver():
    o = Options()
    o.binary_location = "/usr/bin/google-chrome"
    for a in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
              "--disable-gpu", "--window-size=1366,768"):
        o.add_argument(a)
    o.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120 Safari/537.36")
    return webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=o)


def first_result_url(driver, keyword):
    """Search the site via DuckDuckGo (site: operator) and return first result URL."""
    q = urllib.parse.quote_plus(f"site:{DOMAIN} {keyword}")
    driver.get(f"https://html.duckduckgo.com/html/?q={q}")
    for a in driver.find_elements(By.CSS_SELECTOR, "a.result__a"):
        href = a.get_attribute("href") or ""
        if "uddg=" in href:  # DDG redirect wrapper
            href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
        if DOMAIN in href:
            return href
    return None


def article_text(driver, url):
    driver.get(url)
    paras = [p.text.strip() for p in driver.find_elements(By.TAG_NAME, "p")]
    return " ".join(p for p in paras if len(p) > 40)


STOP = set("the a an and or of to in on for is are was were be by with as at it this that from "
           "has have had not but they their he she his her its we you i will would can could".split())


def summarize(text, n=3):
    sents = re.split(r"(?<=[.!?])\s+", text)
    if len(sents) <= n:
        return text
    freq = Counter(w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOP)
    scored = []
    for i, s in enumerate(sents):
        words = re.findall(r"[a-z']+", s.lower())
        if 8 <= len(words) <= 60:
            scored.append((sum(freq[w] for w in words) / len(words), i, s))
    top = sorted(sorted(scored, reverse=True)[:n], key=lambda x: x[1])
    return " ".join(s for _, _, s in top)


@app.route("/")
def home():
    return f"<h1>Registration: {REGISTRATION}</h1><p>News source: {NEWS_SOURCE}</p>" \
           f"<p>Use /get?keyword=your_keyword</p>"


@app.route("/get")
def get():
    keyword = request.args.get("keyword", "").strip()
    out = {"registration": REGISTRATION, "newssource": NEWS_SOURCE,
           "keyword": keyword, "url": "", "summary": ""}
    if not keyword:
        out["summary"] = "Missing keyword parameter"
        return jsonify(out), 400
    driver = make_driver()
    try:
        url = first_result_url(driver, keyword)
        if not url:
            out["summary"] = "No result found"
            return jsonify(out), 404
        out["url"] = url
        out["summary"] = summarize(article_text(driver, url))
    except Exception as e:
        out["summary"] = f"Error: {e}"
        return jsonify(out), 500
    finally:
        driver.quit()
    return jsonify(out)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)