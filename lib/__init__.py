from os import makedirs
from os.path import join, dirname, isdir
from .Config import Config

SETTINGS = Config.read(join(dirname(dirname(__file__)), "settings.py"))

if not isdir(SETTINGS['workdir']):
    makedirs(SETTINGS['workdir'])
if not isdir(SETTINGS['logdir']):
    makedirs(SETTINGS['logdir'])
if not isdir(SETTINGS['analytics_dir']):
    makedirs(SETTINGS['analytics_dir'])

from .pattern import Singleton
from .Logger import Logger, Level, Color, Background, bold

logger = Logger(SETTINGS["logging_level"])
log = logger.log

from .model import path, Repository, ResourceCollection
from .utils import inheritdoc
from .analytics import Point, Area, FixationDetector, IVT, Subject, Experiment


def reload() -> None:
    global logger
    global log
    logger = Logger(SETTINGS["logging_level"])
    log = logger.log

def hard_reload() -> None:
    global SETTINGS
    global logger
    global log
    SETTINGS = Config.read(join(dirname(dirname(__file__)), "settings.py"))
    logger = Logger(SETTINGS["logging_level"])
    log = logger.log
