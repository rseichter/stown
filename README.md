stown
=====

"stown" manages file system object mapping via symlinks. It was inspired by GNU
Stow, which I found very useful but too unwieldly for my personal use. GNU Stow
relies on a number of Perl modules and can be a hassle to install on
minimalistic systems. In contrast, stown requires only Python 3.9 or newer,
without any additional dependencies.

If you are looking for a lightweight tool instead of a full-fledged symlink
farm manager, stown might be for you.

Comprehensive [documentation](https://www.seichter.de/stown/) is provided in
HTML and [PDF](https://www.seichter.de/stown/stown.pdf) format.

Installing
----------

To install the [PyPI package](https://pypi.org/project/stown/), you can use
this shell command:

```bash
pip install stown
```

Example use case
----------------

If you store your dotfiles in a special repository, like many of us do, the
following simple statement can help you quickly set up a new user account with your
favourite settings:

```bash
stown $HOME /path/to/dotfiles
```

This brief teaser is obviously not much to go by. Please see the [full
documentation](https://www.seichter.de/stown/) for detailed information about
how stown is used and how it operates.
