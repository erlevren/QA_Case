import pytest
from playwright.sync_api import expect
import logging
from conftest import take_screenshot

logging.basicConfig(level=logging.INFO, force=True)

# ===============================================================
# TEST 1️⃣ – Positive Login Test
# ---------------------------------------------------------------
# Purpose:
# - Verify that a valid user can successfully log in.
# - Ensure the page redirects to the product listing page.
# Expected Result:
# - URL should contain "/inventory.html"
# - "Products" text should be visible.
# - Verify that the page header contains "Swag Labs"
# ===============================================================
@pytest.mark.order(1)
def test_login_success(page, base_url, user_data):
    logging.info("Running test_login_success")
    user = user_data["correctUser"]
    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.locator("//input[@id='login-button']").click()
    page.get_by_text("Products").wait_for(timeout=5000)
    assert "/inventory.html" in page.url
    take_screenshot(page, name="login_success")
    header_text = page.locator("div.app_logo")
    expect(header_text).to_contain_text("Swag Labs")
    logging.info("Verified that the page header contains 'Swag Labs'.")


# ===============================================================
# TEST 2️⃣ – Problem User Scenario (Known UI & Checkout Bugs)
# ---------------------------------------------------------------
# Purpose:
# - Test login with "problem_user" and verify known UI inconsistencies.
# - Ensure product list loads and Add to Cart buttons are functional.
# - Reproduce checkout form corruption bug specific to this user.
# Expected Bugs:
# - Product images are identical.
# - Add-to-Cart buttons behave inconsistently.
# - Typing a single char into “Last Name” corrupts “First Name” field.
# ===============================================================
@pytest.mark.order(2)
def test_login_problem(page, base_url, user_data):
    logging.info("Running test_login_problemUser")
    user = user_data["problemUser"]

    # -----------------------------------------------------------
    # 1️⃣ LOGIN AND VERIFY HEADER
    # -----------------------------------------------------------
    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.locator("//input[@id='login-button']").click()
    page.get_by_text("Products").wait_for(timeout=5000)
    assert "/inventory.html" in page.url, "Fail Login."

    # Verify “Swag Labs” header text
    header_text = page.locator("div.app_logo")
    expect(header_text).to_contain_text("Swag Labs")
    logging.info("Verified that the page header contains 'Swag Labs'.")

    # -----------------------------------------------------------
    # 2️⃣ VERIFY PRODUCT LIST
    # -----------------------------------------------------------
    names_locator = page.locator(".inventory_item_name")
    total_products = names_locator.count()
    assert total_products > 0, "No products found."

    # -----------------------------------------------------------
    # 3️⃣ ADD TO CART FUNCTIONALITY
    # -----------------------------------------------------------
    add_buttons = page.locator("button.btn_inventory")
    total_buttons = add_buttons.count()
    logging.info(f"{total_buttons} 'Add to cart' buttons found.")
    assert total_buttons == total_products, "Add-to-Cart button count mismatch."
    take_screenshot(page, name="products_page_problem_user")

    for i in range(total_buttons):
        button = add_buttons.nth(i)
        try:
            if button.is_visible() and button.is_enabled():
                button.click()
                logging.info(f"{i+1}. product added.")
            else:
                logging.info(f"{i+1}. product button inactive.")
        except Exception as e:
            logging.info(f"{i+1}. product could not be clicked: {e}")

    # -----------------------------------------------------------
    # 4️⃣ VERIFY THE NUMBER IN THE CART
    # -----------------------------------------------------------
    cart_badge = page.locator(".shopping_cart_badge")
    if cart_badge.is_visible():
        cart_count = int(cart_badge.inner_text().strip())
        logging.info(f"There are {cart_count} items in the cart.")
        assert cart_count > 0, "The cart should not be empty."
    else:
        logging.info("Cart badge is not visible — probably no items were added.")

    # -----------------------------------------------------------
    # 5️⃣ PROCEED TO CHECKOUT
    # -----------------------------------------------------------
    page.locator(".shopping_cart_link").click()
    page.locator("#checkout").click()
    expect(page.get_by_text("Checkout: Your Information")).to_be_visible(timeout=5000)

    # -----------------------------------------------------------
    # 6️⃣ REPRODUCE CHECKOUT FORM BUG
    # -----------------------------------------------------------
    first = page.get_by_placeholder("First Name")
    last = page.get_by_placeholder("Last Name")
    zipc = page.get_by_placeholder("Zip/Postal Code")

    # Fill First Name successfully
    first.fill("John")

    # Fill one character in Last Name (should corrupt First Name)
    last_char = "X"
    last.fill(last_char)

    # Validate corrupted behavior
    first_val = first.input_value()
    last_val = last.input_value()
    assert first_val == last_char, (
        f"Bug not reproduced: expected First Name to be overwritten by '{last_char}', got '{first_val}'"
    )
    assert last_val in ("", last_char), f"Unexpected Last Name value: '{last_val}'"

    # Fill Zip Code and click Continue
    zipc.fill("12345")
    page.get_by_role("button", name="Continue").click()

    # -----------------------------------------------------------
    # 7️⃣ VERIFY EXPECTED ERROR MESSAGE
    # -----------------------------------------------------------
    error_banner = page.locator("[data-test='error']")
    expect(error_banner).to_be_visible(timeout=5000)
    expect(error_banner).to_have_text("Error: Last Name is required")
    logging.info("Error banner appeared as expected for corrupted checkout form.")

    # -----------------------------------------------------------
    # 8️⃣ CAPTURE FINAL SCREENSHOT
    # -----------------------------------------------------------
    take_screenshot(page, name="problem_user_checkout_error")
    logging.info("Screenshot captured for corrupted checkout state.")



# ===============================================================
# TEST 3️⃣ – Error User Scenario
# ---------------------------------------------------------------
# Purpose:
# - Verify that the page header contains "Swag Labs"
# - Validate checkout flow with “error_user”.
# - Known behavior: Checkout button visible but not clickable.
# Expected Bugs:
# - “Last Name” field not fillable.
# - “Finish” button is visible but cannot be clicked.
# ===============================================================
@pytest.mark.order(3)
def test_login_errorUser(page, base_url, user_data):
    user = user_data["errorUser"]
    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.locator("//input[@id='login-button']").click()
    page.get_by_text("Products").wait_for(timeout=5000)
    assert "/inventory.html" in page.url, "Fail Login."
    header_text = page.locator("div.app_logo")
    expect(header_text).to_contain_text("Swag Labs")
    logging.info("Verified that the page header contains 'Swag Labs'.")

    names_locator = page.locator(".inventory_item_name")
    total_products = names_locator.count()
    assert total_products > 0, "No products found."

    add_buttons = page.locator("button.btn_inventory")
    total_buttons = add_buttons.count()
    logging.info(f"{total_buttons} 'Add to cart' buttons found.")
    take_screenshot(page, name="error_user_products_page")

    for i in range(total_buttons):
        button = add_buttons.nth(i)
        try:
            if button.is_visible() and button.is_enabled():
                button.click()
                logging.info(f"{i+1}. product added.")
            else:
                logging.info(f"{i+1}. product button inactive.")
        except Exception as e:
            logging.info(f"{i+1}. product could not be clicked: {e}")

    # Proceed to checkout
    page.locator(".shopping_cart_link").click()
    page.locator("#checkout").click()
    expect(page.get_by_text("Checkout: Your Information")).to_be_visible(timeout=5000)

    # Known issue: Last Name cannot be filled
    page.get_by_placeholder("First Name").fill("John")
    try:
        page.get_by_placeholder("Last Name").fill("Doe")
        logging.warning("Unexpected: Last Name field accepted input.")
    except Exception:
        logging.info("Expected: Last Name field cannot be filled (bug confirmed).")

    # Continue checkout
    page.get_by_placeholder("Zip/Postal Code").fill("12345")
    page.get_by_role("button", name="Continue").click()

    finish_button = page.locator("#finish")
    expect(finish_button).to_be_visible(timeout=5000)
    try:
        finish_button.click()
        logging.warning("Unexpected: Finish button clicked successfully — should not be clickable.")
    except Exception:
        logging.info("Expected: Finish button is visible but cannot be clicked (bug confirmed).")

    take_screenshot(page, name="error_user_checkout_issue")


# ===============================================================
# TEST 4️⃣ – Performance Glitch User
# ---------------------------------------------------------------
# Purpose:
# - Verify that the user “performance_glitch_user” can log in.
# - Measure and tolerate delayed page loading (~15s).
# Expected Behavior:
# - Login succeeds but “Products” page takes longer to load.
# - Verify that the page header contains "Swag Labs"
# ===============================================================
@pytest.mark.order(4)
def test_login_performance_success(page, base_url, user_data):
    user = user_data["performanceUser"]
    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.locator("//input[@id='login-button']").click()
    page.get_by_text("Products").wait_for(timeout=15000)
    assert "/inventory.html" in page.url
    header_text = page.locator("div.app_logo")
    expect(header_text).to_contain_text("Swag Labs")
    logging.info("Verified that the page header contains 'Swag Labs'.")
    take_screenshot(page, name="performance_user_login")


# ===============================================================
# TEST 5️⃣ – Visual User Layout Check
# ---------------------------------------------------------------
# Purpose:
# - Confirm that “visual_user” logs in successfully.
# - Verify that the page header contains "Swag Labs"
# - Detect potential UI layout differences (element misplacement).
# Expected Result:
# - Login successful; elements appear differently than normal users.
# ===============================================================
@pytest.mark.order(5)
def test_login_visual_success(page, base_url, user_data):
    logging.info("Running test_login_visual_success")
    user = user_data["visualUser"]
    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.locator("//input[@id='login-button']").click()
    page.get_by_text("Products").wait_for(timeout=5000)
    header_text = page.locator("div.app_logo")
    expect(header_text).to_contain_text("Swag Labs")
    logging.info("Verified that the page header contains 'Swag Labs'.")
    take_screenshot(page, name="visual_user_login")
    assert "/inventory.html" in page.url


# ===============================================================
# TEST 6️⃣ – Negative Login Scenarios
# ---------------------------------------------------------------
# Purpose:
# - Validate login behavior with various invalid credentials.
# - Check that error messages appear correctly.
# Expected Result:
# - “Epic sadface” error message should be visible.
# - User should NOT be redirected to inventory page.
# ===============================================================
@pytest.mark.order(6)
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
        take_screenshot(page, name=f"login_failure_{key}")
