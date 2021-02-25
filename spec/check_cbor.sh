#!/bin/bash
# Read stdin and verify it as valid CBOR against a CDDL schema.
set -e
SELFDIR=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))

COMBINED_CDDL=$1

cat | diag2cbor.rb | cddl "${COMBINED_CDDL}" validate -
