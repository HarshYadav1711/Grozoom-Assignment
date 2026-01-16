# Registration Portal Automation

Python script that automates user registration on a protected portal by replicating browser behavior.

## Requirements

- Python 3.6 or higher
- `requests` library
- `beautifulsoup4` library

## Installation

Install dependencies:

```bash
pip install requests beautifulsoup4
```

## Usage

Run the script:

```bash
python solve.py
```

Or on Unix-like systems:

```bash
./solve.py
```

## Output

On success, the script prints:
- Registration success message
- Flag value

On failure, error messages are printed to stderr.

## Notes

- The script creates a fresh session on each run
- All tokens and cookies are extracted dynamically
- No hardcoded values or session data required
