"""
Created on Mon Jul  3 09:46:33 2023

@author: jtm545
"""

import os
import errno


def force_symlink(file, target):
    """Force overwrite if symlink target file already exists.
    
    Args:
        file (str): Full path to file that will be symlinked.
        target (str): Full path to new symlink.

    Returns:
        None
    """
    try:
        os.symlink(file, target)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(target)
            os.symlink(file, target)
    finally:
        print('{} --> {}'.format(file, target))
    return None