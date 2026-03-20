from typing import List, Dict

def filter_orders_by_symbol(orders: List[Dict], symbol: str) -> List[Dict]:

    target = (symbol or "").strip().upper()

    matched = []

    for o in orders:

        order_symbol = (
            o.get("trading_symbol")
            or o.get("symbol")
            or o.get("instrument")
            or ""
        ).strip().upper()

        # contains match instead of exact match
        if target in order_symbol:
            matched.append(o)

    return matched