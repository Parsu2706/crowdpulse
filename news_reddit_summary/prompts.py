TOPIC_NARRATIVE_PROMPT = """
You are an analyst comparing institutional media and public discourse.

TOPIC (News): {news_topic}
TOPIC (Reddit): {reddit_topic}

NEWS TEXTS:
{news_texts}

REDDIT TEXTS:
{reddit_texts}

SENTIMENT CONTEXT:
News sentiment: {news_sentiment}
Reddit sentiment: {reddit_sentiment}

TASK:
Explain:
1. What both sides agree on
2. How framing differs
3. What Reddit emphasizes that News downplays
4. What News emphasizes that Reddit ignores

Keep the tone analytical and concise.
"""
