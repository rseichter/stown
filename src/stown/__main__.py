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
import os, sys
from . import __version__


def fail(message: str, returncode: int = 1) -> int:
    print(message, file=sys.stderr)
    return returncode


def linkto(target, source):
    print(f"ln -s {source} {target}")


def stow(args: argparse.Namespace) -> int:
    if args.source:
        sources = args.source
    else:
        sources = ["."]
    for source in sources:
        sr: os.stat_result = os.stat(source, follow_symlinks=False)
        try:
            tr: os.stat_result = os.stat(args.target, follow_symlinks=False)
        except FileNotFoundError:
            linkto(args.target, source)
            continue
        print(f"\nTarget {args.target} {tr}\nSource {source} {sr}")
        if sr.st_dev == tr.st_dev and sr.st_ino == tr.st_ino:
            return fail(f"Source and target must not be identical: {source}")
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
    args = parser.parse_args()
    if args.action == "stow":
        return stow(args)
    else:
        print(f"Action not implemented: {args.action}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
