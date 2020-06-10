import logging

from . import kazemai, mooncell

logger = logging.getLogger('masterdata')


def make_masterdata(path: str, old_id: str = None):
    new_id = kazemai.lastest_master_js_id()
    if old_id == new_id:
        logger.info('Up to date, quit.')
        return
    _ = kazemai.make_database(path)
    logger.info('database updated.')
    return new_id


def integrate_with_mooncell(database_path: str, dest_path: str = None):
    if dest_path and dest_path != database_path:
        from shutil import copyfile
        copyfile(database_path, dest_path)
    else:
        dest_path = database_path
    mooncell.integrate_into_db(dest_path)
