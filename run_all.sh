#!/usr/bin/env sh
set -eu

exec "${PYTHON:-python3}" "$(dirname "$0")/Supplementary_Material_S1/run_models.py" --proverif "${PROVERIF:-proverif}"
