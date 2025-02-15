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

ID = "stown"
VERSION = "0.8.0-dev2"
EPILOG = f"{ID} version {VERSION} Copyright © 2025 Ralph Seichter"

log = logging.getLogger(ID)


def init_logging(level=logging.DEBUG):  # pragma: no cover
    format = "%(message)s"
    if isinstance(level, str):
        level = logging.getLevelName(level.upper())
    logging.basicConfig(stream=sys.stdout, format=format, level=level)


def fail(message: str, rc: int = 1) -> int:
    log.error(message)
    return rc


def getenv(key, default=None):
    if key in os.environ:
        return os.environ[key]
    return default


def parsed_filename(fn: str) -> str:
    if fn[0:4] == "dot-":
        return f".{fn[4:]}"
    return fn


def remove(pathlike, dry_run=True) -> int:
    log.debug(f"rm {pathlike}")
    if not dry_run:
        os.remove(pathlike)
    return 0


def pathto(pathlike, absolute: bool, relstart=None):
    if absolute:
        p = path.abspath(pathlike)
    else:
        p = path.relpath(pathlike, start=relstart)
    return p


def is_overwrite_allowed(args: argparse.Namespace, pathlike) -> bool:
    is_allowed = args.force or args.action == "unstow"
    log.debug(f"write permission for {pathlike}: {is_allowed}")
    return is_allowed


def linkto(args: argparse.Namespace, target, source) -> int:
    target_exists = path.lexists(target)
    if target_exists and not is_overwrite_allowed(args, target):
        return fail(f"Target {target} exists and --force was not specified", 2)
    start = path.dirname(target)
    src = pathto(source, args.absolute, start)
    if not args.dry_run:
        if target_exists:
            target_removed = remove(target, args.dry_run) == 0
        else:
            target_removed = False
        if args.action == "stow":
            log.info(f"{target} -> {src}")
            os.symlink(src, target)
        elif args.action == "unstow":
            if target_removed:
                log.info(f"{target} removed")
        else:
            # Should only happen during unit tests
            return fail("Unsupported action '{args.action}'", 8)
    return 0


def is_same_file(target, source) -> bool:
    try:
        s: os.stat_result = os.stat(source, follow_symlinks=False)
        t: os.stat_result = os.stat(target, follow_symlinks=False)
        return s.st_dev == t.st_dev and s.st_ino == t.st_ino
    except FileNotFoundError:
        return False


def stown(args: argparse.Namespace, target, sources, depth=0, parent_path=None) -> int:
    if depth >= args.depth:
        return fail(f"Depth limit ({depth}) reached", 3)
    for source in sources:
        if parent_path:
            source = path.join(parent_path, source)
        log.debug(f"target: '{target}' source: '{source}' depth: {depth}")
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
                tchild = parsed_filename(child)
                rc = stown(args, path.join(target, tchild), [child], depth + 1, source)
                if rc != 0:  # pragma: no cover
                    return rc
        else:
            return fail(f"Unexpected pair: target {target} and source {source}", 7)
    return 0


def arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog=ID,
        description="Stow file system objects by creating links",
        epilog=EPILOG,
    )
    ap.add_argument(
        "-a",
        "--action",
        choices=["stow", "unstow"],
        default="stow",
        help="action to take (default: stow)",
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
        help="print operations only",
    )
    d = getenv("STOWN_LOGLEVEL", "WARN")
    ap.add_argument(
        "-l",
        "--loglevel",
        default=d,
        help=f"log level (default: {d})",
        metavar="LEVEL",
    )
    d = 10
    ap.add_argument(
        "-p",
        "--depth",
        default=d,
        type=int,
        help=f"maximum recursion depth (default: {d})",
    )
    ap.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="force action (overwrites existing targets)",
    )
    ap.add_argument("-v", "--verbose", default=False, action="store_true", help="verbose messages")
    ap.add_argument("target", help="action target (links are created here)")
    ap.add_argument("source", nargs="+", help="action sources (links point here)")
    return ap


def main():  # pragma: no cover
    args = arg_parser().parse_args()
    init_logging(args.loglevel)
    rc = stown(args, args.target, args.source)
    sys.exit(rc)


if __name__ == "__main__":  # pragma: no cover
    main()
