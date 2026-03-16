---
min_views: 5000
min_duration_minutes: 4
max_duration_minutes: 45
max_age_years: 3
preferred_channels: []
blocked_channels: []
quality_prompt: "Prefer videos from medical professionals, researchers, hospitals, or universities. Avoid clickbait, overly promotional, or low-quality content. Prioritize educational depth over entertainment."
scrape_multiplier: 3
---

# Research Brain

This file controls how the YouTube Research App selects and filters videos.
Edit the values above to change default behavior.

## Settings explained

- **min_views**: Minimum view count to consider a video
- **min_duration_minutes / max_duration_minutes**: Duration range in minutes
- **max_age_years**: Ignore videos older than this many years
- **preferred_channels**: List of channel names to prioritize (leave empty for none)
- **blocked_channels**: List of channel names to always exclude
- **quality_prompt**: Instructions for Claude when evaluating video quality
- **scrape_multiplier**: How many times more videos to scrape before filtering (3 = scrape 3x target, filter down)
