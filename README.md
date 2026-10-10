# Proactive Key Distribution for 0-RTT Handover Authentication

Companion reproducibility materials for **Proactive Key Distribution for 0-RTT Handover Authentication in 6G Integrated Satellite-Terrestrial Networks**.

## Current materials

- [Supplementary Material S1](Supplementary_Material_S1/README.md): eight ProVerif 2.05 models, complete recorded outputs, model-to-claim mapping and a reproduction runner.
- [Supplementary Material S2](Supplementary_Material_S2/README.md): cryptographic software benchmarks, a synthetic availability/loss study, raw batch timings and selected implementation/state checks.
- [Verification results](verification_results.md): an index to the recorded results and their interpretation.
- `SHA256SUMS.txt`: checksums of the repository files, excluding the checksum file itself and generated reproduction outputs.

## Reproduction

Install ProVerif 2.05 from its [official distribution](https://bblanche.gitlabpages.inria.fr/proverif/), and use Python 3.

```text
python Supplementary_Material_S1/run_models.py --proverif /path/to/proverif
```

For S2, follow its README for the two measurement environments (`cryptography` 50.0.1 and 50.0.2). The recorded arithmetic/endpoint and gateway-preparation cohorts must not be treated as a controlled before/after speed comparison. Reproduction writes into each supplement's `reproduced_results/`, leaving recorded measurements unchanged.

```text
python -m pip install cryptography==50.0.2
python Supplementary_Material_S2/refresh_gateway_prepare.py
python Supplementary_Material_S2/validate_protocol.py
```

The root `run_all.ps1` and `run_all.sh` helpers invoke the current S1 corpus. Their defaults require both Python and ProVerif on the executable path.

## Interpretation

0-RTT refers to successful target authentication and key activation from one router-to-target message **after candidate preparation**. It does not mean zero propagation time, explicit router-observed confirmation, or completion of radio procedures in zero time.

The artifacts support the stated fresh-target secrecy/authentication and target-local replay results at their respective abstraction levels. Injective handover correspondence is not proved by the full symbolic table models. Deliberate disclosure models include expected failed secrecy/correspondence queries. No forward-secrecy guarantee is claimed. S2 is desktop software and synthetic numerical evidence, not flight-hardware, over-the-air or calibrated constellation testing.

## Historical archive

The [v1.0.1 release](https://github.com/ill-never-retreat/satellite-handover-proverif/releases/tag/v1.0.1) remains available. `legacy/pre_revision/` preserves the repository files at commit `54ec22a03d7c9316811164517a0cb39dfb1f49f5`; those files are historical artifacts, not the current corpus. Use the two supplement directories above for the materials accompanying the current manuscript.

## License and citation

The repository retains its MIT license. See `CITATION.cff` for the software citation metadata. No manuscript, reviewer report, response letter or private deployment credential is included.
