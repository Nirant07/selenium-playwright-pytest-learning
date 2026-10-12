# Selenium vs Playwright

## 1. Overview

Selenium and Playwright are browser automation frameworks that can be used with Python to test web applications. Both support browser interactions and validation of website behavior, but they differ in their APIs and automation approaches.

## 2. Comparison

| Feature | Selenium | Playwright |
|---|---|---|
| Browser automation | Selenium WebDriver | Playwright browser APIs |
| Python support | Yes | Yes |
| Element location | Locators such as ID, CSS selectors, and XPath | Locators such as role, text, CSS selectors, and XPath |
| Waiting | Explicit and implicit waits are available | Auto-waiting for supported actions and assertions |
| Browser management | WebDriver setup and lifecycle management | Browser, context, and page APIs |
| Test execution | Can be used with Pytest or a custom Python runner | Can be used with Pytest or other supported test-running approaches |
| Assertions | Python assertions or testing-framework assertions | Python assertions or Playwright's `expect()` assertions |
| Debugging | Browser inspection, logs, and debugging tools | Inspector, headed mode, traces, and other debugging tools |

## 3. Understanding Pytest

Pytest is not a replacement for Selenium or Playwright. It is a test framework that can run tests written with either browser automation framework.

For example:

- Selenium + Pytest: browser automation using Selenium, with Pytest managing test discovery and execution.
- Playwright + Pytest: browser automation using Playwright, with Pytest managing test discovery and execution.
- Selenium with a custom Python runner: browser automation where the application controls how test functions are called.

## 4. Important Concepts

### Locators

Locators identify elements on a web page, such as search fields, buttons, and product cards.

### Waiting

Web pages often load content dynamically. Automation scripts must wait for the relevant elements or states before interacting with them.

### Assertions

Assertions validate expected behavior, such as whether a destination was selected or a product appears in search results.

### Browser Lifecycle

Browser setup, page creation, and cleanup should be handled consistently. Pytest fixtures can help manage this lifecycle.

## 5. Practical Learning Through Projects

This repository explores two application ideas implemented with Selenium and Playwright:

1. **E-commerce automation:** product search, filtering, sorting, cart interactions, and selected checkout workflows.
2. **Hotel search automation:** destination autocomplete, search, results validation, and exploration of available controls.

These implementations provide a practical basis for comparing browser automation approaches.

## 6. Key Takeaways

- Selenium and Playwright both support Python browser automation.
- Playwright provides built-in auto-waiting for supported operations.
- Selenium offers explicit and implicit waiting mechanisms.
- Pytest can organize and execute tests written with either framework.
- Reliable automation requires meaningful assertions, appropriate waits, maintainable locators, and clear failure reporting.

The most suitable framework depends on the project's requirements, existing infrastructure, browser needs, and team preferences.
