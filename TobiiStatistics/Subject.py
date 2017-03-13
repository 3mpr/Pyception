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

import logging
import getpass

class Subject(object):
    """
    TODO
    """
    logger = logging.getLogger("TobiiStatistics")

# ------------------------------------------------------------------------------------------- MAGIC
    def __init__(self, gaze_data, gaze_data_factory):
        self.log_scheme = {
            "class": self.__class__.__name__,
            "user": getpass.getuser()
        }

        self._gaze_data_factory = gaze_data_factory
        self._gaze_data = gaze_data
        self._name = os.path.basename(gaze_data.source()).split(".")[0]

        self._chunks = {}
        self._nb_chunks = 0
        self._raw = None

        self.logger.debug(
            "Initialized Subject %s.",
            self._name,
            extra=self.log_scheme
        )

    def __iter__(self):
        return iter(self._chunks)

# ----------------------------------------------------------------------------------------- METHODS
    def chunks(self):
        """
        Uses the Datasheet regex <seek()> method to find beginning/end
        triggers within the raw csv file.
        """

        begin_expr = re.compile(r"Debut{1} ([a-zA-Z\s]*) ([1-9]*)")
        end_expr = re.compile(r"Fin{1} ([a-zA-Z\s]*) ([1-9]*)")

        chunks = list()
        position = 0
        in_chunk = False

        self.logger.info(
            "   Scanning %s subject for data chunks...",
            self._name,
            extra=self.log_scheme
        )

        while True:

            # Retrieve the current chunk state
            if not in_chunk:
                self.logger.debug("Seeking chunk beginning trigger.", extra=self.log_scheme)
                position, chunk_state = self._gaze_data.seek(begin_expr, "Action", position)
            else:
                self.logger.debug("Seeking chunk end trigger.", extra=self.log_scheme)
                position, chunk_state = self._gaze_data.seek(end_expr, "Action", position)

            # Break the loop if the iteration is over
            if not position or not chunk_state:
                self.logger.debug("EOF Reached. Exiting chunk analysis...", extra=self.log_scheme)
                break

            # Handle the result
            if not in_chunk:
                self.logger.debug(
                    "Found chunk beginning at %d.",
                    position,
                    extra=self.log_scheme
                )
                chunk = {
                    "begin": position,
                    "name": chunk_state.group(1),
                    "nr": chunk_state.group(2)
                }
                chunks.append(chunk)

                self._nb_chunks = self._nb_chunks + 1
                in_chunk = True

            else:
                self.logger.debug(
                    "Found chunk end at %d.",
                    position,
                    extra=self.log_scheme
                )
                chunks[self._nb_chunks - 1]["end"] = position
                in_chunk = False

            position = position + 1

        self.logger.info(
            "   Found %d chunks.",
            len(chunks),
            extra=self.log_scheme
        )

        return chunks

    def divide(self):
        """
        Anayze attached GazeData object to find segregations and initialize
        the internal chunk table.
        """
        chunks = self.chunks()
        fieldnames = ["Timestamp", "GazePoint"]

        self.logger.info(
            "   Dividing %s raw file into chunks...",
            self._name,
            extra=self.log_scheme
        )

        for chunk in chunks:
            chunk_name = chunk["name"] + chunk["nr"]
            self.logger.debug(
                "Prepairing chunk %s from RAW (lines %d to %d).",
                chunk_name, int(chunk["begin"]), int(chunk["end"]),
                extra=self.log_scheme
            )

            chunk_table = self._gaze_data.copy(
                fieldnames,
                int(chunk["begin"]),
                int(chunk["end"])
            )

            chunk_datasheet = self._gaze_data_factory(None, chunk_table)
            self._chunks[chunk_name] = chunk_datasheet

            self.logger.debug("DONE.", extra=self.log_scheme)

        self.logger.info(
            "   DONE.",
            extra=self.log_scheme
        )

        raw_table = self._gaze_data.copy(fieldnames)
        self._raw = self._gaze_data_factory(None, raw_table)

    def analyze(self, area):
        """
        TODO
        """

        self.logger.info(
            "%s : Scanning chunks for area correlation. AREA : %s",
            self._name.upper(),
            str(area),
            extra=self.log_scheme
        )

        proof_rate_list = list()
        for chunk in self._chunks:
            self.logger.info(
                "   Analysing chunk %s...",
                chunk,
                extra=self.log_scheme
            )

            try:

                proof_length = self._chunks[chunk].time()
                watching_rate = self._chunks[chunk].watch(area)

                proof_element = {
                    "length": proof_length,
                    "watchingRate": watching_rate,
                    "name": chunk
                }

                proof_rate_list.append(proof_element)

                self.logger.info(
                    "   DONE.",
                    extra=self.log_scheme
                )

            except ValueError as error:

                self.logger.error(
                    "FAILED : Corrupted data chunk - Error : %s",
                    error.message,
                    extra=self.log_scheme
                )
                self._nb_chunks = self._nb_chunks -1

            except IndexError as error:

                self.logger.error(
                    self._name + ": Corrupted data chunk - Error : %s",
                    error.message,
                    extra=self.log_scheme
                )

                self._nb_chunks = self._nb_chunks -1

        return proof_rate_list

    def save(self, destination):
        """
        Saves every related datasheet to a directory named after this subject
        name within the given directory directory.
        That is to say len(self.chunk_table) + raw files will be saved.
        """
        subject_folder = os.path.join(destination, self._name)
        raw_destination = os.path.join(subject_folder, "raw.csv")
        self._raw.save(raw_destination)
        self.logger.debug(
            "Saved internal raw file at %s.",
            raw_destination,
            extra=self.log_scheme
        )
        if not os.path.exists(subject_folder):
            os.makedirs(subject_folder)
        for chunk_name in self._chunks:
            chunk_file = chunk_name + ".csv"
            chunk_destination = os.path.join(subject_folder, chunk_file)
            self._chunks[chunk_name].save(os.path.join(subject_folder, chunk_file))
            self.logger.debug(
                "Saved chunk file at %s.",
                chunk_destination,
                extra=self.log_scheme
            )

    def name(self, name=None):
        """
        name mutator.
        """
        if name is None:
            return self._name
        else:
            self._name = name
