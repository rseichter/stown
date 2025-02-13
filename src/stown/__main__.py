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

VERSION = "0.7.0-dev1"
EPILOG = f"stown version {VERSION} Copyright © 2025 Ralph Seichter."


def fail(message: str, rc: int = 1) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return rc


def say(message, verbose=True):
    if verbose:
        print(message)


def parsed_filename(fn):
    if fn[0:4] == "dot-":
        return f".{fn[4:]}"
    return fn


def remove(path, dry_run=True):
    if dry_run:
        print(f"rm {path}")
    else:
        os.remove(path)


def linkto(args: argparse.Namespace, target, source) -> int:
    target_exists = os.path.lexists(target)
    if target_exists and not args.force:
        return fail(f"Target {target} exists and --force was not specified", 2)
    start = os.path.dirname(target)
    src = os.path.relpath(source, start=start)
    if args.dry_run:
        if target_exists:
            opt = "f"
        else:
            opt = ""
        print(f"ln -{opt}s {src} {target}")
    else:
        if target_exists:
            remove(target, args.dry_run)
        os.symlink(src, target)
    return 0


def is_same_file(target, source) -> bool:
    sr: os.stat_result = os.stat(source, follow_symlinks=False)
    tr: os.stat_result = os.stat(target, follow_symlinks=False)
    return sr.st_dev == tr.st_dev and sr.st_ino == tr.st_ino


def stown(args: argparse.Namespace, target, sources, depth=0, parent_path=None) -> int:
    if depth >= args.depth:
        return fail(f"Maximum depth {depth} reached", 3)
    elif args.action != "stow":
        return fail(f"Action {args.action} is not implemented", 5)
    say(f"# {target} (depth {depth})", args.verbose)
    for source in sources:
        if parent_path:
            source = os.path.join(parent_path, source)
        if not os.path.lexists(target):
            return linkto(args, target, source)
        elif is_same_file(target, source):
            return fail(f"Source {source} and target are identical", 4)
        elif os.path.islink(target):
            rc = linkto(args, target, source)
            if rc != 0:
                return rc
        elif os.path.isdir(source):
            for child in os.listdir(source):
                tchild = parsed_filename(child)
                rc = stown(args, os.path.join(target, tchild), [child], depth + 1, source)
                if rc != 0:
                    return rc
        elif os.path.isfile(target) and os.path.isfile(source):
            return fail(f"Both target {target} and source {source} are files")
        else:
            return fail(f"Unexpected pair: target {target} and source {source}")
    return 0


def arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stown",
        description="Stow file system objects by creating links",
        epilog=EPILOG,
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
        default=5,
        type=int,
        help="maximum recursion depth (default: 5)",
    )
    parser.add_argument("-f", "--force", default=False, action="store_true", help="force action")
    parser.add_argument("-v", "--verbose", default=False, action="store_true", help="verbose messages")
    parser.add_argument("target", help="action target (links are created here)")
    parser.add_argument("source", nargs="+", help="action sources (links point here)")
    return parser


def main():
    args = arg_parser().parse_args()
    if args.source:
        rc = stown(args, args.target, args.source)
    else:
        rc = stown(args, args.target, ["."])
    sys.exit(rc)


if __name__ == "__main__":
    main()
