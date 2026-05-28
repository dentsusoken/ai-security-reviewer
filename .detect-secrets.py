#!/usr/bin/env python3
"""Simple secret detection for pre-commit hook."""

import re
import sys
from pathlib import Path

# Secret patterns
SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"aws_secret_access_key\s*=\s*['\"]?[\w/+=]{40}['\"]?", "AWS Secret Key"),
    (r"password\s*[=:]\s*['\"]?[\w@#$%^&*!]{8,}['\"]?", "Password"),
    (r"api[_-]?key\s*[=:]\s*['\"]?[\w\-]{20,}['\"]?", "API Key"),
    (r"private[_-]?key\s*[=:]", "Private Key"),
]

EXCLUDE_PATTERNS = [
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "__pycache__",
    "docs",  # Exclude docs directory (includes examples)
    "mock_data.py",  # Exclude mock data (contains sample vulnerable code for demo)
]


def is_excluded(path):
    """Check if path should be excluded from scanning."""
    parts = Path(path).parts
    return any(part in EXCLUDE_PATTERNS for part in parts)


def scan_file(filepath):
    """Scan a single file for secrets."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            for pattern, secret_type in SECRET_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    return True, secret_type
    except Exception:
        pass
    return False, None


def main():
    """Scan files for secrets."""
    found_secrets = False
    for filepath in sys.argv[1:]:
        if is_excluded(filepath):
            continue

        has_secret, secret_type = scan_file(filepath)
        if has_secret:
            print(f"[WARNING] Secret detected in {filepath}: {secret_type}")
            found_secrets = True

    if found_secrets:
        print("\n[ERROR] Commit blocked: Potential secrets detected")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
