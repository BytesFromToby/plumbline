# Spec: mdtoc

`mdtoc` is a command-line tool that generates a nested, bulleted table of contents from the ATX headings (`#`–`######`) of a Markdown file. It prints the TOC to stdout, or — with `--insert` — writes it back into the file between `<!-- toc -->` / `<!-- /toc -->` markers. Each TOC entry links to a GitHub-style anchor slug of the heading text. Headings inside fenced code blocks are not treated as headings.

## Scope
- Does: parse ATX headings (`#` through `######`) from a Markdown file, build a nested bulleted TOC where each item is indented by heading depth and links to a GitHub-style anchor slug, print it to stdout (default) or insert/update it in the file between `<!-- toc -->` and `<!-- /toc -->` markers (`--insert`).
- Does: ignore any `#` line that falls inside a fenced code block delimited by ``` ``` ``` ``` (or `~~~`).
- Does NOT: parse Setext headings (text underlined with `===` / `---`) — only ATX (`#`-prefixed) headings are recognised.
- Does NOT: read from stdin, accept directories or globs, write to any file other than the one given (it edits in place), or render the source Markdown to HTML.
- Does NOT: provide a configuration file, depth-limit flags, or output-format options in this version — output is a fixed nested bullet list.

## Feature: Heading extraction
Read the file's lines and collect the ATX headings, skipping any `#` line inside a fenced code block.

- Input: the path to a UTF-8 Markdown file.
- Output: an ordered list of `(level, text)` pairs in document order, where `level` is 1–6 (count of leading `#`) and `text` is the trimmed heading text after the `#`s.

Rules:
- A heading is a line whose first non-whitespace content is 1–6 `#` characters followed by at least one space, then the heading text. More than 6 `#`s is not a heading.
- A trailing run of `#` (closing ATX sequence, e.g. `## Title ##`) is stripped from the text.
- A fenced code block opens on a line whose first non-whitespace content is ` ``` ` or `~~~` and closes on the next line with a matching fence of the same character; `#` lines between an open and close fence are ignored.
- An unterminated fence (opened, never closed) keeps everything to end-of-file inside the block — those `#` lines are ignored.

**Done when:**
- Given a file with headings at levels 1–6, extraction returns one `(level, text)` pair per heading with the correct level and trimmed text, in document order  `[automated]`
- A `#`-prefixed line inside a ``` ``` ``` ``` fenced block (and inside a `~~~` block) is excluded from the results  `[automated]`
- A line with 7+ leading `#`s, and a `#` with no following space (e.g. `#tag`), are not returned as headings  `[automated]`
- A closing ATX sequence (`## Title ##`) yields text `Title` with the trailing `#`s removed  `[automated]`

## Feature: Anchor slug generation
Convert each heading's text into a GitHub-style anchor slug, deduplicating collisions.

- Input: a heading text string, and the set of slugs already emitted for this document.
- Output: a unique anchor slug string.

Rules (GitHub-style):
- Lowercase the text.
- Remove characters that are not alphanumeric, spaces, or hyphens (punctuation is dropped, not replaced).
- Replace each run of whitespace with a single hyphen.
- If the resulting slug has already been used in this document, append `-1`, `-2`, … (first duplicate gets `-1`) to make it unique.

**Done when:**
- `"Hello World"` slugifies to `hello-world`  `[automated]`
- `"What's New? (v2)"` slugifies to `whats-new-v2` (apostrophe and parens dropped, `?` dropped)  `[automated]`
- Two headings with identical text produce slugs `x` and `x-1` (the second deduplicated)  `[automated]`

## Feature: TOC rendering
Render the extracted headings as a nested bulleted Markdown list.

- Input: the ordered `(level, text)` pairs and their generated slugs.
- Output: a Markdown string — one `- [text](#slug)` line per heading, indented by `(level - 1) * 2` spaces, lines joined by `\n`, with a single trailing newline.

Rules:
- Indentation is 2 spaces per heading level beyond the first: a level-1 heading has 0 leading spaces, level-2 has 2, level-3 has 4, and so on. Indentation tracks the heading's own level, not the nesting of preceding headings (no level renumbering).
- The link text is the heading's original (trimmed) text; the link target is `#` + the heading's deduplicated slug.

**Done when:**
- A level-1 heading `Intro` renders as `- [Intro](#intro)` with no leading spaces  `[automated]`
- A level-3 heading renders with exactly 4 leading spaces before the `-`  `[automated]`
- An empty input (no headings) renders as an empty TOC (empty string / no list lines), and the tool exits 0  `[automated]`

## Feature: CLI — print mode
`mdtoc <file>` prints the generated TOC to stdout.

- Input: command-line invocation `mdtoc <file>` (one positional file argument).
- Output: the rendered TOC written to stdout; exit code 0 on success.

Rules:
- Exactly one positional file argument is required.
- If the file does not exist or cannot be read, write an error message to stderr and exit non-zero (exit code 1); nothing is written to stdout.
- Without `--insert`, the input file is never modified.

**Done when:**
- `mdtoc sample.md` on a file with headings prints the nested TOC to stdout and exits 0  `[automated]`
- `mdtoc nonexistent.md` writes an error to stderr, prints nothing to stdout, and exits with a non-zero code  `[automated]`
- Running print mode leaves the input file byte-for-byte unchanged  `[automated]`

## Feature: CLI — insert mode
`mdtoc <file> --insert` writes the TOC into the file between `<!-- toc -->` and `<!-- /toc -->` markers, creating the markers near the top if absent and replacing existing content if present.

- Input: command-line invocation `mdtoc <file> --insert`.
- Output: the file is rewritten in place with the TOC between the markers; exit code 0 on success.

Rules:
- If both markers are present, replace whatever is between them with the freshly generated TOC, leaving the marker lines and all other file content intact. Running `--insert` twice in a row produces an identical file the second time (idempotent).
- If the markers are absent, create them near the top of the file: after a leading H1 heading line if the file begins with one (the next blank line after it), otherwise at the very top of the file. The inserted block is `<!-- toc -->`, the TOC, then `<!-- /toc -->`, each on its own line.
- The generated TOC excludes nothing it would have printed in print mode (same extraction and rendering); marker comment lines are themselves Markdown comments and are never parsed as headings.
- On a file-read/write error, write to stderr and exit non-zero (exit code 1).

**Done when:**
- On a file already containing `<!-- toc -->` … `<!-- /toc -->`, `--insert` replaces the content between the markers with the current TOC and leaves the rest of the file unchanged  `[automated]`
- On a file with no markers, `--insert` adds both markers plus the TOC (after the leading H1 if one is present, else at the top) and the file still contains all its original content  `[automated]`
- Running `mdtoc <file> --insert` twice yields an identical file after the second run (idempotent)  `[automated]`

## Assumptions
- Slug algorithm was specified only as "GitHub-style" — assumed the common rules: lowercase, drop non-alphanumeric/space/hyphen punctuation, whitespace runs → single hyphen, collisions deduplicated with `-1`, `-2`, …. Confirm if a different slug convention is wanted.
- Indentation unit was unspecified — assumed 2 spaces per heading level. Confirm if 4 spaces (or tabs) are preferred.
- "Indented by its level" was read as the heading's own level (level-1 = 0 spaces), not relative nesting of preceding headings — assumed no level renumbering. Confirm if relative nesting is wanted.
- The brief named ``` ``` ``` ``` fences; `~~~` fenced blocks were also treated as code fences (CommonMark allows both) — assumed both are honoured. Confirm if only backtick fences should count.
- All heading levels 1–6 are included in the TOC (no implicit dropping of the top-level H1, no depth cap) — assumed full inclusion. Confirm if H1 / a max depth should be excluded.
- "Near the top" for marker creation was read as: after a leading H1 if the file opens with one, else the very top of the file. Confirm if a different anchor point is wanted.
- Error handling for a missing/unreadable file was unspecified — assumed a stderr message and exit code 1, with nothing on stdout. Confirm if a different exit code or behaviour is wanted.
- Input encoding was unspecified — assumed UTF-8. Confirm if other encodings must be supported.
- Setext headings (`===` / `---` underlines) are out of scope — the brief said ATX only; assumed Setext is ignored, not an error. Confirm if Setext support is needed.
