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

from stown import __main__ as stown
from typing import List
import argparse
import json
import os
import shutil
import subprocess
import unittest
import uuid

TMPDIR = "tmp"


def getenv(key, default=None):
    if key in os.environ:
        return os.environ[key]
    return default


def truthy(x) -> bool:
    return x or x == 1 or x == "true" or x == "yes"


def load_json(path):
    with open(path, "rt") as f:
        return json.load(f)


def random_tmp() -> str:
    return os.path.join(TMPDIR, str(uuid.uuid4()))


class TestStown(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(__file__))
        self.datadir = "data"
        stown.args = self.parse_args()
        if os.path.exists(TMPDIR):
            shutil.rmtree(TMPDIR)
        os.mkdir(TMPDIR)
        os.mkdir(os.path.join(TMPDIR, "healthy"))

    def parse_args(self, flags: List[str] = ["-v"]) -> argparse.Namespace:
        ap = stown.arg_parser()
        return ap.parse_args(flags + [TMPDIR, self.datadir])

    def tearDown(self):
        pass

    def assert_json_equal(self, checkme: str, expected: str):
        c = load_json(checkme)
        x = load_json(expected)
        self.assertEqual(c, x)

    def test_fail(self):
        self.assertEqual(stown.fail("dummy", -42), -42)

    def test_linkto_existing(self):
        self.assertEqual(stown.linkto(".", "/tmp"), 2)

    def test_linkto_existing_force(self):
        stown.args = self.parse_args(["-f"])
        t = random_tmp()
        with open(t, "wt") as f:
            print("dummy", file=f)
        self.assertEqual(stown.linkto(t, "expected.json"), 0)

    def test_maxdepth(self):
        stown.args = self.parse_args(["--depth", "0"])
        self.assertEqual(stown.stown("x", "y"), 3)

    def test_linkto_new(self):
        self.assertEqual(stown.linkto(random_tmp(), "expected.json"), 0)

    def test_parsed_fn1(self):
        self.assertEqual(stown.parsed_filename("dot-foo"), ".foo")

    def test_parsed_fn2(self):
        self.assertEqual(stown.parsed_filename("bar"), "bar")

    def test_same_file(self):
        self.assertEqual(stown.stown(".", "."), 4)

    def test_stown(self):
        self.assertEqual(stown.stown(stown.args.target, stown.args.source), 0)
        if not truthy(getenv("DISABLE_TREE")):
            subprocess.run(["tree", "-aJ", "-o", "tmp.json", stown.args.target])
            self.assert_json_equal("tmp.json", "expected.json")

    def test_unstow(self):
        stown.args = self.parse_args(["-a", "unstow"])
        self.assertEqual(stown.stown("x", "y"), 5)


if __name__ == "__main__":
    unittest.main()
