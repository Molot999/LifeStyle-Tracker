import sqlite3

db_name = 'lft.db'

class DBManager:

    def __init__(self):
        pass

    def __enter__(self):
        self._connection = sqlite3.connect(db_name)
        self._cursor = self._connection.cursor()
        return self._cursor

    def __exit__(self, exc_type, exc_value, tb):
        self._cursor.close()
        if exc_type is not None:
            self._connection.rollback()
            print(f"DB transaction failed: {exc_value}")
        else:
            self._connection.commit()
        self._connection.close()