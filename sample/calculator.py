"""Sample calculator module for testing awam's edge case detection."""

def divide(a: float, b: float) -> float:
    """Divide a by b.
    
    Warning: ZeroDivisionError occurs if b is 0.
    """
    return a / b

def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate discounted price.
    
    Expected constraints:
    - price must be positive
    - discount_percent must be between 0 and 100
    """
    if discount_percent > 100:
        raise ValueError("Discount cannot exceed 100%")
    # Missing guard: price < 0 or discount_percent < 0!
    return price * (1.0 - (discount_percent / 100.0))

def parse_user_scores(scores: list[int]) -> dict:
    """Calculate aggregate statistics for scores.
    
    Warning: Fails if scores list is empty!
    """
    return {
        "count": len(scores),
        "average": sum(scores) / len(scores),
        "highest": max(scores),
    }
