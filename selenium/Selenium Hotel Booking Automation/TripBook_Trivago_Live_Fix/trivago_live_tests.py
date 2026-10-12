"""
TripBook - trivago.in live-site Selenium tests.
One visible Chrome session is reused for the whole pytest run.
Tests cover homepage, destination interaction, results, and visible filters.
No login, external booking, reservation, or payment is attempted.

Run:
    python -m pytest -v -s trivago_live_tests.py
"""
from pathlib import Path
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

BASE_URL = "https://www.trivago.in/"
ARTIFACTS = Path(__file__).with_name("artifacts")
ARTIFACTS.mkdir(exist_ok=True)

@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    options.add_argument("--disable-save-password-bubble")
    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(60)
    browser.get(BASE_URL)
    WebDriverWait(browser, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print(f"\n[BROWSER] One visible Chrome session started: {browser.current_url}")
    print(f"[BROWSER] Title: {browser.title}")
    yield browser
    browser.quit()

def save_screenshot(driver, name):
    path = ARTIFACTS / f"{name}.png"
    driver.save_screenshot(str(path))
    print(f"[ARTIFACT] Screenshot saved: {path}")

def body_text(driver):
    return driver.find_element(By.TAG_NAME, "body").text

def visible_elements(driver, selectors):
    result = []
    for selector in selectors:
        try:
            result.extend(driver.find_elements(By.CSS_SELECTOR, selector))
        except Exception:
            pass
    # de-duplicate by element id and only return elements that are still attached/visible
    unique, seen = [], set()
    for el in result:
        try:
            key = el.id
            if key not in seen and el.is_displayed() and el.is_enabled():
                unique.append(el)
                seen.add(key)
        except StaleElementReferenceException:
            continue
    return unique

def destination_candidates(driver):
    # Prefer destination-specific accessible names/placeholders; avoid selecting the date input.
    candidates = visible_elements(driver, [
        'input[placeholder*="Destination" i]',
        'input[aria-label*="Destination" i]',
        'input[placeholder*="Where" i]',
        'input[aria-label*="Where" i]',
        'input[placeholder*="city" i]',
        'input[aria-label*="city" i]',
        'input[role="combobox"]',
    ])
    if candidates:
        return candidates
    # Trivago has used a non-input destination trigger in some variants.
    return visible_elements(driver, [
        '[data-testid*="destination"]',
        '[data-testid*="location"]',
        'button[aria-label*="destination" i]',
        '[role="button"][aria-label*="destination" i]',
    ])

def test_homepage_and_search_controls(driver):
    print("\n[STEP 1] Verify trivago India homepage and search form")
    WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    assert "trivago.in" in driver.current_url.lower()
    assert "trivago" in driver.title.lower()
    candidates = destination_candidates(driver)
    if not candidates:
        save_screenshot(driver, "destination_control_not_found")
        pytest.fail("Homepage loaded, but no destination control matched the current Trivago layout.")
    print(f"[PASS] Homepage loaded; found {len(candidates)} destination control candidate(s)")

def test_destination_autocomplete_and_search(driver):
    print("\n[STEP 2] Set destination to Bengaluru and submit search")
    wait = WebDriverWait(driver, 20)
    candidates = destination_candidates(driver)
    if not candidates:
        save_screenshot(driver, "destination_input_not_found")
        pytest.fail("Destination input/control is missing.")
    destination = candidates[0]
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", destination)
    try:
        destination.click()
    except Exception:
        driver.execute_script("arguments[0].click();", destination)

    # Re-locate after click because Trivago rerenders the autocomplete control.
    current_inputs = destination_candidates(driver)
    editable = next((e for e in current_inputs if e.tag_name.lower() == "input"), None)
    if editable is None:
        # If the destination is a trigger, try clicking the text/button then re-locate inputs.
        all_inputs = visible_elements(driver, ['input[type="text"]', 'input[type="search"]', 'input:not([type])'])
        editable = next((e for e in all_inputs if "date" not in (e.get_attribute("type") or "").lower()), None)
    if editable is None:
        save_screenshot(driver, "destination_not_editable")
        pytest.skip("Destination field is a non-editable trigger in this Trivago variant.")
    try:
        editable.send_keys(Keys.CONTROL, "a")
        editable.send_keys("Bengaluru")
    except StaleElementReferenceException:
        editable = destination_candidates(driver)[0]
        editable.send_keys(Keys.CONTROL, "a")
        editable.send_keys("Bengaluru")

    # Select an autocomplete option if it is present. Never read .text from a stale element.
    suggestion_selectors = ['[role="option"]', '[role="listbox"] [role="option"]',
                            'li[role="option"]', '[data-testid*="suggestion"]']
    selected_text = ""
    try:
        def find_suggestion(d):
            for el in visible_elements(d, suggestion_selectors):
                try:
                    txt = el.text.strip()
                    if "bengaluru" in txt.lower() or "bangalore" in txt.lower():
                        return (el, txt)
                except StaleElementReferenceException:
                    continue
            return False
        suggestion, selected_text = wait.until(find_suggestion)
        # Use saved text before click; clicking often rerenders/removes the suggestion.
        suggestion.click()
        print(f"[INFO] Selected destination suggestion: {selected_text[:100]}")
    except TimeoutException:
        print("[INFO] No Bengaluru autocomplete suggestion was identified.")

    # Search button is re-located just before click to avoid stale references.
    search_buttons = [e for e in driver.find_elements(By.XPATH,
        "//button[normalize-space()='Search' or .//*[normalize-space()='Search']]"
    ) if e.is_displayed() and e.is_enabled()]
    if search_buttons:
        search_buttons[0].click()
    else:
        current_inputs = destination_candidates(driver)
        editable = next((e for e in current_inputs if e.tag_name.lower() == "input"), None)
        if editable:
            editable.send_keys(Keys.ENTER)
        else:
            save_screenshot(driver, "search_button_not_found")
            pytest.fail("Could not find a visible Search button or editable destination field.")

    try:
        wait.until(lambda d: d.current_url != BASE_URL or any(
            term in body_text(d).lower()
            for term in ["hotels found", "hotel results", "sort by", "price range", "guest rating"]
        ))
    except TimeoutException:
        save_screenshot(driver, "search_results_not_detected")
        pytest.fail("Search was submitted, but a results state was not detected.")
    print(f"[PASS] Search reached a results state: {driver.current_url}")
    print(f"[INFO] Page title: {driver.title}")

def test_results_have_properties_or_explain_no_results(driver):
    print("\n[STEP 3] Verify results state")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    body = body_text(driver).lower()
    property_links = visible_elements(driver, [
        'a[href*="/hotel/"]',
        '[data-testid*="item-name"]',
        '[data-testid*="accommodation"]',
    ])
    meaningful_state = any(term in body for term in [
        "hotels found", "properties found", "no results", "no hotels",
        "price range", "sort by", "guest rating", "our recommendations",
        "per night", "book"
    ])
    if not property_links and not meaningful_state:
        save_screenshot(driver, "results_not_identified")
        pytest.fail("Could not verify property results or an empty-results state.")
    print(f"[PASS] Results state verified; property-like links found: {len(property_links)}")

def test_filter_and_sort_controls_if_available(driver):
    print("\n[STEP 4] Inspect filter/sort controls")
    body = body_text(driver).lower()
    controls = visible_elements(driver, [
        'select', 'button[aria-haspopup="listbox"]', '[role="combobox"]',
        'button', '[role="button"]'
    ])
    terms = ["price", "rating", "sort", "filter", "recommendation", "distance"]
    matching = []
    for el in controls:
        try:
            text = el.text.strip()
            aria = (el.get_attribute("aria-label") or "")
            label = text or aria
            if label and any(term in label.lower() for term in terms):
                matching.append(label)
        except StaleElementReferenceException:
            continue
    if not matching and not any(term in body for term in terms):
        save_screenshot(driver, "filter_sort_controls_not_found")
        pytest.skip("No identifiable filter/sort controls in this layout; screenshot saved.")
    print(f"[PASS] Filter/sort-related labels detected: {matching[:10] or ['labels found in page text']}")

def test_property_details_optional(driver):
    print("\n[STEP 5] Open a Trivago property page if a stable link exists")
    links = visible_elements(driver, ['a[href*="/hotel/"]', 'a[data-testid*="item-name"]'])
    if not links:
        print("[SKIP] No stable property-detail link found; staying on results.")
        return
    href = links[0].get_attribute("href")
    if not href or "trivago.in" not in href.lower():
        print("[SKIP] No internal Trivago property link; not following external booking links.")
        return
    driver.get(href)
    WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
    assert driver.title.strip()
    print(f"[PASS] Opened Trivago property page: {driver.title}")
    save_screenshot(driver, "property_details")
