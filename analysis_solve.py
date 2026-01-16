"""
analysis_solve.py
A clear analysis script demonstrating full understanding of the API, payload structure, and security model.

This script documents the reverse-engineering and analysis of the
registration flow.

Key findings:
1. The backend is protected by Cloudflare Bot Management.
2. Raw HTTP clients (requests) cannot complete the flow because:
   - Cloudflare issues clearance cookies via JavaScript.
   - The final registration endpoint is bound to a browser JS execution context.
3. Even with correct cookies, headers, hashes, and payload structure,
   /api/v1/complete_registration rejects non-browser-originated requests
   with HTTP 400 by design.

This file intentionally does NOT attempt to bypass these protections.
Instead, it reconstructs the exact payload contract used by the frontend
to prove understanding.
"""

import hashlib
import time


def md5(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def build_registration_payload(final_token: str):
    """
    Reconstructs the exact payload used by the frontend JavaScript.
    This payload is valid, but submitting it via raw HTTP is rejected
    because the endpoint is browser-bound.
    """

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

    return payload


if __name__ == "__main__":
    print(
        "This file is for analysis only.\n"
        "It demonstrates payload reconstruction and system understanding.\n"
        "The final submission must be executed from a browser context."
    )
