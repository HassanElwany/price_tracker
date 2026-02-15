#!/usr/bin/env python3
"""
Noon Selector Finder - Find the right CSS selectors and XPath for Noon's current HTML
Run this when Noon selectors stop working to find the new ones
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def find_noon_selectors():
    """Interactively find working selectors for Noon"""
    
    # Setup browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(15)
    
    try:
        # Load Noon
        url = "https://www.noon.com/saudi-en/search?q=laptop"
        print(f"\n🌐 Loading {url}...")
        driver.get(url)
        
        print("⏳ Waiting 15 seconds for page to load...")
        time.sleep(15)
        
        print("✓ Page loaded\n")
        
        # Test product selectors
        print("="*70)
        print("FINDING PRODUCT SELECTORS")
        print("="*70)
        
        selectors = [
            '//div[@data-qa="plp-product-box"]',
            '//div[@data-qa]',
            '//div[contains(@class, "product")]',
            "//article",
            "//div[contains(@class, 'item')]",
            "//div[@role='option']",
        ]
        
        best_selector = None
        best_count = 0
        
        print("\nTesting selectors:\n")
        for sel in selectors:
            try:
                elements = driver.find_elements(By.XPATH, sel)
                count = len(elements)
                status = "✓" if count > 0 else "✗"
                print(f"{status} {sel}")
                print(f"  → Found {count} products")
                
                if count > best_count:
                    best_selector = sel
                    best_count = count
            except Exception as e:
                print(f"✗ {sel}")
                print(f"  → Error: {type(e).__name__}")
        
        if best_selector:
            print(f"\n🎯 Best selector: {best_selector} ({best_count} products)")
            
            # Now examine the first product
            print("\n" + "="*70)
            print("EXAMINING FIRST PRODUCT")
            print("="*70)
            
            products = driver.find_elements(By.XPATH, best_selector)
            first_product = products[0]
            
            # Get HTML
            html = first_product.get_attribute("outerHTML")
            print(f"\nProduct HTML size: {len(html)} bytes")
            print("\nFirst 1500 characters:")
            print("-" * 70)
            print(html[:1500])
            print("-" * 70)
            
            # Save full HTML
            with open("/tmp/noon_first_product.html", "w") as f:
                f.write(html)
            print("✓ Full product HTML saved to /tmp/noon_first_product.html")
            
            # Find price selectors
            print("\n" + "="*70)
            print("FINDING PRICE SELECTORS")
            print("="*70)
            print("\nSearching for price patterns...\n")
            
            price_selectors = [
                (".//span[contains(@class, 'price')]", "span with 'price' class"),
                (".//div[contains(@class, 'price')]", "div with 'price' class"),
                (".//span[contains(text(), 'SAR')]", "span containing 'SAR'"),
                (".//span[contains(text(), 'AED')]", "span containing 'AED'"),
                (".//span[contains(text(), ',')]", "span with comma (thousands sep)"),
                (".//span[@data-price]", "span with data-price attribute"),
            ]
            
            for xpath, desc in price_selectors:
                try:
                    elems = first_product.find_elements(By.XPATH, xpath)
                    if elems:
                        for i, elem in enumerate(elems[:2]):  # Show first 2
                            text = elem.text.strip()
                            if text:
                                print(f"✓ {desc}")
                                print(f"  → Text: '{text}'")
                except Exception as e:
                    pass
            
            # Find title selectors
            print("\n" + "="*70)
            print("FINDING TITLE SELECTORS")
            print("="*70)
            print("\nSearching for title patterns...\n")
            
            title_selectors = [
                (".//h2", "h2 tag"),
                (".//h3", "h3 tag"),
                (".//h4", "h4 tag"),
                (".//span[contains(@class, 'title')]", "span with 'title' class"),
                (".//a[@href]", "link element"),
            ]
            
            for xpath, desc in title_selectors:
                try:
                    elems = first_product.find_elements(By.XPATH, xpath)
                    if elems:
                        elem = elems[0]
                        text = elem.text.strip()
                        if text and len(text) > 10:
                            print(f"✓ {desc}")
                            print(f"  → Text: '{text[:80]}'")
                except Exception as e:
                    pass
            
            # Summary
            print("\n" + "="*70)
            print("SUMMARY")
            print("="*70)
            print(f"\n✓ Product Selector:\n  {best_selector}")
            print(f"\n→ Update in browser.py line 25:")
            print(f"  NOON_PRODUCT_XPATH = '{best_selector}'")
            print("\n→ Check /tmp/noon_first_product.html to manually inspect")
            print("→ Look for price/title selectors in the HTML")
            
        else:
            print("\n❌ ERROR: Could not find any products!")
            print("This might mean:")
            print("  • Noon blocked the request")
            print("  • JavaScript didn't render properly")
            print("  • HTML structure changed completely")
            print("\nTry:")
            print("  1. Increase wait time to 20-25 seconds")
            print("  2. Change user-agent")
            print("  3. Use a proxy server")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════╗
║         Noon Selector Finder - Find Working Selectors              ║
║                                                                     ║
║ This tool will:                                                    ║
║ 1. Load Noon's search page                                        ║
║ 2. Test different product selectors                               ║
║ 3. Find the correct XPath/CSS selectors                          ║
║ 4. Show you what to update in browser.py                         ║
║                                                                     ║
║ It will take ~20 seconds to complete                              ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    find_noon_selectors()
