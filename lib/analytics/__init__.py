from .IVT import IVT
from .Subject import *

from lib.conf import analytics_dir
import os

if not os.path.isdir(analytics_dir):
    os.makedirs(analytics_dir)
