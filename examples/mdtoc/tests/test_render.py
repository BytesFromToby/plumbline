from mdtoc.core import render_toc


def test_level_1_no_leading_spaces():
    result = render_toc([(1, "Intro")])
    lines = result.splitlines()
    assert "- [Intro](#intro)" in lines
    # The level-1 line has no leading spaces.
    assert lines[0] == "- [Intro](#intro)"


def test_level_3_has_four_leading_spaces():
    result = render_toc([(3, "Deep")])
    line = result.splitlines()[0]
    assert line.startswith("    - ")
    assert line == "    - [Deep](#deep)"
    # Exactly 4 leading spaces.
    assert len(line) - len(line.lstrip(" ")) == 4


def test_empty_input_renders_empty():
    result = render_toc([])
    assert result == ""
    assert result.splitlines() == []
