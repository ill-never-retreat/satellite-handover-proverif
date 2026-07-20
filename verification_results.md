# ProVerif 2.05 Verification Results

## 2026-07-15 expiration-semantics revalidation

The five current models were re-executed with the ProVerif 2.05 Windows binary after the candidate-specific residue and handover KDF were changed to bind the absolute bundle expiration $T_{\mathrm{exp}}$ rather than the gateway issuance timestamp. All five executions exited normally. The baseline, isolated-modulus, and serving-compromise models exercise two distinct target handovers, $S_1$ and $S_2$, under the same three-candidate token; $S_3$ remains unused redundancy. Real-time ranking, numerical expiration inequalities, and current/previous-modulus scheduling remain operational refinements outside the symbolic arithmetic abstraction.

## Execution date and tool

- Execution date: 2026-07-15
- Tool: ProVerif 2.05 official Windows binary
- Models: three replicated protocol models plus the phase-separated `CRT_post_session_link_key_exposure.pv` and `CRT_post_session_joint_exposure.pv` boundary experiments
- Complete outputs: corresponding `*.result.txt` files

## Result matrix

| Property / witness | Baseline | Isolated target-modulus exposure | Historical serving compromise |
|---|---:|---:|---:|
| Serving-session witness secret | true | true | false, as expected after serving-link-key disclosure |
| $S_1$ and $S_2$ target-session witnesses secret | both true | both true | both true |
| $S_1$ and $S_2$ protected payloads secret | both true | both true | both true |
| $S_1$ / $S_2$ residues secret | true / true | false / true, expected isolated $N_1$ exposure | true / true |
| $S_1$ / $S_2$ recovery tags secret | true / true | false / true, expected isolated $N_1$ exposure | true / true |
| Hidden bundle expiration secret | true | false, expected exposure | true |
| $N_1$ / $N_2$ secret | true / true | false / true, $N_1$ explicitly released | true / true |
| Injective initial-access correspondence | true | true | true |
| Non-injective handover correspondence | true | true | true |
| Injective handover correspondence | cannot be proved | cannot be proved | cannot be proved |
| Accepted handover corresponds to GW issuance | true | true | true |

## Conditional forward-secrecy boundary experiments

| Property / witness | Post-session target-link-key exposure | Post-session joint link-key/modulus exposure |
|---|---:|---:|
| Target link key released in phase 1 | yes | yes |
| Target modulus released in phase 1 | no | yes |
| Historical-key witness secret | true | false; explicit derivation found |
| Historical payload secret | true | false; explicit derivation found |
| Recovery tag secret | true | false |
| Hidden bundle expiration secret | true | false |
| Exposure event follows modeled session completion | true | true |

## Interpretation

The isolated-modulus model confirms the intended layered and target-specific consequence: releasing $N_1$ exposes the $S_1$ residue, recovery tag, and hidden expiration, but does not expose either target authentication key or protected payload while $K_{S_1-\mathrm{GW}}$ remains private. The $S_2$ residue and recovery tag remain non-derivable, showing that isolated exposure at one candidate does not propagate through the shared token. The serving-compromise model intentionally loses the serving-session witness but retains both fresh target-session and payload witnesses, supporting cross-satellite compromise containment rather than standard perfect forward secrecy.

ProVerif proves non-injective handover correspondence for the representative $S_1$ and $S_2$ handovers but cannot prove the stronger injective query under the table and mutex abstraction. Accordingly, the manuscript does not attribute replay-acceptance uniqueness to ProVerif alone. Target-specific private locks and the target-indexed monotonic table represent serialized fail-closed commitment, while the separate state-machine argument establishes uniqueness from atomic compare-and-insert, active-entry retention, and capacity-full rejection.

The phase-separated experiments continue to establish the symbolic split-exposure boundary for one completed historical target session. When only $K_{S_1-\mathrm{GW}}$ is released after completion, ProVerif still reports the historical-key witness, historical payload, recovery tag, bundle expiration, and $N_1$ as non-derivable. When $K_{S_1-\mathrm{GW}}$ and $N_1$ are both released, the trace reduces the recorded token with $N_1$, recovers the tag and expiration, reconstructs the historical KDF output, and decrypts both witnesses. This supports conditional forward secrecy under isolated post-session link-key exposure and simultaneously rules out a full-PFS claim under joint exposure.
