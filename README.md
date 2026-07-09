# nov-cli

> Search and read novels from the web, right in your terminal — *ani-cli* style.

[![CI](https://github.com/buddhistblueberry/nov-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/buddhistblueberry/nov-cli/actions/workflows/ci.yml)

`nov-cli` is a small command-line tool for **Termux / Linux** that lets you
find a novel online and read it in your terminal. You type a search, pick a
book, pick a part, and it opens in `less` — no browser, no app.

## Features

- 🔎 Search across multiple providers from one command
- 📖 Interactive picking with `fzf` (falls back to a numbered menu)
- 📜 Read in `less` — scroll with the arrow keys, `q` to quit
- 🧩 Pluggable **provider** system — add your own sites easily
- 🛡️ Retries on flaky networks and clean error messages (no raw tracebacks)
- 🧪 Unit tests run on every push, so a broken provider is caught fast
- 💾 **Download** any part to a `.txt` file with `-d`
- 🔖 **Resume** your last-read book with `-r`
- ☁️ **Offline cache** — re-reads work without the network
- 🚫 **Ad-free & tracker-free** — just text in your terminal, no ads, no
  accounts, no telemetry. What you read stays on your device.

## Install (Termux / Linux)

**Recommended — pip:**

```bash
pkg install python fzf less        # Termux; on Debian/Ubuntu use apt
pip install .
nov-cli "pride and prejudice"
```

**Or the one-line script:**

```bash
bash install.sh
```

**Or clone + run directly:**

```bash
pkg install python fzf less
git clone https://github.com/buddhistblueberry/nov-cli
cd nov-cli
pip install -r requirements.txt
python nov_cli.py "pride and prejudice"
```

If you cloned it, you can also copy the script into your `PATH`:

```bash
cp nov_cli.py "$PREFIX/bin/nov-cli"
nov-cli "sherlock holmes"
```

## Usage

| Command | What it does |
|---------|--------------|
| `nov-cli "query"` | Search, then pick a book and a part |
| `nov-cli -p gutenberg "query"` | Limit the search to one provider |
| `nov-cli -d "query"` | Save the chosen part to a `.txt` file |
| `nov-cli -r` | Resume the last-read bookmarked book |
| `nov-cli --no-cache "query"` | Skip the offline cache for this run |
| `nov-cli -U` | Self-update from git |
| `nov-cli -h` | Show the help text |

### Example session

```text
$ nov-cli "alice"
Searching for: alice
Novel:
  1. Alice's Adventures in Wonderland — Lewis Carroll
  2. Alice's Adventures Under Ground — Lewis Carroll
  ...
Part:
  1. Read — Plain Text (UTF-8)
  2. Read — HTML
Fetching…
# the text opens in less — scroll and press q to quit
```

## Providers

nov-cli ships with these providers:

- **gutenberg** — [Project Gutenberg](https://www.gutenberg.org), public-domain books.
- **standardebooks** — [Standard Ebooks](https://standardebooks.org), cleaned-up
  public-domain ebooks with a plain-text reading view.

Each provider lives in its own file under `providers/` and follows a tiny
interface: given a search term it returns books; for a book it returns
readable parts; for a part it returns the text. That separation means if one
site changes its layout, only that one file needs fixing.

### Adding a provider

1. Create `providers/yourapp.py` with a class that extends `Provider`
   (see `providers/base.py`) and implements `search`, `chapters`, `content`.
2. Call `register(YourProvider())` at the bottom of the file.
3. Import it in `providers/__init__.py`.

See `disclaimer.md` before scraping any site.

## Local data

nov-cli keeps a little state on your device:

- **Offline cache** — fetched chapters are stored in `~/.cache/nov-cli/`
  so re-reading works without the network. Clear that folder to force a
  refresh, or pass `--no-cache`.
- **Bookmarks** — your last-read position per book lives in
  `~/.config/nov-cli/bookmarks.json` (used by `-r`). Delete the file to
  start fresh.
- **Downloads** — `-d` saves files to `~/nov-cli-books/` as
  `<Novel> - <Part>.txt`.

## How it's built

The code is plain Python with three small pieces:

- `nov_cli.py` — the command-line front end (argument parsing + the
  search → pick book → pick part → read flow).
- `core/` — shared helpers: `http.py` (fetching + retries) and `ui.py`
  (the `fzf` picker and the `less` viewer).
- `providers/` — one file per website. Each follows the same tiny
  interface (`search`, `chapters`, `content`), so adding a site means
  writing one class, not touching the rest of the app.

Every push runs the CI workflow (`.github/workflows/ci.yml`), which
compiles the code, runs the unit tests in `tests/`, and does a weekly live
"is the scraper still working?" check. To develop locally:

```bash
git clone https://github.com/buddhistblueberry/nov-cli
cd nov-cli
pip install -r requirements-dev.txt
pytest -q
```

## Troubleshooting

- **`nov-cli: command not found`** — you installed with `git clone` but
  didn't copy `nov_cli.py` to your `PATH`, or `pip install .` didn't put
  the script on your `PATH`. Use the full path, or re-run `pip install .`.
- **It opens a numbered menu instead of a fuzzy finder** — `fzf` isn't
  installed. Run `pkg install fzf` (Termux) or `apt install fzf`.
- **`[error] could not fetch …`** — usually no internet, or the site
  blocked the request. nov-cli retries automatically; if it still fails,
  the site may be down or have changed.
- **Self-update says "only works inside a git checkout"** — you installed
  via `pip` from PyPI; update with `pip install --upgrade .` instead, or
  use the `git clone` method.

## Disclaimer

nov-cli fetches public web pages. Respect each site's Terms of Service and
copyright; the bundled `gutenberg` provider uses public-domain works only.
See [`disclaimer.md`](disclaimer.md).

## License

[GPL-3.0](LICENSE)
