import logging
from typing import Union, List, Tuple
import asyncio
from .extractor import ServantExtractor
from . import api
logger = logging.getLogger('masterdata.mooncell')


def extract_servant_with_name(name: str):
    text = api.get_page(name)
    return ServantExtractor(text).extract()


def extract_all_servants():
    name_links = (servant.name_link  for servant in api.get_servants())

    async def get_servant_detail(name_link: str):
        text = await api.async_get_page(name_link)
        d = ServantExtractor(text).extract()
        return name_link, d

    loop = asyncio.get_event_loop()
    task_gen = [loop.create_task(get_servant_detail(name_link)) for name_link in name_links]
    res = loop.run_until_complete(asyncio.gather(*task_gen))
    return res
