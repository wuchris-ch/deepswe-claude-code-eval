"""Visible tests. These encode part of the spec in evaluator.py's docstring
and must not be weakened — the full spec is also exercised elsewhere."""

import pytest

from evaluator import evaluate


def test_basic_precedence():
    assert evaluate("1+2*3") == 7
    assert evaluate("(1+2)*3") == 9


def test_division_is_true_division():
    assert evaluate("10/4") == 2.5
    assert evaluate("8/2") == 4.0


def test_power_is_right_associative():
    assert evaluate("2^3^2") == 512


def test_unary_minus_vs_power():
    assert evaluate("-2^2") == -4


def test_unbalanced_parens_raise():
    with pytest.raises(ValueError):
        evaluate("(1+2")
