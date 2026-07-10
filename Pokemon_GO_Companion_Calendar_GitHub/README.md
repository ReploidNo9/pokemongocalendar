# Pokémon GO Companion Calendar

A GitHub Pages–hosted set of Apple Calendar–compatible subscription feeds.

## What this solves

An imported `.ics` file is a one-time copy. These files are published at stable web
addresses. When `data/events.json` is updated and pushed, GitHub Actions rebuilds and
republishes the feeds at the same URLs.

## Deploy

1. Create a new public GitHub repository.
2. Upload this folder's contents to the repository's `main` branch.
3. Open **Settings → Pages**.
4. Under **Build and deployment**, choose **GitHub Actions**.
5. Open the repository's **Actions** tab and run **Build and publish calendars** if it
   did not start automatically.

Your feed URLs will look like:

- `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/combined.ics`
- `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/events.ics`
- `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/raids.ics`
- `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/spotlight.ics`
- `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/deadlines.ics`

## Subscribe in Apple Calendar

### iPhone or iPad

1. Open **Settings → Apps → Calendar → Calendar Accounts**.
2. Tap **Add Account → Other → Add Subscribed Calendar**.
3. Paste one of the published `.ics` URLs.
4. Save it.

### Mac

1. Open Calendar.
2. Select **File → New Calendar Subscription**.
3. Paste the published `.ics` URL.
4. Set auto-refresh to the shortest available interval you prefer.

Do not import the file through **Add All** if you want updates. Subscribe using the URL.

## Updating events

Edit `data/events.json`, keeping each `uid` stable for an existing event. Commit and push.
The workflow rebuilds the calendars and GitHub Pages republishes them at the same URLs.

For Raid Hours, put the boss, weaknesses, five counters, movesets, shiny status, CP values,
weather boost, trainer estimate, and source links in `description`.

## Important limitation

The feed updates automatically after repository data changes. The included workflow does
not scrape announcements automatically because official event pages can change structure
and automated counter rankings require maintained battle data. This avoids silently adding
incorrect dates or counters. A scheduled monitoring task can flag new announcements for
review, after which the JSON can be updated and published.
