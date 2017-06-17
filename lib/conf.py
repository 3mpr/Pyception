import os
import os.path

workdir = os.path.join(os.path.expanduser("~"), ".pyception")
analytics_dir = os.path.join(os.path.expanduser("~"), os.path.join("Documents", "pct_analytics"))
if not os.path.isdir(analytics_dir):
    os.makedirs(analytics_dir)
db_file = os.path.join(workdir, "data.db")
