#!/usr/bin/env python3
"""Validate secure-page configuration and its documentation targets."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "secure-pages.json"
DEFAULT_DOCS_DIR = PROJECT_ROOT / "docs"
REQUIRED_PROPERTIES = ("path", "group", "password_hash")
GROUP_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HASH_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


def load_configuration(config_path: Path) -> tuple[Any | None, list[str]]:
    """Load JSON configuration and return useful parsing errors."""
    try:
        with config_path.open(encoding="utf-8") as config_file:
            return json.load(config_file), []
    except FileNotFoundError:
        return None, [f"configuration file does not exist: {config_path}"]
    except OSError as error:
        return None, [f"cannot read configuration file {config_path}: {error}"]
    except json.JSONDecodeError as error:
        return None, [
            f"malformed JSON in {config_path} at line {error.lineno}, "
            f"column {error.colno}: {error.msg}"
        ]


def documentation_path(page_path: str, docs_dir: Path) -> Path:
    """Map a canonical documentation URL path to its Markdown source."""
    relative_path = page_path.strip("/")
    if not relative_path:
        return docs_dir / "index.md"
    return docs_dir / f"{relative_path}.md"


def validate_page_path(page_path: object, label: str, docs_dir: Path) -> list[str]:
    """Validate a configured URL path and its Markdown target."""
    if not isinstance(page_path, str) or not page_path.strip():
        return [f"{label}.path must be a non-empty string"]

    errors: list[str] = []
    if not page_path.startswith("/") or not page_path.endswith("/"):
        errors.append(f"{label}.path must start and end with '/': {page_path!r}")

    pure_path = PurePosixPath(page_path)
    if ".." in pure_path.parts or "." in pure_path.parts:
        errors.append(f"{label}.path must not contain relative segments: {page_path!r}")

    if "//" in page_path:
        errors.append(f"{label}.path must not contain empty segments: {page_path!r}")

    if not errors:
        source_path = documentation_path(page_path, docs_dir)
        if not source_path.is_file():
            errors.append(
                f"{label}.path does not correspond to a documentation page: "
                f"{page_path!r} (expected {source_path})"
            )
    return errors


def validate_configuration(data: object, docs_dir: Path) -> list[str]:
    """Return all semantic errors found in a decoded configuration."""
    if not isinstance(data, dict):
        return ["configuration root must be a JSON object"]

    pages = data.get("secure_pages")
    if not isinstance(pages, list):
        return ["property 'secure_pages' must be an array"]

    errors: list[str] = []
    paths: dict[str, dict[str, Any]] = {}
    groups: dict[str, str] = {}

    for index, page in enumerate(pages):
        label = f"secure_pages[{index}]"
        if not isinstance(page, dict):
            errors.append(f"{label} must be an object")
            continue

        missing = [name for name in REQUIRED_PROPERTIES if name not in page]
        if missing:
            errors.append(f"{label} is missing required properties: {', '.join(missing)}")

        page_path = page.get("path")
        errors.extend(validate_page_path(page_path, label, docs_dir))

        group = page.get("group")
        if not isinstance(group, str) or not group.strip():
            errors.append(f"{label}.group must be a non-empty string")
        elif not GROUP_PATTERN.fullmatch(group):
            errors.append(
                f"{label}.group must use lowercase letters, numbers, and single "
                f"hyphens: {group!r}"
            )

        password_hash = page.get("password_hash")
        if not isinstance(password_hash, str) or not password_hash.strip():
            errors.append(f"{label}.password_hash must be a non-empty string")
        elif not HASH_PATTERN.fullmatch(password_hash):
            errors.append(f"{label}.password_hash must be a 64-character SHA-256 hex digest")

        if isinstance(page_path, str) and page_path:
            previous = paths.get(page_path)
            if previous is not None:
                errors.append(f"{label}.path duplicates an earlier page path: {page_path!r}")
                if previous != page:
                    errors.append(
                        f"{label} conflicts with the earlier configuration for {page_path!r}"
                    )
            else:
                paths[page_path] = page

        if (
            isinstance(group, str)
            and GROUP_PATTERN.fullmatch(group)
            and isinstance(password_hash, str)
            and HASH_PATTERN.fullmatch(password_hash)
        ):
            previous_hash = groups.get(group)
            normalized_hash = password_hash.lower()
            if previous_hash is not None and previous_hash != normalized_hash:
                errors.append(
                    f"{label}.group {group!r} conflicts with another password hash; "
                    "pages in one group must share a password hash"
                )
            else:
                groups[group] = normalized_hash

    return errors


def validate_file(config_path: Path, docs_dir: Path) -> list[str]:
    """Load and validate one secure-page configuration file."""
    data, load_errors = load_configuration(config_path)
    if load_errors:
        return load_errors
    return validate_configuration(data, docs_dir)


def parse_args() -> argparse.Namespace:
    """Parse optional paths for local testing and build integration."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--docs-dir", type=Path, default=DEFAULT_DOCS_DIR)
    return parser.parse_args()


def main() -> int:
    """Print validation results and return a shell-friendly status."""
    args = parse_args()
    errors = validate_file(args.config.resolve(), args.docs_dir.resolve())
    if errors:
        print("Secure-page configuration validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Secure-page configuration is valid: {args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
