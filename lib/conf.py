import os
import os.path
from lib.Logger import Level
from lib import workdir

db_file = os.path.join(workdir, "data.db")  # Might change
logging_level = Level.INFORMATION
