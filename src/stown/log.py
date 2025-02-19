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

import logging
import sys

COMMIT_SHA = "47b3371"  # Updated by the build process
ID = "stown"
VERSION = "0.11.1"

log = logging.getLogger(ID)


def init_logging(level=logging.DEBUG, filename="-"):
    format = "%(message)s"
    if isinstance(level, str):  # pragma: no cover
        # Get numeric representation of the log level string
        level = logging.getLevelName(level.upper())
    if filename == "-":  # pragma: no cover
        logging.basicConfig(stream=sys.stdout, format=format, level=level)
    else:
        logging.basicConfig(filename=filename, format=format, level=level)
