#!/usr/bin/env python3
"""Behavioral tests for skills/spec-auditor/scripts/spec_audit_lint.py.

Stdlib only — the repository has no dependency manifest and CI provides just
`python3`. Every test names a defect reported in issue #38 and fails against
the pre-fix script, so a green run is evidence the defect is gone rather than
evidence the file merely parses.

Fixtures are built by mutating one known-good spec. `variant()` refuses a
substitution that does not match, so a typo in a fixture fails loudly instead
of silently re-testing the baseline.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "spec-auditor" / "scripts" / "spec_audit_lint.py"
SPEC_FORMAT = REPO_ROOT / "skills" / "feature-to-plan" / "references" / "spec-format.md"


# The script lives inside a skill folder that ships to users via `npx skills add`.
# Loading it by path would drop a __pycache__ directory in there, so bytecode
# writing is disabled before the import.
sys.dont_write_bytecode = True


def _load_module():
    # The parent directory is `spec-auditor`, which is not a legal module name,
    # so the script is loaded by path rather than imported.
    spec = importlib.util.spec_from_file_location("spec_audit_lint", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    # Register before exec: the module defines dataclasses, and @dataclass
    # resolves annotations through sys.modules[cls.__module__].
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


lint_module = _load_module()


# A spec that satisfies every check the script makes. Deliberately free of terms
# on AMBIGUOUS_TERMS so ambiguity assertions stay unambiguous.
BASELINE = '''# Feature: Password reset

## Problem Statement

Account holders who forget a password cannot regain access without an operator.

## Personas

| Persona | Impact |
| --- | --- |
| Account holder | Locked out until an operator intervenes |
| Operator | Absorbs manual reset requests |

## Value Assessment

Removes the manual reset queue and its operator cost.

## User Stories

### Story 1: Request a reset link

As a **account holder**,
I want **a reset link sent to my address**,
so that I can **regain access without an operator**.

#### Acceptance Criteria

- When the account holder requests a reset, the system shall send a signed link.
- If the link is older than one hour, the system shall reject it with `410`.

### Story 2: Audit completed resets

As a **operator**,
I want **an audit record for each reset**,
so that I can **trace who reset which account**.

#### Acceptance Criteria

- When a reset completes, the system shall write an audit record.

## Design

### Diagrams

```mermaid
flowchart TB
  A[Reset request] --> B[Token service]
  B --> C[Mailer]
```

```mermaid
sequenceDiagram
  AccountHolder->>API: POST /reset
  API-->>AccountHolder: 202 Accepted
```

## Tasks

### Task 1: Add the reset endpoint

**Objective**: Add `POST /reset` behind the existing rate limiter.

**Context**: No route issues reset tokens today.

**Affected files**:
- `src/auth/reset.ts`

**Requirements**:
- Reject more than five requests per hour per address.

**Verification**:
- `npm test src/auth/reset.test.ts`

**Done when**:
- [ ] The endpoint returns `202` for a known address.

## Out of Scope

- Delivery over SMS.

## Future Considerations

- Passkey enrollment as a reset path.
'''

STORY_2_CRITERIA = (
    "#### Acceptance Criteria\n\n"
    "- When a reset completes, the system shall write an audit record.\n"
)
STORY_1_CRITERIA = (
    "#### Acceptance Criteria\n\n"
    "- When the account holder requests a reset, the system shall send a signed link.\n"
    "- If the link is older than one hour, the system shall reject it with `410`.\n"
)
FLOWCHART_BLOCK = (
    "```mermaid\nflowchart TB\n  A[Reset request] --> B[Token service]\n  B --> C[Mailer]\n```\n"
)
SEQUENCE_BLOCK = (
    "```mermaid\nsequenceDiagram\n  AccountHolder->>API: POST /reset\n"
    "  API-->>AccountHolder: 202 Accepted\n```\n"
)


def variant(old: str, new: str, source: str = BASELINE) -> str:
    """Replace `old` once, refusing a no-op substitution."""
    if old not in source:
        raise AssertionError(f"fixture anchor not found, test would be vacuous: {old!r}")
    return source.replace(old, new, 1)


@contextmanager
def spec_file(text: str):
    """A spec on disk for the duration of one assertion."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as handle:
        handle.write(text)
        path = Path(handle.name)
    try:
        yield path
    finally:
        path.unlink()


def lint(text: str):
    with spec_file(text) as path:
        return lint_module.run_lint(path)


def titles(findings) -> list[str]:
    return [f.title for f in findings]


def matching(findings, needle: str):
    return [f for f in findings if needle.lower() in f.title.lower()]


def has_title(findings, needle: str) -> bool:
    return bool(matching(findings, needle))


class BaselineTests(unittest.TestCase):
    """Guards the shared fixture. If these fail, every other test is meaningless."""

    def test_baseline_produces_no_high_findings(self):
        highs = [f for f in lint(BASELINE) if f.severity == "High"]
        self.assertEqual(highs, [], f"baseline should be clean, got: {titles(highs)}")

    def test_baseline_reports_no_ambiguous_terms(self):
        self.assertEqual(matching(lint(BASELINE), "ambiguous term"), [])

    def test_variant_refuses_vacuous_substitution(self):
        with self.assertRaises(AssertionError):
            variant("text that is definitely not in the baseline", "x")


class FenceScannerTests(unittest.TestCase):
    """Which lines a document treats as fenced code, per CommonMark."""

    def classify(self, text: str) -> list[bool]:
        return lint_module.build_doc(text.split("\n")).in_code

    def test_backtick_fence_marks_delimiters_and_body(self):
        flags = self.classify("before\n```\ninside\n```\nafter")
        self.assertEqual(flags, [False, True, True, True, False])

    def test_tilde_fence_is_not_closed_by_backticks(self):
        flags = self.classify("~~~\n```\nstill inside\n~~~\nafter")
        self.assertEqual(flags, [True, True, True, True, False])

    def test_shorter_inner_fence_does_not_close_a_longer_one(self):
        # This is exactly the shape used by feature-to-plan/references/spec-format.md.
        flags = self.classify("````markdown\n```mermaid\nflowchart TB\n```\n````\nafter")
        self.assertEqual(flags, [True, True, True, True, True, False])

    def test_longer_closer_closes_a_shorter_opener(self):
        self.assertEqual(
            self.classify("before\n```\ncode\n````\nafter"),
            [False, True, True, True, False],
            "a closer at least as long as its opener closes the fence",
        )

    def test_two_backticks_do_not_open_a_fence(self):
        self.assertEqual(self.classify("before\n``\ninside\nafter"), [False] * 4)

    def test_closer_may_not_carry_an_info_string(self):
        flags = self.classify("```py\ncode\n```py\nstill inside\n```\nafter")
        self.assertEqual(flags, [True, True, True, True, True, False])

    def test_unterminated_fence_runs_to_end_of_document(self):
        flags = self.classify("before\n```\nno closer here")
        self.assertEqual(flags, [False, True, True])

    def test_unterminated_fence_is_still_recorded_as_a_fence(self):
        doc = lint_module.build_doc("# F\n\n## Design\n\n```mermaid\nflowchart TB\n  A --> B".split("\n"))
        self.assertEqual(
            [(f.open_line, f.close_line, f.info) for f in doc.fences],
            [(5, None, "mermaid")],
            "an unterminated block is still a fence; dropping it loses the diagram",
        )

    def test_three_space_indent_opens_a_fence_but_four_does_not(self):
        self.assertEqual(self.classify("   ```\ninside\n   ```"), [True, True, True])
        self.assertEqual(self.classify("    ```\nnot a fence"), [False, False])

    def test_real_spec_format_reference_has_no_top_level_mermaid_fence(self):
        # spec-format.md wraps every mermaid example in a four-backtick fence, so a
        # correct scanner sees zero top-level mermaid blocks. Asserted structurally
        # so the test survives edits to that reference.
        doc = lint_module.build_doc(SPEC_FORMAT.read_text(encoding="utf-8").split("\n"))
        infos = [f.info.split()[0].lower() for f in doc.fences if f.info.split()]
        self.assertNotIn("mermaid", infos)


class FencedContentTests(unittest.TestCase):
    """Fenced blocks are illustrations, so no check reads them as spec content."""

    def test_fenced_heading_does_not_satisfy_required_section(self):
        spec = variant(
            "Account holders who forget a password cannot regain access without an operator.",
            "Account holders cannot regain access. A spec must not stop at:\n\n"
            "```markdown\n## Tasks\n\n### Task 1: Do the thing\n```",
        )
        spec = variant("## Tasks\n\n### Task 1: Add the reset endpoint", "### Task 1: Add the reset endpoint", spec)
        self.assertTrue(
            has_title(lint(spec), "Missing required section: Tasks"),
            "a fenced `## Tasks` example must not satisfy the required-section check",
        )

    def test_fenced_todo_is_not_flagged(self):
        spec = variant(
            "## Out of Scope",
            "## Out of Scope\n\nAvoid placeholders such as:\n\n```markdown\nTODO: decide later\n```\n",
        )
        self.assertEqual(matching(lint(spec), "placeholder marker"), [])

    def test_fenced_ambiguous_term_is_not_flagged(self):
        spec = variant(
            "## Out of Scope",
            "## Out of Scope\n\nDo not write criteria like:\n\n"
            "```markdown\nThe system shall be fast and robust.\n```\n",
        )
        self.assertEqual(matching(lint(spec), "ambiguous term"), [])

    def test_fenced_checked_checkbox_is_not_flagged(self):
        spec = variant(
            "## Out of Scope",
            "## Out of Scope\n\nDrafts must not ship pre-checked boxes:\n\n"
            "```markdown\n- [x] Already done\n```\n",
        )
        self.assertEqual(matching(lint(spec), "Completed checkbox"), [])

    def test_mermaid_fence_nested_in_a_wider_fence_does_not_count(self):
        spec = variant(
            FLOWCHART_BLOCK + "\n" + SEQUENCE_BLOCK,
            "Diagrams are written like this:\n\n"
            "````markdown\n```mermaid\nflowchart TB\n  A --> B\n```\n````\n",
        )
        self.assertTrue(
            has_title(lint(spec), "No Mermaid diagrams found"),
            "a mermaid fence nested inside a four-backtick example fence is not a real diagram",
        )

    def test_fenced_bullets_do_not_satisfy_acceptance_criteria(self):
        spec = variant(
            "- When a reset completes, the system shall write an audit record.",
            "```markdown\n- When a reset completes, the system shall write an audit record.\n```",
        )
        self.assertTrue(
            has_title(lint(spec), "Empty acceptance criteria section"),
            "bullets inside an illustrative fence are not acceptance criteria",
        )

    def test_fenced_task_heading_does_not_count_as_a_task(self):
        spec = variant(
            "### Task 1: Add the reset endpoint",
            "```markdown\n### Task 1: Add the reset endpoint\n```",
        )
        self.assertTrue(
            has_title(lint(spec), "No numbered task headings found"),
            "a fenced task example is not a real task",
        )

    def test_fenced_task_fields_do_not_satisfy_required_fields(self):
        spec = variant(
            "**Objective**: Add `POST /reset` behind the existing rate limiter.",
            "```markdown\n**Objective**: <what this accomplishes>\n```",
        )
        self.assertTrue(
            [f for f in lint(spec) if "objective" in f.title.lower()],
            "a field shown inside a fenced example is an illustration, not a value",
        )

    def test_a_backtick_in_the_info_string_does_not_open_a_fence(self):
        spec = variant(
            "Account holders who forget a password cannot regain access without an operator.",
            "Account holders cannot regain access without an operator.\n\n```text `inline` sample",
        )
        self.assertEqual(
            matching(lint(spec), "Missing required section"),
            [],
            "a line with a backtick in its info string is prose; treating it as a fence eats the document",
        )


class RequiredSectionTests(unittest.TestCase):
    """Which headings satisfy the template's required sections."""

    EXPECTED_REQUIRED_SECTIONS = [
        "Problem Statement",
        "Personas",
        "Value Assessment",
        "User Stories",
        "Design",
        "Tasks",
        "Out of Scope",
        "Future Considerations",
    ]

    def test_every_required_section_is_reported_when_absent(self):
        for name in self.EXPECTED_REQUIRED_SECTIONS:
            with self.subTest(section=name):
                spec = BASELINE.replace(f"## {name}", f"## Renamed {name}", 1)
                self.assertTrue(has_title(lint(spec), f"Missing required section: {name}"))

    def test_the_required_section_list_matches_the_template(self):
        self.assertEqual(lint_module.REQUIRED_SECTIONS, self.EXPECTED_REQUIRED_SECTIONS)

    def test_nested_heading_does_not_satisfy_required_section(self):
        spec = variant("## Tasks\n\n### Task 1:", "#### Tasks\n\n### Task 1:")
        self.assertTrue(
            has_title(lint(spec), "Missing required section: Tasks"),
            "a level-4 heading titled Tasks is not the required level-2 section",
        )

    def test_a_section_heading_at_any_other_level_does_not_satisfy_the_requirement(self):
        for hashes in ("#", "###", "####", "#####", "######"):
            with self.subTest(level=len(hashes)):
                spec = variant("## Tasks\n", f"{hashes} Tasks\n")
                self.assertTrue(has_title(lint(spec), "Missing required section: Tasks"))

    def test_hashes_without_a_space_are_not_a_heading(self):
        spec = variant("## Problem Statement", "##Problem Statement")
        self.assertTrue(has_title(lint(spec), "Missing required section: Problem Statement"))

    def test_a_trailing_colon_does_not_break_a_section_title(self):
        spec = variant("## Personas", "## Personas:")
        self.assertEqual(matching(lint(spec), "Missing required section"), [])

    def test_stakeholders_satisfies_personas(self):
        spec = variant("## Personas", "## Stakeholders")
        self.assertFalse(
            has_title(lint(spec), "Missing required section: Personas"),
            "feature-to-plan sanctions `## Stakeholders` for `## Personas`",
        )

    def test_acceptance_opens_an_acceptance_criteria_section(self):
        spec = BASELINE.replace("#### Acceptance Criteria", "#### Acceptance")
        findings = lint(spec)
        self.assertFalse(has_title(findings, "No acceptance criteria bullets found"))
        self.assertFalse(
            any("story has no" in f.title.lower() for f in findings),
            "`#### Acceptance` must satisfy the per-story criteria check too",
        )

    def test_unsanctioned_title_is_still_flagged(self):
        spec = variant("## Personas", "## Cast Of Characters")
        self.assertTrue(has_title(lint(spec), "Missing required section: Personas"))


class PlaceholderMarkerTests(unittest.TestCase):
    """Which unresolved-placeholder markers a spec is flagged for."""

    def test_bare_question_mark_placeholder_is_flagged(self):
        spec = variant("**Context**: No route issues reset tokens today.", "**Context**: ???")
        self.assertTrue(has_title(lint(spec), "placeholder marker"))

    def test_four_question_marks_are_flagged(self):
        spec = variant("**Context**: No route issues reset tokens today.", "**Context**: ????")
        self.assertTrue(has_title(lint(spec), "placeholder marker"))

    def test_two_question_marks_are_not_a_placeholder(self):
        spec = variant(
            "**Context**: No route issues reset tokens today.",
            "**Context**: Reset volume today?? Unmeasured but nonzero.",
        )
        self.assertEqual(matching(lint(spec), "placeholder marker"), [])

    def test_ordinary_question_is_not_flagged(self):
        spec = variant("- Delivery over SMS.", "- Delivery over SMS. Is that right?")
        self.assertEqual(matching(lint(spec), "placeholder marker"), [])

    def test_word_markers_still_flagged(self):
        spec = variant("**Context**: No route issues reset tokens today.", "**Context**: TBD")
        self.assertTrue(has_title(lint(spec), "placeholder marker"))

    def test_every_placeholder_marker_is_flagged_in_any_case(self):
        for marker in ("TODO", "TBD", "FIXME", "XXX", "todo", "Fixme"):
            with self.subTest(marker=marker):
                spec = variant(
                    "**Context**: No route issues reset tokens today.",
                    f"**Context**: {marker} decide the token store.",
                )
                self.assertTrue(has_title(lint(spec), "placeholder marker"))


class AcceptanceCriteriaTests(unittest.TestCase):
    """Whether criteria bullets exist and read as EARS."""

    def test_non_ears_criterion_is_still_flagged(self):
        spec = variant(
            "- When a reset completes, the system shall write an audit record.",
            "- Audit records get written.",
        )
        self.assertTrue(has_title(lint(spec), "EARS"))

    def test_an_ears_opener_without_shall_is_not_ears_like(self):
        spec = variant(
            "- When a reset completes, the system shall write an audit record.",
            "- The system writes an audit record.",
        )
        self.assertTrue(
            has_title(lint(spec), "may not be EARS-like"),
            "an EARS opener without `shall` states no obligation",
        )

    def test_every_ears_opener_is_recognized(self):
        for opener in (
            "When a reset completes",
            "While a reset is pending",
            "Where audit logging is enabled",
            "If the token is expired",
        ):
            with self.subTest(opener=opener):
                spec = variant(
                    "- When a reset completes, the system shall write an audit record.",
                    f"- {opener}, the system shall write an audit record.",
                )
                self.assertEqual(matching(lint(spec), "may not be EARS-like"), [])

    def test_shall_must_be_a_whole_word(self):
        spec = variant(
            "- When a reset completes, the system shall write an audit record.",
            "- When a reset completes, the operator marshalls the audit record.",
        )
        self.assertTrue(has_title(lint(spec), "may not be EARS-like"))

    def test_a_checkbox_prefix_does_not_break_ears_detection(self):
        spec = variant(
            "- When a reset completes, the system shall write an audit record.",
            "- [ ] When a reset completes, the system shall write an audit record.",
        )
        self.assertEqual(matching(lint(spec), "may not be EARS-like"), [])

    def test_exactly_half_ears_is_not_reported_as_mostly_non_ears(self):
        spec = variant(
            "- When a reset completes, the system shall write an audit record.",
            "- Audit records get written.\n- Reports get generated.",
        )
        self.assertFalse(has_title(lint(spec), "Most acceptance criteria are not EARS-like"))

    def test_below_half_ears_is_reported(self):
        spec = variant(
            "- When a reset completes, the system shall write an audit record.",
            "- Audit records get written.\n- Reports get generated.\n- Logs get rotated.",
        )
        self.assertTrue(has_title(lint(spec), "Most acceptance criteria are not EARS-like"))


class PerStoryAcceptanceCriteriaTests(unittest.TestCase):
    """Every story carries criteria of its own, at the right level."""

    def test_story_without_acceptance_criteria_is_flagged(self):
        spec = variant(STORY_2_CRITERIA, "")
        findings = [f for f in lint(spec) if "story has no" in f.title.lower()]
        self.assertTrue(
            findings,
            "a story with no criteria must be flagged even when another story has plenty",
        )
        self.assertEqual(findings[0].severity, "High")

    def test_only_the_uncovered_story_is_flagged(self):
        spec = variant(STORY_2_CRITERIA, "")
        findings = [f for f in lint(spec) if "story has no" in f.title.lower()]
        self.assertEqual(len(findings), 1, f"expected exactly one story finding, got {titles(findings)}")
        self.assertIn("Audit completed resets", findings[0].evidence)

    def test_covered_stories_produce_no_story_findings(self):
        self.assertEqual([f for f in lint(BASELINE) if "story has no" in f.title.lower()], [])

    def test_numbered_story_heading_form_is_recognized(self):
        spec = variant(STORY_1_CRITERIA, "")
        self.assertTrue(
            [f for f in lint(spec) if "story has no" in f.title.lower()],
            "`### Story 1: <Title>` is the template's own numbered form",
        )

    def test_unnumbered_story_heading_form_is_recognized(self):
        spec = variant("### Story 2: Audit completed resets", "### Story: Audit completed resets")
        spec = variant(STORY_2_CRITERIA, "", spec)
        self.assertTrue(
            [f for f in lint(spec) if "story has no" in f.title.lower()],
            "`### Story: <Title>` appears in spec-format.md and must match too",
        )

    def test_a_lowercase_story_heading_is_still_a_story(self):
        spec = variant("### Story 2: Audit completed resets", "### story 2: Audit completed resets")
        spec = variant(STORY_2_CRITERIA, "", spec)
        self.assertTrue([f for f in lint(spec) if "story has no" in f.title.lower()])

    def test_storybook_heading_is_not_treated_as_a_story(self):
        spec = variant(
            "## Out of Scope",
            "### Storybook integration\n\nNot planned for this release.\n\n## Out of Scope",
        )
        self.assertEqual(
            [f for f in lint(spec) if "storybook" in f.evidence.lower()],
            [],
            "`### Storybook integration` is not a user story",
        )

    def test_a_story_at_any_level_other_than_three_is_reported(self):
        for hashes in ("##", "####", "#####"):
            with self.subTest(level=len(hashes)):
                spec = variant("### Story 2: Audit completed resets", f"{hashes} Story 2: Audit completed resets")
                self.assertTrue(
                    [f for f in lint(spec) if "story heading must be level 3" in f.title.lower()]
                )

    def test_story_at_the_wrong_level_is_reported_not_skipped(self):
        spec = variant("### Story 2: Audit completed resets", "#### Story 2: Audit completed resets")
        spec = variant(STORY_2_CRITERIA, "", spec)
        level = [f for f in lint(spec) if "story heading must be level 3" in f.title.lower()]
        self.assertTrue(level, "a misplaced story must not silently escape the checks")
        self.assertEqual(level[0].severity, "Medium")

    def test_a_misplaced_story_is_still_checked_for_criteria(self):
        spec = variant("### Story 2: Audit completed resets", "#### Story 2: Audit completed resets")
        spec = variant(STORY_2_CRITERIA, "", spec)
        self.assertTrue(
            [f for f in lint(spec) if "story has no" in f.title.lower()],
            "reporting the level must not replace checking the story",
        )

    def test_criteria_at_the_same_level_as_the_story_still_count(self):
        # The template nests criteria at level 4, but a spec that writes them at
        # level 3 must not be told its stories have none.
        spec = BASELINE.replace("#### Acceptance Criteria", "### Acceptance Criteria")
        findings = lint(spec)
        self.assertEqual(
            [f for f in findings if "story has no" in f.title.lower()],
            [],
            "criteria written at the story's own level still belong to that story",
        )
        self.assertTrue(
            [f for f in findings if "not nested" in f.title.lower()],
            "the nesting is still worth reporting, just not as missing criteria",
        )

    def test_level_two_acceptance_alias_still_covers_its_story(self):
        # `## Acceptance` is a sanctioned title. At level 2 it must not end the
        # story it belongs to and then be reported as missing from it.
        spec = BASELINE.replace("#### Acceptance Criteria", "## Acceptance")
        self.assertEqual(
            [f for f in lint(spec) if "story has no" in f.title.lower()],
            [],
            "a level-2 acceptance heading belongs to its story, not after it",
        )

    def test_criteria_after_the_next_story_do_not_cover_the_previous_one(self):
        spec = variant(STORY_1_CRITERIA, "")
        findings = [f for f in lint(spec) if "story has no" in f.title.lower()]
        self.assertEqual(len(findings), 1)
        self.assertIn("Request a reset link", findings[0].evidence)

    def test_criteria_in_a_later_section_do_not_cover_the_last_story(self):
        spec = variant(STORY_2_CRITERIA, "")
        spec = variant("### Diagrams", "#### Acceptance Criteria\n\n- The system shall render.\n\n### Diagrams", spec)
        self.assertTrue(
            [f for f in lint(spec) if "story has no" in f.title.lower()],
            "an Acceptance Criteria heading under `## Design` does not cover a story",
        )

    def test_a_deeper_next_story_does_not_lend_its_criteria_backwards(self):
        spec = variant(STORY_1_CRITERIA, "")
        spec = variant("### Story 2: Audit completed resets", "#### Story 2: Audit completed resets", spec)
        uncovered = [f for f in lint(spec) if "story has no" in f.title.lower()]
        self.assertTrue(uncovered, "story 2's criteria belong to story 2 even when it is nested deeper")
        self.assertIn("Story 1", uncovered[0].evidence)

    def test_criteria_at_or_above_the_story_level_are_reported_as_unnested(self):
        # A level-2 criteria heading after a level-3 story is ambiguous: it could
        # be that story's criteria under a sanctioned alias, or a separate
        # document section. The script reports the structure instead of guessing,
        # and in particular does not claim the story has no criteria at all.
        spec = variant(STORY_2_CRITERIA, "")
        spec = variant(
            "## Design",
            "## Acceptance Criteria\n\n- When a reset completes, the system shall write an audit record.\n\n## Design",
            spec,
        )
        unnested = [f for f in lint(spec) if "not nested" in f.title.lower()]
        self.assertTrue(unnested, "an unnested criteria heading must be reported, not silently accepted")
        self.assertEqual(unnested[0].severity, "Medium")

    def test_unnested_criteria_are_not_also_reported_as_absent(self):
        spec = variant(STORY_2_CRITERIA, "")
        spec = variant(
            "## Design",
            "## Acceptance Criteria\n\n- When a reset completes, the system shall write an audit record.\n\n## Design",
            spec,
        )
        self.assertEqual(
            [f for f in lint(spec) if "story has no" in f.title.lower()],
            [],
            "criteria that exist must not be reported as absent",
        )

    def test_properly_nested_criteria_are_not_reported_as_unnested(self):
        self.assertEqual([f for f in lint(BASELINE) if "not nested" in f.title.lower()], [])

    def test_a_stray_alias_does_not_unnest_correctly_nested_criteria(self):
        spec = variant(
            "### Story 2: Audit completed resets",
            "## Acceptance\n\n- When an operator reviews a reset, the system shall show the actor.\n\n"
            "### Story 2: Audit completed resets",
        )
        self.assertEqual(
            [f for f in lint(spec) if "not nested" in f.title.lower()],
            [],
            "story 1 has its own nested criteria; a later top-level alias does not unnest them",
        )


class TaskTests(unittest.TestCase):
    """Which headings are tasks, and which fields each task must carry."""

    def test_level_three_task_heading_is_accepted(self):
        self.assertFalse(has_title(lint(BASELINE), "No numbered task headings found"))

    def test_task_heading_below_level_three_is_reported_as_a_level_problem(self):
        spec = variant("### Task 1: Add the reset endpoint", "##### Task 1: Add the reset endpoint")
        level_findings = matching(lint(spec), "level 3")
        self.assertTrue(level_findings, "a `##### Task 1` heading is a task at the wrong level")
        self.assertEqual(level_findings[0].severity, "Medium")

    def test_a_misplaced_task_is_not_reported_as_an_absent_one(self):
        spec = variant("### Task 1: Add the reset endpoint", "##### Task 1: Add the reset endpoint")
        self.assertFalse(
            has_title(lint(spec), "No numbered task headings found"),
            "the tasks exist; reporting them as absent misdirects the author",
        )

    def test_level_two_task_heading_does_not_end_the_tasks_section(self):
        spec = variant("### Task 1: Add the reset endpoint", "## Task 1: Add the reset endpoint")
        self.assertFalse(
            has_title(lint(spec), "No numbered task headings found"),
            "a level-2 task heading is a misplaced task, not an absent one",
        )

    def test_a_level_two_task_heading_is_reported_as_a_level_problem(self):
        spec = variant("### Task 1: Add the reset endpoint", "## Task 1: Add the reset endpoint")
        self.assertTrue([f for f in lint(spec) if "level 3" in f.title.lower()])

    def test_a_level_four_tasks_heading_does_not_open_the_tasks_section(self):
        # The section must be empty of tasks, or the assertion passes even when
        # find_section wrongly matches the level-4 heading.
        spec = variant("## Tasks\n", "#### Tasks\n")
        spec = variant("### Task 1: Add the reset endpoint", "#### Work item", spec)
        self.assertFalse(
            has_title(lint(spec), "No numbered task headings found"),
            "there is no level-2 Tasks section, so lint_tasks must not run at all",
        )

    def test_a_sibling_heading_ends_the_tasks_section(self):
        spec = variant(
            "## Future Considerations\n\n- Passkey enrollment as a reset path.",
            "## Future Considerations\n\n### Task 2: Revisit token lifetime\n\n- Passkey enrollment as a reset path.",
        )
        self.assertEqual(
            [f for f in lint(spec) if "Task 2" in f.evidence],
            [],
            "a task heading under a later section is not inside `## Tasks`",
        )

    def test_tasks_section_with_no_task_headings_is_still_high(self):
        spec = variant(
            "### Task 1: Add the reset endpoint",
            "Implementation is left to the reader.\n\nIGNORED_MARKER",
        )
        spec = spec[: spec.index("IGNORED_MARKER")] + "## Out of Scope" + spec.split("## Out of Scope", 1)[1]
        findings = matching(lint(spec), "No numbered task headings found")
        self.assertTrue(findings)
        self.assertEqual(findings[0].severity, "High")

    def test_an_unnumbered_task_heading_is_not_a_task(self):
        spec = variant("## Out of Scope", "### Task ordering notes\n\nSequential.\n\n## Out of Scope")
        self.assertEqual(
            [f for f in lint(spec) if "Task ordering notes" in f.evidence],
            [],
            "`### Task ordering notes` is prose, not a numbered task",
        )

    def test_empty_field_value_is_flagged(self):
        spec = variant("**Objective**: Add `POST /reset` behind the existing rate limiter.", "**Objective**:")
        findings = [f for f in lint(spec) if "objective" in f.title.lower()]
        self.assertTrue(findings, "a label with no value is not a populated field")
        self.assertEqual(findings[0].severity, "Medium")

    def test_whitespace_only_field_value_is_flagged(self):
        spec = variant("**Objective**: Add `POST /reset` behind the existing rate limiter.", "**Objective**:   ")
        self.assertTrue([f for f in lint(spec) if "objective" in f.title.lower()])

    def test_bare_list_marker_is_not_a_field_value(self):
        spec = variant(
            "**Requirements**:\n- Reject more than five requests per hour per address.",
            "**Requirements**:\n-",
        )
        self.assertTrue([f for f in lint(spec) if "requirements" in f.title.lower()])

    def test_a_bare_unchecked_checkbox_is_not_a_field_value(self):
        spec = variant("**Done when**:\n- [ ] The endpoint returns `202` for a known address.", "**Done when**:\n- [ ]")
        self.assertTrue([f for f in lint(spec) if "done when" in f.title.lower()])

    def test_a_value_with_no_space_after_the_colon_is_not_blank(self):
        spec = variant("**Objective**: Add `POST /reset` behind the existing rate limiter.", "**Objective**:X")
        self.assertEqual([f for f in lint(spec) if "objective" in f.title.lower()], [])

    def test_following_line_field_value_is_accepted(self):
        # `**Affected files**:` puts its value on the next line, not inline.
        self.assertEqual([f for f in lint(BASELINE) if "affected files" in f.title.lower()], [])

    def test_an_indented_field_label_is_still_a_field(self):
        spec = variant(
            "**Objective**: Add `POST /reset` behind the existing rate limiter.",
            "  **Objective**: Add `POST /reset` behind the existing rate limiter.",
        )
        self.assertEqual([f for f in lint(spec) if "objective" in f.title.lower()], [])

    def test_an_empty_middle_field_is_not_masked_by_the_next_one(self):
        spec = variant("**Verification**:\n- `npm test src/auth/reset.test.ts`", "**Verification**:")
        self.assertTrue([f for f in lint(spec) if "verification" in f.title.lower()])

    def test_a_later_task_does_not_supply_an_earlier_tasks_fields(self):
        spec = variant("**Verification**:\n- `npm test src/auth/reset.test.ts`\n\n", "")
        spec = variant(
            "## Out of Scope",
            "### Task 2: Write the audit record\n\n**Objective**: Write an audit row.\n\n"
            "**Context**: No audit table exists today.\n\n**Affected files**:\n- `src/auth/audit.ts`\n\n"
            "**Requirements**:\n- Record actor and timestamp.\n\n**Verification**:\n- `npm test src/auth/audit.test.ts`\n\n"
            "**Done when**:\n- [ ] An audit row exists.\n\n## Out of Scope",
            spec,
        )
        self.assertTrue(
            has_title(lint(spec), "Task missing `Verification` field"),
            "each task's fields are its own; task blocks must not run together",
        )

    def test_a_missing_field_points_at_its_own_task(self):
        spec = variant("**Verification**:\n- `npm test src/auth/reset.test.ts`\n\n", "")
        spec = variant(
            "## Out of Scope",
            "### Task 2: Write the audit record\n\n**Objective**: Write an audit row.\n\n"
            "**Context**: No audit table exists today.\n\n**Affected files**:\n- `src/auth/audit.ts`\n\n"
            "**Requirements**:\n- Record actor and timestamp.\n\n**Verification**:\n- `npm test src/auth/audit.test.ts`\n\n"
            "**Done when**:\n- [ ] An audit row exists.\n\n## Out of Scope",
            spec,
        )
        missing = [f for f in lint(spec) if "Verification" in f.title]
        self.assertTrue(missing)
        self.assertIn("Task 1", missing[0].evidence)

    def test_context_is_a_required_task_field(self):
        spec = variant("**Context**: No route issues reset tokens today.\n\n", "")
        self.assertTrue(
            has_title(lint(spec), "Task missing `Context` field"),
            "the feature-to-plan task template requires Context",
        )

    def test_depends_on_is_not_required(self):
        self.assertFalse(
            has_title(lint(BASELINE), "Depends on"),
            "`Depends on` is recorded only when a dependency exists; requiring it over-fixes",
        )


class MermaidTests(unittest.TestCase):
    """Which Mermaid diagram types the template requires, and how they are detected."""

    def test_both_required_diagrams_present_is_clean(self):
        self.assertEqual(matching(lint(BASELINE), "mermaid"), [])
        self.assertEqual(matching(lint(BASELINE), "diagram"), [])

    def test_missing_sequence_diagram_is_flagged(self):
        spec = variant("\n" + SEQUENCE_BLOCK, "")
        findings = [f for f in lint(spec) if "sequence" in f.title.lower()]
        self.assertTrue(findings, "the template mandates a sequence diagram as well as a data-flow diagram")
        self.assertEqual(findings[0].severity, "Low")

    def test_missing_flowchart_is_flagged(self):
        spec = variant(FLOWCHART_BLOCK + "\n", "")
        findings = [f for f in lint(spec) if "data-flow" in f.title.lower() or "flowchart" in f.title.lower()]
        self.assertTrue(findings)
        self.assertEqual(findings[0].severity, "Low")

    def test_graph_td_counts_as_a_data_flow_diagram(self):
        spec = variant("flowchart TB", "graph TD")
        self.assertEqual(
            [f for f in lint(spec) if "data-flow" in f.title.lower() or "flowchart" in f.title.lower()],
            [],
            "`graph TD` is Mermaid's older spelling of the same diagram",
        )

    def test_every_flowchart_direction_counts(self):
        for direction in ("TB", "TD", "BT", "LR", "RL"):
            with self.subTest(direction=direction):
                spec = variant("flowchart TB", f"flowchart {direction}")
                self.assertEqual([f for f in lint(spec) if "data-flow" in f.title.lower()], [])

    def test_a_directionless_flowchart_is_not_a_data_flow_diagram(self):
        self.assertTrue(has_title(lint(variant("flowchart TB", "flowchart")), "data-flow"))

    def test_a_mistyped_sequence_directive_does_not_satisfy_the_check(self):
        self.assertTrue(has_title(lint(variant("sequenceDiagram", "sequenceDiagrams")), "sequence"))

    def test_mermaid_info_string_is_case_insensitive(self):
        spec = BASELINE.replace("```mermaid", "```Mermaid")
        self.assertEqual(matching(lint(spec), "No Mermaid diagrams found"), [])

    def test_extra_mermaid_info_tokens_do_not_disqualify_the_fence(self):
        spec = variant("```mermaid\nflowchart TB", "```Mermaid title=flow\nflowchart TB")
        self.assertEqual([f for f in lint(spec) if "data-flow" in f.title.lower()], [])

    def test_a_leading_mermaid_comment_does_not_hide_the_directive(self):
        spec = variant("```mermaid\nflowchart TB", "```mermaid\n%% Data flow for a reset request\nflowchart TB")
        self.assertEqual([f for f in lint(spec) if "data-flow" in f.title.lower()], [])

    def test_mermaid_front_matter_does_not_hide_the_directive(self):
        spec = variant("```mermaid\nflowchart TB", "```mermaid\n---\ntitle: Reset flow\n---\nflowchart TB")
        self.assertEqual(
            [f for f in lint(spec) if "data-flow" in f.title.lower()],
            [],
            "Mermaid allows a `---` front-matter block before the directive",
        )

    def test_a_bare_fence_does_not_crash_the_mermaid_check(self):
        spec = variant("## Out of Scope", "```\nplain block\n```\n\n## Out of Scope")
        self.assertEqual(
            matching(lint(spec), "No Mermaid diagrams found"),
            [],
            "an untyped fence is not a diagram, and must not break the check either",
        )

    def test_an_unterminated_fence_still_supplies_its_diagram(self):
        spec = variant("```mermaid\nsequenceDiagram", "```mermaid\nsequenceDiagram") + "\n```mermaid\nflowchart LR\n  A --> B"
        self.assertEqual(matching(lint(spec), "No Mermaid diagrams found"), [])

    def test_the_missing_diagram_finding_points_at_the_first_mermaid_fence(self):
        spec = variant("flowchart TB", "stateDiagram-v2")
        flow = [f for f in lint(spec) if "data-flow" in f.title.lower()]
        self.assertTrue(flow)
        self.assertEqual(flow[0].line, spec[: spec.index("```mermaid")].count("\n") + 1)


class AmbiguityTests(unittest.TestCase):
    """Which prose is flagged for subjective language."""

    def test_prose_ambiguity_is_still_flagged(self):
        spec = variant("Removes the manual reset queue and its operator cost.", "Makes the queue efficient.")
        self.assertTrue(has_title(lint(spec), "ambiguous term"))

    def test_table_rows_are_still_skipped_for_ambiguity(self):
        spec = variant("| Operator | Absorbs manual reset requests |", "| Operator | Wants an efficient queue |")
        self.assertEqual(matching(lint(spec), "ambiguous term"), [])

    def test_a_pipe_inside_prose_does_not_skip_the_ambiguity_check(self):
        spec = variant(
            "Removes the manual reset queue and its operator cost.",
            "Removes the manual reset queue | keeps the operator workflow simple.",
        )
        self.assertTrue(has_title(lint(spec), "ambiguous term"))


class CheckboxTests(unittest.TestCase):
    """Draft specs use unchecked boxes."""

    def test_completed_checkbox_in_prose_is_still_flagged(self):
        spec = variant("- [ ] The endpoint returns `202` for a known address.", "- [x] The endpoint returns `202`.")
        self.assertTrue(has_title(lint(spec), "Completed checkbox"))

    def test_a_checked_box_is_flagged_in_either_case(self):
        for box in ("[x]", "[X]"):
            with self.subTest(box=box):
                spec = variant(
                    "- [ ] The endpoint returns `202` for a known address.",
                    f"- {box} The endpoint returns `202`.",
                )
                self.assertTrue(has_title(lint(spec), "Completed checkbox"))


class ReportContractTests(unittest.TestCase):
    """The report's exit codes and payload shape, which callers depend on."""

    def _run(self, text: str, fmt: str = "json"):
        with spec_file(text) as path:
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--format", fmt],
                capture_output=True,
                text=True,
            )

    def test_clean_spec_exits_zero(self):
        result = self._run(BASELINE)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_high_finding_exits_one(self):
        self.assertEqual(self._run(variant("## Problem Statement", "## Background")).returncode, 1)

    def test_missing_file_exits_two(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(REPO_ROOT / "does-not-exist.md")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)

    def test_unreadable_spec_exits_two(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), directory],
                capture_output=True,
                text=True,
            )
        self.assertEqual(
            result.returncode,
            2,
            "exit 1 means High findings; a read failure must not masquerade as one",
        )
        self.assertEqual(result.stdout, "")

    def test_finding_ids_are_sequential(self):
        spec = variant("## Problem Statement", "## Background")
        ids = [f.id for f in lint(spec)]
        self.assertEqual(ids, [f"SL-{n:03d}" for n in range(1, len(ids) + 1)])

    def test_json_payload_keys_are_stable(self):
        payload = json.loads(self._run(BASELINE).stdout)
        self.assertEqual(set(payload), {"artifact_audited", "finding_count", "findings"})
        self.assertEqual(payload["finding_count"], len(payload["findings"]))

    def test_finding_fields_are_stable(self):
        payload = json.loads(self._run(variant("## Problem Statement", "## Background")).stdout)
        self.assertEqual(
            set(payload["findings"][0]),
            {"id", "severity", "category", "line", "title", "evidence", "recommendation"},
        )

    def test_markdown_format_renders(self):
        result = self._run(BASELINE, fmt="markdown")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Static Spec Audit Lint", result.stdout)

    def test_markdown_location_reflects_the_finding_line(self):
        out = self._run(variant("## Personas", "## Roster"), fmt="markdown").stdout
        self.assertIn("- **Location**: global", out)
        self.assertNotIn("line None", out)


if __name__ == "__main__":
    unittest.main()
