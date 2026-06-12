"""Hidden verification for the minicsv spec (minicsv.py docstring)."""

import pytest

from minicsv import parse


def test_crlf_and_mixed_line_endings():
    assert parse("a,b\r\nc,d\ne,f") == [["a", "b"], ["c", "d"], ["e", "f"]]


def test_crlf_inside_quoted_field_is_literal():
    assert parse('"a\r\nb",c') == [["a\r\nb", "c"]]


def test_empty_fields_preserved():
    assert parse("a,,b") == [["a", "", "b"]]
    assert parse("a,") == [["a", ""]]
    assert parse(",a") == [["", "a"]]
    assert parse(",") == [["", ""]]


def test_empty_quoted_field():
    assert parse('"",a') == [["", "a"]]


def test_blank_middle_line_is_single_empty_field_row():
    assert parse("a\n\nb") == [["a"], [""], ["b"]]


def test_trailing_newline_produces_no_extra_row():
    assert parse("a,b\n") == [["a", "b"]]
    assert parse("a,b\r\n") == [["a", "b"]]


def test_empty_input_is_empty_list():
    assert parse("") == []


def test_field_with_only_doubled_quotes():
    assert parse('""""') == [['"']]


def test_unquoted_whitespace_preserved():
    assert parse(" a , b ") == [[" a ", " b "]]


def test_quote_after_closing_quote_raises():
    with pytest.raises(ValueError):
        parse('"abc"x,y')


def test_unterminated_quote_spanning_lines_raises():
    with pytest.raises(ValueError):
        parse('"a\nb')


def test_multiline_quoted_then_more_rows():
    assert parse('"x\ny",1\nz,2\n') == [["x\ny", "1"], ["z", "2"]]
