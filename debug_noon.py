#!/usr/bin/env python3
"""
Debug script for Noon price scraping.
This shows exactly what Noon's HTML looks like and helps identify selector issues.
"""

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Setup logging to see all debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_driver():
    """Setup Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(15)
    return driver


def debug_noon_scraping():
    """Debug Noon scraping step by step"""
    
    driver = setup_driver()
    search_query = "laptop"
    market = "Saudi Arabia"
    
    try:
        # Step 1: Build and load URL
        base_url = "https://www.noon.com/saudi-en"
        search_url = f"{base_url}/search?q={search_query}"
        
        logger.info(f"📍 Loading URL: {search_url}")
        driver.get(search_url)
        
        # Step 2: Wait for page to render
        logger.info("⏳ Waiting 15 seconds for Noon's JavaScript to render...")
        time.sleep(15)
        
        # Step 3: Check page loaded
        page_title = driver.title
        page_source = driver.page_source
        
        logger.info(f"✓ Page Title: {page_title}")
        logger.info(f"✓ Page Source Length: {len(page_source)} chars")
        
        if "error" in page_title.lower():
            logger.warning(f"⚠️  POSSIBLE ERROR in title: {page_title}")
        
        # Step 4: Save page HTML for inspection
        with open("/tmp/noon_page.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        logger.info("✓ Saved page HTML to /tmp/noon_page.html")
        
        # Step 5: Try to find products with various selectors
        logger.info("\n" + "="*70)
        logger.info("🔍 TESTING PRODUCT SELECTORS")
        logger.info("="*70)
        
        selectors_to_try = [
            ("Original", '//div[@data-qa="plp-product-box"]'),
            ("Alt 1: product class", "//div[contains(@class, 'product')]"),
            ("Alt 2: product-card", "//div[contains(@class, 'product-card')]"),
            ("Alt 3: grid item", "//div[contains(@class, 'grid')]//div[contains(@class, 'item')]"),
            ("Alt 4: article tag", "//article"),
            ("Alt 5: any div with data-qa", "//div[@data-qa]"),
        ]
        
        for selector_name, selector in selectors_to_try:
            try:
                products = driver.find_elements(By.XPATH, selector)
                logger.info(f"✓ [{selector_name}] Found {len(products)} products")
            except Exception as e:
                logger.error(f"✗ [{selector_name}] Error: {e}")
        
        # Step 6: Use the original selector (most likely to work)
        logger.info("\n" + "="*70)
        logger.info("📦 ANALYZING FIRST PRODUCT ELEMENT")
        logger.info("="*70)
        
        try:
            products = driver.find_elements(By.XPATH, '//div[@data-qa="plp-product-box"]')
            logger.info(f"Found {len(products)} products with original selector")
            
            if products:
                first_product = products[0]
                
                # Get the HTML of the first product
                product_html = first_product.get_attribute("outerHTML")
                logger.info(f"\nFirst product HTML ({len(product_html)} chars):\n")
                logger.info(product_html[:1500])  # First 1500 chars
                
                # Save full product HTML for inspection
                with open("/tmp/noon_product.html", "w", encoding="utf-8") as f:
                    f.write(product_html)
                logger.info("✓ Saved first product HTML to /tmp/noon_product.html")
                
                # Step 7: Try price extraction on first product
                logger.info("\n" + "="*70)
                logger.info("💰 TESTING PRICE SELECTORS ON FIRST PRODUCT")
                logger.info("="*70)
                
                price_selectors = [
                    ("a-price-whole", By.CLASS_NAME, "a-price-whole"),
                    ("price class (contains)", By.XPATH, ".//*[contains(@class, 'price')]"),
                    ("data-price attr", By.XPATH, ".//*[@data-price]"),
                    ("span with AED", By.XPATH, ".//span[contains(text(), 'AED')]"),
                    ("any span with number", By.XPATH, ".//span[1]"),
                    ("SAR indicator", By.XPATH, ".//span[contains(text(), 'SAR')]"),
                ]
                
                for selector_name, by_type, selector_value in price_selectors:
                    try:
                        elements = first_product.find_elements(by_type, selector_value)
                        if elements:
                            for idx, elem in enumerate(elements[:3]):  # Show first 3
                                text = elem.text.strip()
                                logger.info(f"  ✓ [{selector_name}] #{idx+1}: '{text}'")
                        else:
                            logger.warning(f"  ✗ [{selector_name}] No elements found")
                    except Exception as e:
                        logger.debug(f"  ✗ [{selector_name}] Error: {str(e)[:100]}")
                
                # Step 8: Extract title
                logger.info("\n" + "="*70)
                logger.info("📝 TESTING TITLE SELECTORS")
                logger.info("="*70)
                
                title_selectors = [
                    ("h2", By.XPATH, ".//h2"),
                    ("h3", By.XPATH, ".//h3"),
                    ("span with length > 10", By.XPATH, ".//*[string-length(normalize-space(text())) > 10]"),
                ]
                
                for selector_name, by_type, selector_value in title_selectors:
                    try:
                        elements = first_product.find_elements(by_type, selector_value)
                        if elements:
                            for idx, elem in enumerate(elements[:2]):
                                text = elem.text.strip()
                                if text:
                                    logger.info(f"  ✓ [{selector_name}] #{idx+1}: '{text[:80]}'")
                    except Exception as e:
                        logger.debug(f"  ✗ [{selector_name}] Error: {str(e)[:100]}")
                
                # Step 9: Get link
                logger.info("\n" + "="*70)
                logger.info("🔗 TESTING LINK SELECTORS")
                logger.info("="*70)
                
                try:
                    link_elem = first_product.find_element(By.XPATH, ".//a")
                    link = link_elem.get_attribute("href")
                    logger.info(f"  ✓ Link: {link}")
                except Exception as e:
                    logger.warning(f"  ✗ Link not found: {e}")
            else:
                logger.warning("❌ No products found with original selector!")
                
        except Exception as e:
            logger.error(f"Error analyzing product: {e}")
        
        # Step 10: Check for bot detection
        logger.info("\n" + "="*70)
        logger.info("🤖 BOT DETECTION CHECK")
        logger.info("="*70)
        
        if "blocked" in page_source.lower() or "robot" in page_source.lower():
            logger.warning("⚠️  POSSIBLE BOT DETECTION!")
        
        if len(page_source) < 10000:
            logger.warning("⚠️  Page source is very small - might indicate bot detection or error")
        else:
            logger.info("✓ Page source seems normal size")
        
        logger.info("\n" + "="*70)
        logger.info("DEBUG COMPLETE - Check /tmp/noon_page.html for full HTML")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}", exc_info=True)
    
    finally:
        driver.quit()


if __name__ == "__main__":
    debug_noon_scraping()
