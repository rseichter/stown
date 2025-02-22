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

from argparse import ArgumentParser
from sys import exit

from .core import getenv
from .core import stown
from .log import COMMIT_SHA
from .log import ID
from .log import VERSION
from .log import init_logging


def full_version(sha=COMMIT_SHA) -> str:  # pragma: no cover
    if sha:  # pragma: no cover
        suffix = f"+{sha}"
    else:
        suffix = ""
    return f"{ID} version {VERSION}{suffix}"


def arg_parser() -> ArgumentParser:
    ap = ArgumentParser(
        prog=ID,
        description="Manage file system object mapping via symlinks",
        epilog=f"{full_version()} Copyright © 2025 Ralph Seichter",
    )
    d = "link"
    ap.add_argument(
        "-a",
        "--action",
        choices=["link", "unlink"],
        default=d,
        help=f"action to take (default: {d})",
    )
    ap.add_argument(
        "-b",
        "--absolute",
        default=False,
        action="store_true",
        help="create links using absolute paths",
    )
    ap.add_argument(
        "-d",
        "--dry-run",
        default=False,
        action="store_true",
        help="log operations but do not modify",
    )
    ap.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="force action (overwrite existing targets)",
    )
    ap.add_argument(
        "-l",
        "--loglevel",
        default=getenv("STOWN_LOGLEVEL", "WARNING"),
        help="log level (default: WARNING)",
        metavar="LEVEL",
    )
    ap.add_argument(
        "-n",
        "--no-dot",
        default=False,
        action="store_true",
        help="disable dot-prefix treatment",
    )
    d = 10
    ap.add_argument(
        "-D",
        "--depth",
        default=d,
        type=int,
        help=f"maximum recursion depth (default: {d})",
    )
    d = 10
    ap.add_argument(
        "-L",
        "--logpath",
        default=getenv("STOWN_LOGPATH", "-"),
        help="log data destination",
        metavar="PATH",
    )
    ap.add_argument("target", help="action target (links are created here)")
    ap.add_argument("source", nargs="+", help="action sources (links point here)")
    return ap


def main():  # pragma: no cover
    args = arg_parser().parse_args()
    init_logging(args.loglevel, args.logpath)
    rc = stown(args, args.target, args.source)
    exit(rc.value)


if __name__ == "__main__":  # pragma: no cover
    main()
