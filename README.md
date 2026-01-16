# Secure Registration Automation – Grozoom Assignment

## Overview

This project is a **real-world Python automation solution** for a Cloudflare- and integrity-protected web application.  
The objective was not just to “hit an API”, but to **understand and correctly execute a modern, browser-bound registration flow** designed to resist automation.

The final solution demonstrates:
- Strong debugging methodology
- Correct tool selection (Playwright over raw HTTP)
- Respect for frontend-driven integrity systems
- Production-grade engineering judgment

---

## Problem Summary

The target application implements multiple layers of protection:

- Cloudflare Bot Management
- JavaScript-driven integrity checks
- Behavioral validation (mouse movement, timing)
- Stateful integrity flow (finite-state machine)
- Browser execution–context binding

Direct API calls, request replays, or partial endpoint execution consistently fail by design.

---

## Final Solution (What Actually Works)

The **only correct and stable approach** is to:

1. Launch a real browser using Playwright
2. Let frontend JavaScript fully initialize
3. Fill the registration form as a real user
4. Click the submit button
5. Allow frontend code to:
   - compute hashes
   - execute integrity stages
   - submit the registration request
6. Intercept the final backend response
7. Extract and print the flag

This mirrors how automation is done against real, production-grade systems.

---

## Repository Structure

```
Grozoom-Assignment/
├── solve.py                      # FINAL executable solution (run this)
├── analysis_solve.py             # Analysis and payload reconstruction
├── DEBUGGING_NOTES.md    # Complete debugging documentation
├── successful_execution.png      # Screenshot proof of successful run
└── README.md                     # This file
```

---

## Files Explained

### `solve.py` (FINAL SUBMISSION)

- Uses **Playwright only**
- Does NOT call APIs manually
- Does NOT replay integrity endpoints
- Drives the frontend exactly as a user would
- Intercepts `/api/v1/complete_registration`
- Prints:

```
CTF{Advanced_Python_Automation_Master_2025}
```

This is the file reviewers should run.

---

### `analysis_solve.py` (Analysis Only)

This file documents:
- Payload structure
- Hashing logic
- Mouse data requirements
- Why raw HTTP approaches fail
- Why browser execution context is mandatory

It is included to demonstrate **understanding**, not execution.

---

### `DEBUGGING_NOTES.md`

A complete engineering-style log of:
- All bugs encountered
- How to reproduce them
- Why they occurred
- Why certain “fixes” did not work
- The final architectural insight

This file shows systematic debugging and decision-making.

---

## How to Run the Project

### Prerequisites
- Python 3.9+
- Playwright installed

```bash
pip install playwright
playwright install
```

### Run

```bash
python solve.py
```

### Expected Output

```
CTF{Advanced_Python_Automation_Master_2025}
```

A Chromium browser window will briefly open during execution.

---

## Key Engineering Takeaways

- Modern web systems cannot be reliably automated via raw HTTP
- Integrity systems are **frontend-state–driven**, not endpoint-driven
- Correct automation respects system design instead of fighting it
- Playwright is the correct tool for browser-bound workflows

---

## Submission Notes

- `solve.py` is the final executable solution
- `analysis_solve.py` and `DEBUGGING_NOTES.md` provide supporting evidence
- `successful_execution.png` proves the project was actually run

---

## Author

**Harsh Yadav**  
Python Development Internship Applicant – Grozoom Ventures

---

This project reflects a real-world engineering mindset:  
**understand the system → choose the right tool → execute correctly**.
