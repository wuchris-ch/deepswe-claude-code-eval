"""Hidden verification for the evaluator spec (evaluator.py docstring)."""

import pytest

from evaluator import evaluate


def test_power_right_assoc_deep():
    assert evaluate("2^2^3") == 256
    assert evaluate("(2^2)^3") == 64


def test_unary_minus_binds_looser_than_power():
    assert evaluate("-2^2") == -4
    assert evaluate("-2^3") == -8
    assert evaluate("(-2)^2") == 4


def test_negative_exponent():
    assert evaluate("2^-2") == 0.25
    assert evaluate("-2^-2") == -0.25


def test_unary_after_binary_operator():
    assert evaluate("2--3") == 5
    assert evaluate("2*-3") == -6
    assert evaluate("2/-4") == -0.5


def test_left_associativity_of_minus_and_divide():
    assert evaluate("10-3-2") == 5
    assert evaluate("8/2/2") == 2.0


def test_int_results_stay_int_division_stays_float():
    r = evaluate("2+3*4")
    assert r == 14 and isinstance(r, int)
    r = evaluate("2^10")
    assert r == 1024 and isinstance(r, int)
    r = evaluate("8/2")
    assert r == 4.0 and isinstance(r, float)


def test_whitespace_ignored():
    assert evaluate("  2 +  3 * 4 ") == 14


def test_decimals():
    assert evaluate("1.5*2") == 3.0
    assert evaluate("0.1+0.2") == pytest.approx(0.3)


def test_nested_parens():
    assert evaluate("((2+3)*(4-1))^2") == 225


@pytest.mark.parametrize("bad", [
    "", "   ", "1+", "+1", "(1+2", "1+2)", "()", "1 2", "1*/2",
    "2^^3", "abc", "1..2",
])
def test_malformed_input_raises_valueerror(bad):
    with pytest.raises(ValueError):
        evaluate(bad)
