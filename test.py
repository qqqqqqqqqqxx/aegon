import unittest
from main import SwapPortfolio
class TestFunction(unittest.TestCase):

    def setUp(self) -> None:
        print('start testing')

    def tearDown(self) -> None:
        print('end of testing')
    def test_n_instruments(self):
        swap_portfolio = SwapPortfolio.get_fund_portfolio_data()
        self.assertEqual(swap_portfolio.n_instruments, 23)
