import os
import time
import argparse

from lib import db_file, workdir, analytics_dir, log, bold, Repository, \
                ResourceCollection, Subject, Experiment


parser = argparse.ArgumentParser(
    description="Command line eye tracking utility."
)
parser.add_argument("action", help="action to perform")


def summary() -> None:
    print(bold("Working directory : ") + workdir)
    print(bold("Analytics directory : ") + analytics_dir)

    dbs = ResourceCollection(workdir, [".db"])
    print(bold("\n{0} database(s) found.".format(len(dbs))))

    for db in dbs.list():
        print("\n{0} ({1})".format(bold(os.path.basename(db)), db))
        repo = Repository(db)

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


def analyze(database: str = "") -> None:
    if not database:
        print("No database specified, falling back to {0}".format(
            bold(db_file)
        ))
        database = db_file

    repo = Repository(database)
    subjects = [Subject(subject["name"]) for subject in
                repo.read("subjects")]

    for subject in subjects:
        subject.analyze()
        subject.save()


args = parser.parse_args()
if args.action == "summary":
    summary()
elif args.action == "analyze":
    analyze()
elif args.action == "refresh":
    Experiment.refresh = True
    analyze()
