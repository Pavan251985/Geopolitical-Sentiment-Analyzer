import yfinance as yf

# 'GC=F' is the ticker symbol for Gold futures
gold = yf.Ticker("GC=F") 

# Get the last 5 days of data
historical_data = gold.history(period="5d")
print(historical_data[['Close']])