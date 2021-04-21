#!/usr/bin/env python3
#
# Copyright 2021 Sony Corporation
# SPDX-License-Identifier: MIT
#
"""
Upload files to a given Sharepoint site/subsite.
"""
import argparse

from config import FilesConfig, Logger, RuntimeConfig, SharepointConfig
from sputil import Sharepoint


class Uploader:
    """
    Uploads files to Sharepoint.
    """

    def __init__(self, params):
        self._debug = params.debug
        self._subsite = params.subsite
        self._logger = Logger("spuppy", "logs", params.debug)
        self._path = params.directory
        self._files = params.files
        self._out = params.out

    def main(self):
        """
        Orchestrate upload of a file using given configurations.
        """

        spconf = SharepointConfig(self._subsite)
        runtime = RuntimeConfig(self._debug)
        fconf = FilesConfig(self._path, self._files, self._out)
        verify = fconf.verify()

        if self._debug:
            self._logger.debug(spconf)
            self._logger.debug(runtime)
            self._logger.debug(fconf)

        if verify:
            for v in verify:
                self._logger.error(v)
            return

        if self._debug:
            self._logger.debug(fconf)

        try:
            sp = Sharepoint(fconf, spconf, runtime, self._logger)
            sp.get_token()
            if self._debug:
                self._logger.debug(sp)

            if not sp.verify_url():
                return

            if fconf.out_folder and not sp.add_folder():
                return

            sp.upload_files()
        except Exception as e:  # pylint: disable=broad-except
            # This `except` is intentionally broad to capture it in
            # the log for posterity. main exists anyway.
            self._logger.exception(e)


if __name__ == "__main__":
    ARGS = argparse.ArgumentParser(
        description="Upload a file to a specified folder of a Sharepoint site."
    )
    ARGS.add_argument(
        "-d",
        "--debug",
        help="print additional debug information",
        action="store_true",
    )
    ARGS.add_argument(
        "-s",
        "--subsite",
        help="subsite of a configured Sharepoint site",
        required=False,
    )
    ARGS.add_argument(
        "-i",
        "--directory",
        help="folder with files to upload (if no files specified, upload the whole directory)",
        required=False,
    )
    ARGS.add_argument(
        "-f",
        "--files",
        help="comma separated list of files to upload (if not specified, upload the -i directory)",
        required=False,
    )
    ARGS.add_argument(
        "-o",
        "--out",
        help="folder name to create at the target site (if not specified, "
        "use the folder name of -i directory",
        required=False,
    )

    PARAMS = ARGS.parse_args()

    Uploader(PARAMS).main()
