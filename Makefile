# vim: ft=make ts=4 sw=4 noet
# Copyright © 2025 Ralph Seichter

define usage

Available 'make' targets are:

build   Build distribution artifacts.
clean   Cleanup workspace.
cov     Coverage analysis.
help    Display this text.
pypi    Upload distribution artifacts to PyPI.
setver  Set version number.
shc     Shell script care.
test    Run unit tests.

endef

pyenv	:= PYTHONPATH=.:src
ver		?=

.PHONY:	build clean cov fmt help pypi setver shc test

help:
	$(info $(usage))
	@exit 0

clean:
	rm -fr dist
	find . -type d -name __pycache__ -or -name '*.bak' -or -name '*.egg-info' | xargs -r rm -r

setver:
	@if [[ -z "$(ver)" ]]; then echo Usage: make $@ ver="{semantic-version}"; exit 1; fi
	sed -i '' -E 's/^(version) =.*/\1 = "$(ver)"/i' pyproject.toml src/stown/stown.py

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
