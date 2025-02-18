#!/usr/bin/env bash
# vim: ft=bash ts=4 sw=4 noet
# Copyright © 2025 Ralph Seichter
#
# Prepare development session. Source this file in your shell.

alias fla="make fla"
alias fmt="make fmt"
alias mc="make cov"
alias md="make docs"
alias mp="make pdocs"
alias mt="make test"
alias stown="python -m stown"

export PYTHONPATH=.:src
export STOWN_LOGLEVEL=INFO

say() {
	echo >&2 "$@"
}

venv_activate() {
	local act dir
	for dir in .venv ~/.venv; do
		act="$dir"/bin/activate
		say Checking "$act"
		if [[ -r $act ]]; then
			echo "$act"
			return 0
		fi
	done
	return 1
}

cd "$(dirname "$0")"/.. || return
