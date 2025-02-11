# vim: ft=make ts=4 sw=4 noet
# Copyright © 2025 Ralph Seichter

v ?= 0.0.$(shell date +%s)

define usage

Available 'make' targets are:

clean   Cleanup workspace.
help    Display this text.
setver  Set version (v=$(v)).
shc     Shell script care.

endef

.PHONY:	clean help setver shc

help:
	$(info $(usage))
	@exit 0

clean:
	rm -fr dist
	find . -name '*.bak' -delete

setver:
	sed -i '' -E 's/^(version|__version__) =.*/\1 = "$(v)"/' pyproject.toml src/stown/__init__.py

shc:
	shcare *.sh
