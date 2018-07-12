from stock_data_examples.basic_financials.Stock import Stock

from stock_data_examples.basic_financials.Environment import Environment
from stock_data_examples.utils.ConfigsParameters import *

# Import
stocks = Stock.import_data(configs)

# Persist results
Environment.persist_all(configs, stocks)