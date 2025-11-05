import pytest
from playwright.sync_api import expect

@pytest.mark.order(1)
#User logs in with valid credentials and verifies login was successful.
def test_login_success(page, base_url, user_data):
    user = user_data["correctUser1"]
    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.locator("//input[@id='login-button']").click()
    page.get_by_text("Products").wait_for(timeout=5000)
    assert "/inventory.html" in page.url

@pytest.mark.order(2)
def test_login_failure(page, base_url, user_data, login_failure_users):
    for key in login_failure_users:
        user = user_data[key]
        page.goto(base_url)
        page.get_by_placeholder("Username").fill(user["username"])
        page.get_by_placeholder("Password").fill(user["password"])
        page.locator("//input[@id='login-button']").click()
        page.get_by_text("Epic sadface").wait_for(timeout=5000)
        error_banner = page.locator("[data-test='error']")
        expect(error_banner).to_be_visible(timeout=5000)
        expect(error_banner).to_contain_text("Epic sadface")
        assert "/inventory.html" not in page.url