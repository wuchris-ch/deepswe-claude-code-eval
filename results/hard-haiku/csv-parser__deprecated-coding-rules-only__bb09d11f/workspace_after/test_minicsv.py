"""Visible tests. These encode part of the spec in minicsv.py's docstring
and must not be weakened — the full spec is also exercised elsewhere."""

import pytest

from minicsv import parse


def test_simple_rows():
    assert parse("a,b,c\n1,2,3") == [["a", "b", "c"], ["1", "2", "3"]]


def test_quoted_field_with_comma():
    assert parse('a,"b,c",d') == [["a", "b,c", "d"]]


def test_doubled_quote_inside_quoted_field():
    assert parse('"say ""hi""",x') == [['say "hi"', "x"]]


def test_quoted_field_with_embedded_newline():
    assert parse('"line1\nline2",x') == [["line1\nline2", "x"]]


def test_unterminated_quote_raises():
    with pytest.raises(ValueError):
        parse('"never closed')
