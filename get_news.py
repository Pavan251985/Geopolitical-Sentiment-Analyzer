import requests

print("Fetching the latest geopolitical news...")

# Your personal API key
api_key = "c006938da8224234b9f34ecf7d2ebae8"

# We are asking the API for recent news containing the words "Middle East" and "Oil"
url = f"https://newsapi.org/v2/everything?q=Middle+East+Oil&language=en&sortBy=publishedAt&apiKey={api_key}"

# Send the request and get the data back in JSON format
response = requests.get(url).json()

# Grab the very first article from the results
top_article = response['articles'][0]

print("\n--- TOP HEADLINE ---")
print(f"Title: {top_article['title']}")
print(f"Source: {top_article['source']['name']}")