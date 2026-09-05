"""Tests for protected-page filtering in the MkDocs search index."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parent.parent
HOOK_PATH = PROJECT_ROOT / "scripts" / "mkdocs_hooks.py"


def load_hooks() -> object:
    spec = importlib.util.spec_from_file_location("mkdocs_hooks", HOOK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load MkDocs hooks")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SearchSanitizerTests(unittest.TestCase):
    def test_keeps_secure_title_and_removes_secure_sections(self) -> None:
        hooks = load_hooks()
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            config_path = root / "secure-pages.json"
            index_path = root / "search_index.json"
            config_path.write_text(
                json.dumps(
                    {
                        "secure_pages": [
                            {
                                "path": "/network/vyos/",
                                "group": "vyos",
                                "password_hash": "a" * 64,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            index_path.write_text(
                json.dumps(
                    {
                        "config": {},
                        "docs": [
                            {"location": "network/vyos/", "title": "VyOS", "text": ""},
                            {
                                "location": "network/vyos/#commands",
                                "title": "Commands",
                                "text": "protected sentinel",
                            },
                            {
                                "location": "network/bgp/#verification",
                                "title": "Verification",
                                "text": "public sentinel",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with patch.object(hooks, "SECURE_CONFIG", config_path):
                hooks.sanitize_search_index(index_path)

            documents = json.loads(index_path.read_text(encoding="utf-8"))["docs"]
            self.assertEqual(
                documents,
                [
                    {"location": "network/vyos/", "title": "VyOS", "text": ""},
                    {
                        "location": "network/bgp/#verification",
                        "title": "Verification",
                        "text": "public sentinel",
                    },
                ],
            )

    def test_makes_generated_404_urls_relative(self) -> None:
        hooks = load_hooks()
        with tempfile.TemporaryDirectory() as temporary_directory:
            not_found_path = Path(temporary_directory) / "404.html"
            not_found_path.write_text(
                '<link href="/assets/main.css"><a href="/network/">Network</a>'
                '<a href="https://example.com/">External</a>',
                encoding="utf-8",
            )
            hooks.make_404_urls_relative(not_found_path)
            html = not_found_path.read_text(encoding="utf-8")
            self.assertIn('href="./assets/main.css"', html)
            self.assertIn('href="./network/"', html)
            self.assertIn('href="https://example.com/"', html)


if __name__ == "__main__":
    unittest.main()
