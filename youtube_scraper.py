import scrapetube


def _safe(video, *keys, default=""):
    try:
        val = video
        for k in keys:
            val = val[k]
        return str(val) if val is not None else default
    except (KeyError, IndexError, TypeError):
        return default


def search_youtube(keyword: str, max_results: int) -> list[dict]:
    videos = scrapetube.get_search(keyword, limit=max_results)
    results = []
    for video in videos:
        video_id = video.get("videoId")
        if not video_id:
            continue
        title = _safe(video, "title", "runs", 0, "text") or video_id
        view_count = (
            _safe(video, "viewCountText", "simpleText")
            or _safe(video, "viewCountText", "runs", 0, "text")
        )
        duration = _safe(video, "lengthText", "simpleText")
        published = _safe(video, "publishedTimeText", "simpleText")
        channel = (
            _safe(video, "ownerText", "runs", 0, "text")
            or _safe(video, "longBylineText", "runs", 0, "text")
        )
        results.append({
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "keyword": keyword,
            "view_count": view_count,
            "duration": duration,
            "published": published,
            "channel": channel,
        })
    return results


def collect_videos(keywords: list[str], max_per_keyword: int) -> list[dict]:
    seen_urls = set()
    all_videos = []
    for kw in keywords:
        for video in search_youtube(kw, max_per_keyword):
            if video["url"] not in seen_urls:
                seen_urls.add(video["url"])
                all_videos.append(video)
    return all_videos
