from app.utils.exceptions import TradeException

def calculate_price_with_action(
    current_price: float,
    action: str,
    step: float = 2.0
) -> float:
    if action not in ["+", "-"]:
        raise TradeException("Invalid action. Allowed: + or -")

    if current_price <= 0:
        raise TradeException("Current price must be > 0")

    new_price = current_price + step if action == "+" else current_price - step

    if new_price <= 0:
        raise TradeException("Resulting price invalid")

    return new_price
