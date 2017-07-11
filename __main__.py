import os
import sys
import argparse
import lib
from lib import SETTINGS, bold, Repository, ResourceCollection, Subject, \
                Experiment, Level, log

# Parser creation

parser = argparse.ArgumentParser(
    description="Command line eye tracking utility."
)

parser.add_argument("-a", "--analyze",      help="performs database analysis",                                                      action="store_true")
parser.add_argument("-v", "--verbose",      help="increases output verbosity",                                                      action="store_true")
parser.add_argument("-r", "--refresh",      help="deletes old results and performs full analysis, use when source data changed",    action="store_true")
parser.add_argument("-d", "--delete",       help="deletes specified database, content is lost forever")
parser.add_argument("-s", "--source",       help="specifies the source database file, the path is relative pyception working directory")
parser.add_argument("-o", "--destination",  help="specifies analytics output files destination path")
parser.add_argument("-i", "--info",         help="displays general information",                                                    action="store_true")

args = parser.parse_args()

# Parser parsing

if args.verbose:
    lib.SETTINGS["logging_level"] = Level.DEBUG
    lib.reload()

if args.destination:
    lib.SETTINGS["analytics_dir"] = args.destination

if args.source:
    lib.SETTINGS["db_file"] = os.path.join(SETTINGS["workdir"], args.source)
    if not os.path.isfile(lib.SETTINGS["db_file"]):
        Repository(lib.SETTINGS["db_file"]).initialize()

if args.refresh:
    Experiment.refresh = True

if args.info:
    print(bold("Working directory : ") + lib.SETTINGS["workdir"])
    print(bold("Analytics directory : ") + lib.SETTINGS["analytics_dir"])

    dbs = ResourceCollection(lib.SETTINGS["workdir"], [".db"])
    print(bold("\n{0} database(s) found.".format(len(dbs))))

    for db in dbs.list():
        print("\n{0} ({1})".format(bold(os.path.basename(db)), db))
        repo = Repository(db)
        Subject.repository = repo
        Experiment.repository = repo

        print("  Nb subjects: {0}".format(repo.count("subjects")))
        print("  Nb experiments : {0}".format(repo.count("experiments")))

        subjects = [Subject(subject["name"]) for subject in
                    repo.read("subjects")]
        analysis_completion = 0
        for subject in subjects:
            analysis_completion += 1 if subject.saved_analysis else 0
        print("  Analysis completion : {0}/{1}".format(
            analysis_completion,
            len(subjects)
        ))
    sys.exit(0)

if args.delete:
    decision = ""

    database_path = os.path.join(lib.SETTINGS["workdir"], args.delete)
    if not os.path.isfile(database_path):
        log("Specified database does not exist.", Level.ERROR)
    else:
        while decision != "y" and decision != "n":
            decision = input("This action is definitive, are you sure you " +
                             "want to delete %s ? (y/n) " % args.delete)
        if decision == "n":
            log("Deletion cancelled.")
            sys.exit(0)
        log("Deleting database %s..." % args.delete, Level.INFORMATION, "")
        os.remove(database_path)
        log(" Done", Level.DONE)
    sys.exit(0)

if args.analyze:
    repo = Repository(lib.SETTINGS["db_file"])
    Subject.repository = repo
    Experiment.repository = repo
    subjects = [Subject(subject["name"]) for subject in repo.read("subjects")]

    for subject in subjects:
        subject.analyze()
        subject.save()
    sys.exit(0)

parser.print_help()
