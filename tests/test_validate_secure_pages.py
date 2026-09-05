"""Tests for the secure-page configuration validator."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR_PATH = PROJECT_ROOT / "scripts" / "validate-secure-pages.py"
VALID_HASH = "a" * 64
OTHER_HASH = "b" * 64


def load_validator() -> object:
    spec = importlib.util.spec_from_file_location("secure_pages_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load secure-page validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SecurePageValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = load_validator()
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.docs_dir = self.root / "docs"
        (self.docs_dir / "network").mkdir(parents=True)
        (self.docs_dir / "network" / "vyos.md").write_text("# VyOS\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_config(self, data: object) -> Path:
        config_path = self.root / "secure-pages.json"
        config_path.write_text(json.dumps(data), encoding="utf-8")
        return config_path

    def valid_page(self, **overrides: object) -> dict[str, object]:
        page: dict[str, object] = {
            "path": "/network/vyos/",
            "group": "network-internal",
            "password_hash": VALID_HASH,
        }
        page.update(overrides)
        return page

    def test_valid_configuration(self) -> None:
        errors = self.validator.validate_configuration(
            {"secure_pages": [self.valid_page()]}, self.docs_dir
        )
        self.assertEqual(errors, [])

    def test_malformed_json(self) -> None:
        config_path = self.root / "secure-pages.json"
        config_path.write_text('{"secure_pages": [', encoding="utf-8")
        errors = self.validator.validate_file(config_path, self.docs_dir)
        self.assertTrue(any("malformed JSON" in error for error in errors))

    def test_missing_required_properties(self) -> None:
        errors = self.validator.validate_configuration(
            {"secure_pages": [{"path": "/network/vyos/"}]}, self.docs_dir
        )
        self.assertTrue(any("missing required properties" in error for error in errors))

    def test_duplicate_and_conflicting_page_paths(self) -> None:
        errors = self.validator.validate_configuration(
            {
                "secure_pages": [
                    self.valid_page(),
                    self.valid_page(group="other-group", password_hash=OTHER_HASH),
                ]
            },
            self.docs_dir,
        )
        self.assertTrue(any("duplicates an earlier page path" in error for error in errors))
        self.assertTrue(any("conflicts with the earlier configuration" in error for error in errors))

    def test_empty_hash_and_invalid_groups(self) -> None:
        errors = self.validator.validate_configuration(
            {
                "secure_pages": [
                    self.valid_page(password_hash=""),
                    self.valid_page(path="/network/second/", group="Invalid Group"),
                ]
            },
            self.docs_dir,
        )
        self.assertTrue(any("password_hash must be a non-empty string" in error for error in errors))
        self.assertTrue(any("group must use lowercase" in error for error in errors))

    def test_group_with_conflicting_hashes(self) -> None:
        (self.docs_dir / "network" / "second.md").write_text("# Second\n", encoding="utf-8")
        errors = self.validator.validate_configuration(
            {
                "secure_pages": [
                    self.valid_page(),
                    self.valid_page(path="/network/second/", password_hash=OTHER_HASH),
                ]
            },
            self.docs_dir,
        )
        self.assertTrue(any("pages in one group must share" in error for error in errors))

    def test_missing_document_path(self) -> None:
        errors = self.validator.validate_configuration(
            {"secure_pages": [self.valid_page(path="/network/missing/")]},
            self.docs_dir,
        )
        self.assertTrue(any("does not correspond to a documentation page" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
