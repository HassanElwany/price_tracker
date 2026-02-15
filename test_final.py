#!/usr/bin/env python3
"""
Final verification test - run the complete price tracker workflow.
"""

import sys
import time
from browser import PriceScraper

def main():
    print("\n" + "="*70)
    print("FINAL VERIFICATION TEST - Price Tracker")
    print("="*70)
    
    market = "Saudi Arabia"
    product = "laptop"
    
    print(f"\nMarket: {market}")
    print(f"Product: {product}")
    print("-" * 70)
    
    scraper = PriceScraper(market)
    all_results = []
    
    try:
        # Amazon
        print("\n>>> Scraping Amazon...")
        amazon_results = scraper.scrape_amazon(product)
        print(f"✓ Found {len(amazon_results)} Amazon products")
        
        if amazon_results:
            for i, r in enumerate(amazon_results[:2], 1):
                print(f"  {i}. {r['product'][:60]}")
                print(f"     Price: {r['price']}")
        
        all_results.extend(amazon_results)
        
        # Noon
        print("\n>>> Scraping Noon...")
        noon_results = scraper.scrape_noon(product)
        print(f"✓ Found {len(noon_results)} Noon products")
        
        if noon_results:
            for i, r in enumerate(noon_results[:2], 1):
                print(f"  {i}. {r['product'][:60]}")
                print(f"     Price: {r['price'][:20]}...")
        
        all_results.extend(noon_results)
        
        # Summary
        print("\n" + "="*70)
        print(f"TOTAL PRODUCTS FOUND: {len(all_results)}")
        print(f"Amazon: {len(amazon_results)} | Noon: {len(noon_results)}")
        print("="*70)
        
        # Verify CSV would be created
        import csv
        from datetime import datetime
        
        if all_results:
            filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = f"data/{filename}"
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['platform', 'product', 'price', 'link'])
                writer.writeheader()
                writer.writerows(all_results)
            
            print(f"\n✓ Results would be saved to: {filepath}")
        
        return all_results
        
    finally:
        scraper.close()
        print("\n✓ Browser closed successfully\n")

if __name__ == "__main__":
    results = main()
    sys.exit(0 if len(results) > 0 else 1)
