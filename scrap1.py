import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_pubmed(search_query, max_results=100):
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    search_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={search_query.replace(' ', '+')}"
    
    articles = []
    page = 0
    results_per_page = 20  # Number of results per page

    while len(articles) < max_results:
        # Create the URL for the current page of results
        page_url = f"{search_url}&page={page + 1}"
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the article links on the page
        article_elements = soup.find_all('article', class_='full-docsum')
        if not article_elements:  # Break if no more articles are found
            break

        for article in article_elements:
            title_tag = article.find('a', class_='docsum-title')
            title = title_tag.get_text(strip=True) if title_tag else "No Title"
            link = base_url + title_tag['href'] if title_tag else "No Link"

            # Request the individual article page
            article_response = requests.get(link)
            article_soup = BeautifulSoup(article_response.content, 'html.parser')

            # Extract data
            authors = [author.get_text(strip=True) for author in article_soup.find_all('a', class_='full-name')]
            abstract = article_soup.find('div', class_='abstract-content selected').get_text(strip=True) if article_soup.find('div', class_='abstract-content selected') else "No abstract available"
            
            # Append the article details to the list
            articles.append({
                'Title': title,
                'Authors': ', '.join(authors),
                'Abstract': abstract,
                'Link': link
            })

            # Break if we've reached the desired number of results
            if len(articles) >= max_results:
                break
        
        page += 1
        time.sleep(1)  # Pause between requests to avoid overloading the server

    return pd.DataFrame(articles)

def save_to_csv(dataframe, filename):
    dataframe.to_csv(filename, index=False, encoding='utf-8')

# Example usage
if __name__ == "__main__":  # Corrected line
    query = "cancer"  # Searching for cancer-related papers
    max_results = 500  # Maximum number of results to scrape
    
    # Scrape the data
    data = scrape_pubmed(query, max_results)
    
    # Save the scraped data to a CSV file
    save_to_csv(data, r'C:\Users\jaelh\OneDrive\Desktop\cancer_research_pubmed.csv')
    print(f"Data saved to cancer_research_pubmed.csv with {len(data)} articles.")
