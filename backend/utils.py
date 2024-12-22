def convert_yearly_interest_to_monthly(rate: float) -> float:
    monthly_rate = rate / 12
    return monthly_rate


def flo_investment_formula(current_stock_price: float,
                           n_shares_hold: float,
                           target_number_of_shares: int = 120,
                           average_stock_price: float = 35,
                           step_size_shares: int = 20,
                           price_steps: int = 4) -> float:
    """
    Calculate the amount of stock to buy or sell based on the current value and other variables.

    Parameters:
    current_stock_price (float): Current stock price (aktueller Kurs).
    n_shares_hold (int): Current number of shares held (current shares).
    target_number_of_shares (int): Base investment in the number of shares at the average price (Langfristigige basisanlagesumme). Default is 120.
    average_stock_price (float): Average price (Kursmittel). Default is 35.
    step_size_shares (int): Step size for additional shares (Stufenschritt). Default is 20.
    price_steps (float): Price step (Kursstufen). Default is 4.

    Returns:
    int: The number of shares to buy or sell to adjust the etf.
    """

    # Calculate the step difference (n) based on how far the current price (current_stock_price) is from the average price (average_stock_price)
    n = round((current_stock_price - average_stock_price) / price_steps)  # Determine the price step difference

    # Constrain n to the range [-3, 3] to avoid excessive buying/selling
    n = max(n, -3)  # Minimum value for n is -3
    n = min(n, 3)  # Maximum value for n is 3

    if n != 0:
        # Calculate the adjusted amount of shares needed based on the step difference (n)
        return target_number_of_shares - n * step_size_shares - n_shares_hold
    else:
        # If there is no step difference, maintain the base investment adjusted for current shares
        return target_number_of_shares - n_shares_hold
