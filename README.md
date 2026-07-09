# nov-cli

A Termux-friendly command-line tool to **search and read novels from the web**,
inspired by [ani-cli](https://github.com/pystardust/ani-cli).

Type a query, pick a book, pick a part, and it opens in your terminal pager
(`less`).

## Features

- Search across providers
- Interactive selection with `fzf` (falls back to a numbered menu)
- Read in `less` — scroll with arrow keys, `q` to quit
- Pluggable provider system (add your own sites easily)

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

Or copy it to your PATH:

```bash
cp nov_cli.py "$PREFIX/bin/nov-cli"
nov-cli "sherlock holmes"
```

## Usage

| Command | Description |
|---------|-------------|
| `nov-cli "query"` | Search, then pick a book and a part |
| `nov-cli -p gutenberg "query"` | Limit to one provider |
| `nov-cli -U` | Self-update from git |
| `nov-cli -h` | Show help |

## Providers

nov-cli ships with one example provider:

- **gutenberg** — [Project Gutenberg](https://www.gutenberg.org) (public-domain books)

### Adding a provider

1. Create `providers/yourapp.py` with a class that extends `Provider`
   (see `providers/base.py`) and implements `search`, `chapters`, and `content`.
2. Call `register(YourProvider())` at the bottom of the file.
3. Import it in `providers/__init__.py`.

See `disclaimer.md` before scraping any site.

## Development

This project is built and tested entirely on GitHub. Editing files in the
GitHub web editor and pushing triggers the CI workflow
(`.github/workflows/ci.yml`), which compiles the code and runs a smoke test
in the cloud — no local toolchain required.

## License

[GPL-3.0](LICENSE)
