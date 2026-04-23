from flask import Flask, render_template
import requests
from datetime import datetime, timedelta
import os 

app = Flask(__name__)

# Securely grab both API keys from the Render environment
NEWS_API_KEY = os.environ.get("NEWS_API_KEY") 
HF_TOKEN = os.environ.get("HF_TOKEN")

# THE FIX: Direct pipeline URL and explicit Content-Type header
HF_API_URL = "https://router.huggingface.co/hf-inference/models/ProsusAI/finbert"
headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def analyze_sentiment(text):
    """Sends text to Hugging Face for analysis with advanced error trapping."""
    try:
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": text})
        
        # Check if Hugging Face sent an error page instead of JSON
        if response.status_code != 200:
            print(f"HF RAW ERROR [{response.status_code}]: {response.text}")
            
            # 503 means the AI model is currently asleep and booting up
            if response.status_code == 503:
                return "LOADING", 0.0
            return "UNKNOWN", 0.0
            
        result = response.json()
            
        # Extract the highest scoring sentiment cleanly
        # Handles nested lists: [[{'label': 'POSITIVE', 'score': 0.9}]]
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
            predictions = result[0]
            best_prediction = sorted(predictions, key=lambda x: x['score'], reverse=True)[0]
            return best_prediction['label'].upper(), round(best_prediction['score'] * 100, 1)
        # Handles flat lists: [{'label': 'POSITIVE', 'score': 0.9}]
        elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            best_prediction = sorted(result, key=lambda x: x['score'], reverse=True)[0]
            return best_prediction['label'].upper(), round(best_prediction['score'] * 100, 1)
            
    except Exception as e:
        print(f"HF Code Error: {e}")
        
    return "UNKNOWN", 0.0

@app.route('/')
def home():
    commodities = {
        "🛢️ Crude Oil": "Crude Oil market",
        "🪙 Gold": "Gold market",
        "🥈 Silver": "Silver market",
        "🔥 Natural Gas": "Natural Gas market" 
    }
    
    today = datetime.now()
    last_week = today - timedelta(days=7)
    date_to = today.strftime("%Y-%m-%d")
    date_from = last_week.strftime("%Y-%m-%d")
    
    all_analyzed_news = {}
    
    for commodity_name, search_query in commodities.items():
        base_url = "https://newsapi.org/v2/everything"
        query_parameters = {
            "q": search_query,
            "from": date_from,
            "to": date_to,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": NEWS_API_KEY
        }
        
        response = requests.get(base_url, params=query_parameters).json()
        
        # Debug tool if NewsAPI acts up
        if response.get('status') == 'error':
            print(f"NewsAPI ERROR for {commodity_name}: {response.get('message')}")
            
        top_articles = response.get('articles', [])[:5] 
        analyzed_news = []
        
        for article in top_articles:
            headline = article['title']
            
            # Call our upgraded Hugging Face function
            sentiment_label, confidence = analyze_sentiment(headline)
            
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
                "source": article.get('source', {}).get('name', 'Unknown Source'),
                "sentiment": sentiment_label,
                "confidence": confidence,
                "date": formatted_date
            })
            
        all_analyzed_news[commodity_name] = analyzed_news
        
    return render_template('index.html', all_news_data=all_analyzed_news)

if __name__ == '__main__':
    app.run(debug=True)
