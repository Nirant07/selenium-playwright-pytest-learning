from pathlib import Path

import pytest
import re
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError

ROOT = Path(__file__).resolve().parent
WAIT_MS = 15_000


def test_local_store_search_filters_and_cart(page: Page) -> None:
    """Test local product search, category/price filters, and add-to-cart."""
    store_url = (ROOT / "mock_store.html").resolve().as_uri()
    page.goto(store_url)

    search = page.get_by_role("searchbox", name="Search products")
    search.fill("headphones")

    visible_products = page.locator(".product:visible")
    expect(visible_products).to_have_count(1)
    expect(visible_products).to_contain_text("Wireless Headphones")
    print("PASS: local demo product search")

    search.fill("")
    page.locator("#category").select_option(label="Home")
    page.locator("#max-price").fill("500")

    expect(visible_products).to_have_count(1)
    expect(visible_products).to_contain_text("Coffee Mug")
    print("PASS: local demo category and price filters")

    coffee_mug = page.locator(".product:visible").filter(has_text="Coffee Mug")
    coffee_mug.get_by_role("button", name="Add to cart").click()
    expect(coffee_mug.get_by_role("button", name="Added")).to_be_disabled()
    print("PASS: local demo add-to-cart interaction")


def test_checkout_on_saucedemo(page: Page) -> None:
    """Test login, cart, and checkout on the public SauceDemo test store."""
    page.goto("https://www.saucedemo.com/")

    page.locator("#user-name").fill("standard_user")
    page.locator("#password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()

    expect(page.locator(".inventory_list")).to_be_visible()
    print("PASS: SauceDemo login")

    page.locator("#add-to-cart-sauce-labs-backpack").click()
    expect(page.locator(".shopping_cart_badge")).to_have_text("1")
    print("PASS: SauceDemo product added to cart")

    page.locator(".shopping_cart_link").click()
    expect(page).to_have_url(re.compile(r".*/cart\.html"))
    item = page.locator(".cart_item")
    expect(item).to_contain_text("Sauce Labs Backpack")
    print("PASS: SauceDemo cart contents")

    page.locator("#checkout").click()
    page.locator("#first-name").fill("Test")
    page.locator("#last-name").fill("User")
    page.locator("#postal-code").fill("560001")
    page.locator("#continue").click()

    expect(page.locator(".summary_info")).to_be_visible()
    expect(page.locator(".cart_item")).to_contain_text("Sauce Labs Backpack")
    print("PASS: SauceDemo checkout overview")

    page.locator("#finish").click()
    expect(page.locator(".complete-header")).to_contain_text("Thank you for your order")
    print("PASS: SauceDemo checkout confirmation (demo only)")


def test_amazon_india_search_sort_product_and_cart_smoke(page: Page) -> None:
    """Live Amazon smoke test; never logs in or proceeds to checkout/payment."""
    page.goto("https://www.amazon.in/")

    search_box = page.locator("#twotabsearchtextbox")
    expect(search_box).to_be_visible(timeout=WAIT_MS)
    search_box.fill("wireless headphones")
    page.locator("#nav-search-submit-button").click()

    results = page.locator("[data-component-type='s-search-result']")
    try:
        expect(results.first).to_be_visible(timeout=WAIT_MS)
    except AssertionError:
        page.screenshot(path=str(ROOT / "amazon_search_debug.png"), full_page=True)
        body = (page.locator("body").inner_text() or "").lower()
        if any(term in body for term in ("captcha", "robot", "verify", "enter the characters")):
            pytest.skip("Amazon verification/CAPTCHA appeared; saved amazon_search_debug.png")
        pytest.fail("Amazon search results did not appear; saved amazon_search_debug.png")

    result_count = results.count()
    print(f"PASS: Amazon India product search ({result_count} result cards detected)")

    # Sorting is optional because Amazon's live markup/options can vary.
    try:
        sort_select = page.locator("#s-result-sort-select")
        if sort_select.count() and sort_select.is_visible():
            options = sort_select.locator("option").all()
            low_value = None
            for option in options:
                label = (option.inner_text() or "").strip()
                value = option.get_attribute("value")
                if "Price: Low to High" in label and value:
                    low_value = value
                    break
            if low_value:
                sort_select.select_option(value=low_value, timeout=5_000)
                expect(results.first).to_be_visible(timeout=WAIT_MS)
                print("PASS: Amazon sort by Price: Low to High")
            else:
                print("SKIP: Amazon low-to-high sort option unavailable")
        else:
            print("SKIP: Amazon sort dropdown unavailable")
    except Exception as exc:
        print(f"SKIP: Amazon sort could not be applied ({type(exc).__name__})")

    # Find a product card with both a meaningful title and a detail-page link.
    chosen_card = None
    product_title = ""
    product_price = ""
    cards = page.locator("[data-component-type='s-search-result']")
    for index in range(cards.count()):
        card = cards.nth(index)
        title_locators = [
            card.locator("h2 a span"),
            card.locator("h2 span"),
            card.locator("h2"),
        ]
        title = ""
        for locator in title_locators:
            if locator.count():
                try:
                    candidate = (locator.first.inner_text(timeout=2_000) or "").strip()
                except Exception:
                    candidate = ""
                if candidate and len(candidate) > 3:
                    title = candidate
                    break

        product_link = card.locator("a[href*='/dp/'], a[href*='/gp/']").first
        href = product_link.get_attribute("href") if product_link.count() else None
        if title and href:
            chosen_card = card
            product_title = title
            price_loc = card.locator(".a-price .a-offscreen, .a-price-whole").first
            if price_loc.count():
                try:
                    product_price = (price_loc.inner_text(timeout=2_000) or "").strip()
                except Exception:
                    product_price = ""
            break

    if chosen_card is None:
        page.screenshot(path=str(ROOT / "amazon_results_debug.png"), full_page=True)
        pytest.fail("Results appeared, but no product card with title/detail link was found. "
                    "Saved amazon_results_debug.png")

    print("PASS: Amazon result product title extracted:", product_title[:120])
    if product_price:
        print("PASS: Amazon result price extracted:", product_price)
    else:
        print("WARNING: Price not available in the selected result card")

    # Try the selected card first. Never click unrelated page buttons.
    add_button = chosen_card.get_by_role("button", name=re.compile("add to cart", re.I))
    if not add_button.count():
        add_button = chosen_card.locator(
            "input.s-add-to-cart-button, input[name='submit.add-to-cart'], "
            "input[name='submit.addToCart'], button[aria-label*='Add to cart' i], "
            "input[aria-label*='Add to cart' i], input[type='submit'][value*='Add to cart' i]"
        )
    if not add_button.count():
        print("SKIP: No Add to cart control in the selected live result card; not clicking another control")
        return

    try:
        add_button.first.scroll_into_view_if_needed(timeout=5_000)
        add_button.first.click(timeout=5_000)
        print("INFO: Add-to-cart action clicked; Amazon confirmation varies by page layout.")
    except Exception as exc:
        page.screenshot(path=str(ROOT / "amazon_cart_debug.png"), full_page=True)
        print(f"SKIP: Add-to-cart control could not be clicked ({type(exc).__name__}); "
              "saved amazon_cart_debug.png")
        return

    # Do not navigate to checkout or payment. Avoid deleting anything from a
    # potentially pre-existing cart; live-site cleanup is intentionally manual.
    print("INFO: Did not log in or proceed to checkout/payment.")
    print("INFO: If Amazon added the product, remove it from the cart manually if desired.")
