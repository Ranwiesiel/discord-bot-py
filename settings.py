import pathlib
from logging.config import dictConfig
import logging

import tracemalloc
tracemalloc.start()

BASE_DIR = pathlib.Path(__file__).parent  #path root atau parent

CMDS_DIR = BASE_DIR / "cmds"  #membaut path yang dituju
COGS_DIR = BASE_DIR / "cogs"

# GUILDS_ID = discord.Object(id=int(os.environ['GUILD']))

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format":
            "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {
            "format": "%(levelname)-10s - %(name)-15s : %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/infos.log",
            "mode": "w",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "bot": {
            "handlers": ['file','console'],
            "level": "INFO",
            "propagate": False
        },
        "discord": {
            "handlers": ["file", 'console2'],
            "level": "INFO",
            "propagate": False
        },
    },
}

dictConfig(LOGGING_CONFIG)
