# vim: ft=make ts=4 sw=4 noet
# Copyright © 2025 Ralph Seichter

define usage

Available 'make' targets are:

all …………………… Build everything.
build ……………… Build distribution artifacts.
clean ……………… Cleanup workspace.
cov …………………… Coverage analysis.
docs ………………… Generate documentation.
fla …………………… Run flake8 checks.
fmt …………………… Format source code.
help ………………… Display this text.
mrproper ……… Thoroughly cleanup workspace.
pdocs ……………… Publish documentation.
pypi ………………… Upload artifacts to PyPI.
setver …………… Set version number.
shc …………………… Shell script care.
test ………………… Run unit tests.

endef

pyenv	:= PYTHONPATH=.:src
ver		?=

.PHONY:	all build clean cov dbranch docs fla fmt help mrproper pdocs pypi setver shc stamp tagclean test

help:
	$(info $(usage))
	@exit 0

find_ := find . -regextype posix-extended
clean:
	$(find_) '(' -name dist -o -regex '.*\.(bak|log|tmp)' ')' -print0 | xargs -0r rm -rv

mrproper:	clean
	$(find_) '(' -name 'tmp*' -o -regex '.*/(egg-info|__pycache__)' ')' -print0 | xargs -0r rm -rv

setver:
	@if [[ -z "$(ver)" ]]; then echo Usage: make $@ ver="{semantic-version}"; exit 1; fi
	sed -i '' -E 's/^(version =).*/\1 "$(ver)"/i' pyproject.toml src/stown/*.py
	sed -i '' -E 's/^(:revnumber:).*/\1 $(ver)/' docs/stown.adoc

docs:
	$(pyenv) python >usage.tmp -m stown -h
	catto -r docs/usage.txt usage.tmp
	make -C docs

pdocs:	docs
	scripts/publish.sh docs

fmt:
	isort src tests
	# pre-commit run -a
	black -l 120 src tests

fla:	fmt
	flake8 . --config=.flake8

rev ?= $(shell git rev-parse --short HEAD)
stamp:
	sed -E -i '' 's/^(COMMIT_SHA =).+/\1 "$(rev)"/' src/stown/*.py

build:	stamp fmt mrproper
	python -m build

all:	build docs

cov:	fmt
	$(pyenv) coverage run -m unittest discover -s tests -v
	coverage html
	coverage report -m

test:
	$(pyenv) python >/dev/null -m unittest discover -s tests -v -f

pypi:
	twine check dist/*
	twine upload dist/*

shc:
	shcare scripts/*

dbranch:
	@if [[ -z "$(b)" ]]; then echo Usage: make $@ b="{git-branch}"; exit 1; fi
	git remote | while read -r r; do git push -d "$$r" "$$b"; done
	git branch -d "$$b"

tagclean:
	@if [[ -z "$(repo)" ]]; then echo Usage: make $@ repo="{git-remote-repository}"; exit 1; fi
	git ls-remote $(repo) --tags '0.*' | awk -F /tags/ '{print $$2}' | \
		xargs -r git push -d $(repo)
