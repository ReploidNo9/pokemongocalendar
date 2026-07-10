# Trainer GO Calendar

A Pokémon-inspired GitHub Pages site and Apple Calendar subscription system for Pokémon GO events.

## What is automated

- `publish.yml` validates `data/events.json`, rebuilds the website and all `.ics` feeds, and commits the generated files.
- `monitor.yml` checks the official Pokémon GO news page every day.
- New official articles are added to `data/review_queue.json`.
- GitHub opens a review Issue with links and a checklist.
- Apple Calendar keeps using the same stable subscription URLs after approved events are published.

The monitor intentionally does not publish guessed dates, bosses, or counters. Official announcements are reviewed before subscribers receive them.

## Replace your repository once

Upload all files and folders from this package to the root of:

`https://github.com/ReploidNo9/pokemongocalendar`

Because `.github` is hidden on macOS, press **Command + Shift + .** in Finder before selecting everything.

The repository root must show:

- `.github`
- `data`
- `docs`
- `scripts`
- `tests`
- `README.md`
- `CONTRIBUTING.md`
- `LICENSE`

## GitHub Pages

Keep:

- Source: **Deploy from a branch**
- Branch: **main**
- Folder: **/docs**

## Apple Calendar URLs

- Master: `https://reploidno9.github.io/pokemongocalendar/combined.ics`
- Events: `https://reploidno9.github.io/pokemongocalendar/events.ics`
- Raid Hours: `https://reploidno9.github.io/pokemongocalendar/raids.ics`
- Spotlight Hours: `https://reploidno9.github.io/pokemongocalendar/spotlight.ics`
- Deadlines: `https://reploidno9.github.io/pokemongocalendar/deadlines.ics`

Existing subscribers to these URLs do not need to resubscribe.

## Publishing a reviewed event

1. Open the GitHub Issue created by the monitor.
2. Verify the official event announcement.
3. Add or update an entry in `data/events.json`.
4. Keep the same `uid` when changing an existing event.
5. Remove the reviewed article from `data/review_queue.json`.
6. Commit the changes.

GitHub Actions rebuilds and republishes the site automatically.

## Raid Hour notes

Use `calendar: "raids"` and put the following in `description`:

- Raid boss
- Weaknesses
- Top five counters
- Recommended movesets
- Shiny availability
- Level 20 and weather-boosted 100% IV CP
- Weather boost
- Suggested trainer count
- Official and simulation links
