import subprocess
import urllib.parse
import requests
from bs4 import BeautifulSoup



amazon_countries = {
    # Gulf / Middle East
    "Saudi Arabia": "amazon.sa",
    "United Arab Emirates": "amazon.ae",
    "Egypt": "amazon.eg",
    "Turkey": "amazon.com.tr",

    # North America
    "United States": "amazon.com",
    "Canada": "amazon.ca",
    "Mexico": "amazon.com.mx",

    # Europe + UK
    "United Kingdom": "amazon.co.uk",
    "Germany": "amazon.de",
    "France": "amazon.fr",
    "Italy": "amazon.it",
    "Spain": "amazon.es",
    "Netherlands": "amazon.nl",
    "Poland": "amazon.pl",
    "Sweden": "amazon.se",
    "Belgium": "amazon.com.be",
    "Ireland": "amazon.ie",

    # Asia-Pacific
    "Australia": "amazon.com.au",
    "Japan": "amazon.co.jp",
    "India": "amazon.in",
    "Singapore": "amazon.sg",

    # South America
    "Brazil": "amazon.com.br"
}

noon_countries = {
    "Saudi Arabia": "https://www.noon.com/saudi-en/",
    "United Arab Emirates": "https://www.noon.com/uae-en/",
    "Egypt": "https://www.noon.com/egypt-en/",
    "Bahrain": "https://www.noon.com/uae-en/",
    "Kuwait": "https://www.noon.com/uae-en/",
    "Qatar": "https://www.noon.com/uae-en/",
    "Oman": "https://www.noon.com/uae-en/"
}



def amazon_normaliz_url(market, product):
    
    if market not in amazon_countries:
        print("Market not supported")
        return None
    
    product_encoded = urllib.parse.quote_plus(product)
    return f"https://{amazon_countries[market]}/s?k={product_encoded}"



def noon_normaliz_url(market, product):
    product_encoded = urllib.parse.quote_plus(product)
    
    if market not in noon_countries and market not in amazon_countries:
        print("Market is not supported")
        return None
    if market not in noon_countries and market in amazon_countries:
        market = noon_countries["United Arab Emirates"]
        return f"{market}/search/?q={product_encoded}"
    
    return f"{noon_countries[market]}/search/?q={product_encoded}"

def main():
    market = input("Choose your market: ").strip()
    product = input("Choose the product: ").strip()
    url = amazon_normaliz_url(market, product)
    # if url:
    #     subprocess.run(["cmd.exe", "/c", "start", url])
    # url = noon_normaliz_url(market, product)
    # if url:
    #     subprocess.run(["cmd.exe", "/c", "start", url])
    
    headers = {
    "User-Agent": "Mozilla/5.0"
    }

    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    products = soup.find_all("div", {"data-component-type": "s-search-result"})

    for product in products:
        title = product.find("h2")
        price = product.find("span", class_="a-offscreen")

        if title and price:
            print("Title:", title.get_text(strip=True))
            print("Price:", price.get_text(strip=True))
            print("-" * 40)

if __name__ == '__main__':
    main()