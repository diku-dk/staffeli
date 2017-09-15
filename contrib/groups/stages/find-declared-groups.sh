#!/usr/bin/env bash
#
# Find all declared groups.  Used by 'groups.sh'.

set -euo pipefail

subs="$1"

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
for group in $(find "${subs}" -type f -iname "group.txt")
do
#  echo "${group}" # Good for debugging
  cat "${group}" | \
    tr -d '\r' | tr '\n' ' ' | \
    perl -pe 's/\s\s+/ /' | perl -pe 's/ $//' | \
    tr '[:upper:]' '[:lower:]'
  echo ""
done
IFS=$SAVEIFS
