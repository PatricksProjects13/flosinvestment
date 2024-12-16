from dataclasses import dataclass

from typing import Callable


class SharePrize:
    """
    Represents a share prize with a mutable value. This class allows updating
    its value through a function passed as a parameter, providing flexibility
    in how the value can be adjusted over time.

    :ivar value: The current value of the share prize.
    :type value: float
    """

    def __init__(self, init_share_prize: float):
        self.value = init_share_prize

    def update_value(self, updater: Callable[[float], float]):
        self.value = updater(self.value)

    def __repr__(self):
        return f"SharePrize({self.value})"


@dataclass
class Share:
    current_prize_per_unit: SharePrize  # We use an instance of a class instead of a pure float to update the price for all the shares at once
    purchasing_prize_per_unit: float
    units: float
    time_bought: tuple[int, int]  # The month, year the asset was bought

    @property
    def current_value(self):
        return self.current_prize_per_unit.value * self.units

    @property
    def purchasing_value(self):
        return self.purchasing_prize_per_unit * self.units


class Portfolio:
    def __init__(self,
                 updater: Callable[[float], float],  # Updated den Aktienpreis für den nächsten Monat
                 yearly_tax_free_allowance: float = 1000,  # Steuerfreibetrag
                 capital_yields_tax_percentage: int = 25,  # Kapitalertragssteuer
                 init_month: int = 1,
                 init_year: int = 2024):
        """
        This class simulates a portfolio of shares.

        It sets up the initial conditions for the portfolio by defining the starting
        month, year, and tax-related details such as the yearly tax-free allowance,
        capital yields tax percentage, and initializes various attributes to manage
        portfolio shares and losses.

        :param updater: Callable to update the stock price for the next month.
        :param yearly_tax_free_allowance: The tax-free allowance provided
            annually for the investment. Default is set to 1000.
        :param capital_yields_tax_percentage: The percentage of tax applied
            to capital yields. Default is set to 25.
        :param init_month: The starting month for the investment timeline.
            Default is set to January (1).
        :param init_year: The initial year for the investment timeline.
            Default is set to 2024.
        """
        self.shares: list[Share] = []
        self.month = init_month
        self.year = init_year
        self.updater = updater
        self.yearly_tax_free_allowance = yearly_tax_free_allowance
        self.remaining_yearly_tax_free_allowance = yearly_tax_free_allowance
        self.yearly_loss_pot = 0.0  # Verlusttopf
        self.capital_yields_tax_percentage = capital_yields_tax_percentage
        self.share_prize_per_unit = SharePrize(1)  # The initial current_value is not important

    @property
    def current_total_value(self) -> float:
        """
        Calculate the current total value of shares.

        This property computes the total value by summing up the product of the
        current prize per unit and the number of units for each share available
        in the 'shares' list attribute.

        :return: Total value of the shares.
        :rtype: float
        """
        return sum(share.current_prize_per_unit.value * share.units for share in self.shares)

    @property
    def invested_money(self) -> float:
        """
        Computes the total invested money calculated by summing the product of
        purchasing price per unit and number of units for each share in the
        'shares' collection.

        :return: The total invested money as a float calculated from share
                 purchasing prices and units.
        :rtype: float
        """
        return sum(share.purchasing_prize_per_unit * share.units for share in self.shares)

    def buy(self, money: float, cost_buy: float):
        """
        Executes a transaction to buy shares based on available money and the cost
        of buying a unit. The method updates the remaining money after the purchase
        and appends a new Share instance to the list of shares if the transaction
        is valid and possible.

        :param money: The current amount of money available for purchasing shares.
        :type money: float
        :param cost_buy: The cost incurred to buy the shares.
        :type cost_buy: float
        :return: None if the purchase cannot be made due to insufficient funds.
        :rtype: None
        """
        money = money - cost_buy
        if money < 0:
            return
        share = Share(current_prize_per_unit=self.share_prize_per_unit,
                      purchasing_prize_per_unit=self.share_prize_per_unit.value,
                      units=money / self.share_prize_per_unit.value,
                      time_bought=(self.month, self.year))
        self.shares.append(share)

    def sell(self, target_money_sell: float, transaction_costs: float) -> tuple[float, float, float]:
        """
        Calculates and executes the sale of shares to achieve a target return after accounting
        for transaction costs and taxes. It handles shares based on their acquisition order,
        considers any accumulated annual loss to offset profits, and applies relevant tax
        allowances. The function stops selling when the target return is met or there are no
        more shares to sell. It operates under the assumption that shares are sold in the
        order they were acquired (FIFO approach).

        :param target_money_sell: Target amount of money to achieve through the sale
            of shares.
        :type target_money_sell: float
        :param transaction_costs: Costs associated with executing the transaction.
        :type transaction_costs: float
        :return: A tuple, containing the returned money, the payed taxes and the amount of transaction costs.
        :rtype: tuple[float, float, float]
        """
        # If selling costs more than the target return or no shares, sell nothing
        if target_money_sell < transaction_costs or not self.shares:
            return 0.0, 0.0, 0.0
        # We collect the returned money from selling in the following variable
        returned_money = 0.0  # Without tax and costs, has to be subtracted afterward
        profit = 0.0
        # Start selling shares, beginning from the first. We can sell fractions
        while True:
            # If there are no shares, nothing to sell
            if not self.shares:
                break
            # Get oldest shares
            oldest_share = self.shares.pop(0)
            current_value = oldest_share.current_value
            # If the share has more value than the target sell, only sell a fraction
            if current_value > target_money_sell:
                # Only sell a fraction:
                selling_amount = target_money_sell / oldest_share.current_prize_per_unit.value
                oldest_share.units -= selling_amount  # Reducer the number of units
                self.shares = [oldest_share] + self.shares  # Add the share again to the history
                profit += target_money_sell - selling_amount * oldest_share.purchasing_prize_per_unit
                returned_money += target_money_sell
                target_money_sell -= target_money_sell
                break
            else:
                profit += current_value - oldest_share.purchasing_value
                returned_money += current_value
                target_money_sell -= current_value
        if profit < 0:
            tax = 0.0
            self.yearly_loss_pot += -profit
        else:
            profit_minus_loss_pot = profit - min(self.yearly_loss_pot, profit)
            self.yearly_loss_pot -= min(profit, self.yearly_loss_pot)
            profit_part_in_tax_free_allowance = min(self.remaining_yearly_tax_free_allowance, profit_minus_loss_pot)
            profit_part_outside_tax_free_allowance = profit_minus_loss_pot - profit_part_in_tax_free_allowance
            self.remaining_yearly_tax_free_allowance -= profit_part_in_tax_free_allowance
            tax = profit_part_outside_tax_free_allowance * self.capital_yields_tax_percentage / 100.0
        return returned_money - transaction_costs - tax, tax, transaction_costs

    def next_month(self):
        """
        Advances the current month by one. If the current month is December, it
        rolls over to January of the next year, and resets the remaining yearly
        tax-free allowance to the initial yearly tax-free allowance. Additionally,
        updates the current prize per unit for each share using a provided updater.

        :return: None
        """
        if self.month < 12:
            self.month += 1
        else:
            self.month = 1
            self.year += 1
            self.remaining_yearly_tax_free_allowance = self.yearly_tax_free_allowance
        self.share_prize_per_unit.update_value(self.updater)


if __name__ == '__main__':
    portfolio = Portfolio(updater=lambda price: 1.05 * price)
    print(portfolio.current_total_value)
    portfolio.buy(money=100, cost_buy=1)
    portfolio.next_month()
    portfolio.buy(money=100, cost_buy=1)
    portfolio.next_month()
    portfolio.buy(money=100, cost_buy=1)
    portfolio.next_month()
    for _ in range(5):
        rm, t, c = portfolio.sell(100, 1)
        print(portfolio.current_total_value, rm, t, c)
