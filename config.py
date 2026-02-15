"""
Configuration Module - URL Processing Utilities
================================================
This module handles URL normalization and canonicalization for different
e-commerce platforms. Useful for cleaning up messy URLs before processing.

IMPROVEMENTS IN THIS FILE:
1. Added comprehensive documentation
2. Better error handling with specific exceptions
3. Organized with clear sections
4. Added type hints (optional - helps with IDE support & clarity)
5. Added docstring examples
"""

from urllib.parse import urlparse
from typing import Optional


# ============================================================================
# URL NORMALIZATION - Make messy URLs consistent
# ============================================================================

def normalize_url(url: str) -> str:
    """
    Add https://www. prefix if not already present.
    
    IMPROVEMENT: Type hints
    WHY: Makes it clear what types are expected/returned
    
    Examples:
        normalize_url("amazon.com") -> "https://www.amazon.com"
        normalize_url("https://amazon.com") -> "https://www.amazon.com"
    
    Args:
        url: The URL to normalize
    
    Returns:
        str: Normalized URL with https://www. prefix
    """
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Ensure www. is present
    if 'https://www.' not in url and 'http://www.' not in url:
        url = url.replace('https://', 'https://www.')
        url = url.replace('http://', 'http://www.')
    
    return url


# ============================================================================
# NOON URL CANONICALIZATION - Simplify Noon product URLs
# ============================================================================

def get_canonical_noon_url(url: str) -> Optional[str]:
    """
    Convert a messy Noon URL into the shortest working version.
    
    IMPROVEMENT: Better documentation with examples
    WHY: Explains what the function does and shows usage
    
    Examples:
        INPUT:  https://www.noon.com/saudi-ar/long-seo-text/N38503505A/p/?utm_source=...
        OUTPUT: https://www.noon.com/saudi-ar/N38503505A/p/
    
    Why this matters:
        - Removes unnecessary URL parameters and SEO text
        - Cleaner, canonical version for comparison
        - Helps identify duplicate products
    
    Args:
        url: A Noon product URL (can be messy with query params, etc.)
    
    Returns:
        str: Clean canonical URL, or None if not a valid product page
    """
    try:
        parsed = urlparse(url)
        # Split the path: e.g., ['', 'saudi-ar', 'seo-text', 'N38503505A', 'p']
        path_parts = parsed.path.strip('/').split('/')
        
        # IMPROVEMENT: Clear validation logic with explanatory comments
        # WHY: Makes it obvious what's being checked and why
        
        # 1. Noon product pages MUST end with 'p' (product indicator)
        if 'p' not in path_parts:
            # This is not a product page, skip it
            return None
        
        # 2. Find the SKU - it's ALWAYS right before the 'p'
        p_index = path_parts.index('p')
        if p_index == 0:
            # 'p' is first element, no SKU before it - invalid
            return None
        
        sku = path_parts[p_index - 1]
        
        # 3. Region is usually the first part of the path
        region = path_parts[0]
        
        # 4. Reconstruct the clean URL
        clean_url = f"https://www.noon.com/{region}/{sku}/p/"
        return clean_url
    
    except (IndexError, ValueError) as e:
        # IMPROVEMENT: Specific exceptions instead of bare except
        # WHY: Know what went wrong, easier to debug
        print(f"Error parsing Noon URL: {e} - URL: {url}")
        return None
    except Exception as e:
        print(f"Unexpected error parsing Noon URL: {e} - URL: {url}")
        return url


# ============================================================================
# AMAZON URL CANONICALIZATION - Simplify Amazon product URLs
# ============================================================================

def get_canonical_amazon_url(url: str) -> Optional[str]:
    """
    Convert a messy Amazon product URL into the shortest canonical version.
    
    IMPROVEMENT: Clear purpose and examples
    WHY: Easy to understand at a glance
    
    Examples:
        INPUT:  https://www.amazon.sa/.../dp/9353949432/ref=...?utm=...
        OUTPUT: https://www.amazon.sa/dp/9353949432/
    
    Why this matters:
        - Removes query parameters, ref codes, and extra path segments
        - All Amazon product URLs can be simplified to just /dp/{ASIN}/
        - Helps identify the same product across different URLs
    
    Args:
        url: An Amazon product URL (can be messy with query params, etc.)
    
    Returns:
        str: Clean canonical URL, or None if not a valid product page
    """
    try:
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        # IMPROVEMENT: Handle multiple Amazon URL formats
        # WHY: Amazon has several ways to format product URLs
        
        asin = None
        
        # Format 1: /dp/{ASIN}/ - Most common
        if 'dp' in path_parts:
            dp_index = path_parts.index('dp')
            if dp_index + 1 < len(path_parts):
                asin = path_parts[dp_index + 1]
        
        # Format 2: /gp/product/{ASIN}/ - Alternative format
        elif 'gp' in path_parts and 'product' in path_parts:
            product_index = path_parts.index('product')
            if product_index + 1 < len(path_parts):
                asin = path_parts[product_index + 1]
        
        # If neither format found, this isn't a valid product URL
        if not asin:
            return None
        
        # IMPROVEMENT: Preserve original domain and scheme
        # WHY: The correct Amazon domain should be maintained
        # E.g., amazon.sa, amazon.com, amazon.co.uk, etc.
        clean_url = f"{parsed.scheme}://{parsed.netloc}/dp/{asin}/"
        return clean_url
    
    except (IndexError, ValueError) as e:
        print(f"Error parsing Amazon URL: {e} - URL: {url}")
        return None
    except Exception as e:
        print(f"Unexpected error parsing Amazon URL: {e} - URL: {url}")
        return url


# ============================================================================
# UNIFIED URL CANONICALIZATION - Auto-detect store and canonicalize
# ============================================================================

def get_canonical_product_url(url: str) -> Optional[str]:
    """
    Detect which store the URL is from and return its canonical form.
    
    IMPROVEMENT: Single entry point for URL canonicalization
    WHY: Easy to use - just pass any URL and let it figure out the store
    
    Supported stores:
        - Noon (noon.com)
        - Amazon (amazon.* - any region)
    
    Args:
        url: Product URL from any supported store
    
    Returns:
        str: Canonical URL for that store, or None if not recognized
    
    Example:
        >>> get_canonical_product_url("amazon.sa/some/messy/url/dp/12345/")
        'https://www.amazon.sa/dp/12345/'
    """
    url = normalize_url(url)
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    # IMPROVEMENT: Clear store detection logic
    # WHY: Easy to add new stores later
    
    if 'noon.com' in domain:
        return get_canonical_noon_url(url)
    
    if 'amazon.' in domain:
        return get_canonical_amazon_url(url)
    
    # Unknown store
    print(f"Unsupported store domain: {domain}")
    return None


# ============================================================================
# USAGE EXAMPLES - Uncomment to test
# ============================================================================

# IMPROVEMENT: Test code as documentation
# WHY: Shows how to use the functions, doubles as examples
# Uncomment to test:
"""
if __name__ == '__main__':
    # Test Noon URL canonicalization
    noon_url = "https://www.noon.com/saudi-ar/long-seo-text/N38503505A/p/?utm_source=..."
    print("Noon:", get_canonical_product_url(noon_url))
    
    # Test Amazon URL canonicalization
    amazon_url = "amazon.sa/Pragmatic-Programmer-David-Thomas/dp/9353949432/ref=..."
    print("Amazon:", get_canonical_product_url(amazon_url))
"""


