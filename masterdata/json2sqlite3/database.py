import json
import sqlite3
from typing import List

from .parse import (find_possible_primary_keys, list2str, parse_creation_sql,
                    parse_list)


def predecode(transform: callable):
    return lambda b: transform(b.decode())


sqlite3.register_adapter(list, list2str)
sqlite3.register_adapter(dict, json.dumps)

sqlite3.register_converter("strList", predecode(parse_list))
sqlite3.register_converter(
    "intList", lambda b: parse_list(b.decode(), transform=int))
sqlite3.register_converter("dict", predecode(json.loads))


class JSDatabase:
    def __init__(self, path: str):
        self.con = sqlite3.connect(path, detect_types=sqlite3.PARSE_COLNAMES)
        self.con.execute('PRAGMA synchronous = OFF')

    def __getattr__(self, name):
        return getattr(self.con, name)

    def __del__(self):
        self.con.close()

    def insert(self, table: str, row: dict):
        keys = row.keys()
        insert_sql = f'INSERT INTO {table} ({",".join(keys)}) values ({",".join(["?"] * len(keys))})'
        self.con.execute(insert_sql, tuple(row.values()))

    def insert_many(self, table, rows: List[dict]):
        keys = rows[0].keys()
        insert_sql = f'INSERT INTO {table} ({",".join(keys)}) values ({",".join(["?"] * len(keys))})'
        try:
            self.con.executemany(insert_sql, map(
                lambda x: tuple(x.values()), rows))
        except sqlite3.ProgrammingError:
            raise Exception(
                f'Table [{table}] has a different number of columns.')

    def table_exists(self, table: str) -> bool:
        for _ in self.con.execute(f'PRAGMA table_info({table})'):
            return True
        return False

    def table_has_field(self, table: str, field: str) -> bool:
        for info in self.con.execute(f'PRAGMA table_info({table})'):
            if info[1] == field:
                return True
        return False

    def begin_transaction(self):
        self.con.execute('BEGIN TRANSACTION')

    def end_transaction(self):
        self.con.execute('END TRANSACTION')

    def load_json(self, tables: dict):
        """Deserialize `tables` to a sqlite3 connection.

        Arguments:
            tables {dict} -- Tables stored in json format.
            >>> tables = {'student': [{'name': 'xxx', 'age': 18}],
                        'teacher': [{'name': 'yyy', 'class': 3}]}
        """
        self.con.execute('PRAGMA synchronous = OFF')

        for table_name, rows in tables.items():
            if not (isinstance(rows, list) and len(rows)):
                continue
            # create table
            primary_keys = find_possible_primary_keys(rows)
            primary_key = primary_keys[0] if primary_keys else None
            row_temp = rows[0]
            creation_sql = parse_creation_sql(
                table_name, row_temp, primary_key=primary_key)
            self.con.execute(creation_sql)
            # insert rows
            self.insert_many(table_name, rows)
        self.con.commit()
