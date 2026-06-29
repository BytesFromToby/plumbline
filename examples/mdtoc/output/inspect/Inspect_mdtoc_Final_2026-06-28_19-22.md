# Inspect Report — mdtoc · Final
Spec: Planning/specs/mdtoc_spec.md
Blueprint: Planning/blueprints/mdtoc_BP.md
Date: 2026-06-28
Run/demo command: `python -m mdtoc <file>` (add `--insert`); tests: `python -m pytest`

Summary: 16 passed · 0 failed · 0 need human sign-off

Preconditions: spec has Done-when items (yes); all 16 tagged `[automated]`, none untagged (yes); run command launches (yes). No `[human-required]` items exist.

Deferred-inspection sweep: one `[inspect]` slice (Slice 5 — insert mode, destructive op). Already stamped `✅ Inspector: PASS — 2026-06-28 19:14`. Nothing owed.

Totals: **16 automated, 0 human-required.**

Test suite: `python -m pytest` → 19 passed in 0.58s.

## Results
| Criterion | Status | Fidelity | Evidence |
|-----------|--------|----------|----------|
| Levels 1–6 → one `(level,text)` pair each, correct level, trimmed, doc order | PASS | ok | test_extract.py::test_levels_1_through_6_in_document_order asserts exact `[(1,"A")…(6,"F")]`. Driven: sample.md printed levels 1–6 with 0/2/4 indents. |
| `#` line inside ``` ``` and `~~~` fenced block excluded | PASS | ok | test_extract.py two cases assert in-fence `#` absent AND surrounding reals present. Driven: `# Not A Heading` and `## Also Not` both absent from print output. |
| 7+ `#`s and `#tag` (no space) not headings | PASS | ok | test_extract.py asserts `result == []` for `####### Too deep\n#tag`. Driven: neither appeared in sample print. |
| Closing ATX `## Title ##` → text `Title` | PASS | ok | test_extract.py asserts `[(2,"Title")]`. Driven: rendered `- [Title](#title)`. |
| `"Hello World"` → `hello-world` | PASS | ok | test_slug.py::test_basic_slug exact assert. Driven via print. |
| `"What's New? (v2)"` → `whats-new-v2` | PASS | ok | test_slug.py::test_punctuation_dropped exact assert. Driven: slug `whats-new-v2` in print output. |
| Identical text → `x` and `x-1` | PASS | ok | test_slug.py::test_collision_deduplication asserts first `x`, second `x-1`. Driven: two `# Hello World` → `#hello-world` and `#hello-world-1`. |
| Level-1 `Intro` → `- [Intro](#intro)`, no leading spaces | PASS | ok | test_render.py asserts `lines[0] == "- [Intro](#intro)"`. |
| Level-3 → exactly 4 leading spaces | PASS | ok | test_render.py asserts `len - len(lstrip) == 4` and exact line. Driven: `    - [Deep Three]`. |
| Empty input → empty TOC, exits 0 | PASS | ok | test_render.py asserts `render_toc([]) == ""`; test_cli_print.py empty-file case asserts exit 0 + empty stdout. Driven: empty.md → exit 0, 0 stdout bytes. |
| `mdtoc sample.md` prints nested TOC, exit 0 | PASS | ok | test_cli_print.py subprocess asserts TOC lines on stdout + rc 0. Driven directly, exit 0. |
| `mdtoc nonexistent.md` → stderr msg, no stdout, non-zero exit | PASS | ok | test_cli_print.py asserts rc==1, stderr non-empty, stdout=="". Driven: exit 1, 0 stdout bytes, stderr message present. |
| Print mode leaves input byte-for-byte unchanged | PASS | ok | test_cli_print.py compares `read_bytes()` before/after. Driven: md5 identical before/after. |
| `--insert` replaces between existing markers, rest unchanged | PASS | ok | test_cli_insert.py asserts stale gone, fresh TOC, surrounding + markers intact. Driven: stale `- [stale]`/`- [old]` replaced by Alpha/Beta; Intro/Body text intact. |
| `--insert` adds markers (after leading H1 else top), original content kept | PASS | ok | test_cli_insert.py two cases (H1 placement + top placement) assert markers, TOC, placement, retained content. Driven: H1 case block lands after `# Project`; no-H1 case block at top. |
| `--insert` twice → identical file (idempotent) | PASS | ok | test_cli_insert.py compares `read_bytes()` across two runs. Driven: md5 identical after run 1 and run 2. |

All 16 backing tests would fail if their criterion were violated (exact-equality or membership/negative-membership assertions, real subprocess runs for CLI items, byte-level comparison for the no-mutation and idempotency items). No vacuous or over-mocked tests found.

## Scope / Does-NOT spot checks (from running software)
- Setext headings not parsed: only ATX `#` lines extracted — confirmed by code path and sample (no `===`/`---` handling).
- Marker comment lines never parsed as headings: insert output's `<!-- toc -->` lines do not appear in the generated TOC.
- Writes only the given file in place; no stdin/dir/glob/HTML rendering paths present.

## Human sign-off
None — spec has no `[human-required]` items.
