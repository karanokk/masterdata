import asyncio
import logging
from functools import reduce
from typing import List, Sequence

from ..json2sqlite3 import JSDatabase
from . import api

logger = logging.getLogger('masterdata.kazemai')


def make_database(path: str = ':memory:') -> JSDatabase:
    logger.debug('Fetching masterdata...')
    master_json = api.get_masterdata()

    logger.debug('Making database...')
    database = JSDatabase(path)
    database.load_json(master_json)
    sql = "SELECT id FROM mstSvt WHERE (type=1 or type=2) and collectionNo>0;"
    servant_ids = [i[0] for i in database.execute(sql)]

    logger.debug('Fetching comments...')
    comments = _get_all_svtcomment(servant_ids)
    mstSvtComment = {'mstSvtComment': comments}

    logger.debug('Add comments...')
    database.load_json(mstSvtComment)


def _get_all_svtcomment(svtIds: Sequence[int]) -> List[dict]:
    loop = asyncio.get_event_loop()

    async def main():
        tasks = (loop.create_task(api.async_get_svtcomment(svtId))
                 for svtId in svtIds)
        return await asyncio.gather(*tasks)

    res = loop.run_until_complete(main())
    comments = reduce(lambda x, y: x + y, res)
    return comments
