import re
import yaml
import json
import requests
import urllib3
import anthropic

urllib3.disable_warnings()

OBSIDIAN_BASE = "https://127.0.0.1:27124"


def load_brain(obsidian_api_key: str) -> dict | None:
    """Load brain.md from Obsidian and parse YAML frontmatter. Returns None if unreachable or unparseable."""
    try:
        r = requests.get(
            f"{OBSIDIAN_BASE}/vault/YouTube%20Research%20App/brain.md",
            headers={"Authorization": f"Bearer {obsidian_api_key}"},
            verify=False, timeout=5,
        )
        if r.status_code != 200:
            return None
        content = r.text
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return None
        return yaml.safe_load(match.group(1))
    except Exception:
        return None


def parse_views(view_text: str) -> int:
    """Convert '1.2M views', '45K views', '2,029 views' to int."""
    if not view_text:
        return 0
    text = view_text.lower().replace(",", "").replace(" views", "").replace(" view", "").strip()
    try:
        if "m" in text:
            return int(float(text.replace("m", "")) * 1_000_000)
        if "k" in text:
            return int(float(text.replace("k", "")) * 1_000)
        return int(float(text))
    except Exception:
        return 0


def parse_duration_minutes(duration_text: str) -> float:
    """Convert '20:57' or '1:05:30' to minutes."""
    if not duration_text:
        return 0
    parts = duration_text.strip().split(":")
    try:
        if len(parts) == 2:
            return int(parts[0]) + int(parts[1]) / 60
        if len(parts) == 3:
            return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60
    except Exception:
        pass
    return 0


def parse_age_years(age_text: str) -> float:
    """Convert '2 years ago', '3 months ago', '1 week ago' to years."""
    if not age_text:
        return 0
    text = age_text.lower()
    try:
        num = float(re.search(r"[\d.]+", text).group())
        if "year" in text:
            return num
        if "month" in text:
            return num / 12
        if "week" in text:
            return num / 52
        if "day" in text:
            return num / 365
    except Exception:
        pass
    return 0


def mechanical_filter(videos: list[dict], brain: dict) -> list[dict]:
    """Apply hard numeric filters before Claude evaluation."""
    filtered = []
    for v in videos:
        views = parse_views(v.get("view_count", ""))
        duration = parse_duration_minutes(v.get("duration", ""))
        age = parse_age_years(v.get("published", ""))
        channel = v.get("channel", "").lower()

        if brain["blocked_channels"] and any(
            b.lower() in channel for b in brain["blocked_channels"]
        ):
            continue
        if views < brain["min_views"]:
            continue
        if duration < brain["min_duration_minutes"]:
            continue
        if duration > brain["max_duration_minutes"]:
            continue
        if age > brain["max_age_years"]:
            continue

        filtered.append(v)
    return filtered


def claude_filter(videos: list[dict], topic: str, brain: dict, target: int, api_key: str) -> list[dict]:
    """Use Claude to intelligently rank and select the best videos."""
    if not videos:
        return []

    client = anthropic.Anthropic(api_key=api_key)

    video_list = "\n".join([
        f"{i+1}. Title: {v['title']} | Channel: {v.get('channel','')} | "
        f"Views: {v.get('view_count','')} | Duration: {v.get('duration','')} | "
        f"Published: {v.get('published','')}"
        for i, v in enumerate(videos)
    ])

    preferred = ", ".join(brain["preferred_channels"]) if brain["preferred_channels"] else "none specified"

    prompt = f"""You are selecting the best YouTube videos for research on: "{topic}"

Quality criteria:
{brain['quality_prompt']}

Preferred channels: {preferred}

Here are the candidate videos:
{video_list}

Select the best {target} videos from this list that are most relevant, credible, and useful for research on "{topic}".
Return ONLY a JSON array of the numbers (1-based) of the selected videos, like: [1, 3, 5, 7]
No explanation, just the JSON array."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    match = re.search(r"\[[\d,\s]+\]", raw)
    if not match:
        return videos[:target]

    indices = json.loads(match.group())
    selected = []
    for i in indices:
        if 1 <= i <= len(videos):
            selected.append(videos[i - 1])
    return selected[:target]


def filter_videos(
    videos: list[dict],
    topic: str,
    target: int,
    brain: dict,
    api_key: str,
    use_claude: bool = True,
) -> tuple[list[dict], str]:
    """
    Full filtering pipeline. Returns (filtered_videos, log_message).
    """
    original = len(videos)
    after_mechanical = mechanical_filter(videos, brain)
    log = f"Mechanical filter: {original} → {len(after_mechanical)} videos. "

    if not after_mechanical:
        log += "No videos passed filters — returning top results unfiltered."
        return videos[:target], log

    if use_claude and len(after_mechanical) > target:
        final = claude_filter(after_mechanical, topic, brain, target, api_key)
        log += f"Claude filter: {len(after_mechanical)} → {len(final)} videos selected."
    else:
        final = after_mechanical[:target]
        log += f"Returning top {len(final)} after mechanical filter."

    return final, log
