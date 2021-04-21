#
# Copyright 2021 Sony Corporation
# SPDX-License-Identifier: MIT
#
"""
Configuration classes to acquire the configuration parameters like
  - Sharepoint urls, tenant id etc.
  - runtime parameters: debug, network etc.
  - logging
  - etc.
"""
import logging
import os
import re
from time import strftime

import yaml
from colorama import Fore, Style


class SharepointConfig:
    # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Configuration class for Sharepoint parameters:
    - tenant id
    - client (application) id
    - Sharepoint site URL (with subsite)
    - client secret
    """

    def __init__(self, subsite):
        with open("config.yaml") as f:
            conf = yaml.safe_load(f)
            self.tenant = conf["sp"]["tenant"]
            self.client = conf["sp"]["client"]
            self.site = conf["sp"]["site"]
            self.secret = conf["sp"]["secret"]
        self.subsite = subsite

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class RuntimeConfig:
    # pylint: disable=too-few-public-methods
    """
    Configuration class for runtime parameters:
    - debug
    - size of the upload file chunk
    """

    def __init__(self, debug):
        self.debug = debug
        with open("config.yaml") as f:
            conf = yaml.safe_load(f)
            self.chunk_size = conf["runtime"]["chunk_size"]

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class FilesConfig:
    # pylint: disable=too-few-public-methods
    """
    Configuration class for files to upload
    - path to files
    - files to upload
    - output folder name
    """

    def __init__(self, path, files, out_folder):
        self.path = path

        if files:
            self.files = files.split(",")
        else:
            self.files = None

        if out_folder:
            self.out_folder = out_folder
        elif path:
            self.out_folder = os.path.basename(os.path.abspath(path))
        else:
            self.out_folder = None

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def verify(self):
        """
        Verify that:
            - paths exist
            - output folder name is correct
        Recreate file paths to absolute paths.
        """
        ret = []
        if not self.path and not self.files:
            ret.append(f"at least one of -i or -f must be present")

        ret += self._verify_path()
        ret += self._verify_files()
        ret += self._verify_out_folder()
        ret = [x for x in ret if x]

        if not ret:
            self._fix_paths()

        return ret

    def _verify_path(self):
        ret = []
        if self.path:
            if not os.path.exists(self.path):
                ret.append(f"{self.path} does not exist")
            elif not os.path.isdir(self.path):
                ret.append(f"{self.path} is not a directory")

        return ret

    def _verify_files(self):
        if not self.files:
            return []

        ret = []
        for f in self.files:
            if not os.path.exists(f):
                if self.path and not os.path.exists(os.path.join(self.path, f)):
                    ret.append(f"{f} does not exist on path {self.path}")
                elif self.path and not os.path.isfile(os.path.join(self.path, f)):
                    ret.append(f"{f} is not a file")
                elif not self.path:
                    ret.append(f"{f} does not exist")
            elif not os.path.isfile(f):
                ret.append(f"{f} is not a file")

        return ret

    def _verify_out_folder(self):
        if not self.out_folder:
            return []

        ret = []
        allowed_path = re.compile("^[a-zA-Z0-9._-]+$")
        if not allowed_path.match(self.out_folder):
            ret.append(
                f"{self.out_folder} contains illegal characters: only a-zA-Z0-9._- are allowed"
            )
        return ret

    def _fix_paths(self):
        if self.path:
            local_path = os.path.abspath(self.path)
        else:
            local_path = os.path.abspath(".")

        if self.files:
            self.files = [os.path.join(local_path, x) for x in self.files]
        else:
            files = []
            for f in os.listdir(local_path):
                path = os.path.join(local_path, f)
                if os.path.isfile(path):
                    files.append(path)
            self.files = files


class Logger:
    """
    Logging configuration and methods.
    """

    def __init__(self, loggerclass, path=".", debug=False):
        date_time = strftime("%Y%m%d_%H%M%S")
        f = os.path.join(path, "SPUPPY_" + date_time + ".log")
        handler = logging.FileHandler(f, mode="a")
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(loggerclass)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # pylint: disable=missing-docstring
    def debug(self, msg):
        print(msg)
        self.logger.debug(msg)

    def info(self, msg):
        print(msg)
        self.logger.info(msg)

    def warning(self, msg):
        print(f"{Fore.YELLOW}WARNING:{Style.RESET_ALL} " + msg)
        self.logger.warning(msg)

    def error(self, msg):
        print(f"{Fore.RED}FAIL:{Style.RESET_ALL} " + msg)
        self.logger.error(msg)

    def exception(self, err):
        print(f"{Fore.RED}FAIL:{Style.RESET_ALL} ", err)
        self.logger.exception(err)

    def success(self, msg):
        print(f"{Fore.GREEN}SUCCESS:{Style.RESET_ALL} " + msg)
        self.logger.info(msg)
