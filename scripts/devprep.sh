#!/usr/bin/env bash
# vim: ft=bash ts=4 sw=4 noet
# Copyright © 2025 Ralph Seichter
#
# Prepare development session. Source this file in your shell.

export PYTHONPATH=.:src
export STOWN_LOGLEVEL=INFO

alias fla="make fla"
alias fmt="make fmt"
alias mc="make cov"
alias md="make docs"
alias mp="make pdocs"
alias mt="make test"
alias stown="python -m stown"

cd "$(dirname "$0")"/.. || true
