import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from dotenv import load_dotenv

from keyword_expander import expand_keywords
from youtube_scraper import collect_videos
from obsidian_writer import write_note, list_folders, list_notes, get_all_urls
from notebooklm_automation import run_notebooklm

load_dotenv()

st.set_page_config(page_title="YouTube Research App", page_icon="🎬", layout="centered")
st.title("🎬 YouTube Research App")
st.caption("Find YouTube videos, save to Obsidian, summarize in NotebookLM")

with st.sidebar:
    st.header("Configuration")
    anthropic_key = st.text_input("Claude API Key", value=os.getenv("ANTHROPIC_API_KEY", ""), type="password")
    obsidian_key = st.text_input("Obsidian REST API Key", value=os.getenv("OBSIDIAN_API_KEY", ""), type="password")
    st.markdown("---")
    st.markdown("**Obsidian Local REST API** must be running on `localhost:27124`")

keyword = st.text_input("Research keyword", placeholder="e.g. machine learning for beginners")

st.markdown("**Obsidian folder**")
existing_folders = list_folders(obsidian_key) if obsidian_key else []
folder_options = existing_folders + ["➕ Create new folder"]
folder_choice = st.selectbox("Select folder", folder_options, label_visibility="collapsed")
selected_folder = st.text_input("New folder name", placeholder="e.g. Finance Research") if folder_choice == "➕ Create new folder" else folder_choice

st.markdown("**Note**")
existing_notes = list_notes(selected_folder, obsidian_key) if (selected_folder and folder_choice != "➕ Create new folder" and obsidian_key) else []
note_options = existing_notes + ["➕ Create new note"]
note_choice = st.selectbox("Select note", note_options, label_visibility="collapsed")
note_title = st.text_input("New note title", placeholder="e.g. ML Research") if note_choice == "➕ Create new note" else note_choice
notebook_title = f"notebook {note_title.strip().replace('_', ' ')}" if note_title.strip() else ""

col1, col2 = st.columns(2)
with col1:
    max_keywords = st.slider("Related keywords", min_value=1, max_value=10, value=3)
with col2:
    max_per_keyword = st.slider("Videos per keyword", min_value=1, max_value=20, value=5)

run_btn = st.button("🚀 Run Research", width="stretch", type="primary")

if run_btn:
    errors = []
    if not keyword.strip(): errors.append("Please enter a keyword.")
    if not anthropic_key: errors.append("Please enter your Claude API key in the sidebar.")
    if not obsidian_key: errors.append("Please enter your Obsidian API key in the sidebar.")
    if not selected_folder or not selected_folder.strip(): errors.append("Please select or create a folder.")
    if not note_title or not note_title.strip(): errors.append("Please select or create a note.")
    for e in errors:
        st.error(e)
    if not errors:
        log_area = st.empty()
        logs = []

        def log(msg):
            logs.append(msg)
            log_area.code("\n".join(logs), language=None)

        with st.spinner("Working..."):
            log(f"[1/4] Expanding keywords for: '{keyword}'...")
            try:
                related = expand_keywords(keyword, max_keywords, anthropic_key)
                all_keywords = [keyword] + related
                log(f"      Keywords: {', '.join(all_keywords)}")
            except Exception as e:
                st.error(f"Keyword expansion failed: {e}")
                st.stop()

            log(f"[2/4] Searching YouTube ({max_per_keyword} videos x {len(all_keywords)} keywords)...")
            try:
                videos = collect_videos(all_keywords, max_per_keyword)
                log(f"      Found {len(videos)} unique videos.")
                for v in videos:
                    log(f"      - {v['title']}")
            except Exception as e:
                st.error(f"YouTube scraping failed: {e}")
                st.stop()

            log(f"[3/4] Writing to Obsidian ({selected_folder}/{note_title})...")
            try:
                ok = write_note(note_title, selected_folder, keyword, all_keywords, videos, obsidian_key)
                log(f"      Note {'saved' if ok else 'failed — check Obsidian API'}.")
            except Exception as e:
                log(f"      Obsidian write failed: {e}")

            log(f"[4/4] Syncing NotebookLM notebook '{notebook_title}'...")
            try:
                all_urls = get_all_urls(note_title, selected_folder, obsidian_key)
                log(f"      Syncing {len(all_urls)} total URLs from note...")
                notebook_url, nb_logs = run_notebooklm(notebook_title, all_urls)
                for l in nb_logs:
                    log(f"      {l}")
                if notebook_url:
                    st.success(f"Research complete! [Open Notebook]({notebook_url})")
                else:
                    st.warning("Research complete, but NotebookLM URL not returned.")
            except Exception as e:
                log(f"      NotebookLM failed: {e}")
                st.warning("Research complete, but NotebookLM step failed.")

        if videos:
            st.subheader("Videos found")
            st.dataframe(
                [{"Title": v["title"], "URL": v["url"], "Keyword": v["keyword"]} for v in videos],
                width="stretch",
            )
