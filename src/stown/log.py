"""
Copyright © 2025 Ralph Seichter

This file is part of "stown".

stown is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

stown is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
stown. If not, see <https://www.gnu.org/licenses/>.
"""

from logging import DEBUG
from logging import basicConfig
from logging import getLevelName
from logging import getLogger
from os import getcwd
from sys import stdout

COMMIT_SHA = "c63554c"
ID = "stown"
VERSION = "0.14.0"

log = getLogger(ID)


def init_logging(level: str = "WARNING", filename: str = "-"):
    format = "%(asctime)s %(message)s"
    datefmt = "%H:%M:%S"
    if filename == "-":  # pragma: no cover
        basicConfig(stream=stdout, format=format, datefmt=datefmt, level=level)
    else:
        basicConfig(filename=filename, format=format, datefmt=datefmt, level=level)
    log.info("-" * 50)
    log.info(f"CWD is {getcwd()}")
