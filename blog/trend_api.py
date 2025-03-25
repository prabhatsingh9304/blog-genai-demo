from pytrends.request import TrendReq
import time



# Initialize pytrends
pytrends = TrendReq(hl="en-US", tz=360)

# Define the keyword
keyword = "coffee"

# Fetch related queries
pytrends.build_payload(["Bitcoin"], timeframe="today 5-y", geo="IN")
time.sleep(5) 
related_queries = pytrends.related_queries()

# Extract rising and top queries
rising = related_queries[keyword]["rising"]
top = related_queries[keyword]["top"]

# Print results
print("Rising Queries:")
print(rising)

print("\nTop Queries:")
print(top)
