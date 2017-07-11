import os
from os.path import join
from lib.Logger import Level

## ------------------------------------------------------------------------- ##
# ------------------------- MAIN CONFIGURATION FILE ------------------------- #
## ------------------------------------------------------------------------- ##

# Pyception working directory, specifies the destination for things such as
# databases and logs
if os.name == 'nt':
    workdir = join(os.getenv("APPDATA"), "Pyception")
    logdir = join(workdir, "log")
else:
    workdir = join(os.path.expanduser("~"), ".local", "share", "pyception")
    logdir = join(os.path.expanduser("~"), ".local", "log", "pyception")
# Analysis directory, specifies where to store the output (png, xlxs, csv) of
# analysis
analytics_dir = os.path.join(
    os.path.expanduser("~"),
    "Documents",
    "Pyception"
)
# Default database when none is provided
db_file = os.path.join(workdir, "data.db")  # Might change
# stdout logging level, default to Level.INFORMATION
# Can be set to :
#   EXCEPTION
#   ERROR
#   WARNING
#   INFORMATION
#   DEBUG
#   TRACE
logging_level = Level.INFORMATION
