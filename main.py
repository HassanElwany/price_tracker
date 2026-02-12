import httpx
from selectolax.parser import HTMLParser

def get_data(store, url, selector):
    response = httpx.get(url, headers= {
        "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
    })

    html = HTMLParser(response.text)
    price = html.css_first(selector).text()
    return {"store": store, "price": price}

def main():
    results = [
        get_data("Amazon", "https://www.amazon.sa/dp/9353949432/", "span.aok-offscreen")
    ]
    print(results)


if __name__ == "__main__":
    main()
