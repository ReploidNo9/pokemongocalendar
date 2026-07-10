#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
import json, sys

ROOT = Path(__file__).resolve().parents[1]
KNOWN = ROOT / "data" / "known_articles.json"
QUEUE = ROOT / "data" / "review_queue.json"
ISSUE = ROOT / "data" / "review_issue.md"
NEWS_URL = "https://pokemongo.com/news"

class NewsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = {}
        self.current_href = None
        self.current_text = []
    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)
        href = attrs.get("href", "")
        if "/news/" in href and href.rstrip("/") != "/news":
            self.current_href = urljoin(NEWS_URL, href)
            self.current_text = []
    def handle_data(self, data):
        if self.current_href:
            self.current_text.append(data.strip())
    def handle_endtag(self, tag):
        if tag == "a" and self.current_href:
            text = " ".join(x for x in self.current_text if x).strip()
            self.links[self.current_href.split("?")[0].rstrip("/")] = text or "Official Pokémon GO article"
            self.current_href = None
            self.current_text = []

def fetch_articles():
    request = Request(NEWS_URL, headers={"User-Agent":"TrainerGOCalendar/1.0 (+GitHub Pages calendar monitor)"})
    with urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
    parser = NewsParser()
    parser.feed(body)
    # Only monitor the first portion of the current page to avoid resurfacing the full archive.
    return list(parser.links.items())[:30]

def main():
    known = set(json.loads(KNOWN.read_text(encoding="utf-8"))) if KNOWN.exists() else set()
    queue = json.loads(QUEUE.read_text(encoding="utf-8")) if QUEUE.exists() else []
    queued_urls = {x["url"] for x in queue}
    found = fetch_articles()
    new_items = []
    for url, title in found:
        if url not in known and url not in queued_urls:
            new_items.append({
                "title": title,
                "url": url,
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "status": "needs-review"
            })
    if new_items:
        queue = new_items + queue
        QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        known.update(url for url, _ in found)
        KNOWN.write_text(json.dumps(sorted(known), indent=2) + "\n", encoding="utf-8")
        lines = [
            "# New official Pokémon GO announcements",
            "",
            "The daily monitor found official news articles that are not yet represented in the published event data.",
            "",
        ]
        for item in new_items:
            lines.append(f"- [{item['title']}]({item['url']})")
        lines += [
            "",
            "## Review checklist",
            "",
            "- Confirm the event date, start time, end time, and whether it should be all-day.",
            "- Add deadlines as separate short reminder events.",
            "- For Raid Hours, verify the boss before adding counters and movesets.",
            "- Preserve stable UIDs when updating an existing event.",
            "- Add approved entries to `data/events.json`, remove reviewed items from `data/review_queue.json`, then commit.",
        ]
        ISSUE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"new_count={len(new_items)}")
    if "--github-output" in sys.argv:
        output = Path(str(__import__("os").environ.get("GITHUB_OUTPUT", "")))
        if output:
            with output.open("a", encoding="utf-8") as handle:
                handle.write(f"new_count={len(new_items)}\n")

if __name__ == "__main__":
    main()
