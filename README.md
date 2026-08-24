# Supplementary Material S1: ProVerif Models and Results

Version: 1.0.1

This package accompanies the manuscript **“An Efficient Scheme for 0-RTT Handover Authentication and Key Distribution in 6G Integrated Satellite-Terrestrial Networks.”** It contains five independent ProVerif models and the complete outputs used to support the formal-verification claims in the manuscript.

## Requirements

- ProVerif 2.05
- No additional libraries or model includes

Official ProVerif releases and documentation are available at <https://bblanche.gitlabpages.inria.fr/proverif/>.

## Files

- `CRT_baseline.pv`: baseline three-candidate execution with two exercised targets.
- `CRT_modulus_exposure.pv`: isolated disclosure of one target modulus while the corresponding target link key remains protected.
- `CRT_serving_compromise.pv`: historical serving-satellite link-key disclosure while fresh target link keys remain protected.
- `CRT_post_session_link_key_exposure.pv`: phase-separated post-session disclosure of the selected target link key while its modulus remains protected.
- `CRT_post_session_joint_exposure.pv`: negative boundary experiment that discloses both the selected target link key and target modulus after session completion.
- `*.result.txt`: complete ProVerif 2.05 outputs for the corresponding model.
- `verification_results.md`: consolidated result matrix and interpretation.
- `SHA256SUMS.txt`: SHA-256 hashes of the frozen package files.
- `run_all.ps1` and `run_all.sh`: convenience scripts that write fresh outputs as `*.rerun.result.txt`.
- `CITATION.cff`: citation metadata for the archived software package.

## Running the models

With `proverif` on the executable path:

```text
proverif CRT_baseline.pv
proverif CRT_modulus_exposure.pv
proverif CRT_serving_compromise.pv
proverif CRT_post_session_link_key_exposure.pv
proverif CRT_post_session_joint_exposure.pv
```

The PowerShell helper accepts an explicit executable path:

```text
.\run_all.ps1 -ProVerifExecutable C:\path\to\proverif.exe
```

## Expected result boundaries

Several negative or non-proved results are intentional and should not be read as unexpected execution failures:

- In the isolated-modulus model, the disclosed modulus exposes its matching residue, recovery tag, and hidden expiration, but not the target authentication key while the target link key remains protected.
- In the serving-compromise model, the historical serving-session witness is exposed by construction, while fresh target-session witnesses remain secret.
- In the joint post-session exposure model, the historical key and protected payload become derivable after both the target link key and modulus are released; this is the stated boundary of conditional forward secrecy.
- The three full protocol models establish non-injective handover correspondence, but ProVerif does not prove the injective handover query under the table abstraction. Replay-acceptance uniqueness is established separately by the target-local atomic state-machine argument in the manuscript.

## Scope of the symbolic abstraction

The models do not verify numerical CRT arithmetic, operand bit lengths, real-time inequalities, orbital target ranking, implementation-level secure erasure, or the atomic uniqueness of the replay cache. The two post-session exposure models are focused phase-separated boundary experiments rather than complete reimplementations of the full protocol flow.

## Verification status

All five models were re-executed with the official Windows ProVerif 2.05 binary. Every process exited normally, and all `RESULT` lines matched the archived outputs. See `verification_results.md` for the complete interpretation.
