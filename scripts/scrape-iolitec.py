import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_product_links(url):
    # Send an HTTP GET request to the page
    response = requests.get(url)
    
    # Raise an exception if the request was not successful
    response.raise_for_status()
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Initialize a list to store product URLs
    product_links = []
    
    # Each product appears to be enclosed in a <div class="product"> with an <a> tag.
    # So we can find all 'div' elements with class='product':
    product_divs = soup.find_all('div', class_='product')
    
    for div in product_divs:
        # Find the first <a> child within the product div (the one with rel="bookmark")
        a_tag = div.find('a', href=True)
        if a_tag:
            # The 'href' attribute contains the relative URL, e.g. 
            # '/index.php/products/ionic_liquids/catalogue/pyridinium-based/il-0214-hp'
            link = a_tag['href']
            
            if link.startswith('/index.php/products/'):
                product_links.append(link)

    return product_links

def scrape_product_data(url):
    # 1. Request the HTML of the page
    response = requests.get(url)
    response.raise_for_status()
    
    # 2. Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 3. Extract the product name from the <h1> tag
    #    e.g. "1-Ethyl-3-methylpyridinium bis(trifluoromethylsulfonyl)imide, 99%"
    product_name_tag = soup.find('h1')
    product_name = product_name_tag.get_text(strip=True) if product_name_tag else None
    
    # 4. Initialize placeholders
    product_number = None
    cas_number = None
    
    # 5. In the "detail-fields-box", each item is usually in <li>,
    #    with something like <div class="field-label">Produkt Nr.:</div> IL-0214-HP
    detail_fields_box = soup.find('div', class_='detail-fields-box')
    if detail_fields_box:
        # Find all <li> items
        li_tags = detail_fields_box.find_all('li')
        for li in li_tags:
            # Try to find the "field-label" <div>, e.g. "Produkt Nr.:"
            label_div = li.find('div', class_='field-label')
            if not label_div:
                continue
            
            label_text = label_div.get_text(strip=True)
            # The rest of the text after removing label_text is the value
            # We can just get li.get_text(), then remove the label portion:
            full_text = li.get_text(strip=True)
            
            # One approach is to split off the label from the full text
            # The label includes the colon, so we can just do:
            # "Produkt Nr.:IL-0214-HP"
            # Then we can remove "Produkt Nr.:" from that string.
            field_value = full_text.replace(label_text, "").strip(" :\n\t")
            
            if label_text.startswith("Produkt Nr."):
                product_number = field_value
            elif label_text.startswith("CAS Nr."):
                # Sometimes CAS is inside a <div>, e.g. <div>[841251-37-4]</div>
                # so just removing the label might suffice, but we can do further processing if needed
                cas_number = field_value.strip("[]")

    return product_name, cas_number, url

if __name__ == "__main__":

    data = []

    # Replace this with the actual URL containing the product list
    url = "https://iolitec.de/index.php/products/list"

    links = scrape_product_links(url)

    for link in links:
        data.append(scrape_product_data(url='https://iolitec.de'+link))

    df = pd.DataFrame(data, columns=['name', 'cas', 'url'])
    df.to_csv('../data/iolitec-raw.tsv', sep='\t', index=False)

