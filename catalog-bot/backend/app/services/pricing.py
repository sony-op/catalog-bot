def calculate_selling_price(average_market_price: float, manufacturing_or_buy_cost: float = 0.0) -> dict:
    """
    Calculates the suggested selling price and estimated profit based on market average.
    Considers an approximate 15% platform fee and fixed shipping rate (₹60).
    """
    # If market price could not be determined, fallback to a base or flag error
    if average_market_price is None or average_market_price <= 0:
        return {
            "suggested_price": None,
            "estimated_profit": None,
            "error": "Could not determine market price."
        }
        
    platform_fee_percent = 0.15
    shipping_fee = 60.0
    
    # Let's suggest matching or slightly undercutting the market average (- 5%)
    suggested_price = round(average_market_price * 0.95, 2)
    
    # Calculate costs
    platform_fee = suggested_price * platform_fee_percent
    total_cost = manufacturing_or_buy_cost + platform_fee + shipping_fee
    
    estimated_profit = round(suggested_price - total_cost, 2)
    
    return {
        "market_average": average_market_price,
        "suggested_price": suggested_price,
        "estimated_profit": estimated_profit,
        "platform_fee": round(platform_fee, 2),
        "shipping_fee": shipping_fee
    }
