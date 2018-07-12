from stock_data_examples.utils.DatabasePostgres import DatabasePostgres
from stock_data_examples.utils.ConfigsParameters import *

# Use this script to interact with the database - create, drop or query stockobjects table

db = DatabasePostgres()
conn, cursor = db.connect_to_db(configs)

print("create")
print("drop")
print("drop_create")
print("query")
print("\n")
table_action = input()

if table_action == "create":
    db.create_stockobjects_table(conn, cursor)
elif table_action == "drop":
    db.drop_stockobjects_table(conn, cursor)
elif table_action == "drop_create":
    db.drop_stockobjects_table(conn, cursor)
    db.create_stockobjects_table(conn, cursor)
elif table_action == "query":
    db.query_stockobjects_table(conn, cursor)

db.close_connection(conn, cursor)