import pytest
from slugify import slugify 
import os
from pathlib import Path
from datetime import datetime, timezone

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return { 
        **browser_context_args, 
        "viewport": { "width": 1280, "height": 800 }
        }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    ci = os.getenv("CI", "false").lower() == "true"
    return {
        **browser_type_launch_args,
        "headless": True if ci else False,   # CI'da headless
        "slow_mo": 0 if ci else 500,         # CI'da hızlan
    }

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    # her faz için rapor objesi oluştur
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(autouse=True)
def screenshot_on_failure(request, page):
    yield
    # test "call" aşamasında fail olduysa ekran görüntüsü al
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        os.makedirs("reports/screenshots", exist_ok=True)
        name = slugify(request.node.nodeid, max_length=120)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        path = f"reports/screenshots/{name}-{ts}.png"
        try:
            page.screenshot(path=path, full_page=True)
            print(f"[screenshot] saved: {path}")
        except Exception as e:
            print(f"[screenshot] failed: {e}")

def take_screenshot(page, name="screenshot", folder="reports/screenshots", full_page=True):
    """Basit ekran görüntüsü helper'ı. Test içinde direkt çağır."""
    out = Path(folder)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{name}.png"
    page.screenshot(path=str(path), full_page=full_page)
    print(f"[screenshot] saved -> {path}")
    return str(path)


# Test Data

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

