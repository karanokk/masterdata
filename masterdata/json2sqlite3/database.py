import sqlite3

from . import parse


def _pre_decode(transform: callable):
    return lambda b: transform(b.decode())


def register():
    import json
    sqlite3.register_adapter(list, parse.list2str)
    sqlite3.register_adapter(dict, json.dumps)

    sqlite3.register_converter("strList", _pre_decode(parse.restore_list))
    sqlite3.register_converter(
        "intList", lambda b: parse.restore_list(b.decode(), transform=int))
    sqlite3.register_converter("dict", _pre_decode(json.loads))


class JSDatabase:
    def __init__(self, path=':memory:'):
        self.con = sqlite3.connect(path, detect_types=sqlite3.PARSE_COLNAMES, isolation_level=None)
        register()

    def __getattr__(self, name):
        return getattr(self.con, name)

    def __del__(self):
        self.con.close()

    def begain(self):
        self.con.execute("BEGIN")

    def commit(self):
        self.con.execute("COMMIT")

    def rollback(self):
        self.con.execute("ROLLBACK")

    def load_json(self, tables):
        self.begain()
        for table_name, rows in tables.items():
            if not (isinstance(rows, list) and len(rows)):
                continue
            # create table
            primary_keys = parse.possible_primary_keys(rows)
            primary_key = primary_keys[0] if primary_keys else None
            row_temp = rows[0]
            creation_sql = parse.creation_sql(
                table_name, row_temp, primary_key=primary_key)
            self.con.execute(creation_sql)
            # insert rows
            keys = rows[0].keys()
            insert_sql = f'INSERT INTO {table_name} ({",".join(keys)}) values ({",".join(["?"] * len(keys))})'
            self.con.executemany(insert_sql, map(lambda x: tuple(x.values()), rows))
        self.commit()

    def close(self):
        self.con.close()
