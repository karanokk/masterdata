import json
import logging
from os import path

from . import kazemai
from .json2sqlite3 import JSDatabase

logger = logging.getLogger('masterdata')


class MasterData:
    def __init__(self, ver_file: str):
        self.ver_file = ver_file

    def make(self, path: str):
        new_id = self.latest_master_js_id()
        old_id = self.read_id()
        logger.info(f'new id: [{new_id}]\n old id: [{old_id}]')
        if old_id == new_id:
            logger.info(f'Update to date, quit')
            return
            
        logger.info('Fetching masterdata...')
        master_json = kazemai.fetch_masterdata()
        logger.info('Making database...')
        database = JSDatabase(path)
        database.load_json(master_json)
        sql = "SELECT id FROM mstSvt WHERE (type=1 or type=2) and collectionNo>0;"
        servant_ids = [i[0] for i in database.execute(sql)]
        logger.info('Fetching comments...')
        comments = kazemai.fetch_svtcomment(servant_ids)
        mstSvtComment = {'mstSvtComment': comments}
        logger.info('Add comments...')
        database.load_json(mstSvtComment)
        self.write_id(new_id)
        logger.info(f'Write new id [{new_id}]')
        logger.info('Complete!')

    def latest_master_js_id(self) -> str:
        latest_id = kazemai.get_lastest_master_js_id()
        return latest_id

    def read_id(self) -> str:
        with open(self.ver_file) as f:
            ver = json.load(f)
        return ver["master_js_id"]

    def write_id(self, id: str):
        with open(self.ver_file, 'r+') as f:
            ver = json.load(f)
            f.seek(0)
            f.truncate()
            ver["master_js_id"] = id
            json.dump(ver, f)
