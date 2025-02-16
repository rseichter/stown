# vim: ft=make ts=4 sw=4 noet
# Copyright © 2025 Ralph Seichter

define usage

Available 'make' targets are:

all       Build everything.
build     Build distribution artifacts.
bumpver   Bump version number.
clean     Cleanup workspace.
cov       Coverage analysis.
docs      Generate documentation.
fla       Run flake8 checks.
help      Display this text.
mrproper  Cleanup workspace, thoroughly.
pdocs     Publish documentation.
pypi      Upload distribution artifacts to PyPI.
setver    Set version number.
shc       Shell script care.
test      Run unit tests.

endef

pyenv	:= PYTHONPATH=.:src
ver		?=

.PHONY:	all build bumpver clean cov docs fla fmt help mrproper pdocs pypi setver shc test

help:
	$(info $(usage))
	@exit 0

find_ := find . -regextype posix-extended
clean:
	$(find_) '(' -name dist -o -regex '.*\.(bak|log|tmp)' ')' -print0 | xargs -0r rm -rv

mrproper:	clean
	$(find_) '(' -name 'tmp*' -o -regex '.*/(egg-info|__pycache__)' ')' -print0 | xargs -0r rm -rv

bumpver:
	make setver ver="$(ver)-dev$(shell date '+%s')"

setver:
	@if [[ -z "$(ver)" ]]; then echo Usage: make $@ ver="{semantic-version}"; exit 1; fi
	sed -i '' -E 's/^(version =).*/\1 "$(ver)"/i' pyproject.toml src/stown/__main__.py
	sed -i '' -E 's/^(:revnumber:).*/\1 $(ver)/' docs/stown.adoc

docs:
	$(pyenv) python >usage.tmp -m stown -h
	catto -r docs/usage.txt usage.tmp
	make -C docs

pdocs:	docs
	scripts/publish.sh docs

fmt:
	black -l 120 src tests

fla:	fmt
	flake8 . --config=.flake8

build:	fmt mrproper
	python -m build

all:	build docs

cov:	fla
	$(pyenv) coverage >/dev/null run -m unittest discover -s tests -v
	coverage html
	coverage report -m

test:
	$(pyenv) python >/dev/null -m unittest discover -s tests

pypi:
	twine check dist/*
	twine upload dist/*

shc:
	shcare scripts/*
