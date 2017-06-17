import os
import lib.conf as conf
import lib as pct

def bootstrap():
    """
    Bootstrap app components.
    """
    if not os.path.isdir(conf.workdir):
        os.makedirs(conf.workdir)
    return pct.Repository(conf.db_file)

repo = bootstrap()
