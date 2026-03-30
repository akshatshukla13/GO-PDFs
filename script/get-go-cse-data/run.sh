#!/bin/bash
set -e

# Download all GATE CSE related HTML and PDF files into the data/ folder.
# The download commands are assembled in customize.py and stored in MLC_RUN_CMD.

echo "Downloading GATE CSE files to: ${MLC_GO_CSE_DATA_PATH}"
echo ""

if [[ ${MLC_FAKE_RUN} != "yes" ]]; then
  eval "${MLC_RUN_CMD}"
fi

echo ""
echo "Done. Files saved to: ${MLC_GO_CSE_DATA_PATH}"

exit 0
