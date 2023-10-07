"""Utilities for pychamber."""

import logging
import subprocess

def run_command(command, env):
    """ Runs requested process with arguments.
        Enable debug logging and raise errors.
    """
    logging.debug("Command: {}".format(command))
    result = subprocess.run(command, env=env, shell=False, capture_output=False)

    return result.returncode