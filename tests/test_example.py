import pytest
from er_custom_module.math_example import add_numbers, multiply_numbers


def test_add_numbers():
    """Test the add_numbers function."""
    assert add_numbers(2, 3) == 5
    assert add_numbers(-1, 1) == 0
    assert add_numbers(0, 0) == 0


def test_multiply_numbers():
    """Test the multiply_numbers function."""
    assert multiply_numbers(2, 3) == 6
    assert multiply_numbers(-1, 1) == -1
    assert multiply_numbers(0, 5) == 0
