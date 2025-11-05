import pytest
from playwright.sync_api import expect

@pytest.mark.order(8)
def test_positive_full_flow(page, base_url, user_data):
    # 1) Login
    user = user_data["correctUser"]
    page.goto(base_url)
    page.get_by_placeholder("Username").fill(user["username"])
    page.get_by_placeholder("Password").fill(user["password"])
    page.get_by_role("button", name="Login").click()

    # “Products” başlığı görünsün
    expect(page.get_by_text("Products")).to_be_visible(timeout=10000)
    assert "/inventory.html" in page.url

    # 2) Tüm ürünlerin tıklanabildiğini doğrula (detaya gidip geri dön)
    names_locator = page.locator(".inventory_item_name")
    total_products = names_locator.count()
    assert total_products > 0, "Hiç ürün bulunamadi."

    product_names = []
    for i in range(total_products):
        name = names_locator.nth(i).inner_text().strip()
        product_names.append(name)
        names_locator.nth(i).click()
        # Detay sayfası açıldı mı ve isim eşleşiyor mu?
        expect(page.locator(".inventory_details_name")).to_be_visible(timeout=10000)
        expect(page.locator(".inventory_details_name")).to_have_text(name)
        page.go_back()
        expect(page.get_by_text("Products")).to_be_visible(timeout=10000)

    # 3) Tüm ürünleri sepete ekle
    add_buttons = page.locator("button.btn_inventory")
    add_count = add_buttons.count()
    # Liste sayfasında listelenen ürün sayısıyla add-to-cart sayısı eşit olmalı
    assert add_count == total_products, f"Add to cart buton sayisi beklenenden farkli: {add_count} != {total_products}"

    for i in range(add_count):
        add_buttons.nth(i).click()

    # “Remove” butonlarının sayısı tüm ürünlerle eşit olmalı (hepsi eklendi)
    expect(page.locator("button:has-text('Remove')")).to_have_count(total_products)

    # 4) Sepet rozeti (badge) ürün sayısıyla eşit mi?
    badge = page.locator(".shopping_cart_badge")
    expect(badge).to_be_visible(timeout=5000)
    expect(badge).to_have_text(str(total_products))

    # 5) Sepete git ve öğe sayısını doğrula
    page.locator("#shopping_cart_container").click()
    assert "cart.html" in page.url
    cart_items = page.locator(".cart_item")
    expect(cart_items).to_have_count(total_products)

    # 6) Sepetteki ürün isimleriyle liste sayfasındaki isimleri karşılaştır
    cart_names_locator = page.locator(".inventory_item_name")
    cart_count = cart_names_locator.count()
    assert cart_count == total_products, "Sepetteki ürün adi sayisi beklenenden farkli."

    cart_names = [cart_names_locator.nth(i).inner_text().strip() for i in range(cart_count)]

    # Sıra farklı olabilir; içerik aynı mı diye karşılaştıralım
    assert sorted(product_names) == sorted(cart_names), \
        f"İsimler uyuşmuyor!\nListe: {sorted(product_names)}\nSepet: {sorted(cart_names)}"
    
        # 7) Ürün listesine dön
    page.get_by_role("button", name="Continue Shopping").click()
    expect(page.get_by_text("Products")).to_be_visible(timeout=10000)
    assert "/inventory.html" in page.url

    # 8) Tüm "Remove" butonlarına tıkla (sepetteyken eklediğimiz tüm ürünler artık listedeki item'larda Remove durumunda)
    remove_buttons = page.locator("button.btn_inventory")
    expect(remove_buttons).to_have_count(total_products)

    for i in range(total_products):
        remove_buttons.nth(i).click()

    # 9) Tüm butonların tekrar "Add to cart" olduğunu doğrula
    add_again_buttons = page.locator("button:has-text('Add to cart')")
    expect(add_again_buttons).to_have_count(total_products)

    # 10) Sepet rozetinin (badge) kaybolduğunu doğrula
    badge = page.locator(".shopping_cart_badge")
    expect(badge).not_to_be_visible(timeout=3000)

    

@pytest.mark.order(9)
def test_checkout_happy_path(page,base_url):
  page.goto(base_url)
  page.get_by_placeholder("Username").fill("standard_user")
  page.get_by_placeholder("Password").fill("secret_sauce")
  page.get_by_role("button", name="Login").click()
  page.get_by_text("Products").wait_for()
  page.locator('.inventory_item').first.locator('a[id$="_title_link"]').click()
  page.get_by_role("button", name="Add to cart").click()
  page.locator(".shopping_cart_link").click()
  page.locator("[id='checkout']").click()
  page.get_by_placeholder("First Name").fill("John")
  page.get_by_placeholder("Last Name").fill("Doe")
  page.get_by_placeholder("Zip/Postal Code").fill("12345")
  page.get_by_role("button", name="Continue").click()
  page.get_by_text("Payment Information").wait_for()
  page.get_by_text("Shipping Information").wait_for()
  page.get_by_text("Price Total").wait_for()
  assert "/checkout-step-two.html" in page.url
  page.locator("[id='finish']").click()
  # 1️⃣ Logo (tick işareti)
  logo = page.locator(".pony_express")  # varsa
    # Eğer bu selector sitede yoksa, 'svg' veya 'img' etiketi üzerinden de kontrol edebilirsin
  expect(logo).to_be_visible(timeout=5000)

    # 2️⃣ Başlık metni
  thank_you_text = page.get_by_text("Thank you for your order!", exact=True)
  expect(thank_you_text).to_be_visible(timeout=5000)

    # 3️⃣ Alt açıklama
  sub_text = page.get_by_text(
        "Your order has been dispatched, and will arrive just as fast as the pony can get there!"
    )
  expect(sub_text).to_be_visible(timeout=5000)

    # 4️⃣ Back Home butonu
  back_home_button = page.locator("#back-to-products")
  expect(back_home_button).to_be_visible(timeout=5000)

    # 5️⃣ Ek kontrol – butona tıklayınca inventory sayfasına döner mi?
  back_home_button.click()
  expect(page).to_have_url(f"{base_url}inventory.html")
