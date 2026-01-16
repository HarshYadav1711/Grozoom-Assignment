#!/usr/bin/env python3
#Analysis only

import sys
import re
import time
import hashlib
import json

try:
    import requests
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: Missing required dependencies. Install with: pip install requests playwright", file=sys.stderr)
    sys.exit(1)


def establish_browser_trust(base_url):
    """Use Playwright to establish Cloudflare trust and extract cookies."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to base URL and allow JavaScript to fully execute
        page.goto(base_url)
        time.sleep(5)
        
        # Extract all cookies from browser context
        cookies = context.cookies()
        
        browser.close()
        
        return cookies


def inject_cookies_to_session(sess, cookies, base_url):
    """Inject browser cookies into requests.Session."""
    from urllib.parse import urlparse
    parsed_url = urlparse(base_url)
    default_domain = parsed_url.hostname
    
    for cookie in cookies:
        # Extract cookie attributes
        name = cookie.get('name')
        value = cookie.get('value')
        domain = cookie.get('domain', default_domain)
        path = cookie.get('path', '/')
        
        # Remove leading dot from domain if present
        if domain.startswith('.'):
            domain = domain[1:]
        
        # Set cookie in session using RequestsCookieJar
        sess.cookies.set(name, value, domain=domain, path=path)


def register(base_url):
    """Perform browser-faithful registration flow with Cloudflare trust."""
    # Step 1: Establish browser trust using Playwright
    browser_cookies = establish_browser_trust(base_url)
    
    # Step 2: Create requests.Session and inject browser cookies
    sess = requests.Session()
    sess.timeout = 30
    inject_cookies_to_session(sess, browser_cookies, base_url)
    
    # Step 3: Use realistic static credentials
    username = 'Gehrman88098'
    email = 'kmichaelson190@gmail.com'
    password = 'harsh1mudit2'
    
    # Step 4: POST /api/v1/integrity/handshake
    # Use separate headers dictionary for handshake (anti-replay requirement)
    handshake_headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,en-IN;q=0.8',
        'Content-Type': 'application/json',
        'Origin': base_url,
        'Referer': base_url + '/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36 Edg/143.0.0.0'
    }
    
    handshake_resp = sess.post(
        base_url + '/api/v1/integrity/handshake',
        json={},
        headers=handshake_headers
    )
    handshake_resp.raise_for_status()
    
    # Step 5: Extract final_token from handshake JSON response
    handshake_data = handshake_resp.json()
    final_token = handshake_data.get('final_token') or handshake_data.get('token')
    
    # Fail fast if final_token is missing
    if not final_token or not final_token.strip():
        raise ValueError("Integrity handshake failed: final_token not found in handshake response")
    
    # Step 6: Build /complete_registration payload exactly as browser sends
    email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
    password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
    credential_proof = hashlib.md5((username + email + password).encode('utf-8')).hexdigest()
    
    # Generate mouse_data with coordinates around x≈800–900, y≈0–60, small diagonal movement
    base_time = int(time.time() * 1000)
    mouse_data = [
        {'x': 850, 'y': 30, 't': base_time},
        {'x': 852, 'y': 32, 't': base_time + 8},
        {'x': 855, 'y': 35, 't': base_time + 15},
        {'x': 857, 'y': 38, 't': base_time + 22},
        {'x': 860, 'y': 42, 't': base_time + 30},
        {'x': 863, 'y': 45, 't': base_time + 38}
    ]
    
    registration_payload = {
        'username': username,
        'email': email,
        'password': password,
        'email_hash': email_hash,
        'password_hash': password_hash,
        'credential_proof': credential_proof,
        'credential_proof_type': 'md5',
        'final_token': final_token,
        'mouse_data': mouse_data
    }
    
    # Step 7: POST /api/v1/complete_registration
    # Use separate headers dictionary for registration (anti-replay requirement)
    registration_headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,en-IN;q=0.8',
        'Content-Type': 'application/json',
        'Origin': base_url,
        'Referer': base_url + '/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36 Edg/143.0.0.0'
    }
    
    reg_resp = sess.post(
        base_url + '/api/v1/complete_registration',
        json=registration_payload,
        headers=registration_headers
    )
    reg_resp.raise_for_status()
    
    # Step 8: Parse JSON response and extract flag
    reg_data = reg_resp.json()
    
    # Search for flag in JSON response
    flag = None
    if isinstance(reg_data, dict):
        # Check common flag fields
        for key in ['flag', 'message', 'result', 'data']:
            if key in reg_data:
                value = reg_data[key]
                if isinstance(value, str):
                    # Look for CTF{...} or FLAG{...} pattern
                    match = re.search(r'(?:CTF|FLAG)\{[^}]+\}', value)
                    if match:
                        flag = match.group(0)
                        break
                elif isinstance(value, dict):
                    # Recursively search nested dict
                    flag = find_flag_in_json(value)
                    if flag:
                        break
        # If not found in common fields, search entire structure
        if not flag:
            flag = find_flag_in_json(reg_data)
    elif isinstance(reg_data, str):
        match = re.search(r'(?:CTF|FLAG)\{[^}]+\}', reg_data)
        if match:
            flag = match.group(0)
    
    if not flag:
        raise ValueError("Flag not found in registration response")
    
    return flag


def find_flag_in_json(obj):
    """Recursively search for flag pattern in JSON structure."""
    if isinstance(obj, dict):
        for value in obj.values():
            result = find_flag_in_json(value)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_flag_in_json(item)
            if result:
                return result
    elif isinstance(obj, str):
        match = re.search(r'(?:CTF|FLAG)\{[^}]+\}', obj)
        if match:
            return match.group(0)
    
    return None


def main():
    base_url = 'http://51.195.24.179:8000'
    
    try:
        flag = register(base_url)
        print(flag)
        return 0
    except requests.exceptions.RequestException as e:
        print(f"Error: Network request failed: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
