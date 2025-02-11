# vim: ft=make ts=4 sw=4 noet
# Copyright © 2025 Ralph Seichter

define usage

Available 'make' targets are:

build   Build distribution artifacts.
clean   Cleanup workspace.
help    Display this text.
pypi    Upload distribution artifacts to PyPI.
setver  Set version (v=$(v)).
shc     Shell script care.

endef

v ?= 0.0.$(shell date +%s)

.PHONY:	build clean fmt help pypi setver shc

help:
	$(info $(usage))
	@exit 0

clean:
	rm -fr dist
	find . -name '*.bak' -delete

setver:
	sed -i '' -E 's/^(version|__version__) =.*/\1 = "$(v)"/' pyproject.toml src/stown/__init__.py

fmt:
	black src

build:	fmt
	python -m build

pypi:
	twine check dist/*
	twine upload dist/*

shc:
	shcare *.sh
