# Blueprint: mdtoc
Spec: Planning/specs/mdtoc_spec.md
Date: 2026-06-28

---

## Builder instructions
- Execute steps in order. Do not skip, reorder, or read ahead into the next slice.
- Check off each step when complete: [ ] → [x]
- One step = one logical concern. If a step can't be tested on its own, it's too small — merge it. If it touches more than one concern, split it.
- Deviation: if you do something differently than the step says, note it inline and keep going.
- Stuck: stop immediately. Do not try alternative approaches. Report exactly where and why.

---

## Slice 1: Heading extraction
**Scope:** The package `mdtoc` exists and `mdtoc.extract_headings(text)` returns the ordered `(level, text)` pairs of ATX headings, skipping fenced code blocks.

### Step 1: Create the package skeleton
**Build:** Create `mdtoc/__init__.py` (empty). Create `mdtoc/core.py` (empty for now — the data-layer functions land here). Create `tests/__init__.py` (empty). This package is imported by later slices' rendering and CLI code — keep all pure functions in `mdtoc/core.py` so the CLI in `mdtoc/__main__.py` (Slice 4) can import them.
**Test:** `python -c "import mdtoc"`
**Done When:** `import mdtoc` succeeds with no error; `mdtoc/core.py` and `tests/__init__.py` exist.
**Stuck If:** Python cannot import the package from the project root (path/layout problem).
- [x] Complete

### Step 2: Implement `extract_headings(text)`
**Build:** In `mdtoc/core.py`, add `def extract_headings(text: str) -> list[tuple[int, str]]:`. It takes the full file contents as a string, splits into lines, and returns an ordered list of `(level, text)` pairs in document order. Rules from spec Feature "Heading extraction": a heading line's first non-whitespace content is 1–6 `#` followed by at least one space, then the text; `level` = count of leading `#` (1–6); `text` = the heading text trimmed. More than 6 `#`s is NOT a heading; `#` with no following space is NOT a heading. Strip a trailing run of `#` (closing ATX sequence) from the text before trimming. Track fenced code blocks: a fence opens on a line whose first non-whitespace content is ` ``` ` or `~~~`, and closes on the next line beginning with a matching fence of the **same** character; ignore any `#` line while inside an open fence; an unterminated fence keeps everything to EOF inside the block. Keep this function pure (string in, list out) — Slice 4's CLI reads the file and passes its contents here.
**Test:** `python -m pytest`
**Done When:** `python -m pytest` collects and passes (no failures); `extract_headings` is importable from `mdtoc.core`.
**Stuck If:** The spec's fence rules are ambiguous for an input you must handle and the spec gives no answer.
- [x] Complete

### Step 3: Test — levels 1–6 extraction in document order
**Build:** Create `tests/test_extract.py`. Add a test that feeds a string with headings at levels 1 through 6 (e.g. `# A`, `## B`, … `###### F`) and asserts `extract_headings` returns exactly `[(1,"A"),(2,"B"),(3,"C"),(4,"D"),(5,"E"),(6,"F")]` — one pair per heading, correct level, trimmed text, document order. (Encodes Done-when item 1 of Heading extraction.)
**Test:** `python -m pytest tests/test_extract.py`
**Done When:** The new test passes.
**Stuck If:** The asserted output disagrees with the spec's stated extraction contract.
- [x] Complete

### Step 4: Test — `#` lines inside fenced blocks excluded (``` ``` ``` ``` and `~~~`)
**Build:** In `tests/test_extract.py`, add a test with a real heading, then a ``` ``` ``` ```-fenced block containing a `#`-prefixed line, then another real heading; assert the in-fence `#` line is absent from results. Add a second case using a `~~~`-fenced block with a `#` line inside, asserting the same exclusion. (Encodes Done-when item 2 of Heading extraction.)
**Test:** `python -m pytest tests/test_extract.py`
**Done When:** Both fence cases pass; the in-fence `#` lines are excluded.
**Stuck If:** Extraction includes an in-fence `#` line and the spec's fence rule can't reconcile it.
- [x] Complete

### Step 5: Test — 7+ `#`s and `#`-without-space are not headings
**Build:** In `tests/test_extract.py`, add a test asserting a line with 7 leading `#`s (`####### Too deep`) is not returned, and a line `#tag` (no space after `#`) is not returned. (Encodes Done-when item 3 of Heading extraction.)
**Test:** `python -m pytest tests/test_extract.py`
**Done When:** Neither line appears in the extraction results; test passes.
**Stuck If:** Either non-heading is returned and the spec's "1–6 `#` then a space" rule can't explain it.
- [x] Complete

### Step 6: Test — closing ATX sequence stripped
**Build:** In `tests/test_extract.py`, add a test that `## Title ##` extracts to `(2, "Title")` — trailing `#`s removed and text trimmed. (Encodes Done-when item 4 of Heading extraction.)
**Test:** `python -m pytest tests/test_extract.py`
**Done When:** Test passes with text exactly `Title`.
**Stuck If:** The trailing-`#` strip rule conflicts with another extraction rule on this input.
- [x] Complete

---
End of Slice 1. Builder checkpoint: tests green → continue to Slice 2.

---

## Slice 2: Anchor slug generation
**Scope:** `mdtoc.slugify(text, used)` produces a GitHub-style anchor slug and deduplicates collisions within the document.

### Step 1: Implement `slugify(text, used)`
**Build:** In `mdtoc/core.py`, add `def slugify(text: str, used: set) -> str:`. Rules from spec Feature "Anchor slug generation": lowercase the text; remove characters that are not alphanumeric, spaces, or hyphens (drop, don't replace); replace each run of whitespace with a single hyphen; if the resulting slug is already in `used`, append `-1`, `-2`, … (first duplicate → `-1`) until unique. The function should add the returned slug to `used` (or the caller does) so the next call sees it — keep the dedup state in the passed-in `used` set so Slice 3/4 callers maintain one set per document.
**Test:** `python -m pytest`
**Done When:** `slugify` is importable from `mdtoc.core`; full suite still passes.
**Stuck If:** The dedup-state ownership (function vs caller mutates `used`) is ambiguous for downstream callers.
- [x] Complete

### Step 2: Test — basic slug and punctuation dropping
**Build:** Create `tests/test_slug.py`. Add a test asserting `slugify("Hello World", set())` returns `hello-world`. Add a test asserting `slugify("What's New? (v2)", set())` returns `whats-new-v2` (apostrophe, `?`, and parens dropped; spaces → single hyphen). (Encodes Done-when items 1 and 2 of Anchor slug generation.)
**Test:** `python -m pytest tests/test_slug.py`
**Done When:** Both assertions pass.
**Stuck If:** A produced slug differs from the spec's stated output and the slug rules can't reconcile it.
- [x] Complete

### Step 3: Test — collision deduplication
**Build:** In `tests/test_slug.py`, add a test that slugifies the same text twice against a shared `used` set, asserting the first yields `x` and the second yields `x-1` (use a text whose slug is `x`, e.g. `"x"`). (Encodes Done-when item 3 of Anchor slug generation.)
**Test:** `python -m pytest tests/test_slug.py`
**Done When:** First call returns the bare slug, second returns the slug with `-1` appended.
**Stuck If:** Dedup numbering disagrees with the spec ("first duplicate gets `-1`").
- [x] Complete

---
End of Slice 2. Builder checkpoint: tests green → continue to Slice 3.

---

## Slice 3: TOC rendering
**Scope:** `mdtoc.render_toc(headings)` turns `(level, text)` pairs into a nested bulleted Markdown TOC with per-level indentation and deduplicated slug links.

### Step 1: Implement `render_toc(headings)`
**Build:** In `mdtoc/core.py`, add `def render_toc(headings: list) -> str:`. It takes the ordered `(level, text)` pairs, generates one deduplicated slug per heading using `slugify` with a single shared `used` set across the whole list, and returns a Markdown string: one `- [text](#slug)` line per heading, indented by `(level - 1) * 2` spaces (level-1 = 0 spaces), lines joined by `\n`, with a single trailing newline. Link text is the heading's trimmed text; target is `#` + the deduplicated slug. Indentation tracks the heading's own level, not nesting of preceding headings (no renumbering). For empty input return an empty string (no list lines). This is the same rendering print mode and insert mode both use — keep it pure (pairs in, string out) so Slice 4 and Slice 5 share it.
**Test:** `python -m pytest`
**Done When:** `render_toc` is importable from `mdtoc.core`; full suite still passes.
**Stuck If:** The empty-input return shape (empty string vs something else) is ambiguous against the spec.
- [x] Complete

### Step 2: Test — level-1 rendering and level-3 indentation
**Build:** Create `tests/test_render.py`. Add a test asserting `render_toc([(1,"Intro")])` produces a line `- [Intro](#intro)` with no leading spaces. Add a test asserting a level-3 heading renders with exactly 4 leading spaces before the `-`. (Encodes Done-when items 1 and 2 of TOC rendering.)
**Test:** `python -m pytest tests/test_render.py`
**Done When:** Both assertions pass — level-1 has 0 leading spaces, level-3 has exactly 4.
**Stuck If:** Rendered indentation disagrees with `(level - 1) * 2`.
- [x] Complete

### Step 3: Test — empty input renders empty TOC
**Build:** In `tests/test_render.py`, add a test asserting `render_toc([])` returns an empty TOC (empty string / no list lines). (Encodes Done-when item 3 of TOC rendering, rendering half; the exit-0 half is covered by the print-mode empty-file test in Slice 4.)
**Test:** `python -m pytest tests/test_render.py`
**Done When:** Empty input produces an empty result with no list lines.
**Stuck If:** The empty-render contract is ambiguous against the spec.
- [x] Complete

---
End of Slice 3. Builder checkpoint: tests green → continue to Slice 4.

---

## Slice 4: CLI — print mode
**Scope:** `python -m mdtoc <file>` reads the file, prints the nested TOC to stdout, exits 0; a missing file errors to stderr with a non-zero exit and no stdout; the input file is never modified.

### Step 1: Implement the CLI entry point (print mode)
**Build:** Create `mdtoc/__main__.py`. Parse exactly one positional `file` argument (use `argparse`); accept an optional `--insert` flag now but leave its handling for Slice 5 (a `TODO` branch that does nothing yet, or routes to a not-yet-implemented function — do not implement insert behavior here). For print mode: read the file as UTF-8, call `extract_headings` then `render_toc` (both from `mdtoc.core`, one shared `used` set via `render_toc`), write the rendered TOC to stdout, exit 0. If the file does not exist or cannot be read, write an error message to stderr and exit with code 1, writing nothing to stdout. Without `--insert`, never modify the input file. Expose a `main()` function and call it under `if __name__ == "__main__":` so tests can invoke the module via `python -m mdtoc`. Slice 5 will fill in the `--insert` branch — keep `main()` structured so the insert path is a clean branch off the same parsed args.
**Test:** `python -m pytest`
**Done When:** `python -m mdtoc <some file with headings>` prints a TOC and exits 0; full suite still passes.
**Stuck If:** `python -m mdtoc` cannot be invoked as a module (entry-point/layout problem).
- [x] Complete

### Step 2: Test — print mode prints TOC and exits 0
**Build:** Create `tests/test_cli_print.py`. Add a test that writes a temp Markdown file with headings (use pytest's `tmp_path`), runs the CLI as a subprocess (`python -m mdtoc <file>`), and asserts the nested TOC appears on stdout and the exit code is 0. (Encodes Done-when item 1 of CLI print mode.)
**Test:** `python -m pytest tests/test_cli_print.py`
**Done When:** Subprocess prints the expected TOC and exits 0.
**Stuck If:** The module won't run as a subprocess from the test environment.
- [x] Complete

### Step 3: Test — missing file errors to stderr, no stdout, non-zero exit
**Build:** In `tests/test_cli_print.py`, add a test running `python -m mdtoc nonexistent.md` as a subprocess and asserting: exit code is non-zero (1), stderr is non-empty, stdout is empty. (Encodes Done-when item 2 of CLI print mode.)
**Test:** `python -m pytest tests/test_cli_print.py`
**Done When:** Non-zero exit, error on stderr, nothing on stdout.
**Stuck If:** The error path writes to stdout or exits 0, contradicting the spec.
- [x] Complete

### Step 4: Test — print mode leaves input file byte-for-byte unchanged
**Build:** In `tests/test_cli_print.py`, add a test that writes a temp Markdown file, records its exact bytes, runs `python -m mdtoc <file>` (no `--insert`), and asserts the file's bytes are identical afterward. (Encodes Done-when item 3 of CLI print mode.) Also add an empty-headings case: a file with no headings prints an empty TOC and exits 0 (covers the exit-0 half of TOC rendering's empty-input Done-when item).
**Test:** `python -m pytest tests/test_cli_print.py`
**Done When:** File bytes are unchanged after print mode; empty-file run exits 0 with empty TOC output.
**Stuck If:** Print mode mutates the input file.
- [x] Complete

---
End of Slice 4. Builder checkpoint: tests green → continue to Slice 5.

---

## Slice 5: CLI — insert mode [inspect]
<!-- [inspect]: destructive operation — `--insert` rewrites the user's file in place. -->
**Scope:** `python -m mdtoc <file> --insert` writes the TOC into the file between `<!-- toc -->` / `<!-- /toc -->` markers — replacing existing content if present, creating the markers near the top if absent — and is idempotent.

### Step 1: Implement `insert_toc(text, toc)` in core
**Build:** In `mdtoc/core.py`, add `def insert_toc(text: str, toc: str) -> str:`. It takes the original file contents and the rendered TOC, and returns the new file contents. Rules from spec Feature "CLI — insert mode": if both `<!-- toc -->` and `<!-- /toc -->` markers are present, replace whatever is between them with the fresh TOC, leaving the marker lines and all other content intact. If the markers are absent, insert a block — `<!-- toc -->`, the TOC, `<!-- /toc -->`, each on its own line — after a leading H1 line if the file begins with one (at the next blank line after it), otherwise at the very top of the file. Marker comment lines are Markdown comments and must never be parsed as headings (they aren't `#` lines, so `extract_headings` already ignores them — do not special-case). The transformation must be idempotent: applying it to its own output yields identical text. Keep this a pure string→string function; Slice 5 Step 2 wires it into the CLI which owns the actual file write.
**Test:** `python -m pytest`
**Done When:** `insert_toc` is importable from `mdtoc.core`; full suite still passes.
**Stuck If:** "Near the top" / marker placement is ambiguous for an input the spec doesn't resolve.
- [x] Complete

### Step 2: Wire `--insert` into the CLI
**Build:** In `mdtoc/__main__.py`, fill in the `--insert` branch left as a TODO in Slice 4. When `--insert` is set: read the file (UTF-8), run `extract_headings` → `render_toc` to get the TOC, call `insert_toc(original, toc)`, and write the result back to the **same** file (never any other path). Exit 0 on success. On a file read/write error, write to stderr and exit code 1. Do not touch stdout for insert mode's normal success path beyond what the spec requires.
**Test:** `python -m pytest`
**Done When:** `python -m mdtoc <file> --insert` rewrites the named file in place and exits 0; full suite still passes.
**Stuck If:** The write targets any path other than the input file, or the success/error exit contract is unclear.
- [x] Complete

### Step 3: Test — replace content between existing markers, rest unchanged
**Build:** Create `tests/test_cli_insert.py`. Add a test (using `tmp_path`) that writes a file already containing `<!-- toc -->` … `<!-- /toc -->` (with stale content between them) plus surrounding text and headings, runs `python -m mdtoc <file> --insert`, and asserts the content between the markers is replaced with the current TOC while the marker lines and all other file content remain intact. (Encodes Done-when item 1 of CLI insert mode.)
**Test:** `python -m pytest tests/test_cli_insert.py`
**Done When:** Between-marker content is the fresh TOC; everything else is unchanged.
**Stuck If:** Surrounding content is altered, contradicting the spec.
- [x] Complete

### Step 4: Test — markers created (after leading H1, else top), original content kept
**Build:** In `tests/test_cli_insert.py`, add a test for a file with NO markers but a leading H1 plus headings: after `--insert`, assert both markers and the TOC are present, placed after the leading H1, and the file still contains all its original content. Add a second case for a file with no leading H1: assert the marker block lands at the very top. (Encodes Done-when item 2 of CLI insert mode.)
**Test:** `python -m pytest tests/test_cli_insert.py`
**Done When:** Both markers + TOC added at the correct anchor point; all original content retained.
**Stuck If:** Marker placement disagrees with the spec's "after leading H1, else top" rule.
- [x] Complete

### Step 5: Test — idempotent on second run
**Build:** In `tests/test_cli_insert.py`, add a test that runs `python -m mdtoc <file> --insert` twice on the same file and asserts the file contents after the second run are byte-for-byte identical to after the first. (Encodes Done-when item 3 of CLI insert mode.)
**Test:** `python -m pytest tests/test_cli_insert.py`
**Done When:** Second `--insert` run produces a file identical to the first run's output.
**Stuck If:** The second run changes the file (non-idempotent), and the cause isn't clear from output.
- [x] Complete

---
⛔ End of Slice 5 [inspect]. Inspection due — run **inspector** on this slice before building on it, unless the caller's inspection level defers it to final sign-off.

✅ Inspector: PASS — 2026-06-28 19:14

---

## Final Slice: Spec verification
**Scope:** Edge cases, polish, and full spec verification.

### Final Step: Verify spec Done when items
**Build:** No new code. Confirm all spec `**Done when:**` items are met — across Heading extraction (4), Anchor slug generation (3), TOC rendering (3), CLI print mode (3), CLI insert mode (3): 16 `[automated]` items, each backed by a committed test written in an earlier slice.
**Test:** Run the full test suite — `python -m pytest`. Every `[automated]` item now has a committed test from an earlier step. Capture output. Drive the software directly (`python -m mdtoc <file>` / `--insert`) only for an item that genuinely can't be unit-tested.
**Done When:** Every `[automated]` criterion passes (via its committed test). (No `[human-required]` criteria exist in this spec, so no human-judged evidence is owed.)
**Stuck If:** An automated criterion fails and the cause is not clear from the output.
- [x] Complete

---
⛔ Final slice complete. Run **inspector** for final sign-off.

✅ Inspector: PASS — 2026-06-28 19:22

- [x] **Fully inspected** — every `[inspect]` slice and the final sign-off passed. Inspector ticks this; never check it by hand. Its absence means inspection is still owed somewhere.
