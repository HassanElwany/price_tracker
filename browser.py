"""
Web scraping module using Selenium for e-commerce price tracking.

This module contains the PriceScraper class which handles automated
browser-based scraping of Amazon and Noon platforms using Selenium WebDriver.
"""

import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configure logging for debugging scraping operations
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS: CSS selectors, XPaths, and configuration for web scraping
# ============================================================================

# Product XPath selectors for Amazon
# WHY: Using data-component-type attribute is more reliable than CSS classes
# which Amazon frequently changes. XPath allows us to target structural elements.
AMAZON_PRODUCT_XPATH = '//div[@data-component-type="s-search-result"]'

# Product XPath selector for Noon
# WHY: data-qa attributes are typically stable identifiers used by Noon for testing
NOON_PRODUCT_XPATH = '//div[@data-qa="plp-product-box"]'

# Timeout configuration
# WHY: Increased timeouts prevent premature failures on slow connections
# while still having reasonable limits to avoid hanging indefinitely
WAIT_TIMEOUT = 20

# Base URLs for each platform with country mappings
AMAZON_MARKETS = {
    'Saudi Arabia': 'https://www.amazon.sa',
    'UAE': 'https://www.amazon.ae',
    'Egypt': 'https://www.amazon.eg',
}

NOON_MARKETS = {
    'Saudi Arabia': 'https://www.noon.com/saudi-en',
    'UAE': 'https://www.noon.com/uae-en',
    'Egypt': 'https://www.noon.com/egypt-en',
}


class PriceScraper:
    """
    Automated web scraper for price tracking across e-commerce platforms.
    
    Uses Selenium WebDriver with Chrome in headless mode for efficient
    background scraping without opening a visible browser window.
    
    Attributes:
        market (str): The market/region to scrape (e.g., "Saudi Arabia")
        driver (webdriver.Chrome): Selenium Chrome WebDriver instance
    """
    
    def __init__(self, market):
        """
        Initialize the price scraper with a specific market.
        
        WHY: Initializing the browser once and reusing it is more efficient than
        creating new browser instances for each scraping operation.
        
        Args:
            market (str): The market to scrape (e.g., "Saudi Arabia", "UAE")
        """
        self.market = market
        self.driver = self._setup_driver()
    
    def _setup_driver(self):
        """
        Configure and initialize Chrome WebDriver with optimization options.
        
        WHY: Headless mode runs the browser without a GUI, making it 2-3x faster
        and using less memory. This is essential for background scraping tasks.
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        chrome_options = Options()
        
        # Run browser in background without opening a window
        chrome_options.add_argument("--headless")
        
        # Disable shared memory usage to avoid crashes on systems with limited resources
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Disable sandboxing - may be required on some systems
        chrome_options.add_argument("--no-sandbox")
        
        # Add user-agent to avoid bot detection
        # WHY: Many sites block requests from headless browsers. Adding a real user-agent
        # makes the request look like it's coming from a regular browser
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Additional performance optimizations
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Set page load timeout - if page takes longer than this, raise exception
        driver.set_page_load_timeout(15)
        
        logger.info(f"✓ Chrome WebDriver initialized for {self.market}")
        return driver
    
    def _extract_title(self, element):
        """
        Extract title from a product element using multiple fallback selectors.
        
        WHY: Amazon and Noon frequently change their HTML structure.
        Using multiple selectors makes the scraper robust to these changes.
        
        Args:
            element: WebElement to extract title from
            
        Returns:
            str: Title string or "N/A" if not found
        """
        try:
            # Strategy 1: Try h2 heading (most common)
            try:
                title_elem = element.find_element(By.XPATH, ".//h2")
                title_text = title_elem.text.strip()
                if title_text:
                    return title_text
            except:
                pass
            
            # Strategy 2: Try h3 heading
            try:
                title_elem = element.find_element(By.XPATH, ".//h3")
                title_text = title_elem.text.strip()
                if title_text:
                    return title_text
            except:
                pass
            
            # Strategy 3: Try span with specific data attribute (Amazon format)
            try:
                title_elem = element.find_element(By.XPATH, ".//span[@data-component-type='s-title']")
                title_text = title_elem.text.strip()
                if title_text:
                    return title_text
            except:
                pass
            
            # Strategy 4: Try any element with large text (likely title)
            try:
                # Look for elements with substantial text content
                spans = element.find_elements(By.XPATH, ".//*[string-length(normalize-space(text())) > 10]")
                for span in spans:
                    text = span.text.strip()
                    if text and len(text) > 10:
                        return text
            except:
                pass
            
            return "N/A"
        
        except Exception as e:
            logger.debug(f"Error extracting title: {e}")
            return "N/A"
    
    def _parse_noon_price(self, price_string):
        """
        Parse Noon's mixed price format into structured fields.
        
        Noon combines current price, original price, and discount in one string:
        "4,099\n5,899\n30% OFF\n#2 in Notebook Laptops\nFree Delivery"
        
        This extracts:
        - current_price: The final price (e.g., 4099)
        - original_price: The original price (e.g., 5899)
        - discount_percentage: The discount % (e.g., 30)
        
        Args:
            price_string (str): Raw price string from Noon
            
        Returns:
            dict: Parsed price data with keys: current, original, discount_percent
        """
        import re
        
        result = {
            'current': 'N/A',
            'original': 'N/A',
            'discount_percent': 'N/A'
        }
        
        if not price_string or price_string == "N/A":
            return result
        
        try:
            # Split by newline to get individual components
            lines = [line.strip() for line in price_string.split('\n') if line.strip()]
            
            # Find all numbers (prices) from the first few lines only
            # Prices usually appear in the first 3 lines before metadata
            numbers = []
            discount = None
            
            for idx, line in enumerate(lines):
                # Stop looking for prices after we've checked enough lines
                # Prices are typically in the first 3 lines
                if idx > 4:
                    break
                
                # Look for discount percentage first (it contains both number and %)
                discount_match = re.search(r'(\d+)\s*%\s*OFF', line, re.IGNORECASE)
                if discount_match:
                    discount = int(discount_match.group(1))
                    continue
                
                # Skip lines that clearly contain rankings or other metadata
                if any(keyword in line.lower() for keyword in ['rank', '#', 'in', 'fast', 'left', 'stock']):
                    continue
                
                # Extract price numbers (handle comma separators, e.g., "4,099")
                # Only match if the line looks like a price (mostly numbers)
                if re.search(r'^\d{1,2},?\d{3}$|^\d+$', line):
                    num_str = line.replace(',', '')
                    try:
                        num = int(float(num_str))
                        # Only add if it's a reasonable price (> 50 SAR, < 1 million)
                        if 50 < num < 1000000:
                            numbers.append(num)
                    except ValueError:
                        pass
            
            # Assign extracted values
            # First number is usually current price, second is original (or vice versa)
            if len(numbers) >= 2:
                # If current < original, they're in the right order
                # Otherwise, swap them
                if numbers[0] < numbers[1]:
                    result['current'] = numbers[0]
                    result['original'] = numbers[1]
                else:
                    result['current'] = numbers[1]
                    result['original'] = numbers[0]
            elif len(numbers) == 1:
                # Only one price found
                result['current'] = numbers[0]
            
            # Add discount if found
            if discount:
                result['discount_percent'] = discount
            elif result['current'] != 'N/A' and result['original'] != 'N/A':
                # Calculate discount if not explicitly stated
                try:
                    calculated_discount = round(
                        ((result['original'] - result['current']) / result['original']) * 100
                    )
                    result['discount_percent'] = calculated_discount
                except:
                    pass
        
        except Exception as e:
            logger.debug(f"Error parsing Noon price: {e}")
        
        return result
    
    def _extract_price(self, element, debug=False):
        """
        Extract price from a product element using multiple selector strategies.
        
        WHY: E-commerce sites frequently change their HTML structure. Using multiple
        selectors in order of preference ensures we can find prices even after updates.
        This "fallback" pattern is more robust than relying on a single selector.
        
        Args:
            element: Selenium WebElement representing a product
            debug (bool): If True, logs all attempted selectors
            
        Returns:
            str: Extracted price or "N/A" if not found
        """
        try:
            strategies_tried = []
            
            # Strategy 1: Try the newer Noon/Amazon price CSS class (common format)
            # WHY: a-price-whole is more specific and typically used for whole prices
            try:
                price_elem = element.find_element(By.CLASS_NAME, "a-price-whole")
                price_text = price_elem.get_attribute("innerText")
                if price_text:
                    if debug:
                        logger.debug(f"  ✓ Found price via a-price-whole: {price_text.strip()}")
                    return price_text.strip()
                strategies_tried.append("a-price-whole (found but empty)")
            except:
                strategies_tried.append("a-price-whole")
            
            # Strategy 2: Try generic price-related class
            # WHY: Using contains() makes this selector more flexible and
            # tolerant of small changes in class names
            try:
                price_elem = element.find_element(By.XPATH, ".//*[contains(@class, 'price')]")
                price_text = price_elem.text
                if price_text:
                    if debug:
                        logger.debug(f"  ✓ Found price via price class: {price_text.strip()}")
                    return price_text.strip()
                strategies_tried.append("price class (found but empty)")
            except:
                strategies_tried.append("price class")
            
            # Strategy 3: Try data-price attribute (some platforms use this)
            # WHY: Data attributes are often more stable than CSS classes
            try:
                price_text = element.get_attribute("data-price")
                if price_text:
                    if debug:
                        logger.debug(f"  ✓ Found price via data-price: {price_text.strip()}")
                    return price_text.strip()
                strategies_tried.append("data-price")
            except:
                strategies_tried.append("data-price")
            
            # Strategy 4: Look for SAR/AED currency indicators (Noon/Saudi specific)
            try:
                currency_elem = element.find_element(By.XPATH, ".//*[contains(text(), 'SAR') or contains(text(), 'AED')]")
                price_text = currency_elem.text
                if price_text:
                    if debug:
                        logger.debug(f"  ✓ Found price via currency indicator: {price_text.strip()}")
                    return price_text.strip()
                strategies_tried.append("Currency indicator")
            except:
                strategies_tried.append("Currency indicator")
            
            if debug:
                logger.debug(f"  ✗ No price found. Tried: {', '.join(strategies_tried)}")
            
            return "N/A"
        
        except Exception as e:
            logger.debug(f"Error extracting price: {e}")
            return "N/A"
    
    def scrape_amazon(self, search_query):
        """
        Scrape product prices from Amazon for a given search query.
        
        WHY: Separating scraping logic by platform makes the code modular and
        allows us to handle platform-specific quirks (different selectors, timing, etc.)
        
        Args:
            search_query (str): Product to search for (e.g., "laptop")
            
        Returns:
            list: List of dicts with keys: platform, product, price, link
        """
        results = []
        
        try:
            # Construct Amazon search URL
            base_url = AMAZON_MARKETS.get(self.market, AMAZON_MARKETS['Saudi Arabia'])
            search_url = f"{base_url}/s?k={search_query}"
            
            logger.debug(f"Loading Amazon URL: {search_url}")
            self.driver.get(search_url)
            
            # Wait for products to load - using simple sleep for compatibility
            # WHY: Simple time.sleep() is more reliable in headless mode than WebDriverWait
            # in some cases, and is sufficient when we know expected load time
            time.sleep(3)
            
            # Find all product elements on the search results page
            products = self.driver.find_elements(By.XPATH, AMAZON_PRODUCT_XPATH)
            logger.info(f"Found {len(products)} products on Amazon")
            
            for product in products:
                try:
                    # Extract product title using fallback strategy
                    title = self._extract_title(product)
                    
                    # Skip products with no title
                    if title == "N/A":
                        continue
                    
                    # Extract price using multi-selector fallback strategy
                    price = self._extract_price(product)
                    
                    # Extract product link
                    try:
                        link_elem = product.find_element(By.XPATH, ".//h2/a | .//h3/a | .//a")
                        link = link_elem.get_attribute("href")
                    except:
                        link = "N/A"
                    
                    results.append({
                        'platform': 'Amazon',
                        'product': title,
                        'price': price,
                        'link': link
                    })
                
                except Exception as e:
                    logger.debug(f"Error processing Amazon product: {e}")
                    continue
            
            logger.info(f"✓ Successfully scraped {len(results)} Amazon products")
            return results
        
        except Exception as e:
            logger.error(f"✗ Error scraping Amazon: {e}")
            return []
    
    def scrape_noon(self, search_query, debug=False):
        """
        Scrape product prices from Noon for a given search query.
        
        WHY: Noon has stricter bot detection and requires careful timing.
        The increased wait times and page load timeout help avoid detection
        and ensure JavaScript-rendered content loads properly.
        
        Args:
            search_query (str): Product to search for (e.g., "laptop")
            debug (bool): If True, print detailed debugging information
            
        Returns:
            list: List of dicts with keys: platform, product, price, link
        """
        results = []
        
        try:
            # Construct Noon search URL
            base_url = NOON_MARKETS.get(self.market, NOON_MARKETS['Saudi Arabia'])
            search_url = f"{base_url}/search?q={search_query}"
            
            logger.debug(f"Loading Noon URL: {search_url}")
            self.driver.get(search_url)
            
            # Wait longer for Noon's JavaScript to render products
            # WHY: Noon uses heavy JavaScript rendering. 15 seconds ensures
            # all product elements are loaded before we start scraping. Increased
            # from 10s to 15s to handle slower responses.
            time.sleep(15)
            
            # Debug: Check if page loaded properly
            page_source = self.driver.page_source
            page_title = self.driver.title
            if debug:
                logger.info(f"🔍 DEBUG: Page Title: {page_title}")
                logger.info(f"🔍 DEBUG: Page Source Size: {len(page_source)} bytes")
            
            if "error" in page_title.lower() or len(page_source) < 10000:
                logger.warning(f"Possible page load issue - Title: {page_title}, Source length: {len(page_source)}")
            
            # Find all product elements on Noon search results page
            # Try primary selector first
            products = []
            selector_info = []
            
            try:
                products = self.driver.find_elements(By.XPATH, NOON_PRODUCT_XPATH)
                selector_info.append(f"Primary ({NOON_PRODUCT_XPATH}): {len(products)}")
                if debug:
                    logger.info(f"🔍 DEBUG: Primary selector found {len(products)} products")
            except Exception as e:
                selector_info.append(f"Primary selector failed: {type(e).__name__}")
                if debug:
                    logger.info(f"🔍 DEBUG: Primary selector failed - {type(e).__name__}")
            
            # Try alternative selectors if primary didn't find enough
            if len(products) < 5:
                alt_selectors = [
                    "//div[contains(@class, 'product')]",
                    "//article",
                    "//div[contains(@data-qa, 'product')]",
                ]
                
                for alt_sel in alt_selectors:
                    try:
                        alt_products = self.driver.find_elements(By.XPATH, alt_sel)
                        if alt_products:
                            selector_info.append(f"Alt ({alt_sel:50}): {len(alt_products)}")
                            if len(alt_products) > len(products):
                                products = alt_products
                                if debug:
                                    logger.info(f"🔍 DEBUG: Using alternative selector: {alt_sel}, found {len(alt_products)}")
                    except:
                        pass
            
            if debug:
                logger.info(f"🔍 DEBUG: Selectors tried: {selector_info}")
            
            logger.info(f"Found {len(products)} products on Noon")
            
            for idx, product in enumerate(products):
                try:
                    # Extract product title using fallback strategy
                    title = self._extract_title(product)
                    
                    # Skip products with no title
                    if title == "N/A":
                        continue
                    
                    # Extract price using multi-selector fallback strategy
                    price_raw = self._extract_price(product, debug=debug)
                    
                    # Parse Noon price format into structured data
                    price_data = self._parse_noon_price(price_raw)
                    
                    if debug:
                        logger.info(f"🔍 DEBUG [{idx+1}]: Title='{title[:50]}...' Price='{price_raw}'")
                    
                    # Extract product link
                    try:
                        link_elem = product.find_element(By.XPATH, ".//a")
                        link = link_elem.get_attribute("href")
                    except:
                        link = "N/A"
                    
                    results.append({
                        'platform': 'Noon',
                        'product': title,
                        'price_raw': price_raw,
                        'price_current': price_data['current'],
                        'price_original': price_data['original'],
                        'discount_percent': price_data['discount_percent'],
                        'link': link
                    })
                
                except Exception as e:
                    logger.debug(f"Error processing Noon product: {e}")
                    if debug:
                        logger.info(f"🔍 DEBUG: Error on product {idx+1}: {e}")
                    continue
            
            logger.info(f"✓ Successfully scraped {len(results)} Noon products")
            return results
        
        except Exception as e:
            logger.error(f"✗ Error scraping Noon: {e}")
            return []
    
    def close(self):
        """
        Close the browser and clean up resources.
        
        WHY: Properly closing the browser prevents memory leaks and zombie processes.
        This should always be called when done scraping, ideally in a try/finally block.
        """
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✓ Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
