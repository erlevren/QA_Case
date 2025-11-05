import pytest
from slugify import slugify 
import os
from datetime import datetime

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return { 
        **browser_context_args, 
        "viewport": { "width": 1280, "height": 800 }
        }

"""
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": False,  
        "slow_mo": 500,     
    }
"""
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
        ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        path = f"reports/screenshots/{name}-{ts}.png"
        try:
            page.screenshot(path=path, full_page=True)
            print(f"[screenshot] saved: {path}")
        except Exception as e:
            print(f"[screenshot] failed: {e}")



# Test Data

BASE_URL = "https://www.saucedemo.com/"

USERS = {
    "correctUser1": {      
        "username": "standard_user",
        "password": "secret_sauce"
    },
    "lockedUser1": {
        "username": "locked_out_user",
        "password": "secret_sauce"
    },
    "wrongPass1": {
        "username": "standard_user",
        "password": "wrong_password"
    },
    "emptyUsername1": {
        "username": "",
        "password": "secret_sauce"
    },
    "emptyPassword1": {
        "username": "standard_user",
        "password": ""
    },
    "problemUser1": {
        "username": "problem_user",
        "password": "secret_sauce"
    },
    "visualUser1": {
        "username": "visual_user",
        "password": "secret_sauce"
    },
    "performanceUser1": {
        "username": "performance_glitch_user",
        "password": "secret_sauce"
    },
    "errorUser1": {
        "username": "error_user",
        "password": "secret_sauce"
    }
}
@pytest.fixture
def login_failure_users():
    return [
        "lockedUser1",
        "wrongPass1",
        "emptyUsername1",
        "emptyPassword1"
    ]

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def user_data():
    return USERS

