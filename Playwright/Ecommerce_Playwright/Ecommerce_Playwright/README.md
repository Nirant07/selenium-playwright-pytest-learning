# E-commerce Automation — Playwright + Python

This project migrates the Selenium test scenarios to Playwright with Python and pytest.

## Test coverage

1. **Local practice storefront (`mock_store.html`)**
   - Search products
   - Filter by category and maximum price
   - Add-to-cart button state

2. **SauceDemo**
   - Demo login
   - Add a product to the cart
   - Verify cart contents
   - Complete the demo checkout and verify the confirmation page

3. **Amazon India (live smoke test)**
   - Search for wireless headphones
   - Best-effort low-to-high sorting
   - Extract a product title and optional price
   - Best-effort add-to-cart click when a clearly labelled control is available

The Amazon test does **not** log in, bypass CAPTCHA/verification, or proceed to checkout/payment. Amazon may change its markup or block automation. A live add-to-cart action can affect the current browser session's cart; inspect it manually if needed. The test intentionally does not delete cart items, because it cannot safely distinguish a pre-existing item from a test-added item in every live-site layout.

## Setup (Windows PowerShell)

Run these commands from this project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

If PowerShell blocks activation, either allow the script for the current terminal according to your organization's policy, or run the commands without activation using `.venv\Scripts\python.exe`.

## Run all tests

Headed (visible browser):

```powershell
python -m pytest -v -s --headed test_ecommerce.py
```

Headless:

```powershell
python -m pytest -v -s test_ecommerce.py
```

Run only the local test (no internet required):

```powershell
python -m pytest -v -s test_ecommerce.py -k local_store
```

Run the SauceDemo test only:

```powershell
python -m pytest -v -s --headed test_ecommerce.py -k saucedemo
```

Run the Amazon test only:

```powershell
python -m pytest -v -s --headed test_ecommerce.py -k amazon
```

## Reports and debugging

Create a self-contained HTML report (requires `pytest-html`):

```powershell
python -m pip install pytest-html
python -m pytest -v -s --headed --html=report.html --self-contained-html
```

If Amazon results fail to load, inspect the generated `amazon_search_debug.png` or `amazon_results_debug.png`. If the add-to-cart action fails, inspect `amazon_cart_debug.png`. A skipped/blocked live-site step is not counted as a successful verification.

## Project structure

```text
Ecommerce_Playwright/
├── test_ecommerce.py
├── mock_store.html
├── requirements.txt
└── README.md
```
