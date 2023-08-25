import numpy as np
import pandas as pd
import os

# CONSTANTS
# Files

DATA_FOLDER = "data"  # change data_sources to data
HOLDINGS_FILE = "holdings.csv"
INSTRUMENTS_FILE = "instruments.csv"
KEYRATE_ATTRIBUTION_FILE = "cashflows_attribution.csv"
# Columns
ID = "ISIN"
FUND_NAME = "FUND"
INSTRUMENT_TYPE = "TYPE"
TOTAL_CASHFLOW = "CF_TOTAL"
COUNTERPARTY = "COUNTERPARTY"
CF_COLUMNS = ["CF_1Y", "CF_2Y", "CF_3Y", "CF_4Y", "CF_5Y", "CF_10Y",
              "CF_15Y", "CF_20Y", "CF_25Y", "CF_30Y", "CF_35Y", "CF_40Y"]
CF_TENORS = [2, 10, 20, 40]
# Values
SWAP_TYPE = "SWAP"


# Portfolio classes
class Portfolio:
    """
    A general portfolio class that implements methods common across different portfolio classes.

    :param portfolio_data: a dataframe of all the instruments in the portfolio
    :type portfolio_data: pd.DataFrame
    """

    def __init__(self, portfolio_data: pd.DataFrame):
        """
        Initialize the Portfolio object.

        :param portfolio_data: a dataframe of all the instruments in the portfolio,
            where the index is the ISINs of the instruments and the columns are the other variables.
        :type portfolio_data: pd.DataFrame
        """
        self.data = portfolio_data
        self.cashflows_attribution = self.get_cashflows_attribution()
        self.cashflows = self.calc_portfolio_cashflows

    @property
    def n_instruments(self):
        """Return the number of instruments in the portfolio.

        :return: Number of instruments
        :rtype: int
        """
        return self.data.shape[1]

    @property
    def calc_portfolio_cashflows(self):
        """
        Calculate cashflow pattern for each instrument using the type-specific method.

        :return: a dataframe of cashflows, where the index is the ISINs of the instruments,
            and the columns are the tenors of interest (2, 10, 20, 40).
        :rtype: pd.DataFrame
        """
        return np.matmul(self.data[CF_COLUMNS], self.cashflows_attribution.T)

    @staticmethod
    def get_cashflows_attribution() -> pd.DataFrame:
        """
        Load the matrix used to attribute "detailed" cashflows from the file to tenors of interest.

        :return: a dataframe of attribution weights, where the index is the keyrates,
            and the columns are the years used in the file.
        :rtype: pd.DataFrame
        """
        keyrate_attribution_filepath = os.path.join(DATA_FOLDER, KEYRATE_ATTRIBUTION_FILE)
        keyrate_attribution = pd.read_csv(keyrate_attribution_filepath, index_col=0)
        return keyrate_attribution

    @classmethod
    def get_instrument_cashflows(cls, original_instrument_cashflow: pd.DataFrame):
        """
        A placeholder method; this should be overriden in type-specific child classes.

        :param original_instrument_cashflow: The cashflow data of the original instrument.
        :type original_instrument_cashflow: Specific type (to be defined in child classes)
        :raises: NotImplemented
        """
        raise NotImplemented

    @classmethod
    def get_fund_portfolio_data(cls, fund: str):
        """
        Placeholder method; details to be provided in child classes.

        :param fund: The fund data.
        :type fund: Specific type (to be defined in child classes)
        :raises: NotImplemented
        """
        raise NotImplemented


class SwapPortfolio(Portfolio):
    """ A swap-specific portfolio class. Inherits from the general Portfolio class, and implements
    methods specific to swaps.

    Args:
        portfolio_data (pd.DataFrame): a dataframe of all the swaps in the portfolio,
            where the index is the ISINs of the swaps, and the columns are the other variables.
    """

    def __init__(self, portfolio_data: pd.DataFrame):
        super().__init__(portfolio_data)

    @classmethod
    def get_fund_portfolio_data(cls, fund: str = 'EuroSwaps'):
        """
        Prepare the data for a specific fund.
        Read the holdings file to find out what instruments are in the fund's portfolio.
        Read the instruments file to get the instrument-specific data.
        Append the instrument data to the portfolio.

        :param fund: the name of the fund
        :type fund: str
        :return: a dataframe of all the instruments in the portfolio, where the index is the ISINs of the instruments,
                 and the columns are the other variables.
        :rtype: pd.DataFrame
        """
        # Read files
        instruments_filepath = os.path.join(DATA_FOLDER, INSTRUMENTS_FILE)

        instruments = pd.read_csv(instruments_filepath, delimiter=';', decimal=",",
                                  index_col=ID)  # remove ID, no column name in CSV file
        holdings_filepath = os.path.join(DATA_FOLDER, HOLDINGS_FILE)
        holdings = pd.read_csv(holdings_filepath)

        # Filter fund holdings
        sel_fund = holdings[FUND_NAME] == fund
        fund_holdings = holdings.loc[sel_fund]
        # Merge by column name
        fund_holdings = pd.merge(fund_holdings, instruments, on=ID)
        sel_swaps = fund_holdings["TYPE"] == SWAP_TYPE  # is this for only EuroSwaps
        return cls(fund_holdings.loc[sel_swaps])

    def cashflow_per_counterparty(self):
        """
        Calculate total cashflows for each counterparty across swaps.

        :return: a series of total cashflow for each counterparty in the portfolio.
        :rtype: pd.Series
        """
        total_cf_per_counterparty_new = self.data.groupby(COUNTERPARTY)[TOTAL_CASHFLOW].sum()
        return total_cf_per_counterparty_new


# Instantiate with the class method
if __name__ == '__main__':
    swap_portfolio = SwapPortfolio.get_fund_portfolio_data()

    # Summarize portfolio
    print("There are" + f"{swap_portfolio.n_instruments} + swaps in the portfolio.")

    portfolio_casfhlow = swap_portfolio.cashflows.sum(axis=1)
    print("\nPortfolio has the following  at tenors:")
    print(portfolio_casfhlow)

    total_counterparty_cf = swap_portfolio.cashflow_per_counterparty()
    print("\nThe counterparty with the highest total cashflow is" + f"{total_counterparty_cf.max()}" + ",")
    print(f"with a cashflow of" + f"{total_counterparty_cf}")
