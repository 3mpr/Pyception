#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>

Updated the 12/03/2017
"""

import os
import os.path
from os.path import join
import time
import logging
import json

from Datasheet import Datasheet
from DualEyeGazeData import DualEyeGazeData
from DirectGazeData import DirectGazeData
from FinalGazeData import FinalGazeData
from Subject import Subject
from Point import Point
from Area import Area

class Interpret(object):
    """
    Package entrypoint, encapsulates most of the other classes methods
    within simple method facilities.
    """
    logger = logging.getLogger("TobiiStatistics")
# ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, dual=True, subject_dir=None, save_path=None):
        self.log_scheme = {"class": self.__class__.__name__}
        log_format = "%(asctime)-10s TobiiStatistics : %(message)s"
        logging.basicConfig(format=log_format)
        self.logger.setLevel(20)

        self._data_format = (DualEyeGazeData.create if dual else DirectGazeData.create)
        self.logger.info(
            "Initializing Interpret with %s behaviour.",
            ("dual" if dual else "single"),
            extra=self.log_scheme
        )

        if subject_dir is not None:
            self.bootstrap_raw_data(subject_dir)
        else:
            self._subject_dir = None

        if save_path is not None:
            self._save_path = save_path
        else:
            self._save_path = None

# ----------------------------------------------------------------------------------------- METHODS
    def bootstrap_raw_data(self, subject_dir):
        """
        Initializes the interpret's behaviour to read from a csv folder
        and read and evaluate each cssv data file into Subject files.
        """
        self.logger.info("Preparing Interpret for raw data scan.", extra=self.log_scheme)

        self._subject_dir = subject_dir
        self._subject_list = os.listdir(subject_dir)
        self._subjects = list()

        self.logger.info(
            "Found %d elements in %s.",
            len(self._subject_list),
            subject_dir,
            extra=self.log_scheme
        )

        scan_start_time = time.time()
        for subject in self._subject_list:
            self.logger.info("Scanning %s...", subject, extra=self.log_scheme)
            self._subjects.append(Subject(
                self._data_format(os.path.join(self._subject_dir, subject)),
                FinalGazeData.create
            ))
        scan_end_time = time.time()
        time_taken = scan_end_time - scan_start_time
        self.logger.info(
            "Done. Scan performed in %f seconds",
            time_taken,
            extra=self.log_scheme
        )

    def probe(self, subject_dir=None, save=False, save_path=None):
        """
        Probes attached subjects. The probe analyses the subject files, looking for possible
        chunks as defined in Subject.chunks().
        """
        time_start = time.time()

        if self._subject_dir is None and subject_dir is None:

            raise EnvironmentError("Subject directory needs to be defined"
                                   + "as a probe parameter or before probe call.")
            # TODO REPLACE EnvironmentError w/ another error

        elif self._subject_dir is not None and subject_dir is not None:

            self.logger.info("Subject directory already provided.")

        elif subject_dir is not None and self._subject_dir is None:

            self.bootstrap_raw_data(subject_dir)

        save_path = os.path.join(os.getcwd(), "Analytics") if save_path is None else save_path
        for subject in self._subjects:
            self.logger.debug(
                "Dividing %s raw file into chunks...",
                subject.name(),
                extra=self.log_scheme
            )

            subject.divide()
            if save:
                subject.save(save_path)

        time_end = time.time()

        self.logger.info(
            "Probe finished. Took %f seconds.",
            time_end - time_start,
            extra=self.log_scheme
        )

    def analyze(self, area):
        """
        TODO
        """
        stats = list()
        for subject in self._subjects:

            self.logger.debug(
                "Analysing %s chunks...",
                subject.name(),
                extra=self.log_scheme
            )

            stat = {
                "subject": subject._name,
                "data": subject.analyze(area)
            }

            stats.append(stat)

        return stats

    def inspect(self, areas):
        """
        Shorthand for analyze() on multiple areas.
        """
        audit = list()
        for area in areas:
            data = self.analyze(area)
            data = {
                "area":str(area),
                "stats": data
            }
            audit.append(data)
        return audit

    def investigate(self, areas, save_path=None):
        """
        Does the same as inspect() but dumps the result to a javascript file
        for each subject.
        """
        save_path = os.path.join(os.getcwd(), "Analytics") if save_path is None else save_path
        audit = self.inspect(areas)
        json_file = json.dumps(audit, sort_keys=True, indent=4, separators=(',', ': '))
        with open("log.json", "w") as fout:
            fout.write(json_file)


if __name__ == "__main__":
    ITR = Interpret()

    ITR.probe("RawData", True)

    AREAS = list()
    # AREA = Area(Point(0, 0), Point(1920, 1080))
    # AREAS.append(AREA)
    AREA = Area(Point(0, 0), Point(768, 1080))
    AREAS.append(AREA)
    AREA = Area(Point(1152, 0), Point(1920, 1080))
    AREAS.append(AREA)
    print ITR.investigate(AREAS)
