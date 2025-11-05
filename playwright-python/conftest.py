import pytest
from slugify import slugify 
import os
from pathlib import Path
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO, force=True)

# ===============================================================
# BROWSER CONFIGURATION FIXTURES
# ---------------------------------------------------------------
# browser_context_args:
# - Sets the viewport size for all Playwright test sessions.
# ---------------------------------------------------------------
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return { 
        **browser_context_args, 
        "viewport": { "width": 1280, "height": 800 }
        }

# browser_type_launch_args:
# - Defines browser launch options.
# - In CI (Continuous Integration) it runs headless and faster.
# - Locally, it runs with a delay for better debugging.
# ===============================================================
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    ci = os.getenv("CI", "false").lower() == "true"
    return {
        **browser_type_launch_args,
        "headless": True if ci else False,   
        "slow_mo": 0 if ci else 500,         
    }
# ===============================================================
# PYTEST TEST REPORTING HOOK
# ---------------------------------------------------------------
# pytest_runtest_makereport:
# - Tracks each test’s three phases (setup, call, teardown).
# - Saves the result object (rep) to the test item.
# - Allows detecting if a test failed in the “call” phase
#   inside a fixture.
# ===============================================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

# ===============================================================
# AUTOMATIC SCREENSHOT FIXTURE
# ---------------------------------------------------------------
# screenshot_on_failure:
# - Automatically runs for all tests (autouse=True).
# - Captures a screenshot if the test fails during the “call” phase.
# - Saves it under "reports/screenshots".
# - File name includes test ID + UTC timestamp.
# - Uses logging.info for console and CI visibility.
# ===============================================================
@pytest.fixture(autouse=True)
def screenshot_on_failure(request, page):
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        os.makedirs("reports/screenshots", exist_ok=True)
        name = slugify(request.node.nodeid, max_length=120)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        path = f"reports/screenshots/{name}-{ts}.png"
        try:
            page.screenshot(path=path, full_page=True)
            logging.info(f"[screenshot] saved: {path}")
        except Exception as e:
            logging.info(f"[screenshot] failed: {e}")

# ===============================================================
# MANUAL SCREENSHOT HELPER
# ---------------------------------------------------------------
# take_screenshot:
# - Allows you to capture screenshots manually during tests.
# - Appends a timestamp to create a unique filename.
# - Saves files under "reports/screenshots".
# - Uses logging.info for output (visible locally and in CI logs).
# ===============================================================
def take_screenshot(page, name="screenshot", folder="reports/screenshots", full_page=True):
    out = Path(folder)
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    path = out / f"{name}-{ts}.png"
    page.screenshot(path=str(path), full_page=full_page)
    logging.info(f"[screenshot] saved -> {path}")
    return str(path)


# ===============================================================
# TEST DATA
# ---------------------------------------------------------------
# Defines user credentials for all login scenarios:
# - correctUser: valid user
# - lockedUser: blocked account
# - wrongPass / emptyUsername / emptyPassword: negative cases
# - problemUser / visualUser / performanceUser / errorUser:
#   special test accounts with known issues
# ===============================================================
BASE_URL = "https://www.saucedemo.com/"

USERS = {
    "correctUser": {      
        "username": "standard_user",
        "password": "secret_sauce"
    },
    "lockedUser": {
        "username": "locked_out_user",
        "password": "secret_sauce"
    },
    "wrongPass": {
        "username": "standard_user",
        "password": "wrong_password"
    },
    "emptyUsername": {
        "username": "",
        "password": "secret_sauce"
    },
    "emptyPassword": {
        "username": "standard_user",
        "password": ""
    },
    "problemUser": {
        "username": "problem_user",
        "password": "secret_sauce"
    },
    "visualUser": {
        "username": "visual_user",
        "password": "secret_sauce"
    },
    "performanceUser": {
        "username": "performance_glitch_user",
        "password": "secret_sauce"
    },
    "errorUser": {
        "username": "error_user",
        "password": "secret_sauce"
    }
}

# ===============================================================
# FIXTURES FOR TEST DATA
# ---------------------------------------------------------------
# login_failure_users:
# - Returns a list of keys for negative login tests.
# base_url:
# - Returns the base URL for the test site.
# user_data:
# - Returns the complete user dictionary for use in tests.
# ===============================================================
@pytest.fixture
def login_failure_users():
    return [
        "lockedUser",
        "wrongPass",
        "emptyUsername",
        "emptyPassword"
    ]

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def user_data():
    return USERS

