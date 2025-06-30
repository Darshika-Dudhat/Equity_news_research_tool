# Search live news articles from NewsAPI
# Summerize them with Groq
# Generate real-time insights

from newsapi import NewsApiClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()
newsapi_key = os.getenv("NEWSAPI_KEY")
newsapi = NewsApiClient(api_key=newsapi_key)

today = datetime.now()
yesterday = today - timedelta(days=1)

def get_news_articles(query,days_back=7):
    try:
        # yesterday = datetime.now() - timedelta(days=1)
        # from_date = yesterday.strftime("%Y-%m-%d")

        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        articles = newsapi.get_everything(
            q=query,
            from_param=from_date,
            to=to_date,
            language='en',
            sort_by='publishedAt',
            page_size=5
        )
        if articles["totalResults"] == 0:
            print(f"❌ No articles found for query: '{query}'")
        return articles["articles"]
        # print("Fetched articles:",articles)
        return articles['articles']
    except Exception as e:
        print("NewsAPI Error:", e)
        return []
    
def summarize_articles(articles):
    summaries = []
    for article in articles:
        if article['description']:
            summaries.append(f"Title: {article['title']}. Summary: {article['description']}")
    return " ".join(summaries)

# TEST BLOCK - will run if you execute this file directly
if __name__ == "__main__":
    test_query = "Shubanshu Shukla who enters international space station as a first Indian"
    results = get_news_articles(test_query)

    if results:
        print(f"✅ {len(results)} articles found for query: '{test_query}'\n")
        for idx, article in enumerate(results, 1):
            print(f"{idx}. {article['title']}")
            print(f"   Source: {article['source']['name']}")
            print(f"   URL: {article['url']}\n")
    else:
        print(f"❌ No articles found for query: '{test_query}'")