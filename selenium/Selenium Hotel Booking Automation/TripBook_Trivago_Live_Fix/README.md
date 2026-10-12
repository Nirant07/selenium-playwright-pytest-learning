# TripBook — Trivago India Selenium Suite (Fix)

Target: https://www.trivago.in/

## Fixes
- One visible Chrome window for the entire Pytest session.
- Destination locator prioritizes destination-specific inputs instead of accidentally selecting the date field.
- Avoids reading `.text` from an autocomplete element after clicking it, which caused the `StaleElementReferenceException`.
- Re-finds dynamic elements after Trivago rerenders the search form.
- Saves screenshots under `artifacts/` when a control cannot be found.

## Run
```powershell
python -m pip install -r requirements.txt
python -m pytest -v -s trivago_live_tests.py
```

The tests are for browsing/searching and optional internal property details only. They do not sign in, follow external booking links, or submit reservations/payments.

This is a live commercial site. Layout changes, consent prompts, and A/B tests can still require locator updates. Syntax has been checked; run the suite locally to verify current live behavior.
