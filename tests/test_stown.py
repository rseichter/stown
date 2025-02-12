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

import json
import os
import shutil
import stown.__main__ as stown
import subprocess
import unittest


def getenv(key, default=None):
    if key in os.environ:
        return os.environ[key]
    return default


def truthy(x) -> bool:
    return x or x == 1 or x == "true" or x == "yes"


def load_json(path):
    with open(path, "rt") as f:
        return json.load(f)


class TestStown(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.dirname(__file__))
        self.datadir = "data"
        self.tmpdir = "tmp"
        ap = stown.arg_parser()
        stown.args = ap.parse_args([self.tmpdir, self.datadir])
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)
        os.mkdir(self.tmpdir)
        os.mkdir(os.path.join(self.tmpdir, "healthy"))

    def tearDown(self):
        pass

    def assert_json_equal(self, checkme: str, expected: str):
        c = load_json(checkme)
        x = load_json(expected)
        self.assertEqual(c, x)

    def test_stow(self):
        self.assertEqual(stown.stown(stown.args.target, stown.args.source), 0)
        if not truthy(getenv("DISABLE_TREE")):
            subprocess.run(["tree", "-aJ", "-o", "tmp.json", stown.args.target])
            self.assert_json_equal("tmp.json", "expected.json")


if __name__ == "__main__":
    unittest.main()
