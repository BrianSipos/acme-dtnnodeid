#!/bin/bash
# Read stdin and verify it as valid CBOR against a CDDL schema.
set -e
SELFDIR=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))

COMBINED_CDDL=$1

TMPFILE=$(mktemp)
cat | diag2cbor.rb >${TMPFILE}
cddl validate --cddl "${COMBINED_CDDL}" --cbor ${TMPFILE}
rm ${TMPFILE}
