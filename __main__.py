import os
import PyCeption.conf as conf

def bootstrap():
    """
    Bootstrap app components.
    """
    if not os.path.isdir(conf.workdir):
        os.makedirs(conf.workdir)
    r = Repository(conf.db_file)
    del r
