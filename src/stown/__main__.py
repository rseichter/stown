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

import argparse
import os
import sys
from . import __version__

args: argparse.Namespace


def fail(message: str, rc: int = 1) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return rc


def say(message):
    if args.verbose:
        print(message)


def remove(path):
    if args.dry_run:
        print(f"rm {path}")
    else:
        os.remove(path)


def linkto(target, source) -> int:
    target_exists = os.path.lexists(target)
    if target_exists and not args.force:
        return fail(f"Target {target} exists and --force was not specified", 2)
    if args.dry_run:
        if target_exists:
            opt = "f"
        else:
            opt = ""
        print(f"ln -{opt}s {source} {target}")
    else:
        if target_exists:
            remove(target)
        os.symlink(source, target)
    return 0


def is_same_file(target, source) -> bool:
    sr: os.stat_result = os.stat(source, follow_symlinks=False)
    tr: os.stat_result = os.stat(target, follow_symlinks=False)
    return sr.st_dev == tr.st_dev and sr.st_ino == tr.st_ino


# noqa: C901
def stow(target, sources, depth=0, parent_path=None) -> int:
    if depth >= args.depth:
        return fail(f"Maximum depth {depth} reached", 3)
    say(f"# {target} (depth {depth})")
    for source in sources:
        if parent_path:
            source = os.path.join(parent_path, source)
        if not os.path.lexists(target):
            return linkto(target, source)
        elif is_same_file(target, source):
            return fail(f"Source {source} and target are identical")
        elif os.path.islink(target):
            rc = linkto(target, source)
            if rc != 0:
                return rc
        elif os.path.isdir(source):
            for child in os.listdir(source):
                rc = stow(os.path.join(target, child), [child], depth + 1, source)
                if rc != 0:
                    return rc
        else:
            return fail(f"Unexpected pair: target {target} and source {source}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="stown",
        description="Stow file system objects by creating links",
        epilog=f"stown version {__version__}. Copyright © 2025 Ralph Seichter.",
    )
    parser.add_argument(
        "-a",
        "--action",
        choices=["stow", "unstow"],
        default="stow",
        help="action to take (default: stow)",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        default=False,
        action="store_true",
        help="print operations only",
    )
    parser.add_argument(
        "-p",
        "--depth",
        default=10,
        type=int,
        help="maximum recursion depth (default: 10)",
    )
    parser.add_argument("-f", "--force", default=False, action="store_true", help="force action")
    parser.add_argument("-v", "--verbose", default=False, action="store_true", help="verbose messages")
    parser.add_argument("target", help="action target (links are created here)")
    parser.add_argument("source", nargs="+", help="action sources (links point here)")
    global args
    args = parser.parse_args()
    if args.action == "stow":
        if args.source:
            rc = stow(args.target, args.source)
        else:
            rc = stow(args.target, ["."])
        return rc
    else:
        print(f"Action not implemented: {args.action}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
