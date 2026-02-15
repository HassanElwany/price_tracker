#!/usr/bin/env python3
"""
Quick debug script - fast version to inspect what's on Noon's page
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def debug():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(15)
    
    try:
        url = "https://www.noon.com/saudi-en/search?q=laptop"
        print(f"\n🌐 Loading: {url}")
        driver.get(url)
        
        print("⏳ Waiting 15 seconds for JS to render...")
        time.sleep(15)
        
        print(f"✓ Page loaded. Title: {driver.title}")
        print(f"  Page source size: {len(driver.page_source)} bytes\n")
        
        # Test selectors
        print("="*70)
        print("TESTING PRODUCT SELECTORS")
        print("="*70)
        
        selectors = [
            '//div[@data-qa="plp-product-box"]',
            "//div[contains(@class, 'product')]",
            "//article",
        ]
        
        for sel in selectors:
            try:
                products = driver.find_elements(By.XPATH, sel)
                print(f"✓ '{sel}': {len(products)} products found")
            except Exception as e:
                print(f"✗ '{sel}': {type(e).__name__}")
        
        # Get first product
        print("\n" + "="*70)
        print("INSPECTING FIRST PRODUCT")
        print("="*70)
        
        products = driver.find_elements(By.XPATH, '//div[@data-qa="plp-product-box"]')
        
        if products:
            prod = products[0]
            html = prod.get_attribute("outerHTML")
            
            print(f"✓ First product HTML size: {len(html)} bytes")
            print("\nFirst 1000 chars of product HTML:")
            print(html[:1000])
            
            # Try to extract price with different methods
            print("\n" + "="*70)
            print("PRICE EXTRACTION TESTS")
            print("="*70)
            
            # Method 1: innerText of all elements
            all_elements = prod.find_elements(By.XPATH, ".//*")
            print(f"Total elements in product: {len(all_elements)}")
            
            # Look for prices in text
            print("\nElements containing numbers (potential prices):")
            for elem in all_elements[:20]:  # First 20 elements
                text = elem.text.strip()
                if text and any(c.isdigit() for c in text):
                    tag = elem.tag_name
                    print(f"  <{tag}> {text[:60]}")
            
            # Method 2: Specific selectors
            price_tests = [
                ('//span[contains(@class, "price")]', "price span"),
                ('//div[contains(@class, "price")]', "price div"),
                ('//span[contains(text(), "SAR")]', "SAR span"),
                ('//span[contains(text(), "AED")]', "AED span"),
            ]
            
            print("\nSpecific price selectors:")
            for xpath, desc in price_tests:
                try:
                    elems = prod.find_elements(By.XPATH, xpath)
                    if elems:
                        print(f"  ✓ {desc}: found {len(elems)}")
                        for e in elems[:1]:
                            print(f"     Text: '{e.text}'")
                except:
                    print(f"  ✗ {desc}: not found")
        else:
            print("❌ NO PRODUCTS FOUND!")
        
        # Save page HTML
        print("\n" + "="*70)
        with open("/tmp/noon_debug.html", "w") as f:
            f.write(driver.page_source)
        print("✓ Full page saved to /tmp/noon_debug.html")
        print("  Open this file in a browser to inspect the HTML structure")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug()
