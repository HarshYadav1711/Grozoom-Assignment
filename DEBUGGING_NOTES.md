# DEBUGGING_NOTES.md
**Project:** Secure Registration Automation  
**Context:** Python + Playwright automation of a Cloudflare- and integrity-protected registration flow  
**Objective:** Document all bugs and issues encountered during development, including reproduction steps, root causes, and final resolutions.

---

## 1. HTTP 405 — Method Not Allowed

### Symptoms
Requests returned:
```
405 Method Not Allowed
```

### How to Reproduce
```http
POST /
POST /handshake
POST /api/v1/integrity/config
POST /api/v1/integrity/verify
```

### Root Cause
These routes are either:
- Not intended for POST, or
- Internal backend routes not exposed to the frontend.

### Resolution
Only call endpoints actually triggered by frontend JavaScript:
- `POST /api/v1/integrity/handshake`
- `POST /api/v1/complete_registration`

---

## 2. HTTP 403 — Forbidden (Cloudflare Blocking)

### Symptoms
```
403 Client Error: Forbidden
```

### How to Reproduce
- Call protected endpoints using `requests` or curl.

### Root Cause
Cloudflare Bot Management blocks non-browser clients that do not execute JavaScript.

### Resolution
Use Playwright to run a real Chromium browser so Cloudflare JS challenges can complete.

---

## 3. HTTP 400 — Bad Request (Payload & Heuristics)

### Symptoms
```
400 Client Error: Bad Request
```

### How to Reproduce
- Submit registration with incorrect hashes, unrealistic mouse data, or replayed headers.

### Root Causes
- Incorrect credential_proof calculation
- Unrealistic mouse movement
- Over-randomized credentials
- Reusing identical headers across requests
- Manually setting Accept-Encoding

### Resolutions
- Compute `credential_proof = MD5(username + email + password)`
- Use realistic mouse movement (6+ points, small deltas, ms timing)
- Use realistic static credentials
- Let the HTTP client manage compression
- Avoid header replay patterns

---

## 4. Cloudflare Timing Issues

### Symptoms
Requests fail despite cookies being present.

### How to Reproduce
```python
page.goto(url, wait_until="networkidle")
```

### Root Cause
Cloudflare behavioral scoring completes after network idle.

### Resolution
Use:
```python
page.goto(url)
time.sleep(5)
```

---

## 5. Handshake Token Not Found

### Symptoms
```
RuntimeError: final_token not returned from handshake
```

### How to Reproduce
- Assume handshake response always returns `final_token`.

### Root Cause
Handshake response schema varies:
```json
{ "final_token": "..." }
{ "token": "..." }
{ "data": { "token": "..." } }
```

### Resolution
Extract token robustly:
```python
token = data.get("final_token") or data.get("token") or data.get("data", {}).get("token")
```

---

## 6. Flag Not Found in Response

### Symptoms
```
RuntimeError: Flag not found in response
```

### How to Reproduce
- Assume flag is always at top-level JSON.

### Root Cause
Backend may wrap response:
```json
{ "flag": "..." }
{ "data": { "flag": "..." } }
```

### Resolution
Extract flag defensively:
```python
flag = res.get("flag") or res.get("data", {}).get("flag")
```

---

## 7. Incomplete Integrity Flow

### Symptoms
```json
{ "detail": "Incomplete flow" }
```

### How to Reproduce
- Call `/api/v1/complete_registration` directly after handshake.
- Manually replay integrity endpoints using fetch.

### Root Cause
Integrity system is a **stateful frontend-driven FSM**.
Calling endpoints directly does not advance internal JS state.

### Resolution
Do NOT manually call integrity endpoints.
Instead:
- Fill the registration form
- Click the submit button
- Let frontend JavaScript execute the full integrity lifecycle naturally

---

## 8. Playwright Request API vs Browser Fetch

### Symptoms
Handshake succeeds but token missing or flow rejected.

### How to Reproduce
```python
page.request.post(...)
```

### Root Cause
`page.request` bypasses page JS execution context.

### Resolution
Use `fetch()` via:
```python
page.evaluate(async () => fetch(...))
```
or rely entirely on frontend-triggered requests.

---

## 9. Raw HTTP vs Browser Execution Context

### Symptoms
Persistent 400 errors even with correct cookies, headers, and payload.

### Root Cause
Final registration endpoint is **browser-execution-context bound**.
It validates that requests originate from frontend JS.

### Resolution
Perform final submission only via:
- Real form interaction (fill + click)
- Or frontend-triggered fetch/XHR

---

## 10. Final Architectural Insight (Key Lesson)

The system enforces multiple layers:
- Cloudflare Bot Management
- JavaScript integrity checks
- Behavioral validation
- Schema validation
- Anti-replay detection
- Browser execution context binding

Attempting to replay or shortcut these layers is unreliable.

### Correct Engineering Approach
- Reverse-engineer frontend behavior
- Let frontend JavaScript drive the flow
- Use Playwright for real browser interaction
- Intercept results instead of replaying requests

---

## Final Conclusion

The only stable and correct solution is a **form-driven Playwright script** that:
- Loads the site
- Fills the form
- Clicks submit
- Intercepts `/api/v1/complete_registration`
- Extracts and prints the flag

This mirrors real-world automation under modern web security and reflects production-grade engineering practice.
