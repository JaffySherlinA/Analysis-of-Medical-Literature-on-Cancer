import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta

# Function to scrape PubMed for the past 3 months
def scrape_pubmed_data(query, months=3):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    
    # Define the date range for the last 'months' months
    today = datetime.today()
    start_date = today - timedelta(days=months * 30)
    start_date_str = start_date.strftime('%Y/%m/%d')
    end_date_str = today.strftime('%Y/%m/%d')

    # PubMed query URL for the search term and date range
    search_url = f"{base_url}?term={query}&filter=dates.{start_date_str}:{end_date_str}"
    
    # Request the page content
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # List to store the scraped data
    data = []

    # Parse each result
    articles = soup.find_all('article', class_='full-docsum')
    for article in articles:
        # Extract title
        title_tag = article.find('a', class_='docsum-title')
        title = title_tag.text.strip() if title_tag else "No Title"

        # Extract URL
        link = base_url + title_tag['href'] if title_tag else "No Link"

        # Extract authors
        authors_tag = article.find('span', class_='docsum-authors full-authors')
        authors = authors_tag.text.strip() if authors_tag else "No Authors"

        # Extract published date
        date_tag = article.find('span', class_='docsum-journal-citation full-journal-citation')
        published_date = date_tag.text.strip() if date_tag else "No Date"
        
        # Extract abstract (via article's detailed page)
        article_page = requests.get(link)
        article_soup = BeautifulSoup(article_page.content, 'html.parser')
        abstract_tag = article_soup.find('div', class_='abstract-content selected')
        abstract = abstract_tag.text.strip() if abstract_tag else "No Abstract"

        # Store the extracted data
        data.append({
            "Title": title,
            "Authors": authors,
            "Published Date": published_date,
            "Abstract": abstract,
            "Link": link
        })

    # Convert to pandas DataFrame
    df = pd.DataFrame(data)

    # Check if 'Published Date' column exists
    if 'Published Date' in df.columns:
        # Format the published date properly (convert to datetime)
        df['Published Date'] = pd.to_datetime(df['Published Date'], errors='coerce')
    else:
        print("'Published Date' column not found!")

    # Save data to a CSV file (optional)
    df.to_csv(f'pubmed_{query}_data.csv', index=False)
    
    return df

# Example usage for scraping papers related to cardiovascular disease for the last 3 months
query = "cardiovascular+disease"
df = scrape_pubmed_data(query)
print(df.head())
