#!/usr/bin/env bash
# vim: ft=bash ts=4 sw=4 noet
# Copyright © 2025 Ralph Seichter
#
# Prepare work environment. Source this file in your shell.

alias fmt="make fmt"
alias mc="make cov"
alias mt="make test"
alias stown="python -m stown"

export PYTHONPATH=.:src

if [[ -d ./.venv ]]; then
	# shellcheck disable=1091
	. ./.venv
else
	. ~/.venv/bin/activate
fi
