# Trainer GO Calendar

A polished GitHub Pages website and Apple Calendar subscription feed project.

## Upload

Replace the current repository contents with:

- `data`
- `docs`
- `scripts`
- `workflow-file-to-create`
- `README.md`

Keep GitHub Pages set to:

- Branch: `main`
- Folder: `/docs`

## Live URLs

- Website: `https://reploidno9.github.io/pokemongocalendar/`
- Combined: `https://reploidno9.github.io/pokemongocalendar/combined.ics`
- Events: `https://reploidno9.github.io/pokemongocalendar/events.ics`
- Raid Hours: `https://reploidno9.github.io/pokemongocalendar/raids.ics`
- Spotlight Hours: `https://reploidno9.github.io/pokemongocalendar/spotlight.ics`
- Deadlines: `https://reploidno9.github.io/pokemongocalendar/deadlines.ics`

## Add automation

Create a new file in GitHub at:

`.github/workflows/rebuild-calendars.yml`

Copy the contents from:

`workflow-file-to-create/rebuild-calendars.yml`

## Add or edit events

Edit `data/events.json`. Preserve an event's `uid` when modifying it so subscribed calendars update the existing event instead of creating a duplicate.

For a Raid Hour, use `calendar: "raids"` and place the boss, weaknesses, five counters, movesets, shiny availability, CP values, weather boost, and source links in `description`.
