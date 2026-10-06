#!/usr/bin/env python3
"""Keeps every copy of the EARS Contract identical to the canonical one.

The `to-ears` skill owns the EARS method. Consuming skills install one at a
time (`npx skills add … --skill <name>`), so each carries a verbatim copy of the
compact contract block rather than a cross-skill path that would break when
`to-ears` is absent. This suite turns "verbatim" from a promise into a gate:
a copy that drifts, a marker that goes missing, or a lint table that stops
agreeing with the contract fails CI.

Stdlib only, matching the rest of `tests/`.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = REPO_ROOT / "skills"
CANONICAL = SKILLS / "to-ears" / "references" / "ears-contract.md"
MIRRORS = [
    SKILLS / "feature-to-plan" / "references" / "ears-contract.md",
    SKILLS / "issue-refine-loop" / "references" / "epic-structure.md",
]
# Files that once carried their own EARS tables and must not grow one back.
FORMER_TABLE_HOMES = [
    *MIRRORS,
    SKILLS / "feature-to-plan" / "references" / "spec-format.md",
]
LINT_SCRIPT = SKILLS / "spec-auditor" / "scripts" / "spec_audit_lint.py"
AUDIT_RUBRIC = SKILLS / "spec-auditor" / "references" / "audit-rubric.md"

BEGIN = "<!-- ears-contract:begin -->"
END = "<!-- ears-contract:end -->"

sys.dont_write_bytecode = True


def _load_lint():
    spec = importlib.util.spec_from_file_location("spec_audit_lint_for_contract", LINT_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def contract_block(path: Path) -> str:
    """The text between the markers. Exactly one block per file — a second
    block would let a stale copy hide behind a fresh one."""
    text = path.read_text(encoding="utf-8")
    begins = text.count(BEGIN)
    ends = text.count(END)
    if begins != 1 or ends != 1:
        raise AssertionError(f"{path}: expected one contract block, found {begins} begin / {ends} end markers")
    start = text.index(BEGIN) + len(BEGIN)
    stop = text.index(END)
    if stop < start:
        raise AssertionError(f"{path}: end marker precedes begin marker")
    return text[start:stop]


def contract_vague_terms(block: str) -> list[str]:
    match = re.search(r"^\*\*Vague terms\.\*\*\s+(.+)$", block, re.M)
    if not match:
        raise AssertionError("contract has no `**Vague terms.**` line")
    return [term.strip() for term in match.group(1).split(",") if term.strip()]


def contract_openers(block: str) -> set[str]:
    """Opening keywords of every pattern template in the contract table."""
    openers = set()
    for row in re.findall(r"^\| (?!Pattern \|)[A-Z][^|]+\| (.+?) \|", block, re.M):
        first = row.split()[0].strip("`").lower()
        openers.add(first)
    if "during" in block.lower():
        openers.add("during")
    return openers


class ContractMirrorTests(unittest.TestCase):
    def test_canonical_block_is_present_and_nonempty(self):
        self.assertGreater(len(contract_block(CANONICAL).strip()), 500)

    def test_every_mirror_is_byte_identical_to_the_canonical_block(self):
        canonical = contract_block(CANONICAL)
        for mirror in MIRRORS:
            with self.subTest(mirror=str(mirror.relative_to(REPO_ROOT))):
                self.assertEqual(
                    contract_block(mirror),
                    canonical,
                    "EARS Contract copy drifted from skills/to-ears/references/ears-contract.md — "
                    "edit the canonical file and every mirror in the same change",
                )

    def test_a_drifted_copy_would_be_detected(self):
        # Guards the comparison itself: one changed character must not compare equal.
        canonical = contract_block(CANONICAL)
        self.assertNotEqual(canonical.replace("shall", "should", 1), canonical)

    def test_no_superseded_six_pattern_table_survives_in_a_mirror(self):
        # The pre-contract tables listed a sixth "Complex" pattern and an
        # "is enabled" Optional template. Either reappearing means a stale copy
        # was pasted back beside the contract.
        for mirror in FORMER_TABLE_HOMES:
            text = mirror.read_text(encoding="utf-8")
            with self.subTest(mirror=str(mirror.relative_to(REPO_ROOT))):
                self.assertNotIn("| Complex ", text)
                self.assertNotIn("is enabled, the `<system>` shall", text)


class LintAgreesWithContractTests(unittest.TestCase):
    """spec-auditor's lint is code, so it cannot mirror the block; it must agree with it."""

    @classmethod
    def setUpClass(cls):
        cls.lint = _load_lint()
        cls.block = contract_block(CANONICAL)

    def test_lint_vague_terms_equal_the_contract_list(self):
        self.assertEqual(sorted(self.lint.AMBIGUOUS_TERMS), sorted(contract_vague_terms(self.block)))

    def test_lint_recognizes_every_contract_opener(self):
        lint_openers = {opener.strip() for opener in self.lint.EARS_STARTS}
        missing = contract_openers(self.block) - lint_openers
        self.assertEqual(missing, set(), f"lint EARS_STARTS lacks contract openers: {sorted(missing)}")

    def test_audit_rubric_names_every_contract_vague_term(self):
        rubric = AUDIT_RUBRIC.read_text(encoding="utf-8").lower()
        missing = [t for t in contract_vague_terms(self.block) if t not in rubric]
        self.assertEqual(missing, [], "spec-auditor's Pass 3 must check the contract's full vague-term list")

    def test_contract_examples_read_as_ears_to_the_lint(self):
        examples = re.findall(r"^- `(- AC-[^`]+)`$", self.block, re.M)
        self.assertGreaterEqual(len(examples), 3)
        for example in examples:
            with self.subTest(example=example):
                self.assertTrue(self.lint.is_ears_like(example))


if __name__ == "__main__":
    unittest.main()
