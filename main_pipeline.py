import requests
from transformers import pipeline

print("Loading FinBERT AI Model...")
# Load the AI model
analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")

# 1. Fetch the live news
api_key = "c006938da8224234b9f34ecf7d2ebae8"
url = f"https://newsapi.org/v2/everything?q=Middle+East+Oil&language=en&sortBy=publishedAt&apiKey={api_key}"

print("Fetching live geopolitical news...")
response = requests.get(url).json()

# Grab the top 3 articles instead of just 1
top_articles = response['articles'][:3] 

print("\n================ LIVE AI ANALYSIS ================")

# 2. Loop through the articles and let the AI analyze each one
for index, article in enumerate(top_articles, 1):
    headline = article['title']
    
    # Feed the headline to the AI
    ai_result = analyzer(headline)[0] 
    
    sentiment = ai_result['label'].upper()
    confidence = ai_result['score']
    
    print(f"\n{index}. HEADLINE: {headline}")
    print(f"   -> AI SENTIMENT: {sentiment} (Confidence: {confidence:.2f})")

print("\n==================================================")