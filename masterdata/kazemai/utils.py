import json
import re

from lzstring import LZString


def decode_master_js(s: str) -> dict:
    matched = re.search(
        r"convert_formated_hex_to_string\('(.*)'\)\);", s).group(1)
    # convert formatted hex to string
    compressed = ''.join(
        chr(int(matched[i:i + 2], 16) | (int(matched[i + 2:i + 4], 16) << 8))
        for i in range(0, len(matched) - 1, 4))
    del matched
    res = LZString().decompress(compressed)
    return json.loads(res)
