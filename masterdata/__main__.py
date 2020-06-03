import logging

import masterdata

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

if __name__ == '__main__':
    masterdata.main()
