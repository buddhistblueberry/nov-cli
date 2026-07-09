# Changelog

A timeline of every release of **nov-cli**, newest first. Each entry maps
to a git tag so you can check out any point in the project's history.

## [0.3.0] — 2026-07-09

**Reading features (Phase 2)**

- 💾 **Download** — `-d` saves the chosen part to
  `~/nov-cli-books/<Novel> - <Part>.txt` (`core/save.py`).
- 🔖 **Resume** — `-r` jumps back into the last-read book; your position
  is auto-saved in `~/.config/nov-cli/bookmarks.json` (`core/bookmarks.py`).
- ☁️ **Offline cache** — fetched chapters are cached in `~/.cache/nov-cli/`
  by URL, so re-reads work without the network. `--no-cache` disables it
  for a run (`core/cache.py`, wired into `core/http.fetch`).

*Tag: `v0.3.0` — commit `344f097`*

## [0.2.0] — 2026-07-09

**Robustness, tests & packaging (Phase 1)**

- 🛡️ `core/http.py` now retries on flaky networks / 5xx with backoff and
  raises a clean `NovHttpError` instead of a raw traceback.
- `nov_cli.py` gained a safe `git pull` self-update, wrapped chapter/content
  fetches, and a top-level crash guard.
- 🧪 12 pytest tests (`tests/`) cover HTTP retries, Gutenberg parsing, and
  the picker — run on every push by CI.
- 📦 Packaging: `pyproject.toml` installs a `nov-cli` console command
  (`pip install .`), plus `install.sh` and `requirements-dev.txt`.
- README: pip install instructions + troubleshooting.

*Tag: `v0.2.0` — commit `c838f02`*

## [0.1.0] — 2026-07-09

**Initial release**

- First public version: search → pick book → pick part → read in `less`.
- `gutenberg` provider (Project Gutenberg, public domain) as the example.
- Pluggable provider system (`providers/base.py` + registry).
- `fzf` picker with numbered-menu fallback; GitHub Actions CI
  (compile + smoke test + weekly scraper health check).

*Tag: `v0.1.0` — commit `18318a8`*

---

### Upcoming (not yet released)

- **Phase 3 providers** — `standardebooks` added (public-domain, plain-text
  reading view). Still to come: Internet Archive, AO3/Wattpad.
- Improved author parsing from Gutenberg search.

## [Unreleased] — 2026-07-09

- `standardebooks` provider: search + plain-text reading (`/text/single-page`),
  with offline-cache and bookmark support like every provider.
- `internetarchive` provider: advancedsearch JSON API + metadata lookup for the
  item's plain-text (.txt) file.
- `ao3` provider: fanfiction search + chapter reading (`#chapters .userstuff`).
  Personal reading only — respects AO3 ToS (see disclaimer.md). Wattpad skipped
  (heavy JavaScript, not scrape-friendly).
- README: ad-free point, providers list (4 providers); disclaimer notes AO3 ToS.
- 28 pytest tests across all providers.
