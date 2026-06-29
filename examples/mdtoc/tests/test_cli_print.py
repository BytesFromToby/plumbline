import subprocess
import sys


def _run(args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "mdtoc", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_print_mode_prints_toc_and_exits_zero(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text("# Title\n\n## Section\n", encoding="utf-8")

    result = _run([str(md)])

    assert result.returncode == 0
    assert "- [Title](#title)" in result.stdout
    assert "  - [Section](#section)" in result.stdout


def test_missing_file_errors_to_stderr_no_stdout(tmp_path):
    missing = tmp_path / "nonexistent.md"

    result = _run([str(missing)])

    assert result.returncode != 0
    assert result.returncode == 1
    assert result.stderr.strip() != ""
    assert result.stdout == ""


def test_print_mode_leaves_input_unchanged(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text("# Title\n\n## Section\n", encoding="utf-8")
    before = md.read_bytes()

    result = _run([str(md)])

    assert result.returncode == 0
    assert md.read_bytes() == before


def test_empty_headings_prints_empty_toc_exits_zero(tmp_path):
    md = tmp_path / "empty.md"
    md.write_text("Just some prose, no headings here.\n", encoding="utf-8")

    result = _run([str(md)])

    assert result.returncode == 0
    assert result.stdout == ""
