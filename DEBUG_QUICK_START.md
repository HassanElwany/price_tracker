# Noon Scraping - Quick Start Debugging

## The Problem

Noon prices aren't being scraped properly. The reasons could be:

1. **Noon changed their HTML structure** → Selectors don't match anymore
2. **Bot detection blocked the request** → Page didn't load fully
3. **Price format changed** → Extraction selectors don't match

---

## Quick Diagnosis: Run the Debug Test

```bash
python test_noon_debug.py
```

This will show you exactly:

- How many products were found
- What titles were extracted
- What prices were extracted (or why they failed)
- Specific errors and which selectors worked/failed

---

## What the Output Tells You

### Output Example 1: ✓ Everything Works

```
🔍 DEBUG: Found 12 products on Noon
🔍 DEBUG [1]: Title='Laptop Model XYZ' Price='2,499 SAR'
🔍 DEBUG [2]: Title='Another Laptop' Price='1,899 SAR'
```

→ **No action needed!** Noon scraping is working fine.

---

### Output Example 2: ✗ Found 0 Products

```
🔍 DEBUG: Page Source Size: 2000 bytes  ← TOO SMALL!
Selectors tried: [Primary: 0 results, Alt1: 0 results, ...]
```

→ **Page didn't load properly** (likely bot detection)
→ Go to: "Bot Detection Fix" below

---

### Output Example 3: ✗ Products found but Prices are N/A

```
🔍 DEBUG: Found 12 products on Noon
🔍 DEBUG [1]: Title='Laptop Model XYZ' Price='N/A'
✗ No price found. Tried: a-price-whole, price class, currency indicator
```

→ **Selectors need updating**
→ Go to: "Selector Fix" below

---

## Fix 1: Selector Needs Updating (Prices are N/A)

### Step 1: Find New Selectors

```bash
python find_noon_selectors.py
```

This will:

- Test many different selectors
- Show you which ones work
- Tell you exactly what to update

### Step 2: Update browser.py

The tool will tell you something like:

```
✓ Product Selector:
  //div[@data-qa="new-selector-here"]

Update in browser.py line 25:
  NOON_PRODUCT_XPATH = '//div[@data-qa="new-selector-here"]'
```

Do exactly that.

### Step 3: Test Again

```bash
python test_noon_debug.py
```

If prices still show "N/A":

1. Save the HTML: Add this to test_noon_debug.py before calling scrape_noon():
   ```python
   with open("/tmp/noon_page.html", "w") as f:
       f.write(scraper.driver.page_source)
   ```
2. Open `/tmp/noon_page.html` in your browser
3. Right-click a product → Inspect
4. Find where the price is in the HTML
5. Update the price selectors in [browser.py](browser.py) around line 200

---

## Fix 2: Bot Detection (Page Size Too Small)

### Option A: Increase Wait Time (Safest)

Edit [browser.py](browser.py) line 298:

```python
time.sleep(15)  # Change to 20 or 25
```

Then test:

```bash
python test_noon_debug.py
```

### Option B: Better User-Agent

Edit [browser.py](browser.py) line 83-86:

```python
# Update user-agent or add randomization
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
)
```

### Option C: Add Delays Between Requests

Edit [main.py](main.py) before scraping Noon:

```python
import time

logger.info("Waiting 5 seconds before Noon...")
time.sleep(5)

noon_results = scraper.scrape_noon(product)
```

---

## Step-by-Step Getting Your Selectors Fixed

### When to use which tool:

| Problem              | Tool to Run              | What It Does                           |
| -------------------- | ------------------------ | -------------------------------------- |
| "Found 0 products"   | `find_noon_selectors.py` | Tests selectors & shows new ones       |
| "Prices are all N/A" | `find_noon_selectors.py` | Shows you HTML & finds price selectors |
| Unsure what's wrong  | `test_noon_debug.py`     | Shows exact debug info                 |

---

## Complete Fix Walkthrough

### If you see "Found 0 products":

1. **Check page was loaded**:

   ```bash
   python test_noon_debug.py
   ```

   Look for: `🔍 DEBUG: Page Source Size: XXXX bytes`
   - If < 10000: Noon blocked you (see "Bot Detection" fixes)
   - If > 10000: Selector doesn't match

2. **Find new selector**:

   ```bash
   python find_noon_selectors.py
   ```

   Look for: `🎯 Best selector: ...`

3. **Update browser.py** line 25 with the new selector

4. **Test**:
   ```bash
   python test_noon_debug.py
   ```

### If you see "Prices are N/A":

1. **Inspect the product HTML**:
   Add this to `test_noon_debug.py`:
   ```python
   with open("/tmp/noon_page.html", "w") as f:
       f.write(scraper.driver.page_source)
   ```
2. **Open and inspect**:

   ```bash
   firefox /tmp/noon_page.html
   ```

   Right-click product → Inspect → Find the price element

3. **Note the selector**:
   - Is it a class? `<span class="price">`
   - Is it data-attribute? `<span data-price=...>`
   - Is it containing SAR? `<span>2,499 SAR</span>`

4. **Update `_extract_price()` in [browser.py](browser.py)** around line 200:
   Add a new strategy for your selector

5. **Test**:
   ```bash
   python test_noon_debug.py
   ```

---

## Files You've Been Given

| File                                             | Purpose                             |
| ------------------------------------------------ | ----------------------------------- |
| [test_noon_debug.py](test_noon_debug.py)         | Run this first to see what's wrong  |
| [find_noon_selectors.py](find_noon_selectors.py) | Run this to find correct selectors  |
| [NOON_DEBUG_GUIDE.md](NOON_DEBUG_GUIDE.md)       | Detailed guide with all information |
| [browser.py](browser.py)                         | Enhanced with debug mode            |

---

## Checklist

Before you ask for more help, verify:

- [ ] Ran `python test_noon_debug.py` and noted the output
- [ ] Checked page source size (should be > 10000 bytes)
- [ ] If products found: checked why prices are N/A
- [ ] If 0 products: ran `find_noon_selectors.py`
- [ ] Updated selectors in [browser.py](browser.py) based on tool output
- [ ] Reran `test_noon_debug.py` to verify fix

---

## Need More Help?

If selectors still don't work after trying these steps:

1. **Save the debug output**:

   ```bash
   python test_noon_debug.py > /tmp/debug.log
   ```

2. **Save the HTML**:
   (Add HTML save to test_noon_debug.py as shown above)

3. **Check these specific things**:
   - Is the page loading at all? (Check page size)
   - How many products are found?
   - What exact error for prices?

4. **If it's still bot detection**:
   - Try increasing wait time to 25 seconds
   - Or use a proxy service
   - Or add random delays between requests

The debug tools give you exact information about where the problem is! 🔍
