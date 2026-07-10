# Pokémon GO Companion Calendar v2

This version is designed to launch without requiring a hidden `.github` folder.

## Publish the site first

1. Upload the visible contents of this project to the root of your repository:
   `data`, `docs`, `scripts`, `workflow-file-to-create`, and `README.md`.
2. In GitHub, open **Settings → Pages**.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Select branch **main** and folder **/docs**.
5. Click **Save**.

Your site should become:

`https://reploidno9.github.io/pokemongocalendar/`

Your combined Apple Calendar subscription URL should become:

`https://reploidno9.github.io/pokemongocalendar/combined.ics`

## Add automatic rebuilding afterward

The workflow is supplied as a normal visible file at:

`workflow-file-to-create/rebuild-calendars.yml`

In GitHub:

1. Click **Add file → Create new file**.
2. In the filename box, type exactly:
   `.github/workflows/rebuild-calendars.yml`
3. Copy the contents of `workflow-file-to-create/rebuild-calendars.yml`.
4. Paste them into the editor.
5. Click **Commit changes**.

This browser-created file avoids the macOS hidden-folder upload problem.

## Subscribe on iPhone

Open:

**Settings → Apps → Calendar → Calendar Accounts → Add Account → Other → Add Subscribed Calendar**

Paste:

`https://reploidno9.github.io/pokemongocalendar/combined.ics`

Use the separate feed URLs instead if you want independent calendar toggles.

## Updating events

Edit `data/events.json` and preserve the existing `uid` when modifying an event.
The workflow rebuilds the files in `docs` and commits them automatically.

Multi-day events use all-day banners. Raid Hours and other timed events use their
actual start and end times.
