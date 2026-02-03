import streamlit as st
import pandas as pd
import plotly.express as px
import asyncio
from utils.topic_alignment import align_topic_to_text
from news_reddit_summary.summarizer import analyze_aligned_topics
from utils.topic_similarity import semantic_topic_similarity
from topic_modeling.utils import generate_topic_name


from utils.session_keys import DF_NEWS_TOPICS,DF_REDDIT_TOPICS,NEWS_TOPIC_KEYWORDS,REDDIT_TOPIC_KEYWORDS,TOPIC_SIMILARITY_DF,TOPIC_NARRATIVES
st.set_page_config(page_title="News vs Reddit Comparison" , layout="wide")
st.title("News vs Reddit - Comparative Analysis")
st.divider()
all_keys = [DF_NEWS_TOPICS,DF_REDDIT_TOPICS,NEWS_TOPIC_KEYWORDS,REDDIT_TOPIC_KEYWORDS,TOPIC_SIMILARITY_DF,TOPIC_NARRATIVES]
for key in all_keys: 
    if key not in st.session_state: 
        st.session_state[key] = None
 
df_news = st.session_state.get(DF_NEWS_TOPICS)
df_reddit = st.session_state.get(DF_REDDIT_TOPICS)


news_topic_keywords = st.session_state.get(NEWS_TOPIC_KEYWORDS)
reddit_topic_keywords = st.session_state.get(REDDIT_TOPIC_KEYWORDS)


if df_news is None or df_reddit is None:
    st.info("Please run **Sentiment Analysis and Topic Modeling** for both News and Reddit first.")
    st.stop()

tab1 , tab2 , tab3 = st.tabs(["📊 Sentiment Comparison", "🧠 Topic Alignment", "🧾 Narrative Analysis"])


with tab1: 
    st.subheader("Sentiment Distribution Comparison")
    sentiments_are = ['POSITIVE' , "NEGATIVE" , "NEUTRAL"]
    news_percent = df_news["label"].value_counts(normalize=True) * 100
    reddit_percent = df_reddit["label"].value_counts(normalize=True) * 100
    percentage_df = pd.concat([news_percent , reddit_percent] , axis=1 , keys = ["News (%)" , "Reddit (%)"]).fillna(0).reindex(sentiments_are).round(1)
    
    col1 , col2 = st.columns([1 , 2])

    with col1 : 
        st.markdown("**Percentage Distribution**")
        st.dataframe(percentage_df, use_container_width=True)
    
    with col2: 
        count_df = pd.concat([df_news['label'].value_counts() , df_reddit['label'].value_counts()] , axis=1 , keys = ["News" , "Reddit"]).fillna(0).reindex(sentiments_are)
        fig = px.bar(count_df , barmode="group" , labels= {"value":"count" , "index"  : "Sentiments"} , title="Sentiment Counts : News vs Reddit")
        fig.update_layout(height=300,margin=dict(t=50))
        st.plotly_chart(fig, use_container_width=True)


with tab2: 
    st.subheader("Semantic Topic Alignment")
    if news_topic_keywords is None or reddit_topic_keywords is None:
        st.info("Run **Topic Modeling** on both News and Reddit Data")
        st.stop()
    if st.session_state[TOPIC_SIMILARITY_DF] is None: 
        rows = []

        for r_id , r_words in reddit_topic_keywords.items(): 
            best_match = None
            best_score = 0.0
            for n_id , n_words in news_topic_keywords.items(): 
                score = semantic_topic_similarity(r_words , n_words)
                if score > best_score: 
                    best_score = score
                    best_match = n_id 
            rows.append(
                {
                    "Reddit Topic": generate_topic_name(r_words),
                    "Closest News Topic": (
                        generate_topic_name(news_topic_keywords[best_match])
                        if best_match is not None
                        else "—"
                    ),
                    "Semantic Similarity": round(best_score, 3),
                }
            )

        similarity_df = (pd.DataFrame(rows).sort_values("Semantic Similarity" , ascending=False).reset_index(drop=True))
        st.session_state[TOPIC_SIMILARITY_DF] = similarity_df
    similarity_df = st.session_state[TOPIC_SIMILARITY_DF]

    st.dataframe(similarity_df.style.background_gradient(subset=["Semantic Similarity"] , cmap="Blues") , use_container_width=True)


with tab3: 
    st.subheader("Topic-Based Narrative Analysis")
    if news_topic_keywords is None or reddit_topic_keywords is None:
        st.info("Run Topic Modeling on both news and reddit data")
        st.stop()

    similarity_df = st.session_state.get(TOPIC_SIMILARITY_DF)
    if similarity_df is None: 
        st.info("Generate topic alignment in Tab 2 first")
        st.stop()
        
    if st.button("Generate Topic-Based Narrative Analysis" , type="primary"): 
        with st.spinner("Generating analysis"): 
            aligned_bundle = align_topic_to_text(similarity_df=similarity_df , df_news=df_news , df_reddit=df_reddit , top_k=15 , max_texts_per_side=6)
            loop = asyncio.get_event_loop()
            asyncio.set_event_loop(loop=loop)
            results = loop.run_until_complete(analyze_aligned_topics(aligned_bundle))
            st.session_state[TOPIC_NARRATIVES] = results

    if TOPIC_NARRATIVES in st.session_state:
        st.markdown("---")
        for item in st.session_state[TOPIC_NARRATIVES]:
            st.markdown(
                f"### 🔹 {item['news_topic']} ↔ {item['reddit_topic']}"
            )
            st.markdown(item["analysis"])
            st.divider()