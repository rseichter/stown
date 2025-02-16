#!/usr/bin/env bash
# vim: ft=bash ts=4 sw=4 noet
# Copyright © 2025 Ralph Seichter
#
# Publish documentation.

set -euo pipefail
# shellcheck disable=2155
declare -r BN=$(basename "$0")

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
	local cmd=(
		rsync
		--delete
		-prvz
		-e ssh docs/*.{html,pdf} www.seichter.de:/var/www/stown/
	)
	echo "${cmd[@]}"
	[[ dryrun -eq 1 ]] || "${cmd[@]}"
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
