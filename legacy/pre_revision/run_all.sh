#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"
PROVERIF="${PROVERIF:-proverif}"

for model in \
  CRT_baseline.pv \
  CRT_modulus_exposure.pv \
  CRT_serving_compromise.pv \
  CRT_post_session_link_key_exposure.pv \
  CRT_post_session_joint_exposure.pv
do
  output="${model%.pv}.rerun.result.txt"
  "$PROVERIF" "$model" 2>&1 | tee "$output"
done
