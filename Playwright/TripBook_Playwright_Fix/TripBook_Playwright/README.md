# TripBook — Trivago Playwright Suite (Shared Browser Fix)

## What changed

- Uses one visible Chromium browser, one context, and one page for the whole pytest session.
- Keeps the destination search page alive for the results, filter, and property-detail tests.
- Does not count a URL change alone as proof that hotel results loaded.
- Saves diagnostic screenshots and prints URL/title/body previews when results cannot be verified.
- Does not sign in, follow external booking links, reserve rooms, or make payments.

## Install (PowerShell)

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Run all tests in one browser session

```powershell
python -m pytest -v -s --headed test_trivago.py
```

Run a single test in isolation only if needed. The results/filter/property tests expect the shared page to have gone through the destination-search test first, so run the complete file for the intended end-to-end flow.

## Notes

Trivago is a live commercial website. Its layout, consent dialogs, experiments, and anti-automation measures can change. If a search doesn't produce a detectable results state, inspect the `artifacts/` screenshots and diagnostic output. The test suite's syntax was checked; live behavior has not been independently verified here.
