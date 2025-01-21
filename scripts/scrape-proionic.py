import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_product_links(url):
    # Send a request to the webpage
    response = requests.get(url)
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for all <a> tags whose 'href' starts with "/bestseller/"
    product_links = []
    for a_tag in soup.find_all("a", href=True):
        href_value = a_tag['href']
        if href_value.startswith("/bestseller/"):
            product_links.append(href_value)
    
    return product_links

def scrape_product_data(url):
    # Fetch the webpage
    response = requests.get(url)
    response.raise_for_status()  # Just in case we want to check for errors
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Initialize variables
    product_name = None
    cas_number = None
    product_number = None
    
    # Scrape Product Name
    name_div = soup.find("div", class_="name")
    if name_div:
        spans = name_div.find_all("span")
        if len(spans) > 1:
            product_name = spans[1].get_text(strip=True)
    
    # Scrape CAS Number
    cas_div = soup.find("div", class_="cas")
    if cas_div:
        spans = cas_div.find_all("span")
        if len(spans) > 1:
            cas_number = spans[1].get_text(strip=True)
    
    # Scrape Product Number from <div class="ordernumber">
    ordernumber_div = soup.find("div", class_="ordernumber")
    if ordernumber_div:
        spans = ordernumber_div.find_all("span")
        # The second <span> usually holds the product number
        if len(spans) > 1:
            product_number = spans[1].get_text(strip=True)
    
    return product_name, cas_number, url

if __name__ == "__main__":

    data = []

    # Example URL (the proionic.com webshop page)
    url = "https://proionic.com/ionic-liquids/webshop.php"
    links = scrape_product_links(url)

    for link in links:
        data.append(scrape_product_data(url='https://proionic.com'+link))
    
    df = pd.DataFrame(data, columns=['name', 'cas', 'url'])
    df.to_csv('../data/proionic-raw.tsv', sep='\t', index=False)