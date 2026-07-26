import logging
import pandas as pd
import numpy as np
from fastapi import APIRouter
from pydantic import BaseModel

from backend.config import NEWS_CSV , REDDIT_CSV

router = APIRouter()
logger = logging.getLogger(__name__)

GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_CONTEXT = 18 

class QARequest(BaseModel):
    question : str 
    use_semantic_search : bool = True

def safe_str(val) -> str : 
    if val is None or (isinstance(val , float) and np.isnan(val)):
        return ""
    return str(val)

def load_all_texts() -> list[dict]:
    items = []
    for path , src in [(NEWS_CSV , "news") , (REDDIT_CSV , "reddit")]:
        try: 
            df = pd.read_csv(path)
            if df.empty:
                continue
            for _ , row in df.iterrows():
                t = safe_str(row.get("text" , ""))
                if len(t.split()) >= 8:
                    items.append({
                        "text":   t[:500],
                        "source": src,
                        "title":  safe_str(row.get("title", "")),
                    })
        except Exception :
            pass
    return items

def select_context(question : str , items : list[dict] , use_semantic : bool) -> list[dict] : 
    if not items:
        return []
    
    if use_semantic:
        try: 
            from backend.services.similarity import match_texts_to_query
            texts = [i['text'] for i in items]
            ranked = match_texts_to_query(question , texts , top_k=MAX_CONTEXT)
            ranked_text = {t for t , _ in ranked}
            return [i for i in items if i['text'] in ranked_text][:MAX_CONTEXT]
        except Exception as e:
            logger.warning(f"Semantic search failed ({e})")
            return items[:MAX_CONTEXT]
    else:
        return items[:MAX_CONTEXT]
        

def build_prompt(question : str , context_items : list[dict])-> str:
    context_lines = []
    for i , item in enumerate(context_items , 1) :
        src = item["source"].upper()
        title = f" | {item['title']}" if item.get("title") else ""
        context_lines.append(f"{i}. [{src}{title}]\n   {item['text'][:300]}")
    context = "\n\n".join(context_lines) if context_lines else "No context available."

    return f"""You are CrowdPulse, an AI media intelligence analyst.
Your job is to compare how institutional news media and Reddit public discourse frame current events.
 
CONTEXT — recent news articles and Reddit posts:
{context}
 
USER QUESTION: {question}
 
Instructions:
- Answer clearly and concisely (3-5 sentences max for simple questions).
- Reference whether insights come from NEWS or REDDIT sources.
- If the question asks about differences between news and Reddit, be specific.
- If you cannot answer from the context, say so honestly.
- Use bullet points only when listing multiple items."""
 

@router.post("/qa")
async def ask_question(req : QARequest):
    try: 
        from groq import Groq
        from backend.config import settings

        items = load_all_texts()
        context = select_context(req.question , items , req.use_semantic_search)
        if not context:
            return {
                "status" : "success" , 
                "data" : {
                    "answer" : "No data available. Please fetch data first" , 
                    "sources" : [] , 
                    "n_context" : 0
                }
            }
        prompt = build_prompt(req.question , context)



        if not settings.GROQ_API_KEY:
            return {
                "status" : "success" , 
                "data" : {
                    "answer" : "GROQ_API_KEY is not set in .env" , 
                    "sources" : [] , 
                    "n_context" : 0
                }
            }
        
        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model= GROQ_MODEL , 
            messages= [{'role' : 'user' , "content" : prompt}] , 
            temperature= 0.3 , 
            max_tokens= 800
        )

        answer = response.choices[0].message.content
        return {
            "status": "success",
            "data": {
                "answer":    answer,
                "sources":   [i["title"] or i["text"][:60] for i in context[:5]],
                "n_context": len(context),
            }
        }
    except Exception as e:
        logger.exception("QA generation failed")

        return {
            "status": "error",
            "data": {
                "answer": "An unexpected error occurred while generating the answer.",
                "sources": [],
                "n_context": 0
            }
        }