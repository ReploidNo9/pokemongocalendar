#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "events.json"
OUT = ROOT / "docs"
TZ = "America/Chicago"

CALENDARS = {
    "events": "Pokémon GO — Events",
    "raids": "Pokémon GO — Raid Hours",
    "spotlight": "Pokémon GO — Spotlight Hours",
    "deadlines": "Pokémon GO — Deadlines",
    "combined": "Pokémon GO — Companion Calendar",
}

def esc(value: str) -> str:
    return (value.replace("\\", "\\\\").replace("\n", "\\n")
                 .replace(",", "\\,").replace(";", "\\;"))

def fold(line: str, limit: int = 73):
    # Conservative character folding; safe for the mostly-ASCII metadata used here.
    if len(line) <= limit:
        return [line]
    parts = [line[:limit]]
    line = line[limit:]
    while line:
        parts.append(" " + line[:limit-1])
        line = line[limit-1:]
    return parts

def event_lines(item):
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VEVENT",
        f"UID:{item['uid']}@pokemon-go-companion",
        f"DTSTAMP:{now}",
        f"SUMMARY:{esc(item['title'])}",
        f"DESCRIPTION:{esc(item.get('description', ''))}",
        f"URL:{item.get('url', '')}",
    ]
    if item.get("all_day"):
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

def write_calendar(key, title, items):
    raw = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "PRODID:-//Pokemon GO Companion Calendar//EN",
        f"X-WR-CALNAME:{title}",
        f"X-WR-TIMEZONE:{TZ}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H",
        "X-PUBLISHED-TTL:PT6H",
    ]
    for item in items:
        raw.extend(event_lines(item))
    raw.append("END:VCALENDAR")
    folded = []
    for line in raw:
        folded.extend(fold(line))
    (OUT / f"{key}.ics").write_text("\r\n".join(folded) + "\r\n", encoding="utf-8")

def main():
    OUT.mkdir(exist_ok=True)
    items = json.loads(DATA.read_text(encoding="utf-8"))
    for key in ("events", "raids", "spotlight", "deadlines"):
        write_calendar(key, CALENDARS[key], [x for x in items if x["calendar"] == key])
    write_calendar("combined", CALENDARS["combined"], items)

    index = """<!doctype html>
<html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pokémon GO Companion Calendar</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:760px;margin:48px auto;padding:0 20px;line-height:1.5}
a{display:block;margin:12px 0;font-size:1.05rem}code{background:#eee;padding:2px 5px;border-radius:4px}
</style>
<h1>Pokémon GO Companion Calendar</h1>
<p>Subscribe to a feed below rather than downloading it. Your calendar app can periodically refresh subscribed feeds.</p>
<a href="combined.ics">Combined calendar</a>
<a href="events.ics">Events</a>
<a href="raids.ics">Raid Hours</a>
<a href="spotlight.ics">Spotlight Hours</a>
<a href="deadlines.ics">Deadlines</a>
</html>"""
    (OUT / "index.html").write_text(index, encoding="utf-8")

if __name__ == "__main__":
    main()
