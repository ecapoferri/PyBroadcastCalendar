import configparser
import logging
import traceback
from os import chdir
from os import environ as os_environ
from pathlib import Path
from time import perf_counter

from dotenv import load_dotenv
from logging_setup import HDLR_STRM

PERF_START = perf_counter()
load_dotenv('./.env')
# load_dotenv('../.env')

CALLING_DIR = Path().cwd()
chdir(os_environ['APP_PATH'])

conf = configparser.ConfigParser()
conf.read('.conf')
# conf.read('../app.conf')
# conf.read('../conn.conf')

LOGGER = logging.getLogger(conf['DEFAULT']['LOGGER_NAME'])


def main():

    return


if __name__ == "__main__":
    try:
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.addHandler(HDLR_STRM)
        main()
    finally:
        HDLR_STRM.close()

chdir(CALLING_DIR)
