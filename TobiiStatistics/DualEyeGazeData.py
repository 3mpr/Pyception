# -*- coding: utf-8 -*-

"""
Written the 10/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>
"""

import os
import os.path
import re

from Datasheet import Datasheet
from Point import Point
from GazeData import GazeData

class DualEyeGazeData(GazeData):
    """
    Datasheet for dual eye gaze point csv files.
    """
# ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, source, destination, scalex=1920, scaley=1080, delimiter=";"):
        super(DualEyeGazeData, self).__init__(
            source,
            ["Timestamp", "ActionContext", "Action", "LeftEye", "RightEye"]
        )
        self._destination = destination

        self.add("GazePoint")
        self._altered = True

        self._scale_x = scalex
        self._scale_y = scaley

        self._sequences = list()

        self._convert()

# ----------------------------------------------------------------------------------------- METHODS
    @staticmethod
    def create(source_file_path, scalex=1920, scaley=1080, delimiter=";"):
        return DualEyeGazeData(source_file_path, scalex, scaley, delimiter)

    def activity(self):
        """
        Performs a regular expression match on the given string.
        Returns 1 for a sub-scene beginning, -1 for a sub-scene end
        and 0 otherwise.
        """

        begin_expr = re.compile(r"Debut{1} ([a-zA-Z\s]*) ([1-9]*)")
        end_expr = re.compile(r"Fin{1} ([a-zA-Z\s]*) ([1-9]*)")

        def seek(begin, expression):
            """
            Seeks from <begin> the given expression in the internal csv list.
            """
            for index in range(begin, self._size - 1):
                analyzed = (self._csv[index]["Action"]
                            if self._csv[index]["Action"] is not None
                            else "")
                match = expression.match(analyzed)
                if match:
                    return index, match
            return False, False

        sequences = list()
        nb_sequences = 0
        position = 0
        in_sequence = False

        while True:

            # Retrieve the current sequence state
            if not in_sequence:
                position, sequence_state = seek(position, begin_expr)
            else:
                position, sequence_state = seek(position, end_expr)

            # Break the loop if the iteration is over
            if not position or not sequence_state:
                break

            # Handle the result
            if not in_sequence:
                sequence = {
                    "begin": position,
                    "name": sequence_state.group(1),
                    "nr": sequence_state.group(2)
                }
                sequences.append(sequence)

                nb_sequences = nb_sequences + 1
                in_sequence = True

            else:
                sequences[nb_sequences - 1]["end"] = position
                in_sequence = False

            position = position + 1

        return sequences

    def analyze(self):
        """
        TODO
        """
        subject_source_file = os.path.basename(self._source)
        subject = subject_source_file.split(".")[0]
        subject_destination_path = os.path.join(os.getcwd(), self._destination, subject)

        if not os.path.exists(subject_destination_path):
            os.makedirs(subject_destination_path)

        sequences = self.activity()
        fieldnames = ["Timestamp", "GazePoint"]
        for sequence in sequences:
            sequence_file = sequence["name"] + sequence["nr"] + ".csv"
            sequence_csv = self.copy(fieldnames, int(sequence["begin"]), int(sequence["end"]))
            sequence_datasheet = Datasheet(None, fieldnames, sequence_csv)
            sequence_datasheet.save(os.path.join(subject_destination_path, sequence_file))
        raw = self.copy(fieldnames)
        raw = Datasheet(None, fieldnames, raw)
        raw.save(os.path.join(subject_destination_path, "raw.csv"))

    def _convert(self):
        """
        TODO
        """
        for index in range(self._size):
            gaze_point = self._focal(self._csv[index]["LeftEye"], self._csv[index]["RightEye"])
            self._csv[index]['GazePoint'] = ("" if str(gaze_point) == "None" else str(gaze_point))

    def _focal(self, left_eye, right_eye):
        """
        Takes Eyes coordinates and returns a center point.
        """
        point_a = Point.create(left_eye)
        point_b = Point.create(right_eye)
        if point_a is not None and point_b is not None:
            return Point.center(point_a, point_b)
        return None

    def gaze_points(self):
        for record in self._csv:
            yield record['Timestamp'], record['GazePoint']

    def begin(self):
        return self._csv[-1]["Timestamp"]

    def end(self):
        return self._csv[1]["Timestamp"]

    def raw(self):
        return self._csv
