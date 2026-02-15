"""
Main entry point for the price tracker application.

This module orchestrates the web scraping process for multiple e-commerce platforms,
handles user input, manages the scraping workflow, and persists results to CSV.
"""

import logging
from datetime import datetime
from browser import PriceScraper

# Configure logging with timestamp, level, and message format for tracking application flow
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_user_input():
    """
    Collect market and product search query from user.
    
    WHY: Encapsulating input collection makes the main flow cleaner and easier to test.
    It also allows for future input validation without modifying main().
    
    Returns:
        tuple: (market, product) as strings
    """
    market = input("Enter market (e.g., Saudi Arabia, UAE): ").strip()
    product = input("Enter product to search (e.g., laptop, phone): ").strip()
    
    if not market or not product:
        logger.warning("Market or product cannot be empty")
        return None, None
    
    return market, product


def save_results(all_results):
    """
    Persist scraping results to CSV file with timestamp.
    
    WHY: Separating file I/O logic from scraping logic follows the Single Responsibility Principle.
    This makes testing easier and the code more maintainable.
    
    Args:
        all_results (list): List of product dictionaries to save
    """
    if not all_results:
        logger.warning("No results to save")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/results_{timestamp}.csv"
    
    try:
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            # WHY: Using fieldnames ensures consistent column order
            # Include both raw price and parsed price fields
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
                # Handle both old format (Amazon) and new format (Noon) 
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
    except Exception as e:
        logger.error(f"✗ Error saving results: {e}")


def main():
    """
    Main application flow: collect input, scrape multiple platforms, display and save results.
    
    WHY: Keeping main() focused on orchestration (calling other functions) rather than
    implementation details makes the flow easy to understand at a glance.
    """
    logger.info("=" * 50)
    logger.info("Starting Price Tracker")
    logger.info("=" * 50)
    
    # Collect user input for market and product
    market, product = get_user_input()
    if not market or not product:
        logger.error("Invalid input. Exiting.")
        return
    
    all_results = []
    scraper = None
    
    try:
        # Initialize the scraper with the specified market
        # WHY: Creating the scraper once and reusing it is more efficient than
        # creating separate instances for each platform
        scraper = PriceScraper(market)
        
        # Scrape Amazon prices
        logger.info(f"\n>>> Scraping Amazon for '{product}'...")
        amazon_results = scraper.scrape_amazon(product)
        if amazon_results:
            all_results.extend(amazon_results)
            logger.info(f"✓ Found {len(amazon_results)} Amazon products")
        else:
            logger.warning("No Amazon results found")
        
        # Scrape Noon prices
        logger.info(f"\n>>> Scraping Noon for '{product}'...")
        noon_results = scraper.scrape_noon(product)
        if noon_results:
            all_results.extend(noon_results)
            logger.info(f"✓ Found {len(noon_results)} Noon products")
        else:
            logger.warning("No Noon results found")
        
        # Display summary
        logger.info("\n" + "=" * 50)
        logger.info(f"TOTAL PRODUCTS FOUND: {len(all_results)}")
        logger.info("=" * 50)
        
        if all_results:
            # Display first 5 results as preview
            logger.info("\nFirst 5 results:")
            for i, result in enumerate(all_results[:5], 1):
                logger.info(f"{i}. {result.get('platform')}: {result.get('product')} - Price: {result.get('price')}")
            
            # Save all results to CSV
            save_results(all_results)
        
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}", exc_info=True)
    
    finally:
        # Always close the browser, even if an error occurred
        # WHY: Using finally ensures browser cleanup happens regardless of success/failure
        if scraper:
            scraper.close()
            logger.info("\nBrowser closed successfully")
        
        logger.info("=" * 50)
        logger.info("Price Tracker Complete")
        logger.info("=" * 50)


if __name__ == "__main__":
    main()
