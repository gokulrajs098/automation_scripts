import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Get the current date
current_date = datetime.now()

# Load API key from .env file
load_dotenv()
api_key = os.getenv('news_api_key')

BASE_URL = "https://content.guardianapis.com/search"

def fetch_news(keyword, from_date, to_date, page):
    """Fetch news articles based on a keyword."""
    params = {
        "q": keyword,
        "page": page,
        "api-key": api_key,
        "show-fields": "all", 
        "from-date": from_date,
        "to-date": to_date,
        "page-size": 3
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to fetch data (Status Code: {response.status_code})")
        return None

def fetch_article_html(url):
    """Fetch raw HTML content of an article."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error: Unable to fetch article HTML (Status Code: {response.status_code})")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

def parse_html_with_bs4(html_content):
    """Parse HTML content using Beautiful Soup."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Example: Extract all paragraphs
        paragraphs = soup.find_all('p')
        article_text = "\n".join(p.get_text() for p in paragraphs)
        return article_text
    except Exception as e:
        print(f"Error while parsing HTML: {e}")
        return "Could not parse the article content."

def get_article_content(article):
    """Return the title and parsed content of an article."""
    article_info = {}
    article_info['Title'] = article['webTitle']
    article_info['Published'] = article['webPublicationDate']
    article_info['URL'] = article['webUrl']
    
    # Fetch and parse the article HTML content
    html_content = fetch_article_html(article['webUrl'])
    if html_content:
        parsed_content = parse_html_with_bs4(html_content)
        article_info['Content'] = parsed_content
    else:
        article_info['Content'] = "Could not fetch or parse article HTML."
    
    return article_info

def main():
    """Main function to handle user input and fetch/display articles."""
    keyword = input("Enter a keyword to search for news: ").strip()
    from_date = input("Enter the date from which you want articles from: ")
    to_date = current_date.strftime("%Y-%m-%d")
    page = 1
    all_articles = []  # List to store article info

    data = fetch_news(keyword, from_date, to_date, page)
    
    if data and "response" in data and "results" in data["response"]:
        results = data["response"]["results"]
        if not results:
            print("No articles found.")
        else:
            # Process each article
            for article in results:
                article_content = get_article_content(article)
                all_articles.append(article_content)  # Append to list
    else:
        print("No articles found or an error occurred.")

    return all_articles  # Return the list of articles
