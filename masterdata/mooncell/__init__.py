from os.path import join

from .extract import extract_all_servants
from .integrator import ServantIG
from ..json2sqlite3 import JSDatabase


def dump(dir_name: str):
    import json
    servants = extract_all_servants()
    for servant in servants:
        path = join(dir_name, f'No.{servant["collection_no"]}_{servant["name"]}.json')
        with open(path, 'w+') as f:
            json.dump(servant, path)


def integrate_into_db(path):
    """Add Chinese support for the database by referencing `mooncell` data.

    Some column names in the database will be modified(using `cn` and `jp` prefixes)
    to distinguish between Chinese and Japanese texts.

    Some custom tables(contents from `mooncell`) will be added.
    """
    con = JSDatabase(path).con
    servants = extract_all_servants()
    servant_ig = ServantIG(con)
    for servant in servants:
        servant_ig.integrate(servant)
    # TODO: missions
    con.commit()
    con.close()


__all__ = ['dump', 'integrate_into_db']