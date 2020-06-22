from os.path import join

from .extract import extract_servants
from .integrator import ServantIG
from ..json2sqlite3 import JSDatabase


def dump(dir_name: str):
    import json
    servants = extract_servants()
    for servant in servants:
        path = join(dir_name, f'No.{servant["collection_no"]}_{servant["name"]}.json')
        with open(path, 'w+') as f:
            json.dump(servant, f)


def integrate_into_db(path):
    """Add Chinese support for the database by referencing `mooncell` data.

    Some column names in the database will be modified(using `cn` and `jp` prefixes)
    to distinguish between Chinese and Japanese texts.

    Some custom tables(contents from `mooncell`) will be added.
    """
    db = JSDatabase(path)
    servants = extract_servants()
    db.begain()
    servant_ig = ServantIG(db.con, './patch/')
    for servant in servants:
        servant_ig.integrate(servant)
    # TODO: missions
    with open('./patch/custom.sql') as f:
        custom_patch = f.read()
    db.executescript(custom_patch)
    db.commit()


__all__ = ['dump', 'integrate_into_db', 'extract_servants']
