from transformers import pipeline

print("Loading the FinBERT AI Model... (this might take a minute as it downloads the model for the first time)")

# Load the sentiment analysis pipeline specifically trained on financial data
analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")

# Let's test it with a sample headline
test_headline = "Oil prices plummet as global supply chain stabilizes and tensions ease."

print(f"\nAnalyzing Headline: '{test_headline}'")

# Run the AI
result = analyzer(test_headline)

print("\n--- AI SENTIMENT RESULT ---")
print(result)