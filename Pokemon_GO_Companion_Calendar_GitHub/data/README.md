# Event data format

Each entry in `data/events.json` supports:

```json
{
  "calendar": "raids",
  "uid": "unique-stable-id",
  "title": "⚔️ Example Raid Hour",
  "all_day": false,
  "start": "2026-07-15T18:00:00",
  "end": "2026-07-15T19:00:00",
  "alarm_minutes": 30,
  "description": "Raid boss, weaknesses, top five counters, movesets and links.",
  "url": "https://pokemongo.com/news/..."
}
```

Calendar values: `events`, `raids`, `spotlight`, or `deadlines`.

For multi-day events, set `all_day` to `true`, use dates only, and make `end`
the day after the final displayed day because iCalendar end dates are exclusive.
