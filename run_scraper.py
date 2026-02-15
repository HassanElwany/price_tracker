#!/usr/bin/env python3
"""Quick test script to run scraper with hardcoded parameters."""

import logging
from datetime import datetime
import csv
from browser import PriceScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_results(all_results):
    """Save scraping results to CSV."""
    if not all_results:
        logger.warning("No results to save")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/results_{timestamp}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'Platform', 
                'Product', 
                'Price Current (SAR)', 
                'Price Original (SAR)',
                'Discount %',
                'Price Raw',
                'Link'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in all_results:
                price_current = result.get('price_current', result.get('price', 'N/A'))
                price_original = result.get('price_original', '')
                discount = result.get('discount_percent', '')
                price_raw = result.get('price_raw', result.get('price', 'N/A'))
                
                writer.writerow({
                    'Platform': result.get('platform', 'N/A'),
                    'Product': result.get('product', 'N/A'), 
                    'Price Current (SAR)': price_current,
                    'Price Original (SAR)': price_original,
                    'Discount %': discount,
                    'Price Raw': price_raw,
                    'Link': result.get('link', 'N/A')
                })
        
        logger.info(f"✓ Results saved to {filename}")
        return filename
    except Exception as e:
        logger.error(f"✗ Error saving results: {e}")
        return None

def main():
    """Run scraper with hardcoded parameters."""
    logger.info("=" * 60)
    logger.info("Starting Price Tracker (Full Extraction Test)")
    logger.info("=" * 60)
    
    # Hardcoded parameters for testing
    market = "Saudi Arabia"
    product = "laptop"
    
    logger.info(f"Market: {market}")
    logger.info(f"Product: {product}")
    
    # Initialize scraper
    scraper = PriceScraper(market)
    all_results = []
    
    try:
        # Scrape Noon with full extraction (all ~50 products, no debug limit)
        logger.info("\n🔍 Scraping Noon...")
        noon_results = scraper.scrape_noon(product, debug=False)
        all_results.extend(noon_results)
        logger.info(f"✓ Scraped {len(noon_results)} products from Noon")
        
    except Exception as e:
        logger.error(f"✗ Error during scraping: {e}")
    finally:
        scraper.close()
    
    # Display results summary
    logger.info(f"\n{'=' * 60}")
    logger.info(f"Total Results: {len(all_results)} products")
    logger.info(f"{'=' * 60}")
    
    if all_results:
        # Show first 3 products as sample
        for i, result in enumerate(all_results[:3], 1):
            logger.info(f"\n[{i}] {result['product'][:60]}")
            logger.info(f"    Current: {result.get('price_current', 'N/A')} SAR")
            logger.info(f"    Original: {result.get('price_original', 'N/A')} SAR")
            logger.info(f"    Discount: {result.get('discount_percent', 'N/A')}%")
        
        # Save all results to CSV
        csv_file = save_results(all_results)
        
        if csv_file:
            logger.info(f"\n✓ SUCCESS: {len(all_results)} products extracted and saved!")
    else:
        logger.warning("⚠ No results to save")

if __name__ == "__main__":
    main()
