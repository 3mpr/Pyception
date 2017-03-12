# -*- coding: utf-8 -*-

"""
Written the 12/03/2017 as a part of the TobiiStatistics package
by Florian Indot <florian.indot@gmail.com>
"""

import os
import os.path
import re

from Datasheet import Datasheet
from GazeData import GazeData

class Subject(object):
    """
    TODO
    """
# ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, gaze_data):
        self._gaze_data = gaze_data
        self._name = os.path.basename(gaze_data.source()).split(".")[0]
        self._chunks = {}
        self._raw = list()

    def chunks(self):
        """
        TODO
        """

        begin_expr = re.compile(r"Debut{1} ([a-zA-Z\s]*) ([1-9]*)")
        end_expr = re.compile(r"Fin{1} ([a-zA-Z\s]*) ([1-9]*)")

        chunks = list()
        nb_chunks = 0
        position = 0
        in_chunk = False

        while True:

            # Retrieve the current chunk state
            if not in_chunk:
                position, chunk_state = self._gaze_data.seek(begin_expr, "Action", position)
            else:
                position, chunk_state = self._gaze_data.seek(end_expr, "Action", position)

            # Break the loop if the iteration is over
            if not position or not chunk_state:
                break

            # Handle the result
            if not in_chunk:
                chunk = {
                    "begin": position,
                    "name": chunk_state.group(1),
                    "nr": chunk_state.group(2)
                }
                chunks.append(chunk)

                nb_chunks = nb_chunks + 1
                in_chunk = True

            else:
                chunks[nb_chunks - 1]["end"] = position
                in_chunk = False

            position = position + 1

        return chunks

    def analyze(self):
        """
        TODO
        """
        chunks = self.chunks()
        fieldnames = ["Timestamp", "GazePoint"]

        for chunk in chunks:
            chunk_name = chunk["name"] + chunk["nr"]
            chunk_table = self._gaze_data.copy(
                fieldnames,
                int(chunk["begin"]),
                int(chunk["end"])
            )

            chunk_datasheet = Datasheet(None, fieldnames, chunk_table)
            self._chunks[chunk_name] = chunk_datasheet

        raw_table = self._gaze_data.copy(fieldnames)
        self._raw = Datasheet(None, fieldnames, raw_table)

# ----------------------------------------------------------------------------------------- METHODS
    def save(self, destination):
        """
        TODO
        """
        subject_folder = os.path.join(destination, self._name)
        self._raw.save(os.path.join(subject_folder, "raw.csv"))

        if not os.path.exists(subject_folder):
            os.makedirs(subject_folder)
        for chunk_name in self._chunks:
            chunk_file = chunk_name + ".csv"
            self._chunks[chunk_name].save(os.path.join(subject_folder, chunk_file))
