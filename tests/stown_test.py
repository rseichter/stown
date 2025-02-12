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

import os
import shutil
import stown.__main__ as stown
import subprocess
import unittest


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

    def test_stow(self):
        self.assertEqual(stown.stown(stown.args.target, stown.args.source), 0)
        subprocess.run(["tree", "-aJ", "-o", "tree.json", stown.args.target])

    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())

    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)


if __name__ == "__main__":
    unittest.main()
