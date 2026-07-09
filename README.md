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
- ☁️ Built and tested on GitHub; no local toolchain needed

## Install (Termux / Linux)

```bash
pkg install python fzf less
git clone https://github.com/buddhistblueberry/nov-cli
cd nov-cli
pip install -r requirements.txt
```

Run it:

```bash
python nov_cli.py "pride and prejudice"
```

Or copy it into your `PATH` so you can call it from anywhere:

```bash
cp nov_cli.py "$PREFIX/bin/nov-cli"
nov-cli "sherlock holmes"
```

## Usage

| Command | What it does |
|---------|--------------|
| `nov-cli "query"` | Search, then pick a book and a part |
| `nov-cli -p gutenberg "query"` | Limit the search to one provider |
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

nov-cli ships with one example provider:

- **gutenberg** — [Project Gutenberg](https://www.gutenberg.org), public-domain books.

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

## How it's built

This project is developed entirely on GitHub. Editing a file in the GitHub
web editor and pushing it triggers the CI workflow
(`.github/workflows/ci.yml`), which compiles the code and runs a smoke test
on GitHub's servers — so you never need a compiler or Python installed
locally to contribute.

## Disclaimer

nov-cli fetches public web pages. Respect each site's Terms of Service and
copyright; the bundled `gutenberg` provider uses public-domain works only.
See [`disclaimer.md`](disclaimer.md).

## License

[GPL-3.0](LICENSE)
