import anthropic


def expand_keywords(seed_keyword: str, num_keywords: int, api_key: str) -> list[str]:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Generate {num_keywords} related YouTube search keywords for the topic: '{seed_keyword}'.\n"
                    "Return ONLY a plain list, one keyword per line, no numbering, no bullets, no extra text."
                ),
            }
        ],
    )
    raw = message.content[0].text.strip()
    keywords = [line.strip() for line in raw.splitlines() if line.strip()]
    return keywords[:num_keywords]
