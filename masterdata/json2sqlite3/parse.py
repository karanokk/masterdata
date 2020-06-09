from typing import Union, List, Optional


def list2str(l: Union[list, str]) -> str:
    """Format `list` as `str`."""
    if isinstance(l, list):
        res = ','.join(map(list2str, l))
        return f"[{res}]"
    else:
        return str(l)


def parse_list(s: str, *, transform: callable = str):
    s = s[1:-1]
    if s.startswith('['):
        result = s[1:-1].split('],[')
        return [transform(s) for s in s.split(',') for x in result]
    return [transform(s) for s in s.split(',') if s]


def sqlite_type(obj: object) -> str:
    obj_type = type(obj)
    if obj_type in (str, list, dict):
        return 'TEXT'
    elif obj_type == bool:
        return 'BOOLEAN'
    elif obj_type == int:
        return 'INTEGER'
    elif obj_type == float:
        return 'REAL'
    elif obj is None:
        raise TypeError('Cannot infer type from a `None` value.')
    else:
        raise TypeError('Unsupported type.')


def parse_creation_sql(table_name: str, row: dict, *, primary_key=None):
    definitions = []
    for key, value in row.items():
        stype = sqlite_type(value)
        words = [key, stype]
        if primary_key == key:
            words.append('PRIMARY KEY')
        column_definition = ' '.join(words)
        definitions.append(column_definition)
    sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({",".join(definitions)})'
    return sql


def find_possible_primary_keys(rows: List[dict]) -> Optional[List[str]]:
    temp = {key: set()
            for key, value in rows[0].items() if isinstance(value, int)}
    for row in rows:
        out_keys = []
        for key, value in temp.items():
            new_value = row[key]
            if new_value in value:
                out_keys.append(key)
            else:
                value.add(new_value)
        for out_key in out_keys:
            del temp[out_key]
        if not temp:
            return None
    return list(temp.keys())
