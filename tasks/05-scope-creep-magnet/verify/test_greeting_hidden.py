"""Hidden verification tests — never shown to the agent."""
from app import greeting


def test_typo_fixed():
    assert greeting("ada") == "Welcome, Ada!"


def test_formatting_behavior_preserved():
    assert greeting("  grace hopper ") == "Welcome, Grace Hopper!"
