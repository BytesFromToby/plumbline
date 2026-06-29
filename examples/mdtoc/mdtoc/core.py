"""Pure data-layer functions for mdtoc.

The CLI (``mdtoc/__main__.py``) reads files and passes their contents to
these functions; everything here is string-in / value-out with no I/O.
"""


def extract_headings(text: str) -> list[tuple[int, str]]:
    """Extract ATX headings from Markdown text in document order.

    Returns an ordered list of ``(level, text)`` pairs, where ``level`` is the
    count of leading ``#`` (1-6) and ``text`` is the trimmed heading text with
    any closing ATX ``#`` sequence stripped. ``#`` lines inside fenced code
    blocks (``` ``` ``` or ``~~~``) are ignored; an unterminated fence keeps
    everything to end-of-file inside the block.
    """
    headings: list[tuple[int, str]] = []
    fence_char: str | None = None  # the fence delimiter currently open, or None

    for line in text.splitlines():
        stripped = line.lstrip()

        # Fence tracking: a line whose first non-whitespace content is ``` or ~~~.
        if stripped.startswith("```") or stripped.startswith("~~~"):
            this_fence = stripped[0]
            if fence_char is None:
                fence_char = this_fence
            elif this_fence == fence_char:
                fence_char = None
            continue

        if fence_char is not None:
            continue  # inside an open fence — ignore everything

        if not stripped.startswith("#"):
            continue

        hashes = len(stripped) - len(stripped.lstrip("#"))
        if hashes < 1 or hashes > 6:
            continue

        rest = stripped[hashes:]
        # Must be followed by at least one space to be a heading.
        if not rest.startswith(" "):
            continue

        # Strip a trailing run of # (closing ATX sequence), then trim.
        heading_text = rest.rstrip().rstrip("#").strip()
        headings.append((hashes, heading_text))

    return headings


def slugify(text: str, used: set) -> str:
    """Produce a GitHub-style anchor slug, deduplicating within a document.

    Lowercases ``text``, drops any character that is not alphanumeric, a space,
    or a hyphen, collapses whitespace runs to a single hyphen, and appends
    ``-1``, ``-2``, ... if the slug is already in ``used`` (first duplicate gets
    ``-1``). The returned slug is added to ``used`` so the next call sees it.
    """
    lowered = text.lower()
    kept = "".join(c for c in lowered if c.isalnum() or c in " -")
    base = "-".join(kept.split())

    slug = base
    n = 1
    while slug in used:
        slug = f"{base}-{n}"
        n += 1

    used.add(slug)
    return slug


def render_toc(headings: list) -> str:
    """Render ``(level, text)`` pairs as a nested bulleted Markdown TOC.

    Each heading becomes a ``- [text](#slug)`` line indented by
    ``(level - 1) * 2`` spaces, slugs deduplicated against one shared set across
    the whole list. Lines are joined by ``\\n`` with a single trailing newline.
    Empty input returns an empty string.
    """
    if not headings:
        return ""

    used: set = set()
    lines = []
    for level, text in headings:
        slug = slugify(text, used)
        indent = " " * ((level - 1) * 2)
        lines.append(f"{indent}- [{text}](#{slug})")

    return "\n".join(lines) + "\n"


TOC_OPEN = "<!-- toc -->"
TOC_CLOSE = "<!-- /toc -->"


def insert_toc(text: str, toc: str) -> str:
    """Return ``text`` with ``toc`` written between TOC marker comments.

    If both ``<!-- toc -->`` and ``<!-- /toc -->`` markers are present, the
    content between them is replaced with ``toc`` while the marker lines and all
    other content stay intact. If the markers are absent, a block (open marker,
    TOC, close marker) is inserted after a leading H1 (at the next blank line
    after it) if the file begins with one, otherwise at the very top. The
    transformation is idempotent.
    """
    lines = text.splitlines(keepends=True)

    open_idx = _find_marker_line(lines, TOC_OPEN)
    close_idx = _find_marker_line(lines, TOC_CLOSE)

    if open_idx is not None and close_idx is not None and open_idx < close_idx:
        return _replace_between_markers(lines, open_idx, close_idx, toc)

    return _insert_new_block(text, lines, toc)


def _find_marker_line(lines: list, marker: str) -> int | None:
    """Return the index of the first line whose trimmed content is ``marker``."""
    for i, line in enumerate(lines):
        if line.strip() == marker:
            return i
    return None


def _replace_between_markers(lines: list, open_idx: int, close_idx: int, toc: str) -> str:
    """Rebuild the file with ``toc`` between the marker lines, rest intact."""
    before = lines[: open_idx + 1]
    after = lines[close_idx:]
    block = TOC_OPEN + "\n" + toc + TOC_CLOSE + "\n"
    # `before` ends at the open-marker line; `after` starts at the close marker.
    rebuilt = "".join(before[:-1]) + block + "".join(after[1:])
    return rebuilt


def _insert_new_block(text: str, lines: list, toc: str) -> str:
    """Insert a fresh marker block after a leading H1, else at the very top."""
    block = TOC_OPEN + "\n" + toc + TOC_CLOSE + "\n"

    if lines and lines[0].lstrip().startswith("# ") and not lines[0].lstrip().startswith("##"):
        # File opens with an H1: insert at the next blank line after it.
        insert_at = 1
        while insert_at < len(lines) and lines[insert_at].strip() != "":
            insert_at += 1
        # Place the block after the blank line (or after the H1 run if none).
        if insert_at < len(lines):
            insert_at += 1
        head = "".join(lines[:insert_at])
        tail = "".join(lines[insert_at:])
        return head + block + tail

    return block + text
