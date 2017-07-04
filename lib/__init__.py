import os

workdir = os.path.join(os.path.expanduser("~"), ".pyception")
analytics_dir = os.path.join(
    os.path.expanduser("~"),
    "Documents",
    "pct_analytics"
)

if not os.path.isdir(analytics_dir):
    os.makedirs(analytics_dir)


from .conf import db_file, logging_level
from .pattern import Singleton
from .Logger import Logger, Level, Color, Background, bold
from .persistence import path, Repository, ResourceCollection
from .utils import log, progress, inheritdoc
from .analytics import Point, Area, FixationDetector, IVT, Subject, Experiment
