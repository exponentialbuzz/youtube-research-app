# YouTube Research App — Claude Code Guide

## Standing instruction for Claude
After every accepted change to this project — new feature, bug fix, config change, or structural decision — update this CLAUDE.md file to reflect the new state. Also update the Obsidian copy at `YouTube Research App/CLAUDE.md` via the REST API. This ensures the next session starts with full accurate context.

## What this app does
Takes a keyword, expands it into related search terms using Claude, scrapes YouTube for videos, saves results to an Obsidian note, and syncs all video links to a NotebookLM notebook for AI summarization.

## Project location
`C:\Users\shaynir\youtube-research-app\`
Moved OUT of the Obsidian vault to avoid Obsidian file sync interfering with Python module imports.
Launcher: `C:\Users\shaynir\launcher.bat` → called by VBS at Windows Startup.

## Files
- `app.py` — Streamlit UI (main entry point)
- `keyword_expander.py` — Uses Claude API to generate related keywords
- `youtube_scraper.py` — Scrapes YouTube via scrapetube (no API key needed)
- `obsidian_writer.py` — Reads/writes notes via Obsidian Local REST API
- `notebooklm_automation.py` — Creates/appends to NotebookLM notebooks via notebooklm-py
- `.env` — API keys (never commit this)
- `CLAUDE.md` — This file

## API keys (stored in .env)
- `ANTHROPIC_API_KEY` — Claude API
- `OBSIDIAN_API_KEY` — Obsidian Local REST API key

## Key technical details
-**Obsidian REST API**: HTTPS on `127.0.0.1:27124` (not localhost:27123). SSL verification disabled (self-signed cert). Uses PUT to write notes.
- **NotebookLM**: Uses `notebooklm-py` library. Auth stored at `~/.notebooklm/storage_state.json`. Run `notebooklm login` to refresh. Runs in a separate thread (asyncio conflicts with Streamlit).
- **Streamlit**: Runs on `http://localhost:8501`. Auto-starts on Windows login via `C:\Users\shaynir\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\youtube_research_app.vbs`. File watching is DISABLED (`--server.fileWatcherType none`) — must restart app after code changes.
- **YouTube scraping**: `scrapetube.get_search(keyword, limit=n)` — no API key needed.

## Restarting the app after code changes
After every code change, Claude must restart the app by running this command with `run_in_background: true`:
```
taskkill /F /IM python.exe /T 2>/dev/null; sleep 2; python -m streamlit run app.py --server.headless true --server.fileWatcherType none
```
Then tell the user to refresh `localhost:8501`. The user should never need to restart manually.

## Obsidian vault structure
- Each topic gets its own folder (e.g. `asthma2/`, `Natural sleep/`)
- Notes are named with underscores (e.g. `asthma_type_2.md`)
- All documentation and notes go into Obsidian, not the filesystem
- New apps get their own Obsidian folder

## NotebookLM notebook naming
Notebooks are named `notebook {note title}` (e.g. `notebook asthma type 2`).
Matching is normalized (case-insensitive, underscores = spaces) to prevent duplicate notebooks.

## Deduplication
- **Obsidian**: Notes are appended to (not overwritten) when same note is selected
- **NotebookLM**: Sources are deduplicated by title — existing titles are tracked before adding, duplicates deleted immediately after add

## Git policy
- **Before any significant change** — commit the current working state first
- **After a feature is confirmed working by the user** — commit and push
- **Never commit broken code** — only working states
- **Commit message format**: `feat: description` / `fix: description` / `revert: description`
- **Branch**: always `main`, no feature branches needed for now
- **Never commit**: `.env` (API keys), `__pycache__`
- Remote: `https://github.com/exponentialbuzz/youtube-research-app`

## User preferences
- All new notes, docs, plans go into Obsidian via the REST API — not as filesystem files
- Each app gets its own Obsidian folder; new app = new folder
- Keep responses concise, no trailing summaries
