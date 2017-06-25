from .pattern import Singleton, Visited, VisitorInterface
from .Logger import Logger, Level, Color, Background
from .persistence import path, Repository, ResourceCollection
from .utils import log, progress, inheritdoc
from .conf import analytics_dir, db_file, workdir
from .analytics import Point, Area, FixationDetector, IVT, Subject, Experiment

import os
if not os.path.isdir(analytics_dir):
    os.makedirs(analytics_dir)
