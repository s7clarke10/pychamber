"""Utilities for pychamber."""

import logging
import subprocess

def c(command, env):
    """ Runs requested process with arguments.
        Enable debug logging and raise errors.
    """
    logging.debug("Command: {}".format(command))
    result = subprocess.run(command, env, shell=False, capture_output=True)
    if result.stderr:
        raise subprocess.CalledProcessError(
                returncode = result.returncode,
                cmd = result.args,
                stderr = result.stderr
                )
    if result.stdout:
        logging.debug("Command Result: {}".format(result.stdout.decode('utf-8')))
    return result