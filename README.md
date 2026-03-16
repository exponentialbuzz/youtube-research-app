# YouTube Research App

## What it does
Streamlit app that takes a keyword, expands it using Claude, scrapes YouTube for videos, saves results to Obsidian, and creates a NotebookLM notebook with all sources.

## Stack
- **UI**: Streamlit
- **Keyword expansion**: Claude API (claude-sonnet-4-6)
- **YouTube scraping**: scrapetube
- **Obsidian**: Local REST API plugin (https, port 27124)
- **NotebookLM**: notebooklm-py library

## Project location
`C:\Users\shaynir\youtube-research-app`

## Files
- `app.py` - Streamlit UI
- `keyword_expander.py` - Claude API keyword expansion
- `youtube_scraper.py` - YouTube scraping
- `obsidian_writer.py` - Obsidian REST API writer
- `notebooklm_automation.py` - NotebookLM notebook creation
- `.env` - API keys

## Notes
- NotebookLM auth stored at `~/.notebooklm/storage_state.json`
- Run: double-click desktop shortcut or `streamlit run app.py`
