import pytest

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return { 
        **browser_context_args, 
        "viewport": { "width": 1280, "height": 800 }
        }
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": False,  
        "slow_mo": 500,     
    }


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

