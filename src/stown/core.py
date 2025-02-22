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

from argparse import Namespace
from enum import Enum
from os import environ
from os import listdir
from os import path
from os import remove as os_remove
from os import stat
from os import stat_result
from os import symlink
from typing import List

from .log import log


class Status(Enum):
    OK = 0
    ERROR = 1  # unspecified error
    ACTION_UNKNOWN = 2
    CRUSH_DEPTH = 3
    FORBIDDEN = 4
    IDENTICAL = 5
    UNEXPECTED_PAIR = 6

    def is_ok(self) -> bool:
        return self.value == Status.OK.value


class Permit(Enum):
    DENIED = 0
    FORCED = 1
    GRANTED = 2

    def is_denied(self) -> bool:
        return self.value == Permit.DENIED.value

    def is_forced(self) -> bool:
        return self.value == Permit.FORCED.value

    def is_granted(self) -> bool:
        return self.value == Permit.GRANTED.value


def fail(message: str, rc: Status = Status.ERROR) -> Status:
    log.error(message)
    return rc


def getenv(key, default=None):
    if key in environ:
        return environ[key]
    return default


def parsed_filename(fn: str, ignore_dot_prefix=False) -> str:
    if not ignore_dot_prefix and fn[0:4] == "dot-":
        return f".{fn[4:]}"
    return fn


def remove(path_, dry_run=True) -> bool:
    if dry_run:
        suffix = " (dry)"
    else:
        os_remove(path_)
        suffix = ""
    log.debug(f"removed {path_}{suffix}")
    return not dry_run


def pathto(pathlike, want_abspath: bool, relpath_start=None):
    if want_abspath:
        p = path.abspath(pathlike)
    else:
        p = path.relpath(pathlike, start=relpath_start)
    return p


def is_same_file(target, source) -> bool:
    try:
        s: stat_result = stat(source, follow_symlinks=False)
        t: stat_result = stat(target, follow_symlinks=False)
        return s.st_dev == t.st_dev and s.st_ino == t.st_ino
    except FileNotFoundError:
        return False


def obtain_permit(args: Namespace, target, source) -> Permit:
    if is_same_file(target, source):
        per = Permit.DENIED
    elif not path.lexists(target):
        per = Permit.GRANTED
    elif args.force or args.action == "unlink":
        per = Permit.FORCED
    else:
        per = Permit.DENIED
    log.debug(f"write permit for {target}: {per}")
    return per


def linkto(args: Namespace, target, source) -> Status:
    source = pathto(source, args.absolute, path.dirname(target))
    if obtain_permit(args, target, source).is_denied():
        return fail(f"Target {target} denied", Status.FORBIDDEN)
    if not args.dry_run:
        if path.lexists(target):
            remove(target, args.dry_run)
        if args.action == "link":
            log.info(f"{target} -> {source}")
            symlink(source, target)
        elif args.action != "unlink":
            # Should only happen during unit tests
            return fail(f"Unsupported action: {args.action}", Status.ACTION_UNKNOWN)
    return Status.OK


def stown(args: Namespace, target: str, sources: List[str], depth=0, parent_path=None) -> Status:
    if depth >= args.depth:
        return fail(f"Depth limit ({depth}) reached", Status.CRUSH_DEPTH)
    for source in sources:
        if parent_path:
            source = path.join(parent_path, source)
        if not path.exists(source):
            log.warning(f"Source {source} not found")
            continue
        log.info(f"{'  '*depth}{target} -> {source}")
        if is_same_file(target, source):
            return fail(f"Source {source} and target are identical", Status.IDENTICAL)
        elif path.islink(target):
            rc = linkto(args, target, source)
            if not rc.is_ok():
                return rc
        elif not path.lexists(target):
            return linkto(args, target, source)
        elif path.isdir(source):
            for child in listdir(source):
                tchild = parsed_filename(child, args.no_dot)
                rc = stown(args, path.join(target, tchild), [child], depth + 1, source)
                if not rc.is_ok():  # pragma: no cover
                    return rc
        else:
            return fail(
                f"Target {target} and source {source} have incompatible types",
                Status.UNEXPECTED_PAIR,
            )
    return Status.OK
