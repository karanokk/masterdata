from typing import Union, List, Optional


def list2str(l: Union[list, str]) -> str:
    if isinstance(l, list):
        res = ','.join(map(list2str, l))
        return f"[{res}]"
    else:
        return str(l)


def restore_list(s: str, *, transform: callable = str):
    if s.startswith('['):
        s = s[1:]
    if s.endswith(']'):
        s = s[:-1]
    if s.startswith('['):
        result = s.split('],[')
        return [restore_list(x, transform=transform) for x in result]
    else:
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


def creation_sql(table_name: str, row: dict, *, primary_key=None):
    definitions = []
    for key, value in row.items():
        s_type = sqlite_type(value)
        words = [key, s_type]
        if primary_key == key:
            words.append('PRIMARY KEY')
        column_definition = ' '.join(words)
        definitions.append(column_definition)
    sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({",".join(definitions)})'
    return sql


def possible_primary_keys(rows: List[dict]) -> Optional[List[str]]:
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
