stown
=====

Copyright © 2025 Ralph Seichter. Licensed under
[GPLv3+](https://github.com/rseichter/stown/blob/master/LICENSE).

Stow file system objects by creating links. "stown" was inspired by [GNU
Stow](https://www.gnu.org/software/stow/), which I found very useful but too
unwieldly for my personal use. GNU Stow relies on a number of Perl modules and
can be a hassle to install on minimalistic systems. In contrast, stown only
requires Python 3.9 or newer, without additional modules.

Installing
----------

To install the [PyPI package](https://pypi.org/project/stown/), you can use
this shell command:

```bash
pip install stown
```

Usage
-----

The following example simulates linking the contents of a dotfile repository to
a user's home directory. `--dry-run` causes the necessary steps to be printed
only; no changes will be made.

```bash
stown --dry-run $HOME /path/to/dotfiles
# "stown --help" shows syntax
```

Note that the prefix `dot-` is converted to a dot character in resulting links,
for example a link `$HOME/.vimrc` pointing to `/path/to/dotfiles/dot-vimrc`.
