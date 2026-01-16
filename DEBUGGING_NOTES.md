# DEBUGGING_NOTES.md
**Project:** Secure Registration Automation  
**Context:** Python + Browser-based automation of a Cloudflare-protected registration flow  
**Objective:** Document all issues encountered during development, how to reproduce them, their root causes, and their final resolutions.

---

## 1. HTTP 405 — Method Not Allowed

### Symptoms
Requests to certain endpoints returned:
```
405 Method Not Allowed
```

### How to Reproduce
```http
POST /
POST /handshake
POST /api/status
POST /api/v1/integrity/config
POST /api/v1/integrity/verify
```

### Root Cause
These endpoints are either:
- Not designed to accept POST requests, or
- Internal backend routes not exposed to client-side code.

### Resolution
Restrict all client calls to **only the endpoints actually used by the frontend**:
- `POST /api/v1/integrity/handshake`
- `POST /api/v1/complete_registration`

All other integrity-related routes are server-internal and must not be called.

---

## 2. “Flag Not Found” Errors

### Symptoms
Script executed without crashing but failed with:
```
Flag not found in response
```

### Root Cause
The `flag` is returned **only** by the final registration endpoint upon successful completion.

### Resolution
Search for the flag **only** in the response from:
```
POST /api/v1/complete_registration
```

---

## 3. Runtime Errors (Undefined Variables)

### Symptoms
```
NameError: name 'all_responses' is not defined
```

### Root Cause
Debug variables were referenced outside their valid scope.

### Resolution
Remove unused debug variables or ensure all variables are defined before use.

---

## 4. HTTP 403 — Forbidden

### Symptoms
```
403 Client Error: Forbidden
```

### Root Cause
The endpoint is protected by Cloudflare Bot Management and browser-bound integrity checks.

### Resolution
Execute the flow inside a **real browser environment** using Playwright.

---

## 5. Incorrect Credential Proof Calculation

### Root Cause
Frontend computes:
```
MD5(username + email + password)
```

### Resolution
Compute credential proof exactly as:
```python
credential_proof = md5(username + email + password)
```

---

## 6. Missing or Implicit Payload Fields

### Root Cause
Backend performs strict schema validation; some fields are injected by frontend JavaScript.

### Resolution
Ensure payload structure matches frontend output exactly.

---

## 7. Mouse Data Validation Failures

### Root Cause
Backend validates human-like mouse interaction patterns.

### Resolution
Generate mouse data with:
- ≥ 6 points
- Small diagonal movement
- 5–15 ms timestamp gaps
- Realistic screen coordinates

---

## 8. Anti-Replay Detection via Headers

### Root Cause
Backend detects identical request contexts across integrity boundaries.

### Resolution
Use separate header dictionaries for:
- Integrity handshake
- Registration submission

---

## 9. Accept-Encoding / Compression Issues

### Root Cause
`requests` does not natively support Brotli (`br`).

### Resolution
Do not manually set `Accept-Encoding`.

---

## 10. Playwright Timing and Cloudflare Finalization

### Root Cause
`networkidle` fires before Cloudflare completes JS-based behavioral scoring.

### Resolution
Use:
```python
page.goto(url)
time.sleep(5)
```

---

## 11. Browser vs Raw HTTP Execution Context

### Root Cause
Final registration endpoint is browser-execution-context bound.

### Resolution
Submit the final request **inside Playwright** using:
```python
page.request.post(...)
```

---

## Final Conclusion

The system enforces multiple protection layers:
- Cloudflare Bot Management
- JavaScript integrity checks
- Behavioral validation
- Schema validation
- Anti-replay detection
- Browser execution binding

The correct engineering approach is to reverse-engineer the frontend request contract and execute the final submission inside a real browser context.
