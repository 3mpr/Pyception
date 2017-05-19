# -*- coding: utf-8 -*-

"""
| Part of the **Perception** package.
|
| **created**: 02.04.2017
| **author**: Florian Indot <florian.indot@gmail.com>
| **last updated**: 08.04.2017
"""

import os
import sys
import argparse
import Perception
from Perception.Interaction.Watcher import Watcher

PARSER = argparse.ArgumentParser()
WATCHER = None

PARSER.add_argument("-x", "--graphic",                  help="start Pyception with the experimental graphic interface, "
                                                             + "this option discards other arguments.")
PARSER.add_argument("-s", "--source",                   help="the source directory/file to analyse.")
PARSER.add_argument("-d", "--destination",              help="the analysis destination folder.")
PARSER.add_argument("-S", "--server",                   help="start Pyception in background, server mode.")
PARSER.add_argument("-a", "--aoi_file", default=".aoi", help="Area of Interest file path, relative the source "
                                                             + "directory.")

ARGS = vars(PARSER.parse_args())

if all(cell is None for cell in ARGS):
    PARSER.print_help(sys.stderr)
    sys.exit(0)

if ARGS["graphic"] is not None:
    APP = Perception.App()
    sys.exit(APP.run())

if ARGS["source"] is not None:
    if ARGS["destination"] is None:
        print("Destination not provided.\nUsage : ´pyception --source SOURCE --destination DESTINATION´",
              file=sys.stderr)
        sys.exit(-1)
    ARGS["aoi_file"] = os.path.join(os.getcwd(), ARGS["source"], ARGS["aoi_file"])
    WATCHER = Watcher(ARGS["source"], ARGS["destination"], ARGS["aoi_file"])
    WATCHER.watch()
