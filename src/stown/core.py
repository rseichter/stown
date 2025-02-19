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

from .log import log
from argparse import Namespace
from os import environ
from os import listdir
from os import path
from os import remove as os_remove
from os import stat
from os import stat_result
from os import symlink
from typing import List


def fail(message: str, rc: int = 1) -> int:
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


def remove(pathlike, dry_run=True) -> int:
    log.debug(f"rm {pathlike}")
    if not dry_run:
        os_remove(pathlike)
    return 0


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


def is_permitted(args: Namespace, target, source) -> bool:
    permit = False
    if not path.lexists(target):
        permit = True
    elif args.force or args.action == "unlink":
        permit = not is_same_file(target, source)
    log.debug(f"write permission for {target}: {permit}")
    return permit


def linkto(args: Namespace, target, source) -> int:
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
            symlink(source, target)
        elif args.action == "unlink":
            if target_removed:
                log.info(f"{target} removed")
        else:
            # Should only happen during unit tests
            return fail(f"Unsupported action: {args.action}", 8)
    return 0


def stown(args: Namespace, target: str, sources: List[str], depth=0, parent_path=None) -> int:
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
            for child in listdir(source):
                tchild = parsed_filename(child, args.no_dot)
                rc = stown(args, path.join(target, tchild), [child], depth + 1, source)
                if rc != 0:  # pragma: no cover
                    return rc
        else:  # pragma: no cover
            return fail(f"Unexpected pair: target {target} and source {source}", 7)
    return 0
