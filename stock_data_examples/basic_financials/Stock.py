from stock_data_examples.utils.Persistable import Persistable
from stock_data_examples.APIError import APIError
from alpha_vantage.timeseries import TimeSeries

import time
import sys

class Stock(Persistable):

    def __init__(self, configs, name, symbol, price_history=None):
        # name and symbol are necessary attributes
        # price_history can be provided externally (e.g. taken from a local database);
        #  if not, the most current data is fetched from alphavantage api
        self.name = name
        self.symbol = symbol

        if price_history is None:
            price_history = self.import_price_history(configs)

        price_history = self.process_price_history_data(price_history)
        self.price_history = price_history

    def import_price_history(self, configs):
        # start alphavantage data import for the full history data
        ts = TimeSeries(key=configs["alpha_vantage_key"], output_format='pandas')

        try:
            price_history, meta_data = ts.get_daily(symbol=self.symbol, outputsize='full')
        except:
            raise APIError("Error: Data fetching through API failed")

        # rename columns
        price_history = price_history.rename(index=str, columns={"1. open": "open", "2. high": "high",
                                               "3. low": "low", "4. close": "close"})
        # drop unnecessary columns
        price_history = price_history.drop(columns="5. volume")

        return price_history

    def process_price_history_data(self, price_history):
        # filter out all rows with any zero prices (which are alpha vantages 'missing values')
        price_history = price_history[price_history.apply(lambda x: 0.0 in x.values, axis=1) == False]
        
        return price_history

    @staticmethod
    def import_data(configs):
        filepath = configs["stocks_filepath"]
        stocks = {}
        file = open(filepath, "r")
        for row in file:
            symbol = row.split(",")[0]
            name = row.split(",")[1].rstrip()
            print(symbol)

            # try three times to access api data. If this does not work, inform user and exit
            attempt_nr = 0
            while attempt_nr < 3:
                try:
                    stocks.update({symbol: Stock(configs, name, symbol)})
                    break
                except APIError as e:
                    time.sleep(2)
                    attempt_nr += 1
                    if attempt_nr == 3:
                        print(e)
                        print("attempts: 3, symbol: " + symbol)
                        sys.exit()
        return stocks