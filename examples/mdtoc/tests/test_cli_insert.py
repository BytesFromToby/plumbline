import subprocess
import sys


def _run_insert(path):
    return subprocess.run(
        [sys.executable, "-m", "mdtoc", str(path), "--insert"],
        capture_output=True,
        text=True,
    )


def test_replace_between_existing_markers_rest_unchanged(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text(
        "Intro prose.\n"
        "<!-- toc -->\n"
        "- [stale](#stale)\n"
        "<!-- /toc -->\n"
        "Body text.\n"
        "# Alpha\n"
        "## Beta\n",
        encoding="utf-8",
    )

    result = _run_insert(md)
    assert result.returncode == 0

    out = md.read_text(encoding="utf-8")
    # Marker lines survive.
    assert "<!-- toc -->" in out
    assert "<!-- /toc -->" in out
    # Stale content is gone; fresh TOC is present.
    assert "- [stale](#stale)" not in out
    assert "- [Alpha](#alpha)" in out
    assert "  - [Beta](#beta)" in out
    # Surrounding content intact.
    assert "Intro prose.\n" in out
    assert "Body text.\n" in out
    assert out.startswith("Intro prose.\n")


def test_markers_created_after_leading_h1(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text(
        "# Project\n"
        "\n"
        "Some intro.\n"
        "## Usage\n",
        encoding="utf-8",
    )

    result = _run_insert(md)
    assert result.returncode == 0

    out = md.read_text(encoding="utf-8")
    assert "<!-- toc -->" in out
    assert "<!-- /toc -->" in out
    assert "- [Project](#project)" in out
    assert "  - [Usage](#usage)" in out
    # All original content retained.
    assert "# Project\n" in out
    assert "Some intro.\n" in out
    assert "## Usage\n" in out
    # The marker block lands after the leading H1, not before it.
    assert out.index("# Project") < out.index("<!-- toc -->")


def test_markers_created_at_top_when_no_leading_h1(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text(
        "Just prose first.\n"
        "## Section\n",
        encoding="utf-8",
    )

    result = _run_insert(md)
    assert result.returncode == 0

    out = md.read_text(encoding="utf-8")
    assert out.startswith("<!-- toc -->\n")
    assert "<!-- /toc -->" in out
    assert "  - [Section](#section)" in out
    # Original content retained.
    assert "Just prose first.\n" in out
    assert "## Section\n" in out


def test_idempotent_on_second_run(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text(
        "# Project\n"
        "\n"
        "Intro.\n"
        "## A\n"
        "## B\n",
        encoding="utf-8",
    )

    assert _run_insert(md).returncode == 0
    after_first = md.read_bytes()

    assert _run_insert(md).returncode == 0
    after_second = md.read_bytes()

    assert after_second == after_first
