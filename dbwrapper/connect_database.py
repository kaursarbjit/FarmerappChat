import psycopg2
from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


class ConnectDatabase:
    """
    Creates a connection with the database.
    ...
    Attributes
    ----------
    database : str
        the database name
    user : str
        user name used to authenticate
    password : str
        password used to authenticate
    host : str
        database host address
    port : int
        connection port number
    """

    def __init__(self):
        """configure database"""
        self.connection = psycopg2.connect(database=DB_NAME,
                                           user=DB_USER,
                                           password=DB_PASSWORD,
                                           host=DB_HOST,
                                           port=DB_PORT)
        self.cursor = self.connection.cursor()

    def get_cursor(self):
        return self.cursor

    def close_connection(self):
        self.connection.close()
