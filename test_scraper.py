#!/usr/bin/env python3
"""
Quick test script to verify scraper functionality without interactive input.
"""

import logging
from browser import PriceScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    market = "Saudi Arabia"
    product = "laptop"
    
    print("\n" + "="*50)
    print("Testing Price Tracker Scraper")
    print("="*50)
    print(f"Market: {market}")
    print(f"Product: {product}\n")
    
    scraper = PriceScraper(market)
    
    try:
        # Test Amazon scraping
        print(">>> Scraping Amazon...")
        amazon_results = scraper.scrape_amazon(product)
        print(f"✓ Found {len(amazon_results)} products on Amazon")
        for i, result in enumerate(amazon_results[:3], 1):
            print(f"  {i}. {result['product'][:50]}")
            print(f"     Price: {result['price']}")
        
        # Test Noon scraping
        print("\n>>> Scraping Noon...")
        noon_results = scraper.scrape_noon(product)
        print(f"✓ Found {len(noon_results)} products on Noon")
        for i, result in enumerate(noon_results[:3], 1):
            print(f"  {i}. {result['product'][:50]}")
            print(f"     Price: {result['price']}")
        
        # Summary
        total = len(amazon_results) + len(noon_results)
        print(f"\n{'='*50}")
        print(f"TOTAL PRODUCTS FOUND: {total}")
        print(f"{'='*50}\n")
        
    finally:
        scraper.close()
        print("Browser closed successfully\n")

if __name__ == "__main__":
    main()
