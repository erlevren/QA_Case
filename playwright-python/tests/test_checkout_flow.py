import pytest
import logging
from playwright.sync_api import expect
from conftest import take_screenshot

# ===============================================================
# TEST: Positive Full Flow (Successful Shopping Scenario)
# ---------------------------------------------------------------
# Purpose:
# - Verify successful login, product visibility, cart operations,
#   and that the cart can be emptied again.
# ===============================================================
@pytest.mark.order(8)
def test_positive_full_flow(page, base_url, user_data):
    logging.info("=== Starting Positive Full Flow Test ===")

    # -----------------------------------------------------------
    # 1️⃣ LOGIN STAGE
    # -----------------------------------------------------------
    user = user_data["correctUser"]
    page.goto(base_url)
    logging.info("Navigated to base URL.")
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.get_by_role("button", name="Login").click()
    logging.info("Login button clicked.")

    expect(page.get_by_text("Products")).to_be_visible(timeout=10000)
    assert "/inventory.html" in page.url
    logging.info("Login successful — Products page loaded.")
    take_screenshot(page, "after-login-success")

    # -----------------------------------------------------------
    # 2️⃣ VERIFY PRODUCT DETAILS
    # -----------------------------------------------------------
    names_locator = page.locator(".inventory_item_name")
    total_products = names_locator.count()
    assert total_products > 0, "No products found."
    logging.info(f"Found {total_products} products on the page.")

    product_names = []
    for i in range(total_products):
        name = names_locator.nth(i).inner_text().strip()
        product_names.append(name)
        logging.info(f"Checking product {i+1}: {name}")
        names_locator.nth(i).click()
        expect(page.locator(".inventory_details_name")).to_have_text(name)
        page.go_back()
        expect(page.get_by_text("Products")).to_be_visible(timeout=10000)
    take_screenshot(page, "all-products-verified")

    # -----------------------------------------------------------
    # 3️⃣ ADD ALL PRODUCTS TO CART
    # -----------------------------------------------------------
    add_buttons = page.locator("button.btn_inventory")
    add_count = add_buttons.count()
    assert add_count == total_products, f"Button count mismatch: {add_count} != {total_products}"
    logging.info("Adding all products to cart...")

    for i in range(add_count):
        add_buttons.nth(i).click()
    expect(page.locator("button:has-text('Remove')")).to_have_count(total_products)
    take_screenshot(page, "all-products-added")
    logging.info("All products added successfully.")

    # -----------------------------------------------------------
    # 4️⃣ VERIFY CART BADGE
    # -----------------------------------------------------------
    badge = page.locator(".shopping_cart_badge")
    expect(badge).to_have_text(str(total_products))
    logging.info(f"Cart badge shows {badge.inner_text().strip()} items.")
    take_screenshot(page, "cart-badge-count")

    # -----------------------------------------------------------
    # 5️⃣ OPEN CART AND VERIFY ITEM COUNT
    # -----------------------------------------------------------
    page.locator("#shopping_cart_container").click()
    logging.info("Opened the shopping cart.")
    assert "cart.html" in page.url
    expect(page.locator(".cart_item")).to_have_count(total_products)
    take_screenshot(page, "cart-overview")

    # -----------------------------------------------------------
    # 6️⃣ COMPARE PRODUCT NAMES IN CART AND LIST
    # -----------------------------------------------------------
    cart_names = [page.locator(".inventory_item_name").nth(i).inner_text().strip()
                  for i in range(total_products)]
    assert sorted(product_names) == sorted(cart_names), "Product names mismatch between cart and list."
    logging.info("Cart item names match product list.")
    take_screenshot(page, "cart-names-verified")

    # -----------------------------------------------------------
    # 7️⃣ RETURN TO PRODUCT LIST
    # -----------------------------------------------------------
    page.get_by_role("button", name="Continue Shopping").click()
    expect(page.get_by_text("Products")).to_be_visible(timeout=10000)
    logging.info("Returned to product list page.")

    # -----------------------------------------------------------
    # 8️⃣ REMOVE ALL PRODUCTS
    # -----------------------------------------------------------
    remove_buttons = page.locator("button.btn_inventory")
    for i in range(remove_buttons.count()):
        remove_buttons.nth(i).click()
    logging.info("All products removed from cart.")
    take_screenshot(page, "all-products-removed")

    # -----------------------------------------------------------
    # 🔟 VERIFY CART BADGE IS HIDDEN
    # -----------------------------------------------------------
    expect(page.locator(".shopping_cart_badge")).not_to_be_visible(timeout=3000)
    logging.info("Cart badge disappeared — cart is empty.")
    logging.info("=== Positive Full Flow Test Completed ===")


# ===============================================================
# TEST: Checkout Happy Path (Successful Purchase Flow)
# ---------------------------------------------------------------
# Purpose:
# - Validate a user can complete checkout successfully.
# ===============================================================
@pytest.mark.order(9)
def test_checkout_happy_path(page, base_url, user_data):
    logging.info("=== Starting Checkout Happy Path Test ===")
    user = user_data["correctUser"]

    # -----------------------------------------------------------
    # 1️⃣ LOGIN STAGE
    # -----------------------------------------------------------
    page.goto(base_url)
    logging.info("Navigated to SauceDemo base URL.")
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.get_by_role("button", name="Login").click()
    page.get_by_text("Products").wait_for(timeout=5000)
    assert "/inventory.html" in page.url
    logging.info("User logged in successfully.")
    take_screenshot(page, "checkout-login")

    # -----------------------------------------------------------
    # 2️⃣ ADD FIRST PRODUCT TO CART
    # -----------------------------------------------------------
    page.locator('.inventory_item').first.locator('a[id$="_title_link"]').click()
    logging.info("Opened first product details page.")
    page.get_by_role("button", name="Add to cart").click()
    take_screenshot(page, "product-added")
    logging.info("Product added to cart.")
    page.locator(".shopping_cart_link").click()
    page.locator("[id='checkout']").click()
    logging.info("Navigated to checkout form.")

    # -----------------------------------------------------------
    # 3️⃣ ENTER CHECKOUT INFORMATION
    # -----------------------------------------------------------
    page.get_by_placeholder("First Name").fill("Erol")
    page.get_by_placeholder("Last Name").fill("Evren")
    page.get_by_placeholder("Zip/Postal Code").fill("12345")
    take_screenshot(page, "checkout-form-filled")
    page.get_by_role("button", name="Continue").click()
    page.get_by_text("Payment Information").wait_for()
    assert "/checkout-step-two.html" in page.url
    logging.info("Checkout overview page loaded successfully.")
    take_screenshot(page, "checkout-overview")

    # -----------------------------------------------------------
    # 4️⃣ COMPLETE THE ORDER
    # -----------------------------------------------------------
    page.locator("[id='finish']").click()
    logging.info("Clicked Finish button.")
    logo = page.locator(".pony_express")
    expect(logo).to_be_visible(timeout=5000)
    thank_you_text = page.get_by_text("Thank you for your order!", exact=True)
    expect(thank_you_text).to_be_visible(timeout=5000)
    sub_text = page.get_by_text(
        "Your order has been dispatched, and will arrive just as fast as the pony can get there!"
    )
    expect(sub_text).to_be_visible(timeout=5000)
    back_home_button = page.locator("#back-to-products")
    expect(back_home_button).to_be_visible(timeout=5000)
    take_screenshot(page, "checkout-confirmation")
    logging.info("Order confirmation page verified successfully.")

    # -----------------------------------------------------------
    # 5️⃣ RETURN TO PRODUCT LIST
    # -----------------------------------------------------------
    back_home_button.click()
    expect(page).to_have_url(f"{base_url}inventory.html")
    logging.info("Returned to product list after checkout.")
    take_screenshot(page, "checkout-return")
    logging.info("=== Checkout Happy Path Test Completed ===")
