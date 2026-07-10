#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "events.json"
OUT = ROOT / "docs"
TZ = "America/Chicago"

NAMES = {
    "events": "Pokémon GO — Events",
    "raids": "Pokémon GO — Raid Hours",
    "spotlight": "Pokémon GO — Spotlight Hours",
    "deadlines": "Pokémon GO — Deadlines",
    "combined": "Pokémon GO — Companion Calendar",
}

def esc(value):
    return (str(value).replace("\\", "\\\\").replace("\n", "\\n")
            .replace(",", "\\,").replace(";", "\\;"))

def fold_utf8(line, limit=73):
    chunks, current = [], ""
    for ch in line:
        candidate = current + ch
        if len(candidate.encode("utf-8")) > limit:
            chunks.append(current)
            current = " " + ch
        else:
            current = candidate
    chunks.append(current)
    return chunks

def validate(items):
    seen = set()
    valid_calendars = {"events", "raids", "spotlight", "deadlines"}
    for index, item in enumerate(items, 1):
        required = {"calendar", "uid", "title", "all_day", "start", "end", "description", "url"}
        missing = required - item.keys()
        if missing:
            raise ValueError(f"Entry {index} is missing: {sorted(missing)}")
        if item["calendar"] not in valid_calendars:
            raise ValueError(f"Entry {index} has invalid calendar: {item['calendar']}")
        if item["uid"] in seen:
            raise ValueError(f"Duplicate uid: {item['uid']}")
        seen.add(item["uid"])

def event_lines(item):
    lines = [
        "BEGIN:VEVENT",
        f"UID:{item['uid']}@pokemongocalendar",
        f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        f"SUMMARY:{esc(item['title'])}",
        f"DESCRIPTION:{esc(item['description'])}",
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
            f"DESCRIPTION:{esc(item['title'])}",
            "END:VALARM",
        ]
    lines.append("END:VEVENT")
    return lines

def write_calendar(key, name, items):
    raw = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "PRODID:-//ReploidNo9//Pokemon GO Calendar//EN",
        f"X-WR-CALNAME:{name}",
        f"X-WR-TIMEZONE:{TZ}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H",
        "X-PUBLISHED-TTL:PT6H",
    ]
    for item in items:
        raw.extend(event_lines(item))
    raw.append("END:VCALENDAR")

    folded = []
    for line in raw:
        folded.extend(fold_utf8(line))
    (OUT / f"{key}.ics").write_text("\r\n".join(folded) + "\r\n", encoding="utf-8")

def build_site():
    html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pokémon GO Companion Calendar</title>
<style>
:root{color-scheme:light dark}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:760px;margin:0 auto;padding:48px 22px;line-height:1.5}
h1{font-size:2.2rem;margin-bottom:.4rem}
.card{border:1px solid rgba(127,127,127,.35);border-radius:16px;padding:18px;margin:14px 0}
a.button{display:inline-block;padding:10px 14px;border-radius:10px;background:#1778f2;color:white;text-decoration:none;font-weight:650;margin:4px 6px 4px 0}
small{opacity:.72}
</style>
</head>
<body>
<h1>Pokémon GO Companion Calendar</h1>
<p>Subscribe once. Calendar updates published at these addresses can refresh automatically in Apple Calendar.</p>
<div class="card"><h2>Everything</h2><a class="button" href="combined.ics">Combined feed</a></div>
<div class="card"><h2>Separate feeds</h2>
<a class="button" href="events.ics">Events</a>
<a class="button" href="raids.ics">Raid Hours</a>
<a class="button" href="spotlight.ics">Spotlight Hours</a>
<a class="button" href="deadlines.ics">Deadlines</a>
</div>
<p><small>Use the full HTTPS address as a subscribed calendar URL. Do not import the file as a one-time event list.</small></p>
</body></html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

def main():
    OUT.mkdir(exist_ok=True)
    items = json.loads(DATA.read_text(encoding="utf-8"))
    validate(items)
    for key in ("events", "raids", "spotlight", "deadlines"):
        write_calendar(key, NAMES[key], [x for x in items if x["calendar"] == key])
    write_calendar("combined", NAMES["combined"], items)
    build_site()
    print(f"Built {len(items)} events into {OUT}")

if __name__ == "__main__":
    main()
