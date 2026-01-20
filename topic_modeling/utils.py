def generate_topic_name(keywords: list[str], max_words: int = 4) -> str:
    return " / ".join(keywords[:max_words]).title()
