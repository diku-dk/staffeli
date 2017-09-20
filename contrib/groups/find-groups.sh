#!/usr/bin/env bash
#
# Find all groups.  For individual submissions, print single-person groups.
# Returns a newline-separated list of space-separated group members.

set -euo pipefail

filter_nonempty_dirs() {
    while read dir; do
        if [ "$(ls "$dir")" ]; then
            echo "$dir"
        fi
    done
}

subs="$1"

declared=$("$(dirname "$0")"/stages/find-declared-groups.sh "${subs}" | sort)

undeclared=$(comm -1 -3 \
  <(echo -n "${declared}" | tr ' ' '\n' | sort) \
  <(cd "${subs}"; find . -maxdepth 1 -type d | filter_nonempty_dirs \
        | sed -r 's/^\.\///' \
        | grep -E '^[a-z]{3}[0-9]{3}_[0-9]*$' \
        | sort | cut -d '_' -f 1)  | \
    tr -d '\t')

{
    echo "${declared}"
    echo "${undeclared}"
} | sort
