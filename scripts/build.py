#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import json, html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "events.json"
DOCS = ROOT / "docs"
TZ = "America/Chicago"

CAL_NAMES = {
    "events": "GO Companion — Events",
    "raids": "GO Companion — Raid Hours",
    "spotlight": "GO Companion — Spotlight Hours",
    "deadlines": "GO Companion — Deadlines",
    "combined": "GO Companion Calendar",
}

def esc_ics(value):
    return (str(value).replace("\\", "\\\\").replace("\n", "\\n")
            .replace(",", "\\,").replace(";", "\\;"))

def fold_utf8(line, limit=73):
    chunks, current = [], ""
    for ch in line:
        test = current + ch
        if len(test.encode("utf-8")) > limit:
            chunks.append(current)
            current = " " + ch
        else:
            current = test
    chunks.append(current)
    return chunks

def validate(items):
    required = {"calendar","uid","title","all_day","start","end","description","url"}
    seen = set()
    for idx, item in enumerate(items, 1):
        missing = required - item.keys()
        if missing:
            raise ValueError(f"Entry {idx} missing {sorted(missing)}")
        if item["uid"] in seen:
            raise ValueError(f"Duplicate UID: {item['uid']}")
        seen.add(item["uid"])

def event_lines(item):
    lines = [
        "BEGIN:VEVENT",
        f"UID:{item['uid']}@gocompanion",
        f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        f"SUMMARY:{esc_ics(item['title'])}",
        f"DESCRIPTION:{esc_ics(item['description'] + chr(10) + chr(10) + 'Official information:' + chr(10) + item['url'])}",
        f"URL:{item['url']}",
    ]
    if item["all_day"]:
        lines += [
            f"DTSTART;VALUE=DATE:{item['start'].replace('-', '')}",
            f"DTEND;VALUE=DATE:{item['end'].replace('-', '')}",
            "TRANSP:TRANSPARENT",
        ]
    else:
        start = item["start"].replace("-", "").replace(":", "")
        end = item["end"].replace("-", "").replace(":", "")
        lines += [
            f"DTSTART;TZID={TZ}:{start}",
            f"DTEND;TZID={TZ}:{end}",
            "TRANSP:OPAQUE",
        ]
    alarm = item.get("alarm_minutes", 30)
    if alarm is not None:
        lines += [
            "BEGIN:VALARM",
            f"TRIGGER:-PT{int(alarm)}M",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{esc_ics(item['title'])}",
            "END:VALARM",
        ]
    lines.append("END:VEVENT")
    return lines

def write_calendar(key, name, items):
    raw = [
        "BEGIN:VCALENDAR","VERSION:2.0","CALSCALE:GREGORIAN","METHOD:PUBLISH",
        "PRODID:-//ReploidNo9//GO Companion Calendar//EN",
        f"X-WR-CALNAME:{name}",f"X-WR-TIMEZONE:{TZ}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H","X-PUBLISHED-TTL:PT6H",
    ]
    for item in items:
        raw.extend(event_lines(item))
    raw.append("END:VCALENDAR")
    out = []
    for line in raw:
        out.extend(fold_utf8(line))
    (DOCS / f"{key}.ics").write_text("\r\n".join(out) + "\r\n", encoding="utf-8")

def card(item):
    return f"""
    <article class="event-card" data-category="{html.escape(item.get('category','Event'))}">
      <div class="event-icon">{html.escape(item.get('icon','📅'))}</div>
      <div class="event-copy">
        <div class="event-kicker">{html.escape(item.get('category','Event'))}</div>
        <h3>{html.escape(item['title'])}</h3>
        <p class="event-when">{html.escape(item.get('display_date',''))} · {html.escape(item.get('display_time',''))}</p>
        <p>{html.escape(item.get('summary', item['description']))}</p>
        <div class="event-actions">
          <a href="{html.escape(item['url'])}" target="_blank" rel="noopener">Official details</a>
        </div>
      </div>
    </article>
    """

def build_site(items):
    cards = "\n".join(card(x) for x in items)
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#101826">
<title>GO Companion Calendar</title>
<meta name="description" content="A subscription calendar for Pokémon GO events, Raid Hours, Spotlight Hours, and deadlines.">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="hero">
  <nav class="nav">
    <a class="brand" href="./"><span class="brand-mark">GO</span><span>Companion Calendar</span></a>
    <a class="nav-link" href="#subscribe">Subscribe</a>
  </nav>
  <div class="hero-grid">
    <div>
      <div class="eyebrow">Built for Apple Calendar</div>
      <h1>Your Pokémon GO schedule, without the clutter.</h1>
      <p class="hero-copy">Subscribe once for clean event timing, official links, Raid Hour notes, and separate feeds you can toggle whenever you need them.</p>
      <div class="hero-actions">
        <a class="button primary" href="webcal://reploidno9.github.io/pokemongocalendar/combined.ics">Subscribe to everything</a>
        <a class="button secondary" href="#upcoming">View upcoming events</a>
      </div>
      <p class="microcopy">On iPhone, use a subscribed calendar—not “Add All”—so future updates can refresh automatically.</p>
    </div>
    <div class="hero-panel">
      <div class="status-row"><span class="status-dot"></span><span>Live calendar feeds</span></div>
      <div class="mini-grid">
        <div><strong>Events</strong><span>Festivals, Community Days, special events</span></div>
        <div><strong>Raid Hours</strong><span>Bosses, weaknesses, top counters</span></div>
        <div><strong>Spotlight</strong><span>Featured Pokémon and bonuses</span></div>
        <div><strong>Deadlines</strong><span>Research and reward reminders</span></div>
      </div>
    </div>
  </div>
</header>

<main>
<section class="section" id="subscribe">
  <div class="section-head">
    <div>
      <div class="eyebrow">Choose your setup</div>
      <h2>One calendar or separate feeds</h2>
    </div>
    <p>Use the combined feed for simplicity, or subscribe separately so you can hide Raid Hours, Spotlight Hours, or deadlines independently.</p>
  </div>
  <div class="feed-grid">
    <article class="feed featured"><div class="feed-icon">✨</div><h3>Everything</h3><p>All event types in one subscription.</p><a href="webcal://reploidno9.github.io/pokemongocalendar/combined.ics">Subscribe</a></article>
    <article class="feed"><div class="feed-icon">📅</div><h3>Events</h3><p>GO Fest, Community Days, Raid Days, and seasonal events.</p><a href="webcal://reploidno9.github.io/pokemongocalendar/events.ics">Subscribe</a></article>
    <article class="feed"><div class="feed-icon">⚔️</div><h3>Raid Hours</h3><p>Exact event windows with counter notes and movesets.</p><a href="webcal://reploidno9.github.io/pokemongocalendar/raids.ics">Subscribe</a></article>
    <article class="feed"><div class="feed-icon">⭐</div><h3>Spotlight Hours</h3><p>Featured Pokémon, bonuses, and shiny reminders.</p><a href="webcal://reploidno9.github.io/pokemongocalendar/spotlight.ics">Subscribe</a></article>
    <article class="feed"><div class="feed-icon">⏰</div><h3>Deadlines</h3><p>Short reminders for research and reward claim cutoffs.</p><a href="webcal://reploidno9.github.io/pokemongocalendar/deadlines.ics">Subscribe</a></article>
  </div>
</section>

<section class="section muted" id="upcoming">
  <div class="section-head">
    <div><div class="eyebrow">Coming up</div><h2>Upcoming events</h2></div>
    <p>Event cards are generated from the same data used to build the calendar feeds.</p>
  </div>
  <div class="event-list">
    {cards}
  </div>
</section>

<section class="section">
  <div class="feature-grid">
    <div><span>⚔️</span><h3>Raid-ready notes</h3><p>Weaknesses, five recommended counters, movesets, and official links can live directly inside each Raid Hour event.</p></div>
    <div><span>🧭</span><h3>Clean calendar behavior</h3><p>Multi-day events appear as all-day banners. Timed events block only their actual event window.</p></div>
    <div><span>🔄</span><h3>Stable subscription URLs</h3><p>Future calendar updates publish to the same addresses, allowing Apple Calendar to refresh subscribed feeds.</p></div>
  </div>
</section>
</main>

<footer>
  <div><strong>GO Companion Calendar</strong><p>An independent community calendar project.</p></div>
  <div><a href="combined.ics">Raw combined feed</a></div>
</footer>
</body>
</html>"""
    (DOCS / "index.html").write_text(html_doc, encoding="utf-8")

def main():
    DOCS.mkdir(exist_ok=True)
    items = json.loads(DATA.read_text(encoding="utf-8"))
    validate(items)
    for key in ("events","raids","spotlight","deadlines"):
        write_calendar(key, CAL_NAMES[key], [x for x in items if x["calendar"] == key])
    write_calendar("combined", CAL_NAMES["combined"], items)
    build_site(items)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")

if __name__ == "__main__":
    main()
