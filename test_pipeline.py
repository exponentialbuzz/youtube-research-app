"""
Test script: scrape + filter pipeline for a given keyword.
Usage: python test_pipeline.py
"""
import os
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from dotenv import load_dotenv
from youtube_scraper import collect_videos
from video_filter import load_brain, filter_videos

load_dotenv()

KEYWORD = "sleep"
MAX_PER_KEYWORD = 5
SCRAPE_LIMIT = MAX_PER_KEYWORD * 3  # fixed multiplier
TARGET = MAX_PER_KEYWORD
OBSIDIAN_KEY = os.getenv("OBSIDIAN_API_KEY", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")

print("=" * 60)
print(f"Keyword: {KEYWORD}")
print(f"Scraping {SCRAPE_LIMIT} videos, targeting {TARGET} after filter")
print("=" * 60)

# Load brain
print("\n[1] Loading brain from Obsidian...")
brain = load_brain(OBSIDIAN_KEY)
if brain is None:
    print("ERROR: Could not load brain.md from Obsidian. Is Obsidian running?")
    exit(1)
print(f"    min_views={brain.get('min_views')} | "
      f"duration={brain.get('min_duration_minutes')}-{brain.get('max_duration_minutes')}min | "
      f"max_age={brain.get('max_age_years')}yr")

# Scrape
print(f"\n[2] Scraping YouTube for '{KEYWORD}'...")
videos = collect_videos([KEYWORD], SCRAPE_LIMIT)
print(f"    Scraped {len(videos)} videos:\n")
print(f"  {'#':<3} {'Title':<55} {'Views':<12} {'Duration':<10} {'Published':<15} {'Channel'}")
print(f"  {'-'*3} {'-'*55} {'-'*12} {'-'*10} {'-'*15} {'-'*30}")
for i, v in enumerate(videos, 1):
    print(f"  {i:<3} {v['title'][:54]:<55} {v['view_count'][:11]:<12} {v['duration'][:9]:<10} {v['published'][:14]:<15} {v['channel'][:30]}")

# Filter
print(f"\n[3] Filtering...")
filtered, log = filter_videos(videos, KEYWORD, TARGET, brain, ANTHROPIC_KEY)
print(f"    {log}\n")
print(f"  {'#':<3} {'Title':<55} {'Views':<12} {'Duration':<10} {'Published':<15} {'Channel'}")
print(f"  {'-'*3} {'-'*55} {'-'*12} {'-'*10} {'-'*15} {'-'*30}")
for i, v in enumerate(filtered, 1):
    print(f"  {i:<3} {v['title'][:54]:<55} {v['view_count'][:11]:<12} {v['duration'][:9]:<10} {v['published'][:14]:<15} {v['channel'][:30]}")

print("\n" + "=" * 60)
print(f"Result: {len(videos)} scraped → {len(filtered)} after filter")
print("=" * 60)
