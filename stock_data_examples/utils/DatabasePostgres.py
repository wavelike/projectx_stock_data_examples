import psycopg2
import psycopg2.extras

class DatabasePostgres():

    def __init__(self):
        pass

    @classmethod
    def connect_to_db(cls, configs):

        # open connection to postgres db and initialise cursor
        connect_str = "dbname='" + configs["db_name"] + "' user='" + configs["db_user"] + \
                      "' host='localhost' " + "password='" + configs["db_password"] + "'"

        conn = psycopg2.connect(connect_str)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  # returns python dicts on select queries

        return conn, cursor

    def create_stockobjects_table(self, conn, cursor):
        sql_command = """CREATE TABLE stockObjects (id serial PRIMARY KEY, datetime TIMESTAMP, name varchar,
            object_string BYTEA );"""

        cursor.execute(sql_command)
        conn.commit()  # make changes persistent

    def drop_stockobjects_table(self, conn, cursor):
        cursor.execute("DROP TABLE stockObjects")
        conn.commit()

    @classmethod
    def close_connection(cls, conn, cursor):
        # Close communication with the database
        cursor.close()
        conn.close()

    @classmethod
    def write_object_to_db(cls, conn, cursor, name, object_string):

        # Either update already existing object row or create a new one
        cursor.execute("""SELECT * from stockObjects WHERE name=(%s)""", (name,))
        rows = cursor.fetchall()

        if len(rows) == 1: # if object exists, update row
            cursor.execute("""UPDATE stockObjects SET datetime=now(), object_string=(%s) 
                     WHERE name=(%s)""",
                           (psycopg2.Binary(object_string), name,))
        elif len(rows) == 0: # if object does not exist, create new row
            cursor.execute("""INSERT INTO stockObjects (datetime, name, object_string)
            VALUES (
            now(),
            %s,
            %s
            )""",
            (name, psycopg2.Binary(object_string),))
        else:
            print("duplicate object")

        conn.commit()  # make changes persistent


    def query_stockobjects_table(self, conn, cursor):
        cursor.execute("""SELECT * from stockObjects""")
        rows = cursor.fetchall()
        conn.commit()
        for row in rows:
            print(row)

    @classmethod
    def load_object_from_table(cls, conn, cursor, name):
        print("Load object from db: " + name)
        cursor.execute("""SELECT object_string from stockObjects WHERE name='""" + name + """'""")
        rows = cursor.fetchall()
        conn.commit()  # make changes persistent

        if len(rows) == 1:
            return rows[0][0]
        elif len(rows) == 0:
            print("No such object exists")
        elif len(rows) > 1:
            print("more than one object with the same name found")