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
import json
import os
import shutil
import subprocess
import tempfile
import unittest
import uuid
from os import path
from typing import List

from stown.__main__ import arg_parser
from stown.core import Status
from stown.core import getenv
from stown.core import linkto
from stown.core import obtain_permit
from stown.core import parsed_filename
from stown.core import pathto
from stown.core import remove
from stown.core import stown
from stown.log import init_logging

DATADIR = "data"
TMPDIR = "tmp"
LJSON = "latest.json"
XJSON = "expected.json"


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

    def test_getenv_default(self):
        self.assertEqual(getenv(random_name(), XJSON), XJSON)

    def test_getenv_known_key(self):
        self.assertIsNotNone(getenv("LANG"))

    def test_permit_denied(self):
        p = obtain_permit(self.args, ".", DATADIR)
        self.assertTrue(p.is_denied())

    def test_permit_forced(self):
        rnd = random_tmp()
        with open(rnd, "wt") as f:
            print(file=f)
        a = self.parse_args(["--force"])
        p = obtain_permit(a, rnd, XJSON)
        self.assertTrue(p.is_forced())

    def test_permit_granted(self):
        p = obtain_permit(self.args, random_name(), XJSON)
        self.assertTrue(p.is_granted())

    def test_permit_identical_files(self):
        p = obtain_permit(self.args, XJSON, XJSON)
        self.assertTrue(p.is_denied())

    def test_linkto_existing(self):
        self.assertEqual(linkto(self.args, ".", DATADIR), Status.FORBIDDEN)

    def test_linkto_unsupported_action(self):
        a = self.parse_args(["-f"])
        a.action = "smile"
        t = random_tmp()
        os.symlink(XJSON, t)
        self.assertEqual(linkto(a, t, XJSON), Status.ACTION_UNKNOWN)

    def test_linkto_existing_force(self):
        rnd = random_tmp()
        with open(rnd, "wt") as f:
            print(file=f)
        a = self.parse_args(["--force"])
        ln = linkto(a, rnd, XJSON)
        self.assertTrue(ln.is_ok())

    def test_unlink_nonexistent(self):
        a = self.parse_args(["--action", "unlink"])
        ln = linkto(a, random_name(), XJSON)
        self.assertTrue(ln.is_ok())

    def test_linkto_existing_force_dry(self):
        a = self.parse_args(["-d", "-f"])
        ln = linkto(a, ".", XJSON)
        self.assertTrue(ln.is_ok())

    def test_maxdepth(self):
        a = self.parse_args(["--depth", "0"])
        self.assertEqual(stown(a, "x", ["y"]), Status.CRUSH_DEPTH)

    def test_stown_unexpected(self):
        b = random_tmp()
        with open(b, "wt") as f:
            print(file=f)
        c = random_tmp()
        with open(c, "wt") as f:
            print(file=f)
        self.assertEqual(stown(self.args, b, [c]), Status.UNEXPECTED_PAIR)

    def test_stown_link(self):
        a = self.args
        b = random_tmp()
        c = path.join(DATADIR, "salt")
        os.symlink(c, b)
        self.assertEqual(stown(a, b, [c]), Status.FORBIDDEN)

    def test_linkto_new(self):
        ln = linkto(self.args, random_tmp(), XJSON)
        self.assertTrue(ln.is_ok())

    def test_linkto_new_dry(self):
        a = self.parse_args(["-d"])
        ln = linkto(a, random_tmp(), XJSON)
        self.assertTrue(ln.is_ok())

    def test_parsed_fn(self):
        n = random_name(prefix="")
        self.assertEqual(parsed_filename(f"dot-{n}"), f".{n}")

    def test_parsed_fn_ignore_dot(self):
        n = random_name(prefix="dot-")
        self.assertEqual(parsed_filename(n, ignore_dot_prefix=True), n)

    def test_parsed_fn_nodot(self):
        n = random_name(prefix="nodot-")
        self.assertEqual(parsed_filename(n), n)

    def test_pathto(self):
        ap = pathto(XJSON, want_abspath=True)
        self.assertTrue(path.isabs(ap))

    def test_same_file(self):
        st = stown(self.args, ".", ["."])
        self.assertEqual(st, Status.IDENTICAL)

    def test_remove(self):
        self.assertFalse(remove(XJSON, dry_run=True))

    def test_stown(self):
        st = stown(self.args, self.args.target, self.args.source)
        self.assertTrue(st.is_ok())
        tmp = random_tmp(tempfile.gettempdir(), ".json")
        subprocess.run(["tree", "-aJ", "-o", tmp, self.args.target])
        self.maxDiff = None
        shutil.move(tmp, LJSON)
        self.assert_json_equal(LJSON, XJSON)

    def test_missing_source(self):
        st = stown(self.args, self.args.target, [random_name()])
        self.assertTrue(st.is_ok())

    def test_unlink(self):
        a = self.parse_args(["-a", "unlink", "-f"])
        t = random_tmp()
        os.symlink(XJSON, t)
        st = stown(a, t, [XJSON])
        self.assertTrue(st.is_ok())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
