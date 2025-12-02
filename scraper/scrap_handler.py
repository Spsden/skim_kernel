# import requests
# from bs4 import BeautifulSoup
# import re
# import json
# from datetime import datetime

# def normalize_date(raw_date: str):
#     """Convert TOI date strings like 'Dec 02, 2025, 00:48 IST' → ISO8601."""
#     if not raw_date:
#         return None

#     raw = raw_date.replace("IST", "").strip()

#     # TOI format: Dec 02, 2025, 00:48
#     try:
#         dt = datetime.strptime(raw, "%b %d, %Y, %H:%M")
#         return dt.isoformat()
#     except:
#         pass

#     # JSON-LD ISO format fallback
#     try:
#         dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
#         return dt.isoformat()
#     except:
#         return raw_date   # last fallback


# def extract_body(soup):
#     """
#     Extract full article body text from Times of India page.
#     TOI typically uses:
#         <div class="ga-headlines"> ... </div>
#         <div class="_s30J clearfix"> ... <p>...</p> ... </div>
#     """

#     body_text = []

#     # Primary TOI article body container
#     body_container = soup.find("div", {"class": re.compile(r"(ga-headlines|article-content|_s30J)")})

#     print(f"body container {body_container}")

#     if body_container:
#         paragraphs = body_container.find_all("p")
#         for p in paragraphs:
#             text = p.get_text(strip=True)
#             if text:
#                 body_text.append(text)

#     # Fallback: collect all <p> inside the article section
#     if not body_text:
#         article = soup.find("article")
#         if article:
#             for p in article.find_all("p"):
#                 text = p.get_text(strip=True)
#                 if text:
#                     body_text.append(text)

#     return "\n\n".join(body_text) if body_text else None


# def scrape_toi_article(url):
#     resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#     resp.raise_for_status()
#     soup = BeautifulSoup(resp.text, "html.parser")

#     # ------------------------------
#     # 1. TITLE
#     # ------------------------------
#     title = None
#     if soup.find("h1"):
#         title = soup.find("h1").get_text(strip=True)
#     elif soup.title:
#         title = soup.title.get_text(strip=True)

#     # ------------------------------
#     # 2. DESCRIPTION
#     # ------------------------------
#     description = None

#     meta_desc = soup.find("meta", attrs={"name": "description"})
#     if meta_desc:
#         description = meta_desc.get("content")

#     if not description:
#         sub = soup.find("h2")
#         if sub:
#             description = sub.get_text(strip=True)

#     # ------------------------------
#     # 3. AUTHOR(S) & PUBLISH DATE
#     # ------------------------------
#     authors = []
#     published_date = None

#     # Visible text containing date + authors
#     meta_text = soup.find(text=re.compile(r"Updated:|Published:", re.I))

#     if meta_text:
#         text = meta_text.strip()

#         # Extract authors (TOI format splits with "/")
#         parts = [p.strip() for p in text.split("/") if p.strip()]

#         if len(parts) >= 2:
#             authors = parts[:-1]   # all except last are authors

#         # Extract date
#         m = re.search(r"(Published|Updated):\s*(.*)", text)
#         if m:
#             published_date = normalize_date(m.group(2))

#     # ------------------------------
#     # 4. JSON-LD fallback
#     # ------------------------------
#     scripts = soup.find_all("script", type="application/ld+json")
#     for sc in scripts:
#         try:
#             data = json.loads(sc.string)

#             # JSON-LD may be list or object
#             blocks = data if isinstance(data, list) else [data]

#             for block in blocks:
#                 if not isinstance(block, dict):
#                     continue

#                 if "datePublished" in block:
#                     published_date = published_date or normalize_date(block["datePublished"])

#                 if "author" in block:
#                     auth = block["author"]

#                     if isinstance(auth, dict) and auth.get("name"):
#                         authors.append(auth["name"])

#                     elif isinstance(auth, list):
#                         for a in auth:
#                             if isinstance(a, dict) and a.get("name"):
#                                 authors.append(a["name"])

#         except:
#             pass

#     authors = list(dict.fromkeys(authors))  # unique authors

#     # ------------------------------
#     # 5. FULL BODY EXTRACTION
#     # ------------------------------
#     body = extract_body(soup)

#     return {
#         "title": title or None,
#         "description": description or None,
#         "authors": authors or None,
#         "published_date": published_date or None,
#         "body": body or None
#     }


# # -----------------------------------
# # TEST RUN
# # -----------------------------------
# if __name__ == "__main__":
#     url = "https://timesofindia.indiatimes.com/sports/nhl/news/leon-draisaitl-breaks-silence-with-icy-message-that-puts-new-spotlight-on-connor-mcdavid-leadership/articleshow/125667359.cms"

#     result = scrape_toi_article(url)
#     print(json.dumps(result, indent=4))



import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

def normalize_date(raw_date: str):
    """Convert TOI print-date format → ISO."""
    if not raw_date:
        return None

    raw = raw_date.replace("IST", "").strip()

    # Example: "Dec 02, 2025, 00:48"
    try:
        dt = datetime.strptime(raw, "%b %d, %Y, %H:%M")
        return dt.isoformat()
    except:
        pass

    # Try ISO fallback from JSON
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.isoformat()
    except:
        return raw_date


def extract_body_print(soup):
    """
    Extract article body from TOI print page.
    Print pages use:
        <div class="Normal"> for each paragraph
    """
    paragraphs = soup.find_all("div", {"class": "Normal"})
    body = []

    for p in paragraphs:
        text = p.get_text(strip=True)
        if text:
            body.append(text)

    return "\n\n".join(body) if body else None


def scrape_toi_article_print(url):
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # ------------------------------
    # 1. TITLE
    # ------------------------------
    title = None
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True)

    # ------------------------------
    # 2. AUTHORS
    # ------------------------------
    authors = []

    # Print version often shows authors in <div class="byline">
    byline = soup.find("div", {"class": "byline"})

    if byline:
        raw = byline.get_text(" ", strip=True)
        # Example: "Sehjal Gupta | TIMESOFINDIA.COM"
        parts = re.split(r"[|/]", raw)
        authors = [p.strip() for p in parts if p.strip()]

    # ------------------------------
    # 3. DATE
    # ------------------------------
    published_date = None
    date_tag = soup.find("div", {"class": "byline"})

    if date_tag:
        raw = date_tag.get_text(" ", strip=True)
        # Look for date:  "Updated: Dec 02, 2025, 00:48 IST"
        m = re.search(r"(Updated|Published):\s*(.*)", raw, re.I)
        if m:
            published_date = normalize_date(m.group(2))

    # ------------------------------
    # 4. DESCRIPTION
    # ------------------------------
    description = None

    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        description = meta_desc.get("content")

    # body  extraction 
    body = extract_body_print(soup)

    return {
        "title": title or None,
        "description": description or None,
        "authors": authors or None,
        "published_date": published_date or None,
        "body": body or None
    }


# -------------------------------------------
# TEST
# -------------------------------------------
if __name__ == "__main__":
    url = "https://timesofindia.indiatimes.com/sports/nhl/news/leon-draisaitl-breaks-silence-with-icy-message-that-puts-new-spotlight-on-connor-mcdavid-leadership/articleshowprint/125667359.cms"
    url = "https://timesofindia.indiatimes.com/technology/tech-news/microsoft-ceo-satya-nadella-says-humans-cant-rely-on-brains-alone-to-succeed-at-workplace-they-need/articleshowprint/125709288.cms"

    data = scrape_toi_article_print(url)
    print(json.dumps(data, indent=4))
