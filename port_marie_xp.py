#!/usr/bin/env python3

from lib import ResourceCollection, Repository
import re
import csv
import time
import datetime

csv_path = "/home/eka/Documents/EyeTracking/Marie/subjects/subjects"
csv_list = ResourceCollection(csv_path, ".csv")

opensesame_list = csv_list.find("^subject(a-zA-Z1-9-_)*")

# Creating subject file to tobii file links
observations = list()
for opensesame_file in opensesame_list:
    no_extension = opensesame_file.split(".")[0]
    id = no_extension.split("-")[1]
    tobii_file = csv_list.find("^tobii.*%s(?![0-9]).*" % re.escape(id))[0]

    observations.append({
        'id': id,
        'opensesame': opensesame_file,
        'tobii': tobii_file
    })

# Files opening & conversion to lists
raw_data = list()
for observation in observations:

    # OSEX IO
    osex_file = open(csv_list.get(observation['opensesame']), 'r')
    if osex_file.readline() != '\ufeffsep=,\n':
        osex_file.seek(0)
    osex_reader = csv.DictReader(osex_file, delimiter=",")
    osex_list = list(osex_reader)

    # TOBI IO
    tobii_file = open(csv_list.get(observation['tobii']), 'r')
    tobii_reader = csv.DictReader(tobii_file, delimiter=',')
    tobii_list = list(tobii_reader)

    tobii_list.pop(len(tobii_list) - 1)

    # Synchronizing time
    true_time_index = 0
    true_time = float(tobii_list[0]['TrueTime'])

    for i, tobii_record in enumerate(tobii_list):
        if tobii_record["TrueTime"]:
            true_time = float(tobii_record["TrueTime"])
            true_time_index = i
        delta = float(tobii_record['Timestamp']) - float(tobii_list[true_time_index]['Timestamp'])
        tobii_list[i]['RealTime'] = (true_time + delta) / 1000

    # Treatment is done, append to dataset
    subject = {
        'id': observation['id'],
        'tobii': tobii_list,
        'osex': osex_list
    }
    raw_data.append(subject)

    osex_file.close()
    tobii_file.close()

# When arriving here, osex and timestamp data are still unrelated
# Iterate over each subject
data = list()
for subject in raw_data:

    # Observation time is the same everywhere
    observations_time = time.mktime(datetime.datetime.strptime(
        subject["osex"][0]["datetime"],
        "%m/%d/%y %H:%M:%S"
    ).timetuple())

    # Iterate over each subject's triade
    for index, experiment in enumerate(subject['osex']):
        xp_end = observations_time + float(experiment["time_fixation_testing"]) / 1000

        xp_name = experiment["TargetObject"].split(".")[0]
        xp_name += "_" + experiment["Active1"].split(".")[0]
        xp_name += "_" + experiment["Active2"].split(".")[0]

        analyzed_experiment = {
            'name': subject['id'],
            'experiment': xp_name,
            'gaze': list(),
            'time': xp_end
        }

        # Enumerate over timestamps
        for gaze_index, record in enumerate(subject['tobii']):
            if record['RealTime'] <= xp_end:
                analyzed_experiment['gaze'].append(
                    subject['tobii'].pop(gaze_index)
                )

        data.append(analyzed_experiment)

repo = Repository("/home/eka/.local/share/pyception/marie_data.db")
repo.start_transaction()

for record in data:
    if record["name"] == "C1 (2)":
        record["name"] = "C1"
    id = repo.read({'name': record["name"]}, "subjects")[0]["id"]
    xp_id = repo.create({'subject': id, 'name': record["experiment"]}, "experiments")
    for gazepoint in record["gaze"]:
        repo.create({'experiment': xp_id, 'timestamp': gazepoint["RealTime"], 'x': gazepoint["X"], 'y': gazepoint["Y"]}, "data")

xps = repo.read("experiments")

for xp in xps:
    data = repo.read({"experiment": xp["id"]}, "data")
    if len(data) < 2:
        continue
    length = (data[-1]["timestamp"] - data[0]["timestamp"]) / 10  # /10 is temporary
    sample_rate = len(data) / length
    repo.update({'sample_rate': sample_rate, 'lasted': length}, {"id": xp["id"]}, "experiments", False)

repo.end_transaction()
