import asyncio
from news_reddit_summary.gemini_client import run_topic_analysis

async def analyze_aligned_topics(bundle): 
    tasks = [run_topic_analysis(f) for f in bundle ]
    results =  await asyncio.gather(*tasks , return_exceptions=True)
    cleaned = []
    for res in results:
        if isinstance(res , Exception): 
            cleaned.append({
                "news_topic": "Error" , 
                "reddit_topic" : "Error" , 
                "analysis" : f"Failed to generate analysis{res}"
            })
        else:
            cleaned.append(res)
    return cleaned
    
