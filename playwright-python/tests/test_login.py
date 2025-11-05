import pytest
from playwright.sync_api import expect
import logging
from conftest import take_screenshot

logging.basicConfig(level=logging.INFO, force=True)

@pytest.mark.order(1)
#Pozitive Login Test
#User logs in with valid credentials and verifies login was successful.
def test_login_success(page, base_url, user_data):
    logging.info("Running test_login_success")
    user = user_data["correctUser"]
    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.locator("//input[@id='login-button']").click()
    page.get_by_text("Products").wait_for(timeout=5000)
    assert "/inventory.html" in page.url

@pytest.mark.order(2)
#Pozitive Problem Login Test
#User logs in with the username problem_user, but the product images are identical and there are issues with the Add to Cart buttons.
def test_login_problem(page, base_url, user_data):
    user = user_data["problemUser"]
    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.locator("//input[@id='login-button']").click()
    page.get_by_text("Products").wait_for(timeout=5000)
    assert "/inventory.html" in page.url, "Fail Login."

    names_locator = page.locator(".inventory_item_name")
    total_products = names_locator.count()
    assert total_products > 0, "empty."

    # Find Add to cart buttons and click them
    add_buttons = page.locator("button.btn_inventory")
    total_buttons = add_buttons.count()
    logging.info(f"Toplam {total_buttons} adet 'Add to cart' butonu bulundu.")
    assert total_buttons == total_products, "Add to cart buton sayisi ürün sayisiyla eşleşmiyor."
    take_screenshot(page, name="products_page_problem_user")

    # Just try to click each button, log if any issues
    for i in range(total_buttons):
        button = add_buttons.nth(i)
        try:
            if button.is_visible() and button.is_enabled():
                button.click()
                logging.info(f"{i+1}. product added.")
            else:
                logging.info(f"{i+1}. product button inactive")
        except Exception as e:
            logging.info(f"{i+1}. product dont click: {e}")

    # Verify the number in the cart.
    cart_badge = page.locator(".shopping_cart_badge")
    if cart_badge.is_visible():
        cart_count = int(cart_badge.inner_text().strip())
        logging.info(f"There are {cart_count} items in the cart")
        assert cart_count > 0, "The cart should not be empty."
    else:
        logging.info("Cart badge is not visible — probably no items were added.")

@pytest.mark.order(3)
#Pozitive Login Performance Test
#When the user attempts to log in with the username performance_glitch_user, the products page loads slowly.
def test_login_performance_success(page, base_url, user_data):
    user = user_data["performanceUser"]
    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.locator("//input[@id='login-button']").click()
    page.get_by_text("Products").wait_for(timeout=15000)
    assert "/inventory.html" in page.url       

@pytest.mark.order(4)
#Pozitive Login Test
#The user logs in successfully with the username visual_user, but the elements are positioned differently.
def test_login_visual_success(page, base_url, user_data):
    logging.info("Running test_login_success")
    user = user_data["visualUser"]
    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.locator("//input[@id='login-button']").click()
    page.get_by_text("Products").wait_for(timeout=5000)
    take_screenshot(page, name="visual_user_login")
    assert "/inventory.html" in page.url     

#Negative Login Tests
#User attempt to log in with various invalid credentials and verify appropriate error messages are displayed.       
@pytest.mark.order(5)
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
        take_screenshot(page, name="fail")


