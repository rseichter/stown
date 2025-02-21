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
from stown.__main__ import arg_parser
from stown.core import Permit
from stown.core import fail
from stown.core import getenv
from stown.core import is_permitted
from stown.core import linkto
from stown.core import parsed_filename
from stown.core import pathto
from stown.core import remove
from stown.core import stown
from stown.log import init_logging
from typing import List
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import unittest
import uuid

DATADIR = "data"
TMPDIR = "tmp"
XJSON = "expected.json"


def is_truthy(x) -> bool:
    return x or x == 1 or x == "true" or x == "yes"


def load_json(path):
    with open(path, "rt") as f:
        return json.load(f)


def random_name(prefix="stown.", suffix=".tmp") -> str:
    return f"{prefix}{uuid.uuid4()}{suffix}"


def random_tmp(tmpdir=TMPDIR, suffix=".tmp") -> str:
    return path.join(tmpdir, random_name(suffix=suffix))


class TestStown(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_logging("DEBUG", "tests/test.log")
        # init_logging("FATAL")

    def setUp(self):
        os.chdir(path.dirname(__file__))
        self.args = self.parse_args()
        if path.exists(TMPDIR):  # pragma: no cover
            shutil.rmtree(TMPDIR)
        os.mkdir(TMPDIR)
        os.mkdir(path.join(TMPDIR, "healthy"))

    def parse_args(self, flags: List[str] = []) -> argparse.Namespace:
        return arg_parser().parse_args(flags + [TMPDIR, DATADIR])

    def assert_json_equal(self, checkme: str, expected: str):
        c = load_json(checkme)
        x = load_json(expected)
        self.assertEqual(c, x)

    def test_fail_custom_rc(self):
        self.assertEqual(fail("dummy", -42), -42)

    def test_getenv_default(self):
        self.assertEqual(getenv(random_name(), XJSON), XJSON)

    def test_getenv_known_key(self):
        self.assertIsNotNone(getenv("LANG"))

    def test_permit_denied(self):
        self.assertEqual(is_permitted(self.args, ".", DATADIR), Permit.DENIED)

    def test_permit_forced(self):
        rnd = random_tmp()
        with open(rnd, "wt") as f:
            print(file=f)
        a = self.parse_args(["--force"])
        self.assertEqual(is_permitted(a, rnd, XJSON), Permit.FORCED)

    def test_permit_granted(self):
        self.assertEqual(is_permitted(self.args, random_name(), XJSON), Permit.GRANTED)

    def test_linkto_existing(self):
        self.assertEqual(linkto(self.args, ".", DATADIR), 2)

    def test_linkto_unsupported_action(self):
        a = self.parse_args(["-f"])
        a.action = "smile"
        t = random_tmp()
        os.symlink(XJSON, t)
        self.assertEqual(linkto(a, t, XJSON), 8)

    def test_linkto_existing_force(self):
        rnd = random_tmp()
        with open(rnd, "wt") as f:
            print(file=f)
        a = self.parse_args(["--force"])
        self.assertEqual(linkto(a, rnd, XJSON), 0)

    def test_unlink_nonexistent(self):
        a = self.parse_args(["--action", "unlink"])
        self.assertEqual(linkto(a, random_name(), XJSON), 0)

    def test_linkto_existing_force_dry(self):
        a = self.parse_args(["-d", "-f"])
        self.assertEqual(linkto(a, ".", XJSON), 0)

    def test_maxdepth(self):
        a = self.parse_args(["--depth", "0"])
        self.assertEqual(stown(a, "x", ["y"]), 3)

    def test_stown_link(self):
        a = self.args
        b = random_tmp()
        c = path.join(DATADIR, "salt")
        os.symlink(c, b)
        self.assertEqual(stown(a, b, [c]), 2)

    def test_linkto_new(self):
        self.assertEqual(linkto(self.args, random_tmp(), XJSON), 0)

    def test_linkto_new_dry(self):
        a = self.parse_args(["-d"])
        self.assertEqual(linkto(a, random_tmp(), XJSON), 0)

    def test_parsed_dot(self):
        n = random_name(prefix="")
        self.assertEqual(parsed_filename(f"dot-{n}"), f".{n}")

    def test_parsed_dot_disabled(self):
        n = random_name(prefix="dot-")
        self.assertEqual(parsed_filename(n, True), n)

    def test_parsed_nodot(self):
        n = random_name(prefix="nodot-")
        self.assertEqual(parsed_filename(n), n)

    def test_pathto(self):
        self.assertTrue(path.isabs(pathto(XJSON, True)))

    def test_same_file(self):
        self.assertEqual(stown(self.args, ".", ["."]), 4)

    def test_remove(self):
        self.assertEqual(remove(XJSON, dry_run=True), 0)

    def test_stown(self):
        self.assertEqual(stown(self.args, self.args.target, self.args.source), 0)
        if not is_truthy(getenv("DISABLE_TREE")):  # pragma: no cover
            tmp = random_tmp(tempfile.gettempdir(), ".json")
            subprocess.run(["tree", "-aJ", "-o", tmp, self.args.target])
            self.maxDiff = None
            lj = "latest.json"
            shutil.move(tmp, lj)
            self.assert_json_equal(lj, XJSON)

    def test_missing_source(self):
        self.assertEqual(stown(self.args, self.args.target, [random_name()]), 0)

    def test_unlink(self):
        a = self.parse_args(["-a", "unlink", "-f"])
        t = random_tmp()
        os.symlink(XJSON, t)
        self.assertEqual(stown(a, t, [XJSON]), 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
