from dotenv import load_dotenv
load_dotenv()

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

 
from backend.routes.scraper  import router as scraper_router
from backend.routes.sentiment import router as sentiment_router
from backend.routes.topics   import router as topics_router
from backend.routes.entities import router as entities_router
from backend.routes.digest   import router as digest_router
from backend.routes.qa       import router as qa_router
from backend.routes.history  import router as history_router

logging.basicConfig(
    level=logging.INFO , 
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

app = FastAPI(
    title="CrowdPulse API" , 
    version="1.0.0" , 
    description="Narrative Intelligence: News vs Reddit comparison"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scraper_router,  tags=["Scraper"])
app.include_router(sentiment_router, tags=["Sentiment"])
app.include_router(topics_router,   tags=["Topics"])
app.include_router(entities_router, tags=["Entities"])
app.include_router(digest_router,   tags=["Digest"])
app.include_router(qa_router,       tags=["QA"])
app.include_router(history_router,  tags=["History"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "CrowdPulse Demo API"}

@app.get("/")
def root():
    return {
        "message": "CrowdPulse Demo API",
        "docs":    "/docs",
        "health":  "/health",
    }