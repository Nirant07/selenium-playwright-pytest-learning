from pathlib import Path
import re

import pytest
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    expect,
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)

BASE_URL = "https://www.trivago.in/"
ARTIFACTS = Path(__file__).with_name("artifacts")
ARTIFACTS.mkdir(exist_ok=True)
WAIT_MS = 25_000


@pytest.fixture(scope="session")
def browser_context():
    """Keep one visible browser/context alive for the whole sequential test run."""
    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch(headless=False)
        context: BrowserContext = browser.new_context(
            viewport={"width": 1440, "height": 950},
            accept_downloads=True,
        )
        context.set_default_timeout(8_000)
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="session")
def page(browser_context: BrowserContext):
    """Reuse one page so later tests can continue from the search results."""
    page = browser_context.new_page()
    page.set_default_navigation_timeout(60_000)
    yield page
    page.close()


def save_screenshot(page: Page, name: str) -> None:
    path = ARTIFACTS / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    print(f"[ARTIFACT] Screenshot saved: {path}")


def body_text(page: Page) -> str:
    try:
        return page.locator("body").inner_text(timeout=10_000)
    except Exception:
        return ""


def destination_candidates(page: Page):
    selectors = [
        'input[placeholder*="Destination" i]',
        'input[aria-label*="Destination" i]',
        'input[placeholder*="Where" i]',
        'input[aria-label*="Where" i]',
        'input[placeholder*="city" i]',
        'input[aria-label*="city" i]',
        'input[role="combobox"]',
        '[data-testid*="destination"]',
        '[data-testid*="location"]',
        'button[aria-label*="destination" i]',
        '[role="button"][aria-label*="destination" i]',
    ]
    found = []
    for selector in selectors:
        locator = page.locator(selector)
        for index in range(locator.count()):
            item = locator.nth(index)
            try:
                if item.is_visible() and item.is_enabled():
                    found.append(item)
            except Exception:
                continue
    return found


def test_homepage_and_search_controls(page: Page) -> None:
    print("\n[STEP 1] Verify Trivago India homepage and search form")
    page.goto(BASE_URL, wait_until="domcontentloaded")
    expect(page.locator("body")).to_be_visible()
    assert "trivago.in" in page.url.lower()
    expect(page).to_have_title(re.compile("trivago", re.I), timeout=WAIT_MS)

    candidates = destination_candidates(page)
    if not candidates:
        save_screenshot(page, "destination_control_not_found")
        pytest.fail("Homepage loaded, but no destination control matched the current Trivago layout.")
    print(f"[PASS] Homepage loaded; found {len(candidates)} destination control candidate(s)")


def test_destination_autocomplete_and_search(page: Page) -> None:
    print("\n[STEP 2] Set destination to Bengaluru and submit search")
    if "trivago.in" not in page.url.lower():
        page.goto(BASE_URL, wait_until="domcontentloaded")

    candidates = destination_candidates(page)
    if not candidates:
        save_screenshot(page, "destination_input_not_found")
        pytest.fail("Destination input/control is missing.")

    try:
        candidates[0].scroll_into_view_if_needed()
        candidates[0].click()
    except Exception:
        candidates = destination_candidates(page)
        if not candidates:
            save_screenshot(page, "destination_not_editable")
            pytest.skip("Destination control changed after rerender.")
        candidates[0].click(force=True)

    candidates = destination_candidates(page)
    editable = next(
        (el for el in candidates if el.evaluate("(e) => e.tagName.toLowerCase() === 'input'")),
        None,
    )
    if editable is None:
        all_inputs = page.locator('input[type="text"], input[type="search"], input:not([type])')
        for i in range(all_inputs.count()):
            candidate = all_inputs.nth(i)
            try:
                if candidate.is_visible() and candidate.is_enabled():
                    editable = candidate
                    break
            except Exception:
                continue

    if editable is None:
        save_screenshot(page, "destination_not_editable")
        pytest.skip("Destination field is a non-editable trigger in this Trivago variant.")

    editable.fill("Bengaluru")

    suggestion_selectors = [
        '[role="option"]',
        '[role="listbox"] [role="option"]',
        'li[role="option"]',
        '[data-testid*="suggestion"]',
    ]
    selected = False
    try:
        page.wait_for_function(
            """selectors => selectors.some(s => [...document.querySelectorAll(s)].some(
                e => e.getClientRects().length &&
                /bengaluru|bangalore/i.test(e.innerText || e.textContent || '')
            ))""",
            arg=suggestion_selectors,
            timeout=8_000,
        )
        for selector in suggestion_selectors:
            options = page.locator(selector)
            for i in range(options.count()):
                option = options.nth(i)
                try:
                    label = option.inner_text(timeout=1_000).strip()
                    if option.is_visible() and re.search(r"bengaluru|bangalore", label, re.I):
                        option.click()
                        print(f"[INFO] Selected destination suggestion: {label[:100]}")
                        selected = True
                        break
                except Exception:
                    continue
            if selected:
                break
    except PlaywrightTimeoutError:
        print("[INFO] No matching autocomplete suggestion appeared; will try submitting the entered destination.")

    search_button = page.get_by_role("button", name=re.compile(r"^\s*search\s*$", re.I)).first
    if search_button.count() and search_button.is_visible() and search_button.is_enabled():
        search_button.click()
    else:
        # Re-query the destination input after any frontend rerender.
        candidates = destination_candidates(page)
        editable = next(
            (el for el in candidates if el.evaluate("(e) => e.tagName.toLowerCase() === 'input'")),
            None,
        )
        if editable is None:
            save_screenshot(page, "search_button_not_found")
            pytest.fail("Could not find a Search button or editable destination input.")
        editable.press("Enter")

    # Do not pass just because the URL changed. Wait for a result-specific signal.
    try:
        page.wait_for_function(
            """() => {
                const text = (document.body?.innerText || '').toLowerCase();
                const cards = document.querySelectorAll(
                    '[data-testid*="accommodation"], [data-testid*="item-name"], a[href*="/hotel/"]'
                );
                const resultWords = [
                    'hotels found', 'properties found', 'no results', 'no hotels',
                    'price range', 'guest rating', 'our recommendations', 'per night'
                ];
                return cards.length > 0 || resultWords.some(word => text.includes(word));
            }""",
            timeout=WAIT_MS,
        )
    except PlaywrightTimeoutError:
        save_screenshot(page, "search_results_not_detected")
        print(f"[DEBUG] URL after search: {page.url}")
        print(f"[DEBUG] Title after search: {page.title()}")
        print(f"[DEBUG] Body preview: {body_text(page)[:1200]}")
        pytest.fail("Search was submitted, but no hotel-results or empty-results signal appeared.")

    print(f"[PASS] Search reached a results state: {page.url}")
    print(f"[INFO] Page title: {page.title()}")


def test_results_have_properties_or_explain_no_results(page: Page) -> None:
    print("\n[STEP 3] Verify results state on the same page")
    expect(page.locator("body")).to_be_visible(timeout=WAIT_MS)
    body = body_text(page).lower()
    property_links = page.locator(
        'a[href*="/hotel/"], [data-testid*="item-name"], [data-testid*="accommodation"]'
    )
    link_count = property_links.count()
    empty_signals = ["no results", "no hotels", "no properties found"]
    positive_signals = [
        "hotels found", "properties found", "price range", "sort by",
        "guest rating", "our recommendations", "per night",
    ]
    empty_state = any(term in body for term in empty_signals)
    results_state = link_count > 0 or any(term in body for term in positive_signals)

    if not results_state and not empty_state:
        save_screenshot(page, "results_not_identified")
        print(f"[DEBUG] URL: {page.url}")
        print(f"[DEBUG] Title: {page.title()}")
        print(f"[DEBUG] Body preview: {body[:1500]}")
        pytest.fail("Could not verify hotel results or an explicit empty-results state.")
    print(f"[PASS] Results state verified; property-like links found: {link_count}")
    if empty_state and link_count == 0:
        print("[INFO] Trivago displayed an empty-results state.")


def test_filter_and_sort_controls_if_available(page: Page) -> None:
    print("\n[STEP 4] Inspect filter/sort controls")
    body = body_text(page).lower()
    controls = page.locator(
        'select, button[aria-haspopup="listbox"], [role="combobox"], button, [role="button"]'
    )
    terms = ["price", "rating", "sort", "filter", "recommendation", "distance"]
    matching = []
    for i in range(controls.count()):
        item = controls.nth(i)
        try:
            if not item.is_visible():
                continue
            label = (item.inner_text(timeout=1_000) or "").strip()
            if not label:
                label = item.get_attribute("aria-label") or ""
            if label and any(term in label.lower() for term in terms):
                matching.append(label)
        except Exception:
            continue

    if not matching and not any(term in body for term in terms):
        save_screenshot(page, "filter_sort_controls_not_found")
        pytest.skip("No identifiable filter/sort controls in this Trivago layout; screenshot saved.")
    print(f"[PASS] Filter/sort-related labels detected: {matching[:10] or ['labels found in page text']}")


def test_property_details_optional(page: Page) -> None:
    print("\n[STEP 5] Open a Trivago property page if a stable internal link exists")
    links = page.locator('a[href*="/hotel/"], a[data-testid*="item-name"]')
    chosen_href = None
    for i in range(links.count()):
        item = links.nth(i)
        try:
            href = item.get_attribute("href")
            if href and "trivago.in" in href.lower() and "/hotel/" in href.lower():
                chosen_href = href
                break
        except Exception:
            continue

    if not chosen_href:
        print("[SKIP] No stable internal property-detail link found; staying on results.")
        return

    page.goto(chosen_href, wait_until="domcontentloaded", timeout=60_000)
    expect(page.locator("body")).to_be_visible(timeout=WAIT_MS)
    assert page.title().strip()
    print(f"[PASS] Opened Trivago property page: {page.title()}")
    save_screenshot(page, "property_details")
