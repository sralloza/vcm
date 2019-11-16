import sqlite3
from datetime import datetime

from vcm.core.settings import GeneralSettings


class DatabaseInterface:
    def __init__(self):
        self.connection = sqlite3.connect(GeneralSettings.database_path.as_posix())
        self.cursor = self.connection.cursor()
        self.ensure_table()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.close()

    def ensure_table(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS database_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                subject TEXT NOT NULL,
                datetime TEXT NOT NULL
                )"""
        )

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

    def save_link(self, link):
        data = [
            link.url,
            link.subject.name,
            datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
        ]
        try:
            self.cursor.execute("INSERT INTO database_links VALUES (NULL,?,?,?)", data)
            return True
        except sqlite3.IntegrityError:
            return False


class DatabaseLinkInterface:
    @staticmethod
    def save(link):
        with DatabaseInterface() as connection:
            return connection.save_link(link)
