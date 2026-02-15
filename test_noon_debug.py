#!/usr/bin/env python3
"""
Debug test for Noon scraping - run with debug=True flag
"""

import logging
from browser import PriceScraper

# Configure logging to show all messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_noon_debug():
    """Test Noon scraping with debug output"""
    
    market = "Saudi Arabia"
    product = "laptop"
    
    print("\n" + "="*70)
    print("NOON SCRAPING DEBUG TEST")
    print("="*70)
    print(f"Market: {market}")
    print(f"Product: {product}")
    print("="*70 + "\n")
    
    scraper = PriceScraper(market)
    
    try:
        print("🔍 Starting Noon scrape with DEBUG=TRUE...\n")
        # Call with debug=True to see detailed output
        results = scraper.scrape_noon(product, debug=True)
        
        print("\n" + "="*70)
        print(f"Results: Found {len(results)} products")
        print("="*70)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Platform: {result['platform']}")
            print(f"   Product: {result['product'][:80]}")
            print(f"   Price: {result['price']}")
            print(f"   Link: {result['link'][:80] if result['link'] != 'N/A' else 'N/A'}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    test_noon_debug()
