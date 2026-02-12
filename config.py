from urllib.parse import urlparse



def normalize_url(url):
    url = url.strip()
    if not url.startswith(('http://www.', 'https://www.')):
        url = 'https://www.' + url
    return url

def get_canonical_noon_url(url):
    """
    Converts a messy Noon URL into the shortest working version.
    Input:  https://www.noon.com/saudi-ar/long-seo-text/N38503505A/p/?utm_source=...
    Output: https://www.noon.com/saudi-ar/N38503505A/p/
    """
    # url = normalize_url(url)
    try:
        parsed = urlparse(url)
        # Split the path into parts: ['', 'saudi-ar', 'seo-text', 'N38503505A', 'p']
        path_parts = parsed.path.strip('/').split('/')

        # 1. Validate it's a product page (must have 'p')
        if 'p' not in path_parts:
            print(f"Skipping: Not a valid product page -> {url}")
            return None

        # 2. Find the index of 'p'. The SKU is ALWAYS the item right before 'p'.
        p_index = path_parts.index('p')
        sku = path_parts[p_index - 1]

        # 3. The Region is usually the first part of the path
        region = path_parts[0] 

        # 4. Reconstruct the clean URL
        clean_url = f"https://www.noon.com/{region}/{sku}/p/"
        return clean_url

    except Exception as e:
        print(f"Error parsing URL: {e}")
        return url # Return original if we fail



def get_canonical_amazon_url(url):
    """
    Converts a messy Amazon product URL into the shortest canonical version.
    Input:  https://www.amazon.sa/.../dp/9353949432/ref=...
    Output: https://www.amazon.sa/dp/9353949432/
    """
    # url = normalize_url(url)
    try:
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')

        # Amazon product identifiers
        if 'dp' in path_parts:
            asin = path_parts[path_parts.index('dp') + 1]
        elif 'gp' in path_parts and 'product' in path_parts:
            asin = path_parts[path_parts.index('product') + 1]
        else:
            print(f"Skipping: Not a valid Amazon product URL -> {url}")
            return None

        return f"{parsed.scheme}://{parsed.netloc}/dp/{asin}/"

    except Exception as e:
        print(f"Error parsing Amazon URL: {e}")
        return url


def get_canonical_product_url(url):
    """
    Detects the store and returns the canonical product URL.
    """
    url = normalize_url(url)
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if 'noon.com' in domain:
        return get_canonical_noon_url(url)

    if 'amazon.' in domain:
        return get_canonical_amazon_url(url)

    print(f"Unsupported store -> {url}")
    return None


# Output: https://www.noon.com/saudi-ar/N38503505A/p/


print(get_canonical_product_url("amazon.sa/-/en/Pragmatic-Programmer-David-Thomas/dp/9353949432/ref=sr_1_2?crid=HDMH9R1BWE1&dib=eyJ2IjoiMSJ9.kdai51KlSmR00Eeka59ye5yWLz5gCLavdX-lbjBXTa8ZHty2sHX0n1IsAHY91IBcAFay1u9xV7OvnEj0ToWqYg_3vM0xlkpcXUe4a20F1SAw7VbGq9XT0DuUPbUEMgtejrWiQIbvn_Ov7wh3mWY7UfBZpRvf_t0JtTPZIqEqImfK95aaNnILJQMpNpBIBBDdKQEdH5U1MY4VPh7ps_poXyriUD2rAtz7ebm96jojvUy-fH07QFAM9bZx3MM-1OitwL2eJQhxdxzxurVFBf0TVDQIVJJZUajuEffbDOu5I3Y.EIt1r7PZHKOLU-x2JmqsomzfZ4rHPjqOImSf_p3_-B4&dib_tag=se&keywords=the+pragmatic+programmer&qid=1770712044&sprefix=%2Caps%2C189&sr=8-2"))


