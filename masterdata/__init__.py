from optparse import OptionParser

from . import masterdata
from .utils import read_master_js_id, write_new_master_js_id, AppSession


def main():
    parser = OptionParser()
    parser.add_option("-F", "--integrate_file_path", dest="integrate_path")
    parser.add_option("-f", "--file", dest="filepath", default='./masterdata.sqlite3')
    parser.add_option("--verpath", "--verpath", dest="verpath")

    options, _ = parser.parse_args()
    filepath = options.filepath
    verpath = options.verpath
    integrate_path = options.integrate_path

    old_id = read_master_js_id(verpath) if verpath else None
    new_id = masterdata.make_masterdata(filepath, old_id)
    if True:
        if integrate_path:
            masterdata.integrate_with_mooncell(filepath, integrate_path)
        if verpath:
            write_new_master_js_id(verpath)
