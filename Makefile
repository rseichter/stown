# vim: ft=make ts=4 sw=4 noet
# Copyright © 2025 Ralph Seichter

define usage

Available 'make' targets are:

build   Build distribution artifacts.
clean   Cleanup workspace.
cov     Coverage analysis.
help    Display this text.
pypi    Upload distribution artifacts to PyPI.
setver  Set version (v=$(v)).
shc     Shell script care.
test    Run unit tests.

endef

pyenv	?= PYTHONPATH=.:src
v		?= 0.3.dev1

.PHONY:	build clean cov fmt help pypi setver shc test

help:
	$(info $(usage))
	@exit 0

clean:
	rm -fr dist
	find . -type d -name __pycache__ -or -name '*.bak' -or -name '*.egg-info' | xargs -r rm -r

setver:
	sed -i '' -E 's/^(version) =.*/\1 = "$(v)"/i' pyproject.toml src/stown/stown.py

fmt:
	black -l 120 src tests

build:	fmt
	python -m build

cov:
	$(pyenv) coverage run -m unittest discover -s tests
	coverage html
	coverage report -m

test:
	$(pyenv) python -m unittest discover -s tests

pypi:
	twine check dist/*
	twine upload dist/*

shc:
	shcare *.sh
