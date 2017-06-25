import os
import os.path
import importlib

# Path & directories
workdir = os.path.join(os.path.expanduser("~"), ".pyception")
analytics_dir = os.path.join(
    os.path.expanduser("~"),
    "Documents",
    "pct_analytics"
)
db_file = os.path.join(workdir, "data.db")  # Might change