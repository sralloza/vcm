import sqlite3

from vcm.core.options import Options


class DatabaseInterface:
    def __init__(self):
        self.connection = sqlite3.connect(Options.DATABASE_PATH.as_posix())
        self.cursor = self.connection.cursor()
        self.ensure_table()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.close()

    def ensure_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS database_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL
                )""")

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def save_link(self, link):
        try:
            self.cursor.execute("INSERT INTO database_links VALUES (NULL,?)", [link.url])
            return True
        except sqlite3.IntegrityError:
            return False


class DatabaseLinkInterface:
    @staticmethod
    def save(link):
        with DatabaseInterface() as connection:
            return connection.save_link(link)
