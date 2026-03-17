import requests
import urllib3
import re
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://127.0.0.1:27124"


def _headers(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}"}


def list_folders(api_key: str) -> list[str]:
    try:
        r = requests.get(f"{BASE}/vault/", headers=_headers(api_key), verify=False, timeout=5)
        if r.status_code != 200:
            return []
        files = r.json().get("files", [])
        folders = sorted({f.split("/")[0] for f in files if "/" in f})
        return folders
    except Exception:
        return []


def list_notes(folder: str, api_key: str) -> list[str]:
    try:
        r = requests.get(f"{BASE}/vault/{folder}/", headers=_headers(api_key), verify=False, timeout=5)
        if r.status_code != 200:
            return []
        files = r.json().get("files", [])
        return sorted([f.replace(".md", "") for f in files if f.endswith(".md")])
    except Exception:
        return []


def get_all_urls(note_title: str, folder: str, api_key: str) -> list[str]:
    filename = note_title.replace(" ", "_") + ".md"
    path = f"{folder}/{filename}" if folder else filename
    r = requests.get(f"{BASE}/vault/{path}", headers=_headers(api_key), verify=False, timeout=5)
    if r.status_code != 200:
        return []
    urls = re.findall(r'https://www\.youtube\.com/watch\?v=[^\s\)]+', r.text)
    return list(dict.fromkeys(urls))


def append_query_result(note_title: str, folder: str, query: str, answer: str, api_key: str) -> bool:
    filename = note_title.replace(" ", "_") + ".md"
    path = f"{folder}/{filename}" if folder else filename
    r = requests.get(f"{BASE}/vault/{path}", headers=_headers(api_key), verify=False, timeout=5)
    if r.status_code != 200:
        return False
    section = "\n".join([
        "",
        f"## NotebookLM Query — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Query:** {query}",
        "",
        answer,
        "",
    ])
    content = r.text + section
    w = requests.put(
        f"{BASE}/vault/{path}",
        headers={**_headers(api_key), "Content-Type": "text/markdown"},
        data=content.encode("utf-8"),
        verify=False,
    )
    return w.status_code in (200, 204)


def write_note(note_title, folder, keyword, keywords_used, videos, api_key):
    filename = note_title.replace(" ", "_") + ".md"
    path = f"{folder}/{filename}" if folder else filename

    existing = requests.get(f"{BASE}/vault/{path}", headers=_headers(api_key), verify=False, timeout=5)

    new_section = "\n".join([
        "",
        f"## Search: {keyword} — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"*Keywords searched: {', '.join(keywords_used)}*",
        "",
    ] + [
        f"- [{v['title']}]({v['url']}) | {v.get('channel', '')} | {v.get('view_count', '')} | {v.get('duration', '')} | {v.get('published', '')} | *{v.get('keyword', '')}*"
        for v in videos
    ])

    content = (existing.text + new_section) if existing.status_code == 200 else f"# {note_title}\n{new_section}"

    r = requests.put(
        f"{BASE}/vault/{path}",
        headers={**_headers(api_key), "Content-Type": "text/markdown"},
        data=content.encode("utf-8"),
        verify=False,
    )
    return r.status_code in (200, 204)
