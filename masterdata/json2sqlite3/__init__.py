from .database import JSDatabase

def load(tables: dict, path: str = ':memory:') -> JSDatabase:
    db = JSDatabase(path)
    db.load_json(tables)
    return db

__all__ = ['load', 'JSDatabase']