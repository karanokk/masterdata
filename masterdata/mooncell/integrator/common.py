import logging
import sqlite3


class Integrator:
    def __init__(self, con: sqlite3.Connection):
        self.con = con
        # TODO: register adaptor
        # self.setup()
        self.logger = logging.getLogger('masterdata.mooncell')

    def setup(self):
        pass

    def rename_column(self, table, **kw):
        for old_name, new_name in kw.items():
            self.con.execute(
                f"ALTER TABLE {table} RENAME {old_name} TO {new_name}")

    def add_column(self, table, **kw):
        for name, type_name in kw.items():
            self.con.execute(f"ALTER TABLE {table} ADD {name} {type_name}")
