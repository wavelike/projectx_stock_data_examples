from stock_data_examples.utils.Persistable import Persistable
from stock_data_examples.utils.DatabasePostgres import DatabasePostgres

import pickle
import sys


class Environment(Persistable):

    def __init__(self):
        pass

    @staticmethod
    def persist_all(configs, stocks):
        # persist stock data - to filesystem or postgres db

        if stocks is not None:
            for stock_name, stock in stocks.items():

                if configs["save_to_filesystem"]:
                    stock.persist(stock.symbol)

                if configs["save_to_database"]:
                    conn, cursor = DatabasePostgres.connect_to_db(configs)
                    object_string = stock.to_object_string()
                    DatabasePostgres.write_object_to_db(conn, cursor,  stock.symbol, object_string)
                    DatabasePostgres.close_connection(conn, cursor)

    @staticmethod
    def load_all(configs):
        # load data - from filesystem or postgres db
        file = open(configs["stocks_filepath"], "r")

        stocks = {}
        if configs["load_objects_from"] == "database":
            conn, cursor = DatabasePostgres.connect_to_db(configs)
            for row in file:
                symbol = row.split(",")[0]
                object_string = DatabasePostgres.load_object_from_table(conn, cursor, symbol)
                loadedObject = pickle.loads(object_string)
                stocks.update({symbol: loadedObject})
            DatabasePostgres.close_connection(conn, cursor)

        elif configs["load_objects_from"] == "filesystem":
            for row in file:
                symbol = row.split(",")[0]
                stocks.update({symbol: Persistable.load(symbol)})

        else:
            print("wrong 'load_objects_from' config specified")
            sys.exit()

        return stocks