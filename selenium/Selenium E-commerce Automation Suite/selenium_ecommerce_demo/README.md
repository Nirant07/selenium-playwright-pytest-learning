# Selenium E-commerce Demo

Test targets:
1. Local `mock_store.html`: product search, category/price filters, and add-button interaction.
2. SauceDemo: demo login, cart, checkout overview, and demo order confirmation.
3. Amazon India: product search, optional sorting, product details/title and best-effort price verification, and a cautious add-to-cart smoke test with best-effort cleanup.

## Run
```powershell
python -m pip install -r requirements.txt
python ecommerce_demo.py
```

Keep `mock_store.html` beside `ecommerce_demo.py`.

## Important Amazon limitations
Amazon is a live website and can change its HTML, show CAPTCHA/verification, or require sign-in. The script does not bypass verification and reports unavailable steps as skipped/blocked. The Amazon test does not submit checkout or payment. If the script adds an item to the cart, it attempts to remove it afterward, but cleanup cannot be guaranteed if Amazon changes its page or requires sign-in. Inspect your cart if a cleanup warning appears.


### Chrome password warning

The script configures its automated Chrome session to disable password-manager prompts and compromised-password leak detection for the test session. This does not change your everyday Chrome profile. Chrome may still show browser-level warnings depending on its version or policy. The SauceDemo credentials are public demo credentials; never use a real personal password in test code.
