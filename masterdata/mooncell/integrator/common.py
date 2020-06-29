import logging
import sqlite3


class Integrator:

    def __init__(self, con: sqlite3.Connection, fallback_data: dict = None):
        self.con = con
        self.fallback_data = fallback_data
        # TODO: register adaptor
        self.setup()
        self.logger = logging.getLogger('masterdata.mooncell')

    def setup(self):
        pass

    def rename_column(self, table, **kw):
        for old_name, new_name in kw.items():
            self.con.execute(
                f'ALTER TABLE {table} RENAME {old_name} TO {new_name}')

    def add_column(self, table, **kw):
        for name, type_name in kw.items():
            self.con.execute(f'ALTER TABLE {table} ADD {name} {type_name}')

    def update(self, table: str, id: int, **kw):
        keys, values = zip(*kw.items())
        fields = ', '.join(map(lambda k: f'{k}=?', keys))
        sql = f'UPDATE {table} SET {fields} WHERE id=?'
        self.con.execute(sql, values + (id, ))

    def fallback(self, key: str) -> int:
        if key not in self.fallback_data:
            return 0
        values = self.fallback_data[key]
        count = -1
        for table_name, items in values.items():
            count = len(items)
            for kv in items:
                _id = kv.pop("id")
                keys, values = zip(*kv.items())
                fields = ', '.join(map(lambda k: f'{k}=?', keys))
                sql = f'UPDATE {table_name} SET {fields} WHERE id=?'
                self.con.execute(sql, values + (_id,))
        return count
