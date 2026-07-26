import os 
import requests
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st 
 
API_BASE = os.getenv("CROWDPULSE_API_URL", "http://localhost:8000")
TIMEOUT = 30 * 60
SENTIMENT_COLORS = {
    "POSITIVE": "#2ecc71",
    "NEGATIVE": "#e74c3c",
    "NEUTRAL":  "#95a5a6",
}

st.set_page_config(
    page_title="CrowdPulse - Narrative Intelligence" , 
    layout="wide"
)



def api_get(path : str , params : dict | None = None) : 
    try: 
        r = requests.get(f"{API_BASE}{path}" , params=params , timeout=TIMEOUT)
        r.raise_for_status()
        body = r.json()
        if body.get("status") == "success" : 
            return True , body.get("data")
        return False , body.get("message" , "Unknown error")
    except requests.exceptions.ConnectionError:
        return False , f"Cannot reach backend at {API_BASE}"
    except Exception as e :
        return False , str(e)

def api_post(path : str , json_body : dict | None = None):
    try: 
        r = requests.post(f"{API_BASE}{path}" , json=json_body , timeout=TIMEOUT)
        r.raise_for_status() 
        body = r.json()
        if body.get('status') == "success":
            return True , body.get("data")
        return False , body.get("message" , "Unknown error")
    except requests.exceptions.ConnectionError:
        return False, f"Cannot reach backend at {API_BASE}."
    except Exception as e:
        return False, str(e)

def backend_check() -> bool: 
    try : 
        r = requests.get(f"{API_BASE}/health" , timeout=3)
        return r.status_code == 200 
    except Exception:
        return False


with st.sidebar:
    st.title("Crowpulse")
    st.caption("News vs Reddit Narrative Intelligence")

    if backend_check():
        st.success(f"Backend Connected\n{API_BASE}")
    else:
        st.error(f"Backend unreachable\n{API_BASE}")
    
    st.divider()

    if st.button("Fetch fresh data" , use_container_width=True , type='primary'):
        with st.spinner("Scraping news + reddit... THis can take minute"):
            ok , data = api_post("/scrape")
        if ok:
            st.success(f"News: {data['news']}. Reddit: {data['reddit']}")
            if data.get('errors'):
                for e in data['errors']:
                    st.warning(e)
            st.cache_data.clear()
        else:
            st.error(f"Scrape failed: {data}")
    if st.button("♻️ Force-Refresh AI Digest", use_container_width=True):
        with st.spinner("Regenerating digest..."):
            ok, data = api_post("/digest/force")
        if ok:
            st.success("Digest refreshed")
            st.cache_data.clear()
        else:
            st.error(f"Digest refresh failed: {data}")
    st.divider()
tab_overview, tab_sentiment, tab_topics, tab_entities, tab_qa, tab_timeline = st.tabs(
    ["🧭 Overview", "💬 Sentiment", "🗂️ Topics", "🏷️ Entities", "❓ Ask AI", "📅 Timeline"]
)
 
with tab_overview:
    st.header("Daily Intelligence Briefing")
    ok , digest = api_get("/digest")
    if not ok:
        st.error(f"Could not load digest: {digest}")
    else:
        if digest.get("error"):
            st.info(digest.get("headline" , "Digest unavailable"))
            st.caption(digest.get("analyst_note" , ""))
        else:
            st.subheader(digest.get("headline" , "") )

            col1 , col2 = st.columns(2)
            with col1 :
                st.metric("Sentiment Pulse" , digest.get("sentiment_pulse" , "") )
            with col2:
                st.metric("Most Discussed Entity", digest.get("most_discussed_entity", "—"))
            st.markdown("**Top Topics Today**")
            for t in digest.get("top_topics", []):
                st.markdown(f"- **{t.get('topic')}** — {t.get('summary')}")
 
            st.markdown("**News vs. Reddit Narrative Gap**")
            st.info(digest.get("narrative_gap", "—"))
 
            st.markdown("**Analyst Note**")
            st.success(digest.get("analyst_note", "—"))

with tab_sentiment:
    st.subheader("Sentiment Breakdown")
    ok , data = api_get("/sentiment")
    if not ok:
        st.error(f"Could not load sentiment: {data}")
    else:
        col1 , col2 , col3 = st.columns(3)
        with col1:
            st.markdown("**Combined**")
            fig = go.Figure(data=[go.Pie(
                labels=list(data["combined"].keys()),
                values=list(data["combined"].values()),
                marker=dict(colors=[SENTIMENT_COLORS[k] for k in data["combined"]]),
                hole=0.4,
            )])
            fig.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True , key='sentiment_combined')
 
        with col2:
            st.markdown("**News**")
            fig = go.Figure(data=[go.Pie(
                labels=list(data["news"].keys()),
                values=list(data["news"].values()),
                marker=dict(colors=[SENTIMENT_COLORS[k] for k in data["news"]]),
                hole=0.4,
            )])
            fig.update_layout(height = 300 , margin = dict(t = 10 , b = 10 , l = 10 , r = 10))
            st.plotly_chart(fig , use_container_width=True , key = "sentiment_news")
        
        with col3:
            st.markdown("**Reddit**")
            fig = go.Figure(data=[go.Pie(
                labels=list(data["reddit"].keys()),
                values=list(data["reddit"].values()),
                marker=dict(colors=[SENTIMENT_COLORS[k] for k in data["reddit"]]),
                hole=0.4,
            )])
            fig.update_layout(height = 300 , margin = dict(t=10 , b= 10 , l = 10 , r = 10))
            st.plotly_chart(fig , use_container_width=True , key = "sentiment_reddit")
        st.metric("News Avg. Confidence" , data.get("news_avg_conf" , "_"))

with tab_topics:
    st.subheader("Topic Clusetrs")
    ok , data = api_get("/topics")
    if not ok:
        st.warning(f"{data}")
    else:
        st.caption(
            f"{data['total_texts']} texts analyzed . "
            f"{data['n_news']} news · {data['n_reddit']} reddit"
        )
        for tid_str, name in data["topic_names"].items():
            split = data["topic_splits"].get(tid_str) or data["topic_splits"].get(int(tid_str), {})
            keywords = data["keywords"].get(tid_str) or data["keywords"].get(int(tid_str), [])
            reps = data["representatives"].get(tid_str) or data["representatives"].get(int(tid_str), {})

            with st.expander(f"{name} . {split.get('total' , 0)} mentions"):
                st.caption("Keywords: " + ", ".join(keywords))

                c1 , c2 = st.columns(2)
                with c1 :
                    st.markdown(f"**News ({split.get('news' , 0)})")
                    news_rep = reps.get("news" , {})
                    if news_rep.get('title'):
                        st.markdown(f"*{news_rep['title']}*")
                    st.write(news_rep.get('text' , ""))
                    if news_rep.get("url"):
                        st.caption(news_rep['url'])
                
                with c2:
                    st.markdown(f"**Reddit** ({split.get('reddit' , 0)})")
                    reddit_rep = reps.get("reddit" , {})
                    if reddit_rep.get('title'):
                        st.markdown(f"*{reddit_rep['title']}*")
                    st.write(reddit_rep.get("text" , ""))
    

with tab_entities:
    st.header("Top Entities")
    source = st.radio("Source" , ["both" , "news" , "reddit"] , horizontal=True)
    ok , data = api_get("/entities" , params={"source" : source , "top_n" : 20})

    if not ok:
        st.warning(f"{data}")
    else:
        if source == "both":
            c1 , c2 = st.columns(2)
            with c1 :
                st.markdown("**News Entities**")
                if data['news_entities']:
                    df = pd.DataFrame(
                        data["news_entities"].items(), columns=["Entity", "Mentions"]
                    ).sort_values("Mentions", ascending=True)
                    fig = px.bar(df, x="Mentions", y="Entity", orientation="h")
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True , key = "entities_news")
        else:
            if data['entities'] : 
                df = pd.DataFrame(
                    data['entities'].items() , columns=["Entity" , "Mentions"]
                ).sort_values("Mentions" , ascending=True)
                fig = px.bar(df , x="Mentions" , y = "Entity" , orientation="h")
                fig.update_layout(height = 500)
                st.plotly_chart(fig , use_container_width=True , key = "entities_reddit")
            else:
                st.info("No entities found")
        
with tab_qa:
    st.header("Ask CrowdPulse")
    st.caption("Ask questions about how news and reddit are framing current events")
    question = st.text_input("Your question" , placeholder="how does Reddit's reaction differ from news coverage on this topic?")
    use_semantic = st.checkbox("Use semantic search for context" , value=True)

    if st.button("Ask" , type="primary") and question.strip():
        with st.spinner("Thinking..."):
            try:
                r = requests.post(
                    f"{API_BASE}/qa" , 
                    json={"question" : question , "use_semantic_search" : use_semantic} , 
                    timeout=60
                )

                r.raise_for_status()
                body = r.json()
                data = body.get("data" , {})
                if body.get("status") == "success":
                    st.markdown(data.get("answer" , "No answer returned"))
                    if data.get("sources"):
                        with st.expander(f"Sources ({data.get('n_context' , 0)}) context items"):
                            for s in data["sources"]:
                                st.markdown(f"- {s}")
                else:
                    st.error(data.get("answer" , body.get("message" , "Error")))
            except requests.exceptions.ConnectionError:
                st.error(f"Cannot reach backend at {API_BASE}. ")
            except Exception as e:
                st.error(str(e))
    
with tab_timeline:
    st.header("Historical Snapshots")
    days = st.slider("Days of history" , min_value=1 , max_value=90 , value=30)
    ok , data = api_get("/timeline" , params={"days" : days})

    if not ok:
        st.warning(f"{data}")
    else:
        snapshots = data.get("snapshots" , [])
        if not snapshots:
            st.info("No snapshots saved yet. Run a scrape to start building history.")
        else:
            st.caption(f"{data['count']} snapshot(s) found")

            rows = []
            for snap in snapshots:
                s = snap.get("sentiment_summary" , {})
                rows.append({
                    "date" : snap.get("date") , 
                    "news_count" : snap.get("news_count" , 0), 
                    "reddit_count" : snap.get("reddit_count" , 0) , 
                    "positive": s.get("POSITIVE", 0),
                    "negative": s.get("NEGATIVE", 0),
                    "neutral": s.get("NEUTRAL", 0),  
                })
            hist_df = pd.DataFrame(rows).sort_values("date")
 
            fig = px.line(
                hist_df, x="date", y=["news_count", "reddit_count"],
                markers=True, title="Volume Over Time"
            )
            st.plotly_chart(fig, use_container_width=True ,key = "entities_single")
 
            fig2 = px.bar(
                hist_df, x="date", y=["positive", "negative", "neutral"],
                title="Sentiment Over Time",
                color_discrete_map={
                    "positive": SENTIMENT_COLORS["POSITIVE"],
                    "negative": SENTIMENT_COLORS["NEGATIVE"],
                    "neutral":  SENTIMENT_COLORS["NEUTRAL"],
                })
            st.plotly_chart(fig2 , use_container_width=True , key = "timeline_volume")
            with st.expander("View raw snapshot for specific day"):
                date_options = [s["date"] for s in snapshots]
                picked = st.selectbox("Date" , date_options)
                ok2 , snap_detail = api_get(f"/snapshot/{picked}")
                if ok2:
                    st.json(snap_detail)
                else:
                    st.warning(snap_detail)
                    