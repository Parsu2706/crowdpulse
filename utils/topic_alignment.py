def align_topic_to_text(similarity_df , df_news , df_reddit , top_k = 5 , max_texts_per_side = 8): 
    corpus = []
    top_pairs = similarity_df.head(top_k)
    for i , row in top_pairs.iterrows(): 
        reddit_topic = row["Reddit Topic"]
        news_topic = row["Closest News Topic"]

        reddit_texts = (
            df_reddit[df_reddit["topic_name"] == reddit_topic].sample(n=min(max_texts_per_side, len(df_reddit)), random_state=42)
        )

        news_texts = (
            df_news[df_news["topic_name"] == news_topic].sample(n=min(max_texts_per_side, len(df_news)), random_state=42)
        )

        corpus.append(
            {
                "reddit_topic": reddit_topic,
                "news_topic": news_topic,
                "reddit_texts": reddit_texts["text"].tolist(),
                "news_texts": news_texts["text"].tolist(),
                "reddit_sentiment": reddit_texts["label"].value_counts(normalize=True).to_dict(),
                "news_sentiment": news_texts["label"].value_counts(normalize=True).to_dict(),
            }
        )

    return corpus