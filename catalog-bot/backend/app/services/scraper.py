import requests
from bs4 import BeautifulSoup
import urllib.parse
from typing import List, Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def extract_price_from_amazon(query: str) -> List[float]:
    """Scrapes Amazon India for organic prices."""
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.amazon.in/s?k={encoded_query}"
    
    prices = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Amazon search result price tags
        price_tags = soup.find_all('span', class_='a-price-whole')
        for tag in price_tags:
            try:
                # Remove commas, evaluate
                clean_price = tag.text.replace(',', '').strip()
                prices.append(float(clean_price))
                if len(prices) >= 5: # Get only top 5 prices
                    break
            except ValueError:
                continue
    except Exception as e:
        print(f"Amazon Scraper Error: {e}")
        
    return prices

def extract_price_from_flipkart(query: str) -> List[float]:
    """Scrapes Flipkart for organic prices."""
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://www.flipkart.com/search?q={encoded_query}"
    
    prices = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Flipkart price tags often start with ₹ inside a div class starting with _30jeq3
        price_tags = soup.find_all('div', class_='_30jeq3')
        for tag in price_tags:
            try:
                # Extract numbers only
                clean_price = tag.text.replace('₹', '').replace(',', '').strip()
                prices.append(float(clean_price))
                if len(prices) >= 5:
                    break
            except ValueError:
                continue
    except Exception as e:
        print(f"Flipkart Scraper Error: {e}")
        
    return prices

def get_average_market_price(keywords: List[str]) -> Optional[float]:
    """
    Takes a list of keywords or a single search string, queries across multiple 
    e-commerce platforms, and returns an average market price.
    """
    if not keywords:
        return None
        
    query_string = " ".join(keywords) if isinstance(keywords, list) else keywords
    
    all_prices = []
    all_prices.extend(extract_price_from_amazon(query_string))
    all_prices.extend(extract_price_from_flipkart(query_string))
    
    if not all_prices:
        return None
        
    # Average the collected prices
    avg_price = sum(all_prices) / len(all_prices)
    return round(avg_price, 2)
