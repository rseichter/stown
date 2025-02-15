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
from stown import __main__ as stown
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


def random_name(suffix=".tmp") -> str:
    return f"stown.{uuid.uuid4()}{suffix}"


def random_tmp(tmpdir=TMPDIR, suffix=".tmp") -> str:
    return path.join(tmpdir, random_name(suffix))


class TestStown(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stown.init_logging("FATAL")

    def setUp(self):
        os.chdir(path.dirname(__file__))
        self.args = self.parse_args()
        if path.exists(TMPDIR):  # pragma: no cover
            shutil.rmtree(TMPDIR)
        os.mkdir(TMPDIR)
        os.mkdir(path.join(TMPDIR, "healthy"))

    def parse_args(self, flags: List[str] = []) -> argparse.Namespace:
        return stown.arg_parser().parse_args(flags + [TMPDIR, DATADIR])

    def assert_json_equal(self, checkme: str, expected: str):
        c = load_json(checkme)
        x = load_json(expected)
        self.assertEqual(c, x)

    def test_fail_custom_rc(self):
        self.assertEqual(stown.fail("dummy", -42), -42)

    def test_getenv_default(self):
        self.assertEqual(stown.getenv(random_name(), XJSON), XJSON)

    def test_getenv_known_key(self):
        self.assertIsNotNone(stown.getenv("LANG"))

    def test_linkto_existing(self):
        self.assertEqual(stown.linkto(self.args, ".", DATADIR), 2)

    def test_linkto_unsupported_action(self):
        a = self.parse_args(["-f"])
        a.action = "smile"
        t = random_tmp()
        os.symlink(XJSON, t)
        self.assertEqual(stown.linkto(a, t, XJSON), 8)

    def test_linkto_existing_force(self):
        rnd = random_tmp()
        with open(rnd, "wt") as f:
            print(file=f)
        a = self.parse_args(["--force"])
        self.assertEqual(stown.linkto(a, rnd, XJSON), 0)

    def test_linkto_existing_force_dry(self):
        a = self.parse_args(["-d", "-f"])
        self.assertEqual(stown.linkto(a, ".", XJSON), 0)

    def test_stown_unexpected_pair(self):
        rnd = random_tmp()
        with open(rnd, "wt") as f:
            print(file=f)
        self.assertEqual(stown.stown(self.args, rnd, XJSON), 7)

    def test_maxdepth(self):
        a = self.parse_args(["--depth", "0"])
        self.assertEqual(stown.stown(a, "x", "y"), 3)

    def test_stown_link(self):
        # a = self.parse_args(["-d"])
        a = self.args
        b = random_tmp()
        c = path.join(DATADIR, "salt")
        os.symlink(c, b)
        self.assertEqual(stown.stown(a, b, c), 2)

    def test_linkto_new(self):
        self.assertEqual(stown.linkto(self.args, random_tmp(), XJSON), 0)

    def test_linkto_new_dry(self):
        a = self.parse_args(["-d"])
        self.assertEqual(stown.linkto(a, random_tmp(), XJSON), 0)

    def test_parsed_dot(self):
        self.assertEqual(stown.parsed_filename("dot-foo"), ".foo")

    def test_parsed_nodot(self):
        self.assertEqual(stown.parsed_filename("bar"), "bar")

    def test_pathto(self):
        self.assertTrue(path.isabs(stown.pathto(XJSON, True)))

    def test_same_file(self):
        self.assertEqual(stown.stown(self.args, ".", "."), 4)

    def test_remove(self):
        self.assertEqual(stown.remove(XJSON, dry_run=True), 0)

    def test_stown(self):
        self.assertEqual(stown.stown(self.args, self.args.target, self.args.source), 0)
        if not is_truthy(stown.getenv("DISABLE_TREE")):  # pragma: no cover
            out = random_tmp(tempfile.gettempdir(), ".json")
            subprocess.run(["tree", "-aJ", "-o", out, self.args.target])
            self.assert_json_equal(out, XJSON)
            os.remove(out)

    def test_unstow(self):
        a = self.parse_args(["-a", "unstow", "-f"])
        t = random_tmp()
        os.symlink(XJSON, t)
        self.assertEqual(stown.stown(a, t, XJSON), 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
