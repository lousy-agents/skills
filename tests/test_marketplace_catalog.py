#!/usr/bin/env python3
"""Install-path tests for .claude-plugin/marketplace.json.

Claude Code resolves a `./` plugin source from the repository root and does not
apply `metadata.pluginRoot` to it, so `"source": "./<name>"` fails at install
time with "Source path does not exist" even though the JSON is valid. These
tests catch that class of break without needing the `claude` CLI in CI.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
SKILLS_DIR = REPO_ROOT / "skills"


def load_plugins() -> list[dict]:
    return json.loads(MARKETPLACE.read_text(encoding="utf-8"))["plugins"]


class MarketplaceCatalogTest(unittest.TestCase):
    def test_every_source_resolves_from_repo_root_to_a_plugin(self) -> None:
        for plugin in load_plugins():
            with self.subTest(plugin=plugin["name"]):
                source = REPO_ROOT / plugin["source"]
                self.assertTrue(
                    (source / ".claude-plugin" / "plugin.json").is_file(),
                    f'{plugin["source"]} has no .claude-plugin/plugin.json relative to the repo root',
                )
                self.assertTrue((source / "SKILL.md").is_file(), f'{plugin["source"]} has no SKILL.md')

    def test_plugin_manifest_name_matches_marketplace_entry(self) -> None:
        for plugin in load_plugins():
            with self.subTest(plugin=plugin["name"]):
                manifest = REPO_ROOT / plugin["source"] / ".claude-plugin" / "plugin.json"
                if manifest.is_file():
                    self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["name"], plugin["name"])

    def test_every_published_skill_is_in_the_marketplace(self) -> None:
        listed = {plugin["name"] for plugin in load_plugins()}
        published = {path.parent.parent.name for path in SKILLS_DIR.glob("*/.claude-plugin/plugin.json")}
        self.assertEqual(published - listed, set())


if __name__ == "__main__":
    unittest.main()
