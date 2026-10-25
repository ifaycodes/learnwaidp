"""Sample calculator module for testing awam's edge case detection."""

import helper

def divide(a: float, b: float) -> float:
    return a / b

def calculate_discount(price: float, discount_percent: float) -> float:
    if discount_percent > 100:
        raise ValueError("Discount cannot exceed 100%")
    return price * (1.0 - (discount_percent / 100.0))

def calculate_total_with_tax(price: float, region: str) -> float:
    multiplier = helper.get_tax_multiplier(region)
    return price * multiplier

def parse_user_scores(scores: list[int]) -> dict:
    return {
        "count": len(scores),
        "average": sum(scores) / len(scores),
        "highest": max(scores),
    }
