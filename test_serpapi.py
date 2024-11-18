import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

api_key = os.getenv("SEARCH_API_KEY")
query = "test query"  # Simple test query

url = "https://api.serpapi.com/search"
params = {"q": query, "api_key": api_key}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    print("Connection Successful! Here’s the response:")
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
