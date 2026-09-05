"""MkDocs build hooks for publishing browser-readable configuration."""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
from pathlib import Path

from mkdocs.exceptions import ConfigurationError


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SECURE_CONFIG = PROJECT_ROOT / "config" / "secure-pages.json"
VALIDATOR_PATH = PROJECT_ROOT / "scripts" / "validate-secure-pages.py"
ROOT_RELATIVE_ASSET = re.compile(r'(?P<attribute>\b(?:href|src))="/(?!/)')


def load_validator() -> object:
    """Load the validator whose required filename contains hyphens."""
    spec = importlib.util.spec_from_file_location("secure_pages_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise ConfigurationError(f"Unable to load secure-page validator: {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def on_config(config: object, **kwargs: object) -> object:
    """Stop the MkDocs build when secure-page configuration is invalid."""
    validator = load_validator()
    errors = validator.validate_file(SECURE_CONFIG, Path(config["docs_dir"]))
    if errors:
        details = "\n".join(f"  - {error}" for error in errors)
        raise ConfigurationError(
            f"Secure-page configuration validation failed:\n{details}"
        )
    return config


def secure_search_location(page_path: str) -> str:
    """Convert a canonical secure URL path to an MkDocs search location."""
    return page_path.strip("/") + "/" if page_path != "/" else ""


def sanitize_search_index(search_index_path: Path) -> None:
    """Keep secure page titles while removing protected body search entries."""
    if not search_index_path.is_file():
        raise ConfigurationError(
            f"MkDocs search index was not generated: {search_index_path}"
        )

    try:
        search_index = json.loads(search_index_path.read_text(encoding="utf-8"))
        secure_config = json.loads(SECURE_CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigurationError(f"Unable to sanitize MkDocs search index: {error}") from error

    documents = search_index.get("docs")
    if not isinstance(documents, list):
        raise ConfigurationError("MkDocs search index has no valid 'docs' array")

    secure_locations = {
        secure_search_location(page["path"])
        for page in secure_config["secure_pages"]
    }
    sanitized_documents: list[object] = []

    for document in documents:
        if not isinstance(document, dict):
            raise ConfigurationError("MkDocs search index contains an invalid document entry")

        location = document.get("location")
        matching_location = next(
            (
                secure_location
                for secure_location in secure_locations
                if location == secure_location
                or (
                    isinstance(location, str)
                    and (
                        (secure_location and location.startswith(f"{secure_location}#"))
                        or (not secure_location and location.startswith("#"))
                    )
                )
            ),
            None,
        )

        if matching_location is None:
            sanitized_documents.append(document)
        elif location == matching_location:
            title_only_document = dict(document)
            title_only_document["text"] = ""
            sanitized_documents.append(title_only_document)

    search_index["docs"] = sanitized_documents
    search_index_path.write_text(
        json.dumps(search_index, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def make_404_urls_relative(not_found_path: Path) -> None:
    """Keep generated 404 assets and links inside a repository Pages prefix."""
    if not not_found_path.is_file():
        raise ConfigurationError(f"MkDocs 404 page was not generated: {not_found_path}")

    html = not_found_path.read_text(encoding="utf-8")
    relative_html = ROOT_RELATIVE_ASSET.sub(r'\g<attribute>="./', html)
    not_found_path.write_text(relative_html, encoding="utf-8")


def on_post_build(config: object, **kwargs: object) -> None:
    """Publish secure configuration and sanitize public search data."""
    site_dir = Path(config["site_dir"])
    destination = site_dir / "assets" / "config" / SECURE_CONFIG.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SECURE_CONFIG, destination)
    sanitize_search_index(site_dir / "search" / "search_index.json")
    make_404_urls_relative(site_dir / "404.html")
