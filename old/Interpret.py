#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>

Updated the 13/03/2017
"""

import os
import os.path
import csv
import time
import logging
import json
import sys
import re

from Area import Area
from Point import Point
from DirectGazeData import DirectGazeData
from DualEyeGazeData import DualEyeGazeData
from FinalGazeData import FinalGazeData
from Subject import Subject


class Interpret(object):
    """
    Package entrypoint, encapsulates most of the other classes methods
    within simple method facilities.
    """
    logger = logging.getLogger("TobiiStatistics")

    # ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, dual=True):
        # type: (dual) -> bool
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
        # type: (subject_dir) -> string
        """
        Analyzes the given directory and returns a list of <Subject>.
        :type subject_dir: string
        :returns list<Subject>
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

        self.logger.info(
            "DONE. Scan performed in %f seconds",
            time.time() - scan_start_time,
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

    def load(self, directory, gaze_data_factory):
        """
        TODO
        """
        subject_list = os.listdir(directory)
        # Clean potential non-subject files/folders
        for subject_folder in subject_list:
            if len(re.search(r"(.*)", subject_folder).groups()) > 0:
                subject_list.remove(subject_folder)
        subjects = list()
        for subject_folder in subject_list:
            subject_path = os.path.join(directory, subject_folder)
            subject_files = os.listdir(subject_path)
            if "raw.csv" in subject_files:
                with open(os.path.join(subject_path, "raw.csv"), "r") as fin:
                    reader = csv.DictReader(fin, delimiter=";")
                    subject_raw = gaze_data_factory(None, list(reader))
                    subject_files.remove("raw.csv")
            chunks = list()
            for chunk_file in subject_files:
                with open(os.path.join(subject_path, chunk_file), "r") as fin:
                    reader = csv.DictReader(fin, delimiter=";")
                    chunk_data = gaze_data_factory(None, list(reader))
                    chunks.append(chunk_data)
            subject = Subject(subject_raw, gaze_data_factory, chunks)
            subjects.append(subject)
        return subjects

    def cover(self, raw_dir, analytic_dir, areas):
        if os.path.exists(analytic_dir):
            answer = ""
            while answer.lower() != "y" and answer != "n":
                print "Directory %s existed before analysis, attempt to load content ?(y/n)"
                answer = sys.stdin.read()

            if answer == "y":
                subjects = self.load("Analytics", self._data_format)

    def gaze_factory(self, gaze_factory=None):
        if gaze_factory is None:
            return self._data_format
        else:
            self._data_format = gaze_factory


if __name__ == "__main__":
    AREAS = list()
    AREA = Area(Point(0, 0), Point(768, 1080))
    AREAS.append(AREA)
    AREA = Area(Point(1152, 0), Point(1920, 1080))
    AREAS.append(AREA)

    ITR = Interpret(dual=True)

    FOLKS = ITR.load("Analytics", ITR.gaze_factory())
    ITR.investigate(FOLKS, AREAS)
