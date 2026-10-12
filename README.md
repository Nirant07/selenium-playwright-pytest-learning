# Selenium, Playwright & Pytest — Learning Repository

A hands-on learning repository exploring Python-based web automation using **Selenium WebDriver, Playwright, and Pytest**. This repository contains four practical applications built to understand browser automation, test execution, and the differences between Selenium and Playwright.

## About This Repository

The objective of this repository is to document my practical learning of web automation and automated testing through two project ideas, each implemented using Selenium and Playwright.

- **Selenium:** Browser automation using Selenium WebDriver.
- **Playwright:** Browser automation using Playwright for Python.
- **Pytest:** Test discovery, execution, fixtures, assertions, and test reporting.

## Projects

### 1. E-commerce Website Automation

Automated testing scenarios covering product discovery and shopping workflows.

**Test scenarios include:**
- Product search on a local demo store.
- Category and price filtering.
- Add-to-cart interactions.
- Login, cart, and checkout workflows using SauceDemo.
- Product search and sorting on Amazon India.
- Selected product-page and shopping-cart interactions.

**Technologies:** Python, Selenium / Playwright, Pytest (Playwright implementation).

### 2. Hotel Search Automation — Trivago

Browser automation focused on hotel discovery and search functionality.

**Test scenarios include:**
- Homepage and search controls.
- Destination autocomplete and selection.
- Hotel search and results validation.
- Exploration of filters and sorting controls.
- Optional property-detail checks.

**Technologies:** Python, Selenium / Playwright, Pytest.

## Technologies and Tools

| Technology | Purpose |
|---|---|
| Python | Writing automation scripts and test cases |
| Selenium WebDriver | Browser automation and interaction |
| Playwright | Browser automation, locators, and waiting mechanisms |
| Pytest | Test discovery, execution, fixtures, assertions, and reporting |
| HTML | Local demo website used for testing |

## What I Learned

### Selenium
- Automating browser interactions using WebDriver.
- Locating and interacting with web elements.
- Handling search, filtering, sorting, and shopping workflows.
- Understanding browser setup and test execution.

### Playwright
- Using Playwright's Python API for browser automation.
- Working with locators and browser interactions.
- Using automatic waiting and assertions.
- Running browser tests in headed mode for debugging.
- Handling dynamic website behavior and validating search results.

### Pytest
- Writing test functions and following test naming conventions.
- Running tests using the Pytest command-line interface.
- Using fixtures to manage browser and page setup.
- Applying assertions to validate expected behavior.
- Reading test reports and investigating failures.
- Understanding the relationship between Pytest and browser automation frameworks.

### Framework Comparison
- Comparing Selenium WebDriver and Playwright.
- Understanding different approaches to browser management, locators, waiting, and assertions.
- Exploring how Pytest can organize and execute tests written with either framework.

## Running the Tests

Each project contains its own `requirements.txt` and README with setup instructions.

A typical setup for a Python project is:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project's dependencies:

```bash
python -m pip install -r requirements.txt
```

For Pytest-based projects, run:

```bash
python -m pytest -v -s
```

For Playwright projects, install the required browser binaries if prompted:

```bash
python -m playwright install chromium
```

Refer to each project's README for its specific execution command and requirements.

## Important Notes

- Live website tests may be affected by changes to website layouts, consent dialogs, network conditions, and anti-automation protections.
- A failed live test does not necessarily indicate a problem with the automation framework itself; investigate the failure and the website's current behavior.
- Amazon India and Trivago tests are intended for learning and authorized testing.
- These projects do not perform real purchases, payments, or hotel reservations.
- Test results may vary depending on browser versions and website behavior.

## Repository Structure

```text
selenium-playwright-pytest-learning/
├── Playwright/
│   ├── Ecommerce_Playwright/
│   │   └── Ecommerce_Playwright/
│   └── TripBook_Playwright_Fix/
│       └── TripBook_Playwright/
├── selenium/
│   ├── Selenium E-commerce Automation Suite/
│   └── Selenium Hotel Booking Automation/
└── README.md
```

## Objective

This repository serves as a practical record of my learning journey in Python-based browser automation, test automation fundamentals, and framework comparison using Selenium, Playwright, and Pytest.

The projects are intended to reinforce concepts through implementation, debugging, and iterative improvements.
