import os
import asyncio
from google import genai
from dotenv import load_dotenv
from news_reddit_summary.prompts import TOPIC_NARRATIVE_PROMPT

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "models/gemini-1.0-pro"

sem = asyncio.Semaphore(2)


async def run_topic_analysis(full_text): 
    async with sem: 
        prompt = TOPIC_NARRATIVE_PROMPT.format(
            news_topic=full_text["news_topic"],
            reddit_topic=full_text["reddit_topic"],
            news_texts="\n".join(full_text["news_texts"]),
            reddit_texts="\n".join(full_text["reddit_texts"]),
            news_sentiment=full_text["news_sentiment"],
            reddit_sentiment=full_text["reddit_sentiment"],
        )
        response = await client.models.generate_content_async(
            model=MODEL,
            contents=prompt,config={"temperature": 0.2,"max_output_tokens": 1800}
            )
        return {
            "news_topic": full_text["news_topic"] , 
            "reddit_topic" : full_text["reddit_topic"] , 
            "analysis" : response.text.strip()
        }