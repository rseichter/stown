#!/usr/bin/env bash
# vim: ft=bash ts=4 sw=4 noet
# Copyright © 2025 Ralph Seichter
#
# Publish documentation.

set -euo pipefail
# shellcheck disable=2155
declare -r BN=$(basename "$0")
declare -r TMPDIR=${TMPDIR:-/tmp}

mktemp() {
	command mktemp -p "$TMPDIR" "${BN/.sh/.$(whoami)}".XXXXXXXX
}

dryrun=0
trap "builtin unset dryrun" EXIT

die() {
	echo >&2 "$BN:" "$@"
	exit 1
}

usage() {
	cat >&2 <<USAGE

Usage: $BN [option ...] [--] {docs} [argument ...]

Supported options:

-d | --dry-run  Dry run only.
-h | --help     Show this text.

USAGE
	exit 1
}

docs() {
	local sync=(
		rsync
		--delete
		--include '*.html'
		--include '*.pdf'
		-prvz
		-e ssh "$site" "$host:$hostdir/"
	)
	echo "${sync[@]}"
	[[ dryrun -eq 1 ]] || "${sync[@]}"
}

main() {
	while [[ $# -ge 1 ]] && [[ $1 == -* ]]; do
		case $1 in
		-d | --dry-run)
			# shellcheck disable=2034
			dryrun=1
			shift
			;;
		--)
			# Abort option processing
			shift
			break
			;;
		*)
			usage
			;;
		esac
	done

	[[ $# -ge 1 ]] || usage
	local verb=$1
	shift
	case $verb in
	docs)
		"$verb" "$@"
		;;
	*)
		usage
		;;
	esac
}

main "$@"
