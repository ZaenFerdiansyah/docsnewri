#!/usr/bin/env python3
"""Generate a SHA-256 password hash without exposing the password."""

from __future__ import annotations

import getpass
import hashlib


def hash_password(password: str) -> str:
    """Return the lowercase hexadecimal SHA-256 digest for a password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def main() -> int:
    """Prompt for a password twice and print its hash when both entries match."""
    password = getpass.getpass("Enter password: ")
    confirmation = getpass.getpass("Confirm password: ")

    if not password:
        print("Error: password must not be empty.")
        return 1

    if password != confirmation:
        print("Error: password confirmation does not match.")
        return 1

    print("\nPassword hash:\n")
    print(hash_password(password))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
