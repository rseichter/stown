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
import sys
from . import __version__


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="stown",
        description="Stow file system objects by creating links",
        epilog=f"stown version {__version__}. Copyright © 2025 Ralph Seichter.",
    )
    parser.add_argument("action", choices=["stow", "unstow"])
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
    args = parser.parse_args()
    return 0


if __name__ == "__main__":
    sys.exit(main())
