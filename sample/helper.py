"""Helper utilities for calculator module."""

def format_currency(amount: float) -> str:
    """Format numeric amount into currency string."""
    return f"${amount:,.2f}"

def get_tax_multiplier(region: str) -> float:
    """Return tax multiplier for region code.
    """
    rates = {
        "US": 1.07,
        "EU": 1.20,
        "UK": 1.20,
    }
    return rates.get(region, 1.0)
