import asyncio
import logging
from typing import Union, List, Tuple

from .extractors import ServantExtractor
from . import api

logger = logging.getLogger('masterdata.mooncell')


def parse_html_to_servant(html: Union[bytes, str]) -> dict:
    extractor = ServantExtractor(html)
    d = {}
    for func_name in type(extractor).__dict__.keys():
        if func_name.startswith("extract_"):
            name = func_name[8:]
            extract_fn = getattr(extractor, func_name)
            try:
                res = extract_fn()
            except:
                logger.error(f'Failed to extract {d["name"]} for part: {name}.')
            else:
                d[name] = res
    return d


def get_all_servants(name_links) -> Tuple[str, List[dict]]:
    async def get_servant_detail(name_link: str):
        text = await api.async_get_page(name_link)
        d = parse_html_to_servant(text)
        return name_link, d

    loop = asyncio.get_event_loop()
    task_gen = (loop.create_task(get_servant_detail(name_link)) for name_link in name_links)
    res = loop.run_until_complete(asyncio.gather(*task_gen))
    return res