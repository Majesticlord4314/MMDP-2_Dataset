import os
import re
import requests
from bs4 import BeautifulSoup
import time

def clean_structured_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def extract_article(article_url):
    """
    Extracts structured information from an article page.
    Returns a dictionary with keys: 'title', 'date', 'content'
    """
    data = {}
    try:
        response = requests.get(article_url, timeout=10)
        if response.status_code != 200:
            print(f"  Failed to retrieve article: {article_url}")
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title: try <h1> first, then <title>
        title_tag = soup.find('h1')
        if title_tag and title_tag.get_text(strip=True):
            data['title'] = title_tag.get_text(strip=True)
        elif soup.title:
            data['title'] = soup.title.get_text(strip=True)
        else:
            data['title'] = "No Title Found"
        
        # Extract publication date from common meta tags if available
        pub_date = ""
        meta_date = soup.find("meta", {"property": "article:published_time"})
        if meta_date and meta_date.get("content"):
            pub_date = meta_date["content"]
        else:
            meta_date = soup.find("meta", {"name": "pubdate"})
            if meta_date and meta_date.get("content"):
                pub_date = meta_date["content"]
        data['date'] = pub_date if pub_date else "No Publication Date"
        
        # Extract article content:
        article_tag = soup.find("article")
        if article_tag:
            paragraphs = article_tag.find_all('p')
        else:
            paragraphs = soup.find_all('p')
        content = "\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20)
        data['content'] = content if content else "No Content Extracted"
        
        # Return data only if content is of reasonable length
        if len(data['content']) < 200:
            print(f"  Skipping article (content too short): {article_url}")
            return None
    except Exception as e:
        print(f"  Error extracting article from {article_url}: {e}")
        return None
    return data

def extract_articles_from_website(website_url, max_articles=3):
    """
    Given a website URL (assumed to be a homepage), this function attempts to
    find links to articles and then extracts structured article content from them.
    Returns a list of article data dictionaries.
    """
    articles_data = []
    try:
        response = requests.get(website_url, timeout=10)
        if response.status_code != 200:
            print(f"  Failed to retrieve homepage: {website_url}")
            return articles_data
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all <a> tags with an href attribute.
        # Heuristic: Select links that have reasonably long text (likely article headlines)
        link_tags = soup.find_all('a', href=True)
        article_links = set()
        for tag in link_tags:
            link_text = tag.get_text(strip=True)
            href = tag['href']
            # A simple heuristic: if the link text is longer than 20 characters,
            # and the link seems to be an absolute URL belonging to the same domain,
            # consider it as a potential article link.
            if len(link_text) > 20:
                if href.startswith("http") and website_url.split("//")[-1].split("/")[0] in href:
                    article_links.add(href)
                elif href.startswith("/"):
                    full_url = website_url.rstrip("/") + href
                    article_links.add(full_url)
        article_links = list(article_links)[:max_articles]
        print(f"  Found {len(article_links)} candidate article links on {website_url}")
        
        for article_url in article_links:
            article_data = extract_article(article_url)
            if article_data:
                articles_data.append(article_data)
    except Exception as e:
        print(f"  Error processing website {website_url}: {e}")
    return articles_data

# Define 20 categories with 3 websites each.
categories = {
    "Technology": [
        "https://techcrunch.com",
        "https://www.theverge.com",
        "https://www.wired.com"
    ],
    "Sports": [
        "https://www.espn.com",
        "https://www.sportingnews.com",
        "https://www.skysports.com"
    ],
    "Health": [
        "https://www.webmd.com",
        "https://www.healthline.com",
        "https://www.mayoclinic.org"
    ],
    "Entertainment": [
        "https://variety.com",
        "https://www.hollywoodreporter.com",
        "https://www.billboard.com"
    ],
    "Business": [
        "https://www.forbes.com",
        "https://www.bloomberg.com",
        "https://www.cnbc.com"
    ],
    "Science": [
        "https://www.sciencemag.org",
        "https://www.nationalgeographic.com/science",
        "https://www.sciencenews.org"
    ],
    "Journalism": [  # Dedicated journalism/news websites
        "https://www.nytimes.com",
        "https://www.theguardian.com/us",
        "https://www.washingtonpost.com"
    ],
    "Travel": [
        "https://www.lonelyplanet.com",
        "https://www.cntraveler.com",
        "https://www.travelandleisure.com"
    ],
    "Food": [
        "https://www.foodnetwork.com",
        "https://www.eater.com",
        "https://www.seriouseats.com"
    ],
    "Education": [
        "https://www.edutopia.org",
        "https://www.educationworld.com",
        "https://www.thetechedvocate.org"
    ],
    "Fashion": [
        "https://www.vogue.com",
        "https://www.elle.com",
        "https://www.harpersbazaar.com"
    ],
    "Finance": [
        "https://www.investopedia.com",
        "https://www.marketwatch.com",
        "https://www.fool.com"
    ],
    "Automotive": [
        "https://www.caranddriver.com",
        "https://www.motortrend.com",
        "https://www.autocar.co.uk"
    ],
    "Art": [
        "https://www.artnews.com",
        "https://www.artforum.com",
        "https://www.theartnewspaper.com"
    ],
    "Real_Estate": [
        "https://www.realtor.com",
        "https://www.zillow.com",
        "https://www.redfin.com"
    ],
    "Culture": [
        "https://www.culturetrip.com",
        "https://www.newyorker.com/culture",
        "https://www.theatlantic.com/culture"
    ],
    "Environment": [
        "https://www.treehugger.com",
        "https://www.environmentalleader.com",
        "https://www.ecowatch.com"
    ],
    "History": [
        "https://www.history.com",
        "https://www.bbc.co.uk/history",
        "https://www.historyextra.com"
    ],
    "Literature": [
        "https://www.literaryhub.com",
        "https://www.theparisreview.org",
        "https://www.newyorker.com/books"
    ],
    "Gaming": [
        "https://www.polygon.com",
        "https://www.ign.com",
        "https://www.gamespot.com"
    ]
}

# Define the dataset directory
dataset_dir = "Multimodal_Text_MasterSet"
if not os.path.exists(dataset_dir):
    os.mkdir(dataset_dir)

# Process each category
for category, websites in categories.items():
    print(f"\nProcessing category: {category}")
    category_text = ""
    for website in websites:
        print(f" Scraping website: {website}")
        articles = extract_articles_from_website(website, max_articles=3)
        if not articles:
            print(f"  No articles found for {website}.")
        for article in articles:
            # Structure the article text with headers
            article_text = (f"Title: {article['title']}\n"
                            f"Date: {article['date']}\n"
                            f"Content:\n{article['content']}\n"
                            f"{'-'*40}\n")
            category_text += article_text
            print(f"  Extracted article: {article['title']}")
        # Wait a bit between websites to be polite
        time.sleep(2)
    
    if not category_text:
        category_text = "No articles could be extracted for this category."
    
    # Clean the structured text while preserving the structure
    cleaned_text = clean_structured_text(category_text)
    
    # Write the cleaned structured text to a file
    filename = os.path.join(dataset_dir, f"{category}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(cleaned_text)
    print(f" Saved structured text for category {category} to {filename}")
