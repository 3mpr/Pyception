#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>

Updated the 13/03/2017
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
    def __init__(self, dual=True):
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

# ----------------------------------------------------------------------------------------- METHODS
    def folks(self, subject_dir):
        """
        Initializes the interpret's behaviour to read from a csv folder
        and read and evaluate each cssv data file into Subject files.
        """
        self.logger.info("Preparing Interpret for raw data scan.", extra=self.log_scheme)

        subject_list = os.listdir(subject_dir)
        subjects = list()

        self.logger.info(
            "Found %d elements in %s.",
            len(subject_list),
            subject_dir,
            extra=self.log_scheme
        )

        scan_start_time = time.time()

        for subject in subject_list:
            self.logger.info("Scanning %s...", subject, extra=self.log_scheme)
            subjects.append(Subject(
                self._data_format(os.path.join(subject_dir, subject)),
                FinalGazeData.create
            ))

        scan_end_time = time.time()

        self.logger.info(
            "DONE. Scan performed in %f seconds",
            scan_end_time - scan_start_time,
            extra=self.log_scheme
        )

        return subjects

    def probe(self, subjects, save=False, save_path=None):
        """
        Probes attached subjects. The probe analyses the subject files, looking for possible
        chunks as defined in Subject.chunks().
        """
        time_start = time.time()

        self.logger.info(
            "Preparing Intepret for intermediate data probing.",
            extra=self.log_scheme
        )

        save_path = os.path.join(os.getcwd(), "Analytics") if save_path is None else save_path
        for subject in subjects:
            subject.divide()
            if save:
                subject.save(save_path)

        time_end = time.time()

        self.logger.info(
            "DONE. Probe performed in %f seconds.",
            time_end - time_start,
            extra=self.log_scheme
        )

    def analyze(self, subject, area):
        """
        TODO
        """
        self.logger.debug(
            "Analysing %s chunks...",
            subject.name(),
            extra=self.log_scheme
        )

        stat = {
            "subject": subject.name(),
            "data": subject.analyze(area)
        }

        return stat

    def inspect(self, subject, areas):
        """
        Shorthand for analyze() on multiple areas.
        """
        area_data = list()
        for area in areas:
            data = self.analyze(subject, area)
            data = {
                "area": str(area),
                "stats": data
            }
            area_data.append(data)

        return area_data

    def investigate(self, subjects, areas, save_path=None):
        """
        Does the same as inspect() but dumps the result to a json file
        for each subject.
        """
        save_path = os.path.join(os.getcwd(), "Analytics") if save_path is None else save_path

        self.logger.info(
            "Preparing Interpret for data to area correlation.",
            extra=self.log_scheme
        )

        time_start = time.time()

        for subject in subjects:
            correlation_file_path = os.path.join(
                os.getcwd(),
                save_path,
                subject.name(),
                "correlation.json"
            )

            audit = self.inspect(subject, areas)
            json_file = json.dumps(audit, sort_keys=True, indent=4, separators=(',', ': '))

            with open(correlation_file_path, "w") as fout:
                fout.write(json_file)

        time_end = time.time()

        self.logger.info(
            "DONE. Subject data to area correlation performed in %f seconds.",
            time_end - time_start,
            extra=self.log_scheme
        )


if __name__ == "__main__":
    AREAS = list()
    AREA = Area(Point(0, 0), Point(768, 1080))
    AREAS.append(AREA)
    AREA = Area(Point(1152, 0), Point(1920, 1080))
    AREAS.append(AREA)

    ITR = Interpret(dual=True)

    FOLKS = ITR.folks("RawData")
    ITR.probe(FOLKS, True)
    ITR.investigate(FOLKS, AREAS)
