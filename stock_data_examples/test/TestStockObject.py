import unittest
import pandas as pd

from stock_data_examples.basic_financials.Stock import Stock


class TestStockObject(unittest.TestCase):
    # This class contains unittests to ensure the Stock object shows correct behaviour

    @classmethod
    def setUpClass(cls):
        # create test stock
        name = "test_stock"
        symbol = "ts"
        configs = {}
        price_history = pd.DataFrame(None, index=["2000-01-01", "2000-01-02", "2000-01-03"])
        price_history['open'] = [1., 2., 3.]
        price_history['high'] = [2., 0., 4.]
        price_history['low'] = [3., 4., 5.]
        price_history['close'] = [4., 5., 6.]

        test_stock = Stock(configs, name, symbol, price_history)
        cls.test_stock = test_stock

    @classmethod
    def tearDownClass(cls):
        pass

    def test_price_zero_values_are_filtered(self):
        # test if all zero prices are filtered when a new stock object is created
        any_zeros_in_price_history = self.test_stock.price_history.apply(lambda x: 0.0 in x.values, axis=1).any()
        self.assertFalse(any_zeros_in_price_history)


if __name__ == '__main__':
    unittest.main()