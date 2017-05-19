import os
from Perception.Data import *
from Perception.Data.Operators import *
from Perception.Interaction.Drawer import Drawer
from yaml import load, dump
import re


class Watcher(object):
    """
    Main non-interactive logic execution class.
    Analyze a given input directory and produces a set of results to the specified output directory.

    :see:
    """

    Transactions = list()
    AreasOfInterest = []

    ChunkOp = None
    TimeOp  = None
    GazeOp  = None
    IVTOp   = None
    AOIOp   = None

    IVTThreshold = 200

    def __init__(self, source_dir: str, dest_dir: str, aoi_spec_file: str) -> None:
        """
        Class constructor.

        :param source_dir: string The directory to be analyzed
        :param dest_dir: string The directory where analyzed data will be stored
        :param aoi_spec_file: The Area Of Interest specification file ( .aoi -> YAML )
        """
        # Guard - directories existence
        assert os.path.isdir(source_dir), "Source directory {0} doest not exist.".format(source_dir)
        assert os.path.isdir(dest_dir), "Destination directory {0} does not exist.".format(dest_dir)

        # Open AOI specs
        with open(aoi_spec_file, "r") as fin:
            data = load(fin)
        self.AreasOfInterest = self.parse_areas(data)

        # Guard - absolute path
        if not source_dir.startswith('/'): # TODO multi-platform compatibility
            source_dir = os.path.join(os.getcwd(), source_dir)

        # Assignment
        self.source_directory = source_dir
        self.destination_directory = dest_dir
        self.sources = ResourceCollection(source_dir, ".csv")
        self.destinations = self.translate_source(self.sources.list())

        # Transaction list creation
        self.ChunkOp = ChunkOperator()
        self.TimeOp = TimeOperator()
        self.GazeOp = GazeOperator(Area(Point(0, 0), Point(1920, 1080)))
        self.IVTOp = IVTOperator(self.IVTThreshold)

        for source_file in self.sources.list():
            self.Transactions.extend(self.extract(source_file))

        #for transaction_def in self.Transactions:


    @staticmethod
    def parse_areas(data: dict) -> list:
        """
        Iterates over the data dictionary definition as taken from a ´yaml.parse´ call.
        Each iteration creates a corresponding AOI and assign it as well as its target to
        the internal ´AreasOfInterest´ attribute.

        :param data: dict The dictionary as parsed from a ´yaml.parse´ call.
        """
        aois = list()

        for aoi_definition in data["AOIS"]:
            aoi = Area(
                Point(aoi_definition["top_left"]["x"], aoi_definition["top_left"]["y"]),
                Point(aoi_definition["bottom_right"]["x"], aoi_definition["bottom_right"]["y"])
            )

            aois.append({
                "concerns": aoi_definition["concerns"],
                "area": aoi
            })

        return aois

    def translate_source(self, sources: list) -> list:
        """
        Converts a source file path list to a destination file path list.

        :return: list The destination counterparts of the given source paths.
        """
        destinations = list()

        for source in sources:
            din = os.path.join(self.destination_directory, source.lstrip(self.source_directory))
            din.strip(os.path.sep)

            din = din.split(os.path.sep)
            din.pop(0)
            din.pop()

            dout = ""
            for cell in din:
                dout += os.path.sep + cell
            destinations.append(dout)

        return destinations

    def extract(self, fin):
        """
        Retrieves a transaction and relative transaction information from the given file path.

        :param fin: str The file path
        :return: dict
        """
        transactions = list()
        trs = Transaction.open(fin)

        if self.ChunkOp.involve(trs):

            self.ChunkOp.visit(trs)
            for chunk in self.ChunkOp.chunks:
                transactions.append({
                    'name': os.path.basename(fin.split('.')[0]) + ":" + chunk,
                    'transaction': self.ChunkOp.chunks[chunk]
                })

        else:

            transactions.append({
                'name': os.path.basename(fin.split('.')[0]),
                'transaction': trs
            })

        return transactions

    def watch(self):
        din = self.sources.list()
        dout = self.destinations

        for i in range(len(din)):
            trs = Transaction.open(din[i])

            subject_aois = list()
            filename = os.path.basename(din[i]).split(".")[0]

            print("PROCESSING {0}...".format(filename))
            for aoi in self.AreasOfInterest:
                regex = re.search(aoi["concerns"], filename)
                if aoi["concerns"] == "all":
                    subject_aois.append(aoi["area"])
                elif regex is not None and regex.group() != "":
                    subject_aois.append(aoi["area"])

            if not os.path.exists(dout[i]): os.makedirs(dout[i])

            try:
                drawer = Drawer(trs, dout[i], subject_aois)
                drawer.draw(os.path.basename(din[i]).split(".")[0])
            except Exception as e:
                print("Error while drawing {0}.".format(filename))
                raise e