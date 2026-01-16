import time
import hashlib
from playwright.sync_api import sync_playwright

BASE_URL = "http://51.195.24.179:8000"


def md5(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def main():
    with sync_playwright() as p:
        # Launch real browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 1. Load site and allow Cloudflare + JS integrity to finish
        page.goto(BASE_URL)
        time.sleep(5)

        # 2. Integrity handshake (MUST be inside browser context)
        handshake_resp = page.request.post(
            f"{BASE_URL}/api/v1/integrity/handshake",
            headers={"Content-Type": "application/json"},
            data="{}"
        )

        handshake_data = handshake_resp.json()
        final_token = handshake_data.get("final_token")

        if not final_token:
            raise RuntimeError("final_token not returned from handshake")

        # 3. Build browser-faithful payload
        username = "Gehrman88098"
        email = "kmichaelson190@gmail.com"
        password = "harsh1mudit2"

        now = int(time.time() * 1000)
        mouse_data = [
            {"x": 854, "y": 0,  "t": now},
            {"x": 845, "y": 10, "t": now + 6},
            {"x": 832, "y": 22, "t": now + 12},
            {"x": 820, "y": 35, "t": now + 19},
            {"x": 810, "y": 48, "t": now + 27},
            {"x": 800, "y": 62, "t": now + 36},
        ]

        payload = {
            "username": username,
            "email": email,
            "password": password,  # plaintext required
            "email_hash": md5(email),
            "password_hash": md5(password),
            "credential_proof": md5(username + email + password),
            "final_token": final_token,
            "mouse_data": mouse_data,
        }

        # 4. Complete registration INSIDE browser context
        registration_resp = page.request.post(
            f"{BASE_URL}/api/v1/complete_registration",
            json=payload
        )

        result = registration_resp.json()

        # 5. Print flag
        if "flag" not in result:
            raise RuntimeError("Flag not found in response")

        print(result["flag"])

        browser.close()


if __name__ == "__main__":
    main()
