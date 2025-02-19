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

from os import path
import argparse
import logging
import os
import sys
from typing import List

COMMIT_SHA = "47b3371"  # Updated by the build process
ID = "stown"
VERSION = "0.11.1rc2"

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


def fail(message: str, rc: int = 1) -> int:
    log.error(message)
    return rc


def getenv(key, default=None):
    if key in os.environ:
        return os.environ[key]
    return default


def parsed_filename(fn: str, ignore_dot_prefix=False) -> str:
    if not ignore_dot_prefix and fn[0:4] == "dot-":
        return f".{fn[4:]}"
    return fn


def remove(pathlike, dry_run=True) -> int:
    log.debug(f"rm {pathlike}")
    if not dry_run:
        os.remove(pathlike)
    return 0


def pathto(pathlike, want_abspath: bool, relpath_start=None):
    if want_abspath:
        p = path.abspath(pathlike)
    else:
        p = path.relpath(pathlike, start=relpath_start)
    return p


def is_same_file(target, source) -> bool:
    try:
        s: os.stat_result = os.stat(source, follow_symlinks=False)
        t: os.stat_result = os.stat(target, follow_symlinks=False)
        return s.st_dev == t.st_dev and s.st_ino == t.st_ino
    except FileNotFoundError:
        return False


def is_permitted(args: argparse.Namespace, target, source) -> bool:
    permit = False
    if not path.lexists(target):
        permit = True
    elif args.force or args.action == "unlink":
        permit = not is_same_file(target, source)
    log.debug(f"write permission for {target}: {permit}")
    return permit


def linkto(args: argparse.Namespace, target, source) -> int:
    source = pathto(source, args.absolute, path.dirname(target))
    if not is_permitted(args, target, source):
        return fail(f"Target '{target}' seems worth protecting", 2)
    if not args.dry_run:
        if path.lexists(target):
            target_removed = remove(target, args.dry_run) == 0
        else:
            target_removed = False
        if args.action == "link":
            log.info(f"{target} -> {source}")
            os.symlink(source, target)
        elif args.action == "unlink":
            if target_removed:
                log.info(f"{target} removed")
        else:
            # Should only happen during unit tests
            return fail(f"Unsupported action: {args.action}", 8)
    return 0


def stown(args: argparse.Namespace, target: str, sources: List[str], depth=0, parent_path=None) -> int:
    if depth >= args.depth:
        return fail(f"Depth limit ({depth}) reached", 3)
    for source in sources:
        if parent_path:
            source = path.join(parent_path, source)
        if not path.exists(source):
            log.warning(f"Source {source} not found")
            continue
        log.info(f"{'  '*depth}{target} -> {source}")
        if is_same_file(target, source):
            return fail(f"Source {source} and target are identical", 4)
        elif path.islink(target):
            rc = linkto(args, target, source)
            if rc != 0:  # pragma: no cover
                return rc
        elif not path.lexists(target):
            return linkto(args, target, source)
        elif path.isdir(source):
            for child in os.listdir(source):
                tchild = parsed_filename(child, args.no_dot)
                rc = stown(args, path.join(target, tchild), [child], depth + 1, source)
                if rc != 0:  # pragma: no cover
                    return rc
        else:  # pragma: no cover
            return fail(f"Unexpected pair: target {target} and source {source}", 7)
    return 0


def full_version(sha=COMMIT_SHA) -> str:  # pragma: no cover
    if sha:  # pragma: no cover
        suffix = f"+{sha}"
    else:
        suffix = ""
    return f"{ID} version {VERSION}{suffix}"


def arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog=ID,
        description="Stow file system objects by managing symlinks",
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
    sys.exit(rc)


if __name__ == "__main__":  # pragma: no cover
    main()
