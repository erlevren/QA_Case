# QA Case Study – Automated Testing with K6 & Playwright

# 🧪 K6 API Integration Testing (REST + GraphQL)

This module validates one **REST** and one **GraphQL** public API using **Grafana K6**.  
The goal is to demonstrate both **functional correctness** and **light performance characteristics** under realistic, concurrent load — exactly as requested in the case study.

---

## 🔍 Scope & APIs

### 🌐 REST: Rest Countries v3
- **Endpoint exercised:** `/v3.1/all?fields=name,region`  
- **Why this path:** narrowing fields (`name`, `region`) reduces payload size, yields steadier latency, and makes CI more reliable.

### 🧬 GraphQL: Rick & Morty GraphQL
- **Operation exercised:** `characters(page: 1)` fetching basic fields (`id`, `name`, `species`, `status`)  
- **Why this query:** stable, publicly accessible dataset with predictable structure for schema and functional checks.

---

## 🧠 What We Verify

Across both APIs, the tests cover:

### 🟢 Happy Path
Valid requests return **200 OK**, **JSON**, and the **expected structure**.

### 🧩 Schema / Shape
Presence and type of key fields (e.g., arrays exist; required keys are present).

### ⚙️ Functional Assertions
- **REST:** The list contains **Turkey/Türkiye**; total countries > 100.  
- **GraphQL:** At least one character exists, and **“Rick Sanchez”** is included.

### 🔴 Error Handling (Negative Tests)
- **REST:** Invalid country name returns 404 or 200 + empty array (both behaviors occur in this API and are accepted).  
- **GraphQL:** An invalid field query yields 400 or 200 + `errors` — both are considered correct error handling.

---

## 📊 Performance Thresholds (SLA)

| Metric | Target | Description |
|--------|---------|-------------|
| **p(95)** | `< 1000–1500 ms` | 95% of requests should complete under 1–1.5s |
| **Error Rate** | `< 2%` | Less than 2% of positive requests should fail |

These thresholds keep tests meaningful for CI while avoiding false failures from intentional negative calls.

---

## ⚙️ Load Profile

| Setting | Description |
|----------|-------------|
| **Virtual Users (VUs):** | Light, CI-friendly — a few concurrent users |
| **Duration:** | 5–10 seconds per run |
| **Think Time:** | Short delay between requests to simulate pacing |

🧩 **Rationale:**  
Public endpoints may throttle; light load avoids rate limits while still exercising concurrency.  
A short think time between iterations prevents bursty traffic that can distort latency metrics.

---

## 🧱 Threshold Strategy (SLA Logic)

- **Latency:**  
  - REST: `p(95) < 1500 ms`  
  - GraphQL: `p(95) < 1000 ms`  

- **Reliability:**  
  - Error rate for **positive** traffic `< 2%`.

- **Tag Filtering:**  
  SLA only applies to requests tagged as `req:positive`.  
  Negative test cases are intentionally invalid and should not count toward SLA.

🧩 **Why Tag Filtering?**  
This aligns SLA evaluation with real business expectations — we measure responsiveness and reliability for valid traffic, while still verifying error paths separately.

---

## ✅ Positive (Happy Path) Scenarios

### REST
- Expect **200 + JSON**  
- Response is an array  
- Contains **> 100 countries**  
- Includes **Turkey/Türkiye**

### GraphQL
- Expect **200 + JSON**  
- `data.characters.results` is an array with ≥ 1 element  
- Includes **“Rick Sanchez”**

**SLA applies** to these calls.

---

## ❌ Negative (Error Handling) Scenarios

### REST
- A non-existent country should return **404** or **200 + empty array**.  
  Both are considered correct.

### GraphQL
- A query referencing a non-existent field should return **400** or **200 + errors array**.  
  Both are accepted.

**SLA does not apply** to these calls (tagged as negative).

---

## 🧾 Pass / Fail Interpretation

A run is **functionally successful** if all checks pass:
- ✅ Status codes  
- ✅ Schema structure  
- ✅ Functional assertions  
- ✅ Error handling  

A run is **performance successful** if all **positive calls** meet SLA:
- `p(95)` latency under target  
- Error rate < 2%

If `p(95)` occasionally exceeds the bound, this indicates **temporary public API slowness** — not a test defect.  
Such cases are visible in the K6 summary and can be re-run or tuned with relaxed bounds.

---

## ⚙️ CI/CD Integration

Tests run automatically on **push** and **pull_request** via **GitHub Actions**.

**Workflow steps:**
1. Checkout the repository  
2. Set up Grafana K6  
3. Run REST smoke test  
4. Run GraphQL test  
5. Fail CI job if thresholds fail  

This ensures performance regressions and availability issues are caught **during code review**.

---

## 🧪 Test Data & Stability Measures

- `Accept: application/json` header  
- `User-Agent`: added to avoid 403/429 from public APIs  
- Field narrowing (REST) → smaller payload, stable latency  
- Request timeouts to prevent hanging tests  
- `sleep(1)` between requests → human-like pacing  

---

## ⚠️ Known Behavior & Constraints

- Public APIs may **rate-limit or slow down** occasionally.  
- Sporadic `p(95)` breaches usually reflect **network variance**, not defects.  
- Re-running often stabilizes results.  
- In strict CI pipelines, consider slightly **looser p(95)** or **pre-flight checks**.

---

## 🧭 How to Run Locally

1. **Install K6**
   - Windows: `choco install k6`
   - macOS: `brew install k6`

2. **Run the REST test**
   ```bash
   k6 run k6/rest/restcountries-smoke.js

3. **Run the GraphQL test**
   ```bash
   k6 run k6/graphql/rickmorty-characters.js

## 🔍 Review the Summary

After running the tests, review the terminal summary to confirm the results:

- ✅ **All checks** (status, schema, functional assertions, and error handling) should pass.  
- ✅ **SLA thresholds** (p95 latency and error rate) should be within the expected bounds.


### 📈 Combined Summary & Conclusion

| Category                    | REST                       | GraphQL                        |
|-----------------------------|----------------------------|--------------------------------|
| **Happy Path (200 + JSON)** | ✅                        | ✅                             |
| **Schema & Structure**      | ✅ (>100 countries)       | ✅ (`data.characters.results`) |
| **Functional Assertion**    | ✅ Turkey/Türkiye present | ✅ “Rick Sanchez” present      |
| **Negative Case Handling**  | ✅ 404 or 200 + []        | ✅ 400 or 200 + errors         |
| **SLA (p95, error rate)**   | ⚠️ May spike under load   | ✅ Stable                      |
| **CI Integration**          | ✅                        | ✅                             |


### 🏁 Conclusion

This **K6 API testing module** demonstrates a balanced and CI-ready approach for validating **public REST and GraphQL APIs**, focusing on both:

- 🔹 Functional + performance validation of endpoints  
- 🔹 Tagged SLA enforcement for positive traffic  
- 🔹 Clear and measurable pass/fail criteria  
- 🔹 Seamless **CI/CD integration** ensuring reliability and visibility of regressions  

Perfectly aligned for **real-world continuous testing pipelines** that combine correctness, performance, and maintainability.

# 🧪 Playwright UI E2E Tests (Login + Checkout)

This project tests the **SauceDemo** application’s user login, special user behaviors (problem accounts), and checkout (order completion) flow using **Playwright (Python)**.  
The goal is to validate both **functional correctness** and **expected faulty behaviors** step by step — similar to a real QA case study.

---

## 🔍 Test Scope

### 👤 Login Scenarios
- Positive login (valid user credentials)
- Negative login (wrong or missing credentials)
- Special user behaviors (`problem_user`, `error_user`, `visual_user`, `performance_user`)

### 🛒 Checkout Scenario
- Add product(s) to the cart  
- View cart and proceed to checkout  
- Fill out checkout form (First Name, Last Name, Zip Code)  
- Complete the order and verify the confirmation page  

---

## ⚙️ Technology & Tools

| Component       | Description                                                                          |
|-----------------|--------------------------------------------------------------------------------------|
| **Framework**   | Pytest + Playwright                                                                  |
| **Language**    | Python                                                                               |
| **Screenshots** | Managed via `conftest.py`: automatic (on failure) and manual (`take_screenshot()`)   |
| **Browser**     | Headless (CI) / Visible (Local)                                                      |
| **Reports**     | Saved under `reports/screenshots` as PNG files                                       |
| **CI/CD**       | GitHub Actions integration for automated execution                                   |

---

## 🧠 Validation Points

### 🟢 Positive Scenarios
- Successful login with valid credentials  
- Products page visible after login  
- Add to cart and checkout flow complete successfully  

### 🔴 Negative Scenarios
- Invalid username/password combinations  
- Empty username or password fields  
- Expected UI and functional bugs for special users  

---

## 👥 User Data

| User                             | Type     | Expected Behavior                                         |
|----------------------------------|----------|-----------------------------------------------------------|
| `standard_user`                  | Positive | Successful login, normal flow                             |
| `locked_out_user`                | Negative | Login denied                                              |
| `problem_user`                   | Special  | Broken images and malfunctioning buttons                  |
| `visual_user`                    | Special  | Page layout differs from normal                           |
| `performance_glitch_user`        | Special  | Product page loads slowly                                 |
| `error_user`                     | Special  | “Finish” button visible but not clickable during checkout |
| `wrong_password`, `empty fields` | Negative | “Epic sadface” error displayed                            |

---

## 🧾 Test Steps

### 1️⃣ Positive Login
**File:** `tests/test_login.py → test_login_success`

#### Steps:
1. Login with `standard_user`.  
2. “Products” heading is displayed.  
3. URL should be `/inventory.html`.

📷 **Screenshot:** `after-login.png`

---

### 2️⃣ Negative Login Tests
**File:** `tests/test_login.py → test_login_failure`

#### Steps:
1. Attempt login with invalid users (`lockedUser`, `wrongPass`, `emptyUsername`, `emptyPassword`).  
2. “Epic sadface” error appears on each attempt.  
3. No navigation to `/inventory.html`.

📷 **Screenshots:**
- `login-fail-lockedUser.png`
- `login-fail-wrongPass.png`

---

### 3️⃣ Problem User – Visual and Form Bugs
**File:** `tests/test_login.py → test_login_problemuser`

#### Observed Bugs:
- Product images are identical.  
- Some “Add to Cart” buttons do not work.  
- Checkout form behaves incorrectly:
  - After entering “First Name”, typing a single character in “Last Name” overwrites it.  
  - Even with Zip Code filled, clicking **Continue** shows **Error: First Name is required**.

📷 **Screenshots:**
- `problem-user-products.png`
- `problem-user-checkout-error.png`

---

### 4️⃣ Error User – Finish Button Issue
**File:** `tests/test_login.py → test_login_erroruser`

#### Steps:
1. Login with `error_user`.  
2. Add all products to the cart.  
3. Fill out the checkout form.  
4. “Finish” button appears but cannot be clicked.

📷 **Screenshots:**
- `error-user-products.png`
- `error-user-finish-button.png`

---

### 5️⃣ Visual User – Layout Differences
**File:** `tests/test_login.py → test_login_visual_success`

#### Behavior:
- Login succeeds but UI layout differs from the standard user.  
- Screenshot taken to record layout differences.

📷 **Screenshot:** `visual-user-layout.png`

---

### 6️⃣ Performance User – Slow Page Load
**File:** `tests/test_login.py → test_login_performance_success`

#### Behavior:
- “Products” page loads slowly.  
- Functionality remains correct, only latency is affected.

📷 **Screenshot:** `performance-user-products.png`

---

### 7️⃣ Checkout – Happy Path
**File:** `tests/test_checkout_flow.py → test_checkout_happy_path`

#### Steps:
1. Login with `standard_user`.  
2. Add a product to the cart.  
3. Fill out the checkout form (First, Last, Zip).  
4. Click “Continue”.  
5. Verify “Payment Information”, “Shipping Information”, and “Price Total” sections.  
6. Click “Finish”.  
7. Confirm the order screen:
   - ✅ “Thank you for your order!” text  
   - ✅ Description message  
   - ✅ “Back Home” button  
8. Click “Back Home” → verify return to `/inventory.html`.

📷 **Screenshots:**
- `checkout-overview.png`
- `checkout-confirmation.png`

---

## 🧠 Known Issues (Bug Summary)

| User                 | Issue Description                                                                                         |
|----------------------|-----------------------------------------------------------------------------------------------------------|
| **problemUser**      | Typing a single character in Last Name clears First Name; “Error: First Name is required” after Continue. |
| **errorUser**        | Finish button visible but unclickable.                                                                    |
| **visualUser**       | Layout differs; element positions shifted.                                                                |
| **performanceUser**  | Products page loads slower than expected.                                                                 |

---

## 📸 Screenshot Placeholders

```
![After Login](reports/screenshots/after-login.png)
![Locked User Error](reports/screenshots/login-fail-lockedUser.png)
![Problem User Checkout Error](reports/screenshots/problem-user-checkout-error.png)
![Error User Finish Button](reports/screenshots/error-user-finish-button.png)
![Checkout Confirmation](reports/screenshots/checkout-confirmation.png)
```
