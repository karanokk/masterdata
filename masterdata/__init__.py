from optparse import OptionParser

from .MasterData import MasterData


def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filepath",
                      help="write database to FILE", metavar="FILE")
    parser.add_option("--verpath", "--verpath", dest="verpath",
                      help="read version from VFILE", metavar="VFILE")
    options, _ = parser.parse_args()
    filepath = options.filepath
    if filepath is None:
        filepath = './masterdata.sqlite3'
    masterdata = MasterData(options.verpath)
    masterdata.make(filepath)
