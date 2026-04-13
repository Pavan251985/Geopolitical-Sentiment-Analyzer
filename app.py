from flask import Flask, render_template
import requests
from transformers import pipeline
from datetime import datetime, timedelta
import os 

app = Flask(__name__)

print("Loading FinBERT AI Model...")
analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")

# IMPORTANT: Keep this as os.environ for GitHub/hosting!
# (If testing locally on your laptop right now, temporarily swap this to: API_KEY = "YOUR_ACTUAL_KEY")
API_KEY = os.environ.get("NEWS_API_KEY") 

@app.route('/')
def home():
    # Clean, simple search terms
    commodities = {
        "🛢️ Crude Oil": "Crude Oil market",
        "🪙 Gold": "Gold market",
        "🥈 Silver": "Silver market",
        "🔥 Natural Gas": "Natural Gas market" 
    }
    
    # Calculate today and 7 days ago
    today = datetime.now()
    last_week = today - timedelta(days=7)
    
    date_to = today.strftime("%Y-%m-%d")
    date_from = last_week.strftime("%Y-%m-%d")
    
    all_analyzed_news = {}
    
    for commodity_name, search_query in commodities.items():
        
        # --- THE FIX: Using a params dictionary for 100% safe URL encoding ---
        base_url = "https://newsapi.org/v2/everything"
        query_parameters = {
            "q": search_query,
            "from": date_from,
            "to": date_to,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": API_KEY
        }
        
        # The requests library will now safely format the spaces and special characters!
        response = requests.get(base_url, params=query_parameters).json()
        # ---------------------------------------------------------------------
        
        if response.get('status') == 'error':
            print(f"API ERROR for {commodity_name}: {response.get('message')}")
        
        # Grab the top 5 articles
        top_articles = response.get('articles', [])[:5] 
        analyzed_news = []
        
        for article in top_articles:
            headline = article['title']
            ai_result = analyzer(headline)[0]
            
            description = article.get('description') or "No detailed description available for this article."
            
            raw_date = article.get('publishedAt', '')
            formatted_date = ""
            if raw_date:
                try:
                    dt = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%SZ")
                    formatted_date = dt.strftime("%B %d, %Y")
                except ValueError:
                    formatted_date = raw_date[:10]
            
            analyzed_news.append({
                "headline": headline,
                "description": description,
                "source": article['source']['name'],
                "sentiment": ai_result['label'].upper(),
                "confidence": round(ai_result['score'] * 100, 1),
                "date": formatted_date
            })
            
        all_analyzed_news[commodity_name] = analyzed_news
        
    return render_template('index.html', all_news_data=all_analyzed_news)

if __name__ == '__main__':
    app.run(debug=True)