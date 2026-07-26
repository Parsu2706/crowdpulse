"""
services/digest.py
Generates a structured AI briefing using Gemini.
Cached for 1 hour in Redis / memory to avoid burning API quota.
"""
import json
import re
import time
import logging

import pandas as pd

logger = logging.getLogger(__name__)

GROQ_MODEL = "llama-3.3-70b-versatile"
CACHE_KEY    = "crowdpulse:digest"
CACHE_TTL    = 3600   # 1 hour


# ── Context builder ────────────────────────────────────────────────────────


def _load_safe(path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        return df if not df.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def _build_context() -> dict:
    from backend.config import NEWS_CSV, REDDIT_CSV

    news_df   = _load_safe(NEWS_CSV)
    reddit_df = _load_safe(REDDIT_CSV)

    top_news = (
        news_df["title"].dropna().head(15).tolist()
        if not news_df.empty and "title" in news_df.columns else []
    )
    top_reddit = (
        reddit_df.sort_values("score", ascending=False)["title"]
        .dropna().head(15).tolist()
        if not reddit_df.empty and "score" in reddit_df.columns else []
    )

    sub_activity = {}
    if not reddit_df.empty and "subreddit" in reddit_df.columns:
        sub_activity = reddit_df["subreddit"].value_counts().head(5).to_dict()

    return {
        "news_count":       len(news_df),
        "reddit_count":     len(reddit_df),
        "top_news":         top_news,
        "top_reddit":       top_reddit,
        "subreddit_activity": sub_activity,
    }


def _build_prompt(ctx: dict) -> str:
    news_block   = "\n".join(f"- {h}" for h in ctx["top_news"])
    reddit_block = "\n".join(f"- {t}" for t in ctx["top_reddit"])

    return f"""You are CrowdPulse, an AI media intelligence analyst.
Compare how institutional news media and Reddit public discourse frame current events.

DATA SNAPSHOT:
- News articles scraped: {ctx['news_count']}
- Reddit posts scraped:  {ctx['reddit_count']}
- Active subreddits: {ctx['subreddit_activity']}

TOP NEWS HEADLINES:
{news_block if news_block else '- (no data)'}

TOP REDDIT POSTS (by upvotes):
{reddit_block if reddit_block else '- (no data)'}

Produce a daily intelligence briefing. Return ONLY this exact JSON, no markdown, no code fences:
{{
  "headline": "One sharp sentence summarizing today's narrative landscape",
  "top_topics": [
    {{"topic": "topic name", "summary": "why this matters today in 1 sentence"}},
    {{"topic": "topic name", "summary": "why this matters today in 1 sentence"}},
    {{"topic": "topic name", "summary": "why this matters today in 1 sentence"}}
  ],
  "sentiment_pulse": "Overall mood across both platforms — anxious, angry, hopeful, neutral?",
  "most_discussed_entity": "Most-mentioned person or org and why they dominate today",
  "narrative_gap": "Most striking difference between news media and Reddit framing — be specific",
  "analyst_note": "Your sharpest non-obvious insight from the data"
}}"""


def _call_groq(prompt : str , api_key : str) -> str:
    from groq import Groq
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=GROQ_MODEL , 
        messages=[{"role" : "user" , "content" : prompt}] , 
        temperature=0.4 , 
        max_tokens=1000
    )
    return response.choices[0].message.content




def _strip_json(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end != -1:
        return raw[start:end + 1]
    return raw


# ── Public API ─────────────────────────────────────────────────────────────

def generate_digest(force: bool = False) -> dict:

    from backend.config import settings
    from backend.cache import get_cached, set_cached

    if not force:
        cached = get_cached(CACHE_KEY)
        if cached:
            logger.info("Returning cached digest")
            return cached

    if not settings.GROQ_API_KEY:
        return _no_key_response()
    
    ctx = _build_context()
    if ctx["news_count"] == 0 and ctx["reddit_count"] == 0:
        return _no_data_response()

    try:
        prompt = _build_prompt(ctx)

        raw = _call_groq(prompt , settings.GROQ_API_KEY)
        result = json.loads(_strip_json(raw))
        result["generated_at"] = int(time.time())

        set_cached(CACHE_KEY, result, ttl=CACHE_TTL)
        logger.info("Digest generated ✓")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Digest JSON parse error: {e}")
        return _error_response(f"Groq returned malformed JSON: {e}")
    except Exception as e:
        logger.exception("Digest generation failed")
        return _error_response(str(e))


# ── Helper responses ───────────────────────────────────────────────────────

def _no_key_response() -> dict:
    return {
        "error":                "no_api_key",
        "headline":             "AI digest unavailable — GROQ_API_KEY  not set in .env",
        "top_topics":           [],
        "sentiment_pulse":      "—",
        "most_discussed_entity": "—",
        "narrative_gap":        "—",
        "analyst_note":         "Add GROQ_API_KEY  to your .env file to enable this feature.",
        "generated_at":         int(time.time()),
    }


def _no_data_response() -> dict:
    return {
        "error":                "no_data",
        "headline":             "No data scraped yet — click Fetch Fresh Data first",
        "top_topics":           [],
        "sentiment_pulse":      "—",
        "most_discussed_entity": "—",
        "narrative_gap":        "—",
        "analyst_note":         "Visit the sidebar and click Fetch Fresh Data.",
        "generated_at":         int(time.time()),
    }


def _error_response(msg: str) -> dict:
    return {
        "error":                msg,
        "headline":             "Could not generate digest",
        "top_topics":           [],
        "sentiment_pulse":      "—",
        "most_discussed_entity": "—",
        "narrative_gap":        "—",
        "analyst_note":         f"Error: {msg}",
        "generated_at":         int(time.time()),
    }