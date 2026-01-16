#!/usr/bin/env python3
"""
Registration automation script using Playwright.
Lets the frontend JavaScript handle all integrity checks and form submission.
"""

from playwright.sync_api import sync_playwright

BASE_URL = "http://51.195.24.179:8000"

# Static credentials
USERNAME = "Gehrman88098"
EMAIL = "kmichaelson190@gmail.com"
PASSWORD = "harsh1mudit2"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 1. Navigate to base URL and allow all frontend JavaScript to load
        page.goto(BASE_URL, wait_until="networkidle")
        page.wait_for_load_state("domcontentloaded")

        # 2. Wait for form fields to be visible and fill them
        # Wait for at least one input field to appear
        page.wait_for_selector('input', timeout=10000)

        # Fill username field - try multiple selectors
        username_filled = False
        for selector in ['input[name="username"]', 'input[type="text"]', 'input[placeholder*="username" i]', 'input[id*="username" i]', 'input:first-of-type']:
            try:
                if page.locator(selector).count() > 0:
                    page.fill(selector, USERNAME)
                    username_filled = True
                    break
            except Exception:
                continue

        # Fill email field
        email_filled = False
        for selector in ['input[type="email"]', 'input[name="email"]', 'input[placeholder*="email" i]', 'input[id*="email" i]']:
            try:
                if page.locator(selector).count() > 0:
                    page.fill(selector, EMAIL)
                    email_filled = True
                    break
            except Exception:
                continue

        # Fill password field
        password_filled = False
        for selector in ['input[type="password"]', 'input[name="password"]', 'input[placeholder*="password" i]', 'input[id*="password" i]']:
            try:
                if page.locator(selector).count() > 0:
                    page.fill(selector, PASSWORD)
                    password_filled = True
                    break
            except Exception:
                continue

        # 3. Set up response listener and click the "Register Securely" button
        # Wait for the registration response using Playwright's built-in mechanism
        with page.expect_response(lambda response: response.url.endswith('/api/v1/complete_registration'), timeout=30000) as response_info:
            # Click the submit button - let frontend JavaScript handle everything
            button_clicked = False
            for selector in [
                'button:has-text("Register Securely")',
                'button:has-text("Register")',
                'button[type="submit"]',
                'input[type="submit"]',
                'form button',
                'button'
            ]:
                try:
                    if page.locator(selector).count() > 0:
                        page.click(selector)
                        button_clicked = True
                        break
                except Exception:
                    continue

            if not button_clicked:
                raise RuntimeError("Could not find or click the registration button")

        # 4. Extract flag from the response
        # The frontend JavaScript has:
        # - Computed hashes
        # - Run integrity stages
        # - Submitted the request
        response = response_info.value
        response_json = response.json()
        flag = response_json.get("flag") or response_json.get("data", {}).get("flag")

        if not flag:
            raise RuntimeError(f"Flag not found in registration response: {response_json}")

        # 5. Print ONLY the flag to stdout
        print(flag)
        browser.close()


if __name__ == "__main__":
    main()
