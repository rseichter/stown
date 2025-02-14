# vim: ft=make ts=4 sw=4 noet
# Copyright © 2025 Ralph Seichter

define usage

Available 'make' targets are:

build     Build distribution artifacts.
bumpver   Bump version number.
clean     Cleanup workspace.
cov       Coverage analysis.
fla       Run flake8 checks.
help      Display this text.
mrproper  Cleanup workspace, thoroughly.
pypi      Upload distribution artifacts to PyPI.
setver    Set version number.
shc       Shell script care.
test      Run unit tests.

endef

pyenv	:= PYTHONPATH=.:src
ver		?=

.PHONY:	build bumpver clean cov fla fmt help mrproper pypi setver shc test

help:
	$(info $(usage))
	@exit 0

clean:
	rm -fr dist

mrproper:	clean
	find . -type d -name __pycache__ -or -name '*.bak' -or -name '*.egg-info' | xargs -r rm -r

bumpver:
	make setver ver="$(ver)-dev$(shell date '+%s')"

setver:
	@if [[ -z "$(ver)" ]]; then echo Usage: make $@ ver="{semantic-version}"; exit 1; fi
	sed -i '' -E 's/^(version) =.*/\1 = "$(ver)"/i' pyproject.toml src/stown/__main__.py

fmt:
	black -l 120 src tests

fla:	fmt
	flake8 . --config=.flake8

build:	fmt clean
	python -m build

cov:	fla
	$(pyenv) coverage run -m unittest discover -s tests -v
	coverage html
	coverage report -m

test:
	$(pyenv) python -m unittest discover -s tests -v

pypi:
	twine check dist/*
	twine upload dist/*

shc:
	find . -name '*.sh' | xargs -r shcare
