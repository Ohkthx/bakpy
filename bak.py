#!/usr/bin/env python3

"""Backup / Archiving Tool

This program allows a user to either create or use a configuration
file for easy-to-understand archiving of file and directories. The
configuration file is in JSON format with an example below:

    {
        "root": "/home/username",
        "files": [
            "pictures",
            "videos/funny_vid.mp4",
        ],
    }

This example uses "/home/username" as the root directory and will
preserve the directory "pictures" (and contents) and specifically
the file "funny_vid.mp4" in the "videos" directory. Lastly, it
will compress the archive to preserve space.

usage: bak.py [-h] (--use | --create) [-s] config
"""

import argparse
import json
import sys
from pathlib import Path

SILENT_OUTPUT = False


class ConfigError(OSError):
    """Creating and loading configuration file errors."""
    pass


def main():
    # Parse the arguments passed.
    args = get_args()
    global SILENT_OUTPUT
    SILENT_OUTPUT = args.silent
    config_name = args.config

    # Attempt to create or load the supplied configuration file name.
    try:
        if args.use:
            load_config(config_name)
        else:
            create_config(config_name)
            nprint(f"Created '{config_name}'.")
            sys.exit(0)
    except ConfigError as config_err:
        nprint(config_err)
        sys.exit(-1)
    except Exception as exc:
        nprint(f"Unknown error occurred while loading"
               f" or creating configuration a file: {exc}")
        sys.exit(-1)


def get_args():
    """Process the arguments passed to the application."""
    parser = argparse.ArgumentParser(
        description="Archives a list of files and compresses them.")

    # Require either a '--use' or a '--create' command, stored as a group.
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--use",
                        dest="use",
                        action="store_true",
                        help="use a configuration file")
    group.add_argument("--create",
                        dest="create",
                        action="store_true",
                        help="create an example configuration file")

    # Configuration file to either create or use.
    parser.add_argument("config",
                        metavar="config",
                        type=str,
                        help="configuration file containing items to archive")

    # Enable / Disable console output.
    parser.add_argument("-s",
                        "--silent",
                        dest="silent",
                        action="store_true",
                        help="disables output")
    return parser.parse_args()


def create_config(fname):
    """Create a dummy configuration file that can be modified to be used."""
    home = str(Path.home())
    config = {
        "root": home,
        "files": [
            "pictures",
            "videos/funny_vid.mp4",
        ],
    }

    # Create the config file if it does not already exist.
    try:
        if Path(fname).is_file():
            raise ConfigError("File already exists.")

        with open(fname, 'w') as f:
            json.dump(config, f, indent=4)

    except OSError as exc:
        raise ConfigError(f"Could not create '{fname}': {exc}")


def load_config(fname):
    """Load a configuration file supplied by the arguments passed."""
    try:
        if not Path(fname).is_file():
            raise ConfigError("Configuration provided either does"
                            " not exist or it is not a file.")

        with open(fname, 'r') as f:
            data = json.load(f)

        return data
    except OSError as exc:
        raise ConfigError(f"Could not load '{fname}': {exc}")


def nprint(*args, **kwargs):
    """Controls output depending if silent output is enabled or disabled."""
    if not SILENT_OUTPUT:
        print(" ".join(map(str,args)), **kwargs)


if __name__ == "__main__":
    main()
