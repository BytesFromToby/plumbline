from mdtoc.core import slugify


def test_basic_slug():
    assert slugify("Hello World", set()) == "hello-world"


def test_punctuation_dropped():
    assert slugify("What's New? (v2)", set()) == "whats-new-v2"


def test_collision_deduplication():
    used = set()
    first = slugify("x", used)
    second = slugify("x", used)
    assert first == "x"
    assert second == "x-1"
