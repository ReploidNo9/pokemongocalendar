#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone, date
import json, html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "events.json"
QUEUE = ROOT / "data" / "review_queue.json"
OUT = ROOT / "docs"
TZ = "America/Chicago"

CAL_NAMES = {
    "events": "Trainer GO — Events",
    "raids": "Trainer GO — Raid Hours",
    "spotlight": "Trainer GO — Spotlight Hours",
    "deadlines": "Trainer GO — Deadlines",
    "combined": "Trainer GO Calendar",
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
    valid_calendars = {"events","raids","spotlight","deadlines"}
    seen = set()
    for idx, item in enumerate(items, 1):
        missing = required - item.keys()
        if missing:
            raise ValueError(f"Entry {idx} missing {sorted(missing)}")
        if item["calendar"] not in valid_calendars:
            raise ValueError(f"Entry {idx} has invalid calendar {item['calendar']}")
        if item["uid"] in seen:
            raise ValueError(f"Duplicate UID: {item['uid']}")
        seen.add(item["uid"])
        if item["all_day"]:
            date.fromisoformat(item["start"])
            date.fromisoformat(item["end"])
        else:
            datetime.fromisoformat(item["start"])
            datetime.fromisoformat(item["end"])

def event_lines(item):
    details = item["description"] + "\n\nOfficial information:\n" + item["url"]
    lines = [
        "BEGIN:VEVENT",
        f"UID:{item['uid']}@trainer-go-calendar",
        f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        f"SUMMARY:{esc_ics(item['title'])}",
        f"DESCRIPTION:{esc_ics(details)}",
        f"URL:{item['url']}",
        f"CATEGORIES:{esc_ics(item.get('category','Pokémon GO'))}",
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
        "PRODID:-//ReploidNo9//Trainer GO Calendar//EN",
        f"X-WR-CALNAME:{name}",f"X-WR-TIMEZONE:{TZ}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H","X-PUBLISHED-TTL:PT6H",
    ]
    for item in items:
        raw.extend(event_lines(item))
    raw.append("END:VCALENDAR")
    folded = []
    for line in raw:
        folded.extend(fold_utf8(line))
    (OUT / f"{key}.ics").write_text("\r\n".join(folded) + "\r\n", encoding="utf-8")

def sort_key(item):
    return item["start"]

def event_card(item):
    status = item.get("status", "confirmed")
    status_label = {
        "confirmed": "Confirmed",
        "date-confirmed": "Date confirmed",
        "confirmed-time-boss-pending": "Boss pending"
    }.get(status, status.replace("-", " ").title())
    return f"""
    <article class="event-card">
      <div class="event-icon">{html.escape(item.get('icon','📅'))}</div>
      <div class="event-copy">
        <div class="meta-row">
          <span class="event-kicker">{html.escape(item.get('category','Event'))}</span>
          <span class="status status-{html.escape(status)}">{html.escape(status_label)}</span>
        </div>
        <h3>{html.escape(item['title'])}</h3>
        <p class="event-when">{html.escape(item.get('display_date',''))} · {html.escape(item.get('display_time',''))}</p>
        <p>{html.escape(item.get('summary', item['description']))}</p>
        <a class="details" href="{html.escape(item['url'])}" target="_blank" rel="noopener">Official details ↗</a>
      </div>
    </article>"""

def build_site(items, queue):
    cards = "\n".join(event_card(x) for x in sorted(items, key=sort_key))
    updated = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    queue_count = len(queue)
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#ef3340">
<title>Trainer GO Calendar</title>
<meta name="description" content="A Pokémon GO subscription calendar with clean event timing, official links, raid notes, and automatic update monitoring.">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="hero">
  <nav class="nav">
    <a class="brand" href="./"><span class="brand-mark"></span><span>Trainer GO Calendar</span></a>
    <div class="nav-actions"><a href="#schedule">Schedule</a><a href="#subscribe">Subscribe</a></div>
  </nav>
  <div class="hero-grid">
    <div>
      <div class="eyebrow">Your trainer calendar</div>
      <h1>Plan the adventure.<br>Never miss the event.</h1>
      <p class="hero-copy">Clean local-time events, official links, research deadlines, and raid-ready notes—delivered through calendar feeds that can refresh automatically.</p>
      <div class="hero-actions">
        <a class="button primary" href="webcal://reploidno9.github.io/pokemongocalendar/combined.ics">Subscribe to Master Feed</a>
        <a class="button secondary" href="#schedule">View schedule</a>
      </div>
      <p class="microcopy">Use a subscribed calendar URL instead of importing “Add All.”</p>
    </div>
    <div class="trainer-card">
      <div class="trainer-card-top"><span class="pulse"></span>Feed status: online</div>
      <div class="stats">
        <div><strong>{len(items)}</strong><span>published entries</span></div>
        <div><strong>{queue_count}</strong><span>articles awaiting review</span></div>
        <div><strong>6h</strong><span>recommended refresh</span></div>
        <div><strong>4</strong><span>toggleable feeds</span></div>
      </div>
      <p class="updated">Generated {html.escape(updated)}</p>
    </div>
  </div>
</header>

<main>
<section class="section" id="subscribe">
  <div class="section-head"><div><div class="eyebrow dark">Choose a loadout</div><h2>Subscribe once</h2></div>
  <p>Use the Master Feed for everything, or add separate feeds so Raid Hours, Spotlight Hours, and deadlines can be toggled independently.</p></div>
  <div class="feed-grid">
    <article class="feed featured"><span>✨</span><h3>Master Feed</h3><p>Every published event in one calendar.</p><a href="webcal://reploidno9.github.io/pokemongocalendar/combined.ics">Subscribe</a></article>
    <article class="feed"><span>📅</span><h3>Events</h3><p>GO Fest, Community Days, special events, research, and Raid Days.</p><a href="webcal://reploidno9.github.io/pokemongocalendar/events.ics">Subscribe</a></article>
    <article class="feed"><span>⚔️</span><h3>Raid Hours</h3><p>Exact raid windows with weaknesses, counters, and movesets when confirmed.</p><a href="webcal://reploidno9.github.io/pokemongocalendar/raids.ics">Subscribe</a></article>
    <article class="feed"><span>⭐</span><h3>Spotlight</h3><p>Featured Pokémon, bonuses, and shiny availability.</p><a href="webcal://reploidno9.github.io/pokemongocalendar/spotlight.ics">Subscribe</a></article>
    <article class="feed"><span>⏰</span><h3>Deadlines</h3><p>Short reminders for expiring research and reward claims.</p><a href="webcal://reploidno9.github.io/pokemongocalendar/deadlines.ics">Subscribe</a></article>
  </div>
</section>

<section class="section schedule" id="schedule">
  <div class="section-head"><div><div class="eyebrow dark">Officially scheduled</div><h2>Upcoming adventures</h2></div>
  <p>Dates and details are drawn from official Pokémon GO announcements. Pending details are clearly labeled instead of guessed.</p></div>
  <div class="event-list">{cards}</div>
</section>

<section class="section automation">
  <div class="automation-card">
    <div><div class="eyebrow">Automatic monitoring</div><h2>Ready for September and beyond</h2>
    <p>A scheduled GitHub Action checks the official Pokémon GO news page every day. New articles are placed in a review queue and a GitHub Issue is created, so future events can be verified before they are published to subscribers.</p></div>
    <div class="flow"><span>Official news</span><b>→</b><span>Review queue</span><b>→</b><span>Publish</span><b>→</b><span>Apple Calendar</span></div>
  </div>
</section>
</main>
<footer><div><strong>Trainer GO Calendar</strong><p>Independent community project. Pokémon and Pokémon GO are trademarks of their respective owners.</p></div><a href="combined.ics">Raw calendar feed</a></footer>
</body></html>"""
    (OUT / "index.html").write_text(html_doc, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "events.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    items = json.loads(DATA.read_text(encoding="utf-8"))
    queue = json.loads(QUEUE.read_text(encoding="utf-8")) if QUEUE.exists() else []
    validate(items)
    for key in ("events","raids","spotlight","deadlines"):
        write_calendar(key, CAL_NAMES[key], [x for x in items if x["calendar"] == key])
    write_calendar("combined", CAL_NAMES["combined"], items)
    build_site(items, queue)
    print(f"Built {len(items)} calendar entries.")

if __name__ == "__main__":
    main()
