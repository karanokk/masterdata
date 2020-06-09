import json
import logging
from os import path

from . import kazemai, mooncell
from .json2sqlite3 import JSDatabase
from .worker import ChaldeaWorker
from .manager import MasterDatabaseManager

logger = logging.getLogger('masterdata')


class MasterData:
    def __init__(self, ver_file: str):
        self.ver_file = ver_file

    def make_jp_database(self, path: str):
        new_id = kazemai.get_lastest_master_js_id()
        old_id = self.read_id()
        logger.info(f'new id: [{new_id}]\n old id: [{old_id}]')
        if old_id == new_id:
            logger.info(f'Update to date, quit')
            return
        kazemai.make_database(path)
        self.write_id(new_id)
        logger.info(f'Write new id [{new_id}]')
        logger.info('Complete!')

    @classmethod
    def translate_using_mooncell(self):
        db = JSDatabase('/Users/byunfi/Desktop/md.sqlite3')
        manager = MasterDatabaseManager(db.con)

        worker = ChaldeaWorker(manager)
        # worker.setup()
        # name_links = list(map(lambda x: x.name_link, mooncell.get_servants()))
        # servants = mooncell.get_all_servants(name_links)
        # for servant in servants:
        #     with open(f'./servants/No.{servant["collection_no"]}_{servant["name"]}', 'w+') as f:
        #         json.dump(servant, f)
        import os
        for file in os.listdir('./servants/'):
            if file.startswith('.DS'):
                continue
            p = f'./servants/{file}'
            with open(p) as f:
                servant = json.load(f)
                worker.load_servant(servant)
        
        db.commit()


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
