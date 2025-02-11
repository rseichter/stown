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


def fail(message: str, returncode: int = 1) -> int:
    print(message, file=sys.stderr)
    return returncode


def linkto(target, source):
    if args.dry_run:
        print(f"ln -s {source} {target}")
    else:
        os.symlink(source, target)


def remove(path):
    if args.dry_run:
        print(f"rm {path}")
    else:
        os.remove(path)


def stow() -> int:
    if args.source:
        sources = args.source
    else:
        sources = ["."]
    for source in sources:
        if not os.path.exists(args.target):
            linkto(args.target, source)
            continue
        sr: os.stat_result = os.stat(source, follow_symlinks=False)
        tr: os.stat_result = os.stat(args.target, follow_symlinks=False)
        if sr.st_dev == tr.st_dev and sr.st_ino == tr.st_ino:
            return fail(f"Source and target must not be identical: {source}")
        elif os.path.islink(args.target):
            if args.force:
                remove(args.target)
                linkto(args.target, source)
                continue
            else:
                return fail(
                    f"Target '{args.target}' exists and --force was not specified"
                )
        print(f"\nTarget {args.target} {tr}\nSource {source} {sr}")
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
        "-f", "--force", default=False, action="store_true", help="force action"
    )
    parser.add_argument("target", help="action target (links are created here)")
    parser.add_argument("source", nargs="+", help="action sources (links point here)")
    global args
    args = parser.parse_args()
    if args.action == "stow":
        return stow()
    else:
        print(f"Action not implemented: {args.action}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
