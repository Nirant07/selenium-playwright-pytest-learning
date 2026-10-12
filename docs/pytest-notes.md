# Pytest Fundamentals

## 1. What Is Pytest?

Pytest is a Python testing framework used to discover, organize, execute, and report test cases. It can be used with browser automation frameworks such as Selenium and Playwright.

**Key distinction:**
- Selenium and Playwright automate browser interactions.
- Pytest organizes and runs automated tests.

## 2. Writing Test Cases

Pytest typically discovers test files named `test_*.py` or `*_test.py`, and test functions named `test_*`.

```python
def test_addition():
    assert 2 + 3 == 5
```

The `assert` statement checks whether the expected condition is true. If it fails, Pytest reports the test as failed.

## 3. Running Tests

Run all discoverable tests from the current directory:

```bash
python -m pytest
```

Show individual test results:

```bash
python -m pytest -v
```

Show print statements and other captured output:

```bash
python -m pytest -v -s
```

Run a specific test file:

```bash
python -m pytest -v test_example.py
```

## 4. Fixtures

Fixtures provide reusable setup and cleanup for tests. They are commonly used for browser initialization, test data, and other shared resources.

```python
import pytest

@pytest.fixture
def sample_data():
    return {"username": "test_user"}

def test_username(sample_data):
    assert sample_data["username"] == "test_user"
```

Fixture scope controls how often a fixture is created. Common scopes include `function`, `class`, `module`, and `session`.

## 5. Pytest with Selenium and Playwright

Pytest can execute test functions written using either framework.

A Selenium test may create a WebDriver instance, interact with a website, verify the result, and close the browser.

A Playwright test may use a `page` fixture, interact with the website, verify the result using assertions, and rely on fixture teardown for cleanup.

The exact setup depends on the project and the fixtures being used.

## 6. Common Outcomes

- **PASSED:** The test completed and its assertions succeeded.
- **FAILED:** An assertion or another test operation failed.
- **SKIPPED:** The test was intentionally not executed.
- **ERROR:** Test setup, teardown, or another testing operation encountered an error.

## 7. Key Learnings

- Test naming conventions enable automatic test discovery.
- Assertions validate expected behavior.
- Fixtures help manage reusable setup and cleanup.
- Command-line options control test execution and output.
- Failure reports help identify problems in test logic, setup, or website behavior.
