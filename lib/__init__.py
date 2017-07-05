from os import makedirs
from os.path import join, dirname, isdir
from .Config import Config

SETTINGS = Config.read(join(dirname(dirname(__file__)), "settings.py"))

if not isdir(SETTINGS['workdir']):
    makedirs(SETTINGS['workdir'])
if not isdir(SETTINGS['analytics_dir']):
    makedirs(SETTINGS['analytics_dir'])

from .pattern import Singleton
from .Logger import Logger, Level, Color, Background, bold

logger = Logger(SETTINGS["logging_level"])
log = logger.log

from .persistence import path, Repository, ResourceCollection
from .utils import inheritdoc
from .analytics import Point, Area, FixationDetector, IVT, Subject, Experiment


def reload() -> None:
    global logger
    global log
    logger = Logger(SETTINGS["logging_level"])
    log = logger.log
