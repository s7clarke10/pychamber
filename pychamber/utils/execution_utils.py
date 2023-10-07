"""Utilities for pychamber."""

import logging as log
import subprocess

def c(command):
    log.debug("Command: {}".format(command))
    result = subprocess.run(command, shell=True, capture_output=True)
    if result.stderr:
        raise subprocess.CalledProcessError(
                returncode = result.returncode,
                cmd = result.args,
                stderr = result.stderr
                )
    if result.stdout:
        log.debug("Command Result: {}".format(result.stdout.decode('utf-8')))
    return result