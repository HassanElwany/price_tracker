# Noon Scraping Debugging Guide

## Quick Start: Run Debug Test

```bash
python test_noon_debug.py
```

This will show you:

- ✓ Number of products found with each selector
- ✓ What titles are extracted
- ✓ What prices are extracted (or why they failed)
- ✓ Debug logs showing each step

---

## Understanding the Debug Output

### Example Output:

```
🔍 DEBUG: Page Title: Search Results - Noon.com
🔍 DEBUG: Page Source Size: 125430 bytes
🔍 DEBUG: Primary selector found 12 products
🔍 DEBUG [1]: Title='Sample Laptop Model XYZ' Price='2,499 SAR'
🔍 DEBUG [2]: Title='Another Laptop 15"' Price='N/A'
```

### What Each Line Means:

**Page Title & Size**

```
🔍 DEBUG: Page Title: Search Results - Noon.com
🔍 DEBUG: Page Source Size: 125430 bytes
```

- If size < 10000: Page might not have loaded properly (bot blocked?)
- If title contains "error": Something went wrong

**Selector Attempts**

```
🔍 DEBUG: Primary selector found 12 products
Selectors tried: [Primary: 12 results, Alt1: 0 results, ...]
```

- Number should be > 0 if page loaded
- If 0: Noon might have changed their HTML structure

**Product Extraction**

```
🔍 DEBUG [1]: Title='...' Price='2,499 SAR'
✓ Found price via currency indicator: 2,499 SAR
```

- `✓` = Success - price was found
- `✗` = Failed - all strategies tried but no price found

---

## Common Issues & Solutions

### Issue 1: "Found 0 products"

**Problem**: Selectors don't match the HTML

**Solution Steps**:

1. Run the debug test and check what selectors failed
2. Look at the page HTML (see "Inspecting the HTML" below)
3. Find the correct data-qa attribute or class name
4. Update the selector in [browser.py](browser.py) line 25:
   ```python
   NOON_PRODUCT_XPATH = '//div[@data-qa="plp-product-box"]'  # Update this
   ```

### Issue 2: "Found 20 products but Prices are all N/A"

**Problem**: Price selectors don't match Noon's current HTML

**Solution Steps**:

1. Check debug output - which price strategy succeeded?
   - `a-price-whole`?
   - `price class`?
   - Currency indicator?
2. Update `_extract_price()` in [browser.py](browser.py) line 184

### Issue 3: "Page Source Size: 5000 bytes (too small)"

**Problem**: Page wasn't fully loaded (Noon blocked the bot)

**Solutions**:

- Increase wait time in [browser.py](browser.py) line 298:
  ```python
  time.sleep(15)  # Try increasing to 20 or 25
  ```
- Try rotating user-agents (see "Advanced: Bot Detection" below)
- Add delays between requests

---

## Inspecting the HTML

### Quick Method: Save HTML in Debug Test

When you run the test, modify [test_noon_debug.py](test_noon_debug.py) to save the HTML:

```python
# Add after line 23 in test_noon_debug.py:
scraper.driver.get("https://www.noon.com/saudi-en/search?q=laptop")
import time
time.sleep(15)

# Save the HTML
with open("/tmp/noon_page.html", "w") as f:
    f.write(scraper.driver.page_source)
print("Saved to /tmp/noon_page.html")
```

Then:

```bash
# Open in your browser
firefox /tmp/noon_page.html
# Or copy to local machine and open in Chrome DevTools
```

### What to Look For:

1. **Find a product element** - Right-click > Inspect

   ```html
   <div data-qa="plp-product-box">
     ← This is what we're looking for
     <h2>Laptop Name</h2>
     ← Title is here <span class="price">2,499</span> ← Price is here
   </div>
   ```

2. **Check the attributes**:
   - Does `data-qa="plp-product-box"` still exist?
   - Or has it changed to something else?
   - What class does the price have?

3. **Update the selectors** based on what you find

---

## Advanced: Bot Detection

If Noon keeps blocking you (small page size), try:

### Option 1: Increase Wait Time

[browser.py](browser.py) line 298:

```python
time.sleep(20)  # Instead of 15
```

### Option 2: Better User-Agent

[browser.py](browser.py) line 83-86:

```python
# Add this - randomize the user agent
import random
agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]
chrome_options.add_argument(f"user-agent={random.choice(agents)}")
```

### Option 3: Add Delays

[main.py](main.py):

```python
import time

# After amazon results
time.sleep(5)

# Before noon
logger.info(f"\n>>> Scraping Noon (waiting 5 seconds)...")
time.sleep(5)
# Then scrape noon
```

### Option 4: Use Residential Proxy

If Noon blocks frequently, you might need a proxy server.

---

## Step-by-Step Fix Process

### For "Found 0 Products":

1. **Run the test**:

   ```bash
   python test_noon_debug.py 2>&1 | grep "DEBUG"
   ```

2. **Look for this line**:

   ```
   Selectors tried: [Primary: 0 results, Alt1: 0 results, ...]
   ```

3. **Save HTML and inspect** (see "Inspecting the HTML" above)

4. **Find the correct data-qa value**:

   ```
   Right-click product > Inspect > Look for data-qa="..."
   ```

5. **Update [browser.py](browser.py) line 25**:

   ```python
   NOON_PRODUCT_XPATH = '//div[@data-qa="new-value-here"]'
   ```

6. **Rerun the test**:
   ```bash
   python test_noon_debug.py
   ```

### For "Prices all N/A":

1. **Check debug output**:

   ```
   ✗ No price found. Tried: a-price-whole, price class, currency indicator
   ```

2. **Save HTML and inspect** a product element

3. **Find where the price is**:

   ```html
   <span class="product-price">2,499</span> ← If class is different
   <span data-price="2499">...</span> ← Or data attribute
   ```

4. **Add new selector to `_extract_price()` in [browser.py](browser.py) line 184**:

   ```python
   # Strategy 5: Try your new selector
   try:
       price_elem = element.find_element(By.XPATH, ".//*[contains(@class, 'product-price')]")
       if price_elem.text:
           return price_elem.text.strip()
   except:
       pass
   ```

5. **Rerun the test**:
   ```bash
   python test_noon_debug.py
   ```

---

## Debugging Checklist

- [ ] Run `python test_noon_debug.py`
- [ ] Check "Products found" count
  - [ ] If 0: Check selectors need updating
  - [ ] If > 0: Check why prices are N/A
- [ ] Check page size (should be > 10000 bytes)
  - [ ] If < 10000: Bot detection or page error
- [ ] Inspect first product in debug output
  - [ ] Title extracted correctly?
  - [ ] At least some prices found?
- [ ] If prices are N/A, save HTML and inspect selectors
- [ ] Update selectors in [browser.py](browser.py)
- [ ] Rerun test to verify fix

---

## Need Help?

1. **Save this output**: `python test_noon_debug.py > /tmp/debug_output.txt`
2. **Save the HTML**: Check for `/tmp/noon_page.html`
3. **Check what failed**: Look for "✗" marks in output
4. **Inspect the HTML** to see actual structure
5. **Update the selector** based on what you find

The debug test gives you exact information about:

- What selectors were tried
- Which ones worked
- What was extracted
- Where the failures are

Use this to pinpoint exactly what needs to be fixed! 🔍
