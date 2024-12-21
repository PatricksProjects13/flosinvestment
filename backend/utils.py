def convert_yearly_interest_to_monthly(rate: float) -> float:
    monthly_rate = rate / 12
    return monthly_rate


def calculate_amount_to_buy(A, C, X=120, Y=35, Z=20, B=4):
    """
    Calculate the amount of stock to buy or sell based on the current value and other variables.

    Parameters:
    A (float): Current stock price (aktueller Kurs).
    C (int): Current number of shares held (current shares).
    X (int): Base investment in the number of shares at the average price (Langfristigige basisanlagesumme). Default is 120.
    Y (float): Average price (Kursmittel). Default is 35.
    Z (int): Step size for additional shares (Stufenschritt). Default is 20.
    B (float): Price step (Kursstufen). Default is 4.

    Returns:
    int: The number of shares to buy or sell to adjust the portfolio.
    """

    # Calculate the step difference (n) based on how far the current price (A) is from the average price (Y)
    n = round((A - Y) / B)  # Determine the price step difference

    # Constrain n to the range [-3, 3] to avoid excessive buying/selling
    n = max(n, -3)  # Minimum value for n is -3
    n = min(n, 3)  # Maximum value for n is 3

    if n != 0:
        # Calculate the adjusted amount of shares needed based on the step difference (n)
        return X + n * Z - C
    else:
        # If there is no step difference, maintain the base investment adjusted for current shares
        return X - C
