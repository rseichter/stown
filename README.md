stown
=====

"stown" manages file system object mapping via symlinks. It was inspired by
[GNU Stow](https://www.gnu.org/software/stow/), which I found very useful but too
unwieldly for my personal use. GNU Stow relies on a number of Perl modules and
can be a hassle to install on minimalistic systems. In contrast, stown only
requires Python 3.9 or newer, without additional modules.

If you are looking for a lightweight tool instead of a full-fledged symlink
farm manager, stown might be for you.

Full documentation is provided in [HTML](https://www.seichter.de/stown/) and
[PDF](https://www.seichter.de/stown/stown.pdf) format. Source code is
[available here](https://github.com/rseichter/stown).

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

That is of course just a brief teaser an not much to go by. The documentation website
provides detailed information about [how stown is
used](https://www.seichter.de/stown/#_usage) and [how it
operates](https://www.seichter.de/stown/#_strategy).
