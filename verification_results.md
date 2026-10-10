# Recorded verification and evaluation results

## S1: ProVerif 2.05

The following index is derived from the supplied recorded outputs; no new verifier run is implied by this index.

| Model | Exit code | RESULT lines | True | Expected false | Not proved |
|---|---:|---:|---:|---:|---:|
| CRT_baseline.pv | 0 | 17 | 16 | 0 | 1 |
| CRT_candidates_m2.pv | 0 | 4 | 4 | 0 | 0 |
| CRT_candidates_m3.pv | 0 | 5 | 5 | 0 | 0 |
| CRT_candidates_m4.pv | 0 | 6 | 6 | 0 | 0 |
| CRT_candidates_m5.pv | 0 | 7 | 7 | 0 | 0 |
| CRT_modulus_exposure.pv | 0 | 17 | 12 | 4 | 1 |
| CRT_non_target_joint_exposure.pv | 0 | 9 | 6 | 3 | 0 |
| CRT_serving_compromise.pv | 0 | 17 | 15 | 1 | 1 |

False queries occur in deliberate disclosure models and identify the exposed branch/context. Full access models do not prove injective handover correspondence in the replicated table abstraction. Non-injective correspondence and the separate numeric replay-state argument must not be conflated. No forward-secrecy guarantee is claimed. See S1's README and complete outputs for the exact queries.

## S2: software and synthetic evidence

- 16 microbenchmark configurations: two residue profiles, eight candidate-pool sizes.
- 72 synthetic availability/loss cells, with 20,000 episodes per cell.
- 22 selected functional/state/consistency checks are recorded as passing; they do not prove arbitrary parser safety or a complete cryptographic/timed protocol.
- Principal three-candidate profile: 872 activation-control bits, 5264 preparation bits and 112.804 microseconds median software gateway preparation.
- Arithmetic/endpoint timings use cryptography 50.0.1; gateway-preparation timings use 50.0.2 as a separate measurement cohort.
- Recorded data are unchanged. New reproduction outputs are written separately. There is no flight-hardware or calibrated constellation evaluation.
