"""Unit tests generated and audited by awam for sample/calculator.py."""

import pytest
import sys, os
sys.path.insert(0, os.path.abspath('sample'))
from sample.calculator import divide, calculate_discount, parse_user_scores

def test_divide_by_zero():
    """Verify divide raises ZeroDivisionError when denominator is zero."""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)



from sample.calculator import parse_user_scores, calculate_discount, calculate_total_with_tax


# --- Edge cases identified by awam ---

def test_parse_user_scores_empty_list():
    """Verify that empty list input raises ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        parse_user_scores([])

def test_calculate_discount_negative_price():
    """Verify that negative price returns a negative discounted value."""
    assert calculate_discount(-100, 10) == -90.0

def test_calculate_total_with_tax_invalid_region():
    """Verify that unsupported region raises KeyError."""
    with pytest.raises(KeyError):
        calculate_total_with_tax(100, "INVALID")
