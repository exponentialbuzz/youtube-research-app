import scrapetube


def search_youtube(keyword: str, max_results: int) -> list[dict]:
    videos = scrapetube.get_search(keyword, limit=max_results)
    results = []
    for video in videos:
        video_id = video.get("videoId")
        if not video_id:
            continue
        title = ""
        try:
            title = video["title"]["runs"][0]["text"]
        except (KeyError, IndexError):
            title = video_id
        results.append({
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "keyword": keyword,
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
