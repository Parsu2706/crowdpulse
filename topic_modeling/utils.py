from config.paths import sentiment_colors
def generate_topic_name(keywords: list[str], max_words: int = 4) -> str:
    return " / ".join(keywords[:max_words]).title()


def color_sentiment_values(val): 
    color = sentiment_colors.get(val , "")
    return f"background-color: {color}; color: white; font-weight: bold"
