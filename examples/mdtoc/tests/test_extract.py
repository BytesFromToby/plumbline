from mdtoc.core import extract_headings


def test_levels_1_through_6_in_document_order():
    text = "# A\n## B\n### C\n#### D\n##### E\n###### F\n"
    assert extract_headings(text) == [
        (1, "A"),
        (2, "B"),
        (3, "C"),
        (4, "D"),
        (5, "E"),
        (6, "F"),
    ]


def test_hash_line_inside_backtick_fence_excluded():
    text = "# Real One\n```\n# Not A Heading\n```\n# Real Two\n"
    result = extract_headings(text)
    assert (1, "Real One") in result
    assert (1, "Real Two") in result
    assert (1, "Not A Heading") not in result


def test_hash_line_inside_tilde_fence_excluded():
    text = "# Real One\n~~~\n# Not A Heading\n~~~\n# Real Two\n"
    result = extract_headings(text)
    assert (1, "Real One") in result
    assert (1, "Real Two") in result
    assert (1, "Not A Heading") not in result


def test_seven_hashes_and_no_space_not_headings():
    text = "####### Too deep\n#tag\n"
    result = extract_headings(text)
    assert (7, "Too deep") not in result
    assert all("Too deep" != t for _, t in result)
    assert all("tag" != t for _, t in result)
    assert result == []


def test_closing_atx_sequence_stripped():
    assert extract_headings("## Title ##\n") == [(2, "Title")]
