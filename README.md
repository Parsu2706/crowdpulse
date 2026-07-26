
# CrowdPulse — News vs. Reddit Narrative Intelligence

CrowdPulse scrapes live news articles and Reddit posts, analyzes them for sentiment, topics, and key entities, and lets you compare how institutional media and public discourse frame the same events. Ask it a question in plain English and it answers using an LLM grounded in the scraped data — with an AI-generated daily briefing, a topic explorer, an entity tracker, and a historical timeline, all in one dashboard.


## Features

* Dual-source scraping — pulls headlines from 10 major RSS feeds (BBC, NPR, Reuters, AP, The Guardian, Al Jazeera) and hot posts from 10 subreddits via PRAW
* Fine-tuned sentiment analysis — a custom-trained transformer model classifies every article/post as positive, negative, or neutral
* Topic modeling — BERTopic clusters news and Reddit text together so you can see which topics are shared and which are unique to each source
* Named entity extraction — spaCy pulls out the people, organizations, and places dominating the conversation
* AI daily digest — an LLM (via Groq) generates a structured briefing: top topics, sentiment pulse, most-discussed entity, and the biggest gap between how news and Reddit are framing things
* Ask AI (RAG-style Q&A) — ask a natural-language question; semantic search pulls the most relevant scraped snippets and an LLM answers grounded in them, citing sources
* Historical timeline — daily snapshots are saved to disk, so you can track sentiment and volume trends over time
* Scheduled automation — a background scheduler re-scrapes and re-labels data every 6 hours without manual intervention
* Redis caching (with automatic in-memory fallback) for the digest and other expensive computations
* DVC pipeline for reproducible offline runs of the scrape → label → topic-model → extract-entities → snapshot stages
* Dockerized — one docker-compose up starts Redis, the API, the scheduler, and the UI together
## Tech Stack

| Layer | Technology |
|--------|------------|
| **Frontend** | Streamlit, Plotly |
| **Backend API** | FastAPI |
| **News Scraping** | feedparser (RSS) |
| **Reddit Scraping** | PRAW |
| **Sentiment Analysis** | Fine-tuned Hugging Face Transformers model |
| **Topic Modeling** | BERTopic |
| **Named Entity Recognition** | spaCy (`en_core_web_sm`) |
| **Semantic Retrieval** | sentence-transformers (`all-MiniLM-L6-v2`) |
| **LLM Generation** | Groq (`llama-3.3-70b-versatile`) |
| **Caching** | Redis (with in-memory fallback) |
| **Scheduling** | APScheduler |
| **Pipeline Reproducibility** | DVC |
| **Containerization** | Docker Compose |
## Usage

- Click Fetch fresh data in the sidebar to scrape the latest news and Reddit posts (this can take a minute).
- Overview — read the AI-generated daily briefing: top topics, sentiment pulse, most-discussed entity, and the news-vs-Reddit narrative gap.
- Sentiment — see the positive/negative/neutral breakdown, combined and split by source.
- Topics — expand any topic cluster to see representative news and Reddit content side by side.
- Entities — view the most-mentioned people, organizations, and places, filterable by source.
- Ask AI — type a question (e.g. "how does Reddit's reaction differ from news coverage on this topic?") and get an answer grounded in the scraped data, with sources listed.
- Timeline — track sentiment and volume trends over the last 1–90 days, with raw snapshot JSON available per day.
## Limitation

Known limitations
- sources aren't user-configurable yet.
- Topic modeling and entity extraction cap out at a fixed number of texts per run (400 and 100 respectively) for performance, so very high-volume days are sampled rather than fully processed.
- Daily snapshots are never overwritten once created for a given date — if data changes later in the day, the snapshot won't reflect it until the next day.
- The Ask AI feature's semantic search ranks individual scraped snippets, not full articles, so very long-context questions may lose nuance.
- No authentication on the API — not intended for public deployment as-is.