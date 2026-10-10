# Supplementary Material S1: executable symbolic models
Title: Proactive Key Distribution for 0-RTT Handover Authentication in 6G Integrated Satellite-Terrestrial Networks

## Contents and reproduction
Eight ProVerif 2.05 models are in models/. Complete recorded verifier output is in recorded_results/.
Install ProVerif 2.05 from https://bblanche.gitlabpages.inria.fr/proverif/ .
Run one model using: proverif models/CRT_baseline.pv
Run the corpus with Python 3: python run_models.py --proverif /path/to/proverif
The runner writes new results to reproduced_results/, leaving the recorded results unchanged.

## Model-to-claim mapping
- CRT_baseline.pv: full access/distribution with two exercised targets in a three-candidate bundle. Payload/key secrecy, injective initial access, non-injective handover begin/issue correspondence.
- CRT_modulus_exposure.pv: matching residue/tag/expiration are deliberately exposed; unexposed link-key-derived sessions remain symbolically protected.
- CRT_serving_compromise.pv: serving branch is deliberately lost; target branches remain protected.
- CRT_candidates_m2.pv through CRT_candidates_m5.pv: trusted prepared bundles; all candidate targets are exercised. These are finite representative models, not an arbitrary-m proof.
- CRT_non_target_joint_exposure.pv: first branch secrecy and unqualified correspondence deliberately fail; branches 2 and 3 retain secrecy and their target-scoped begin/issue correspondences.

## Key schedule and events
Encryption and MAC receive enc_key(master) and mac_key(master), not the same symbolic key. Candidate derivation includes link key, recovery tag, expiration, router identity and target identity. The gateway independently samples the serving-session master.
In full models, BegAccess/EndAccess bind router, serving satellite and nonce; GWIssue binds router, target, token and session key; BegHandover/EndHandover additionally bind ciphertext. Prepared-bundle models use Issue/Begin/End analogously.
Symbolic role/tuple typing is not a byte-exact parser or HKDF implementation.

## Limits and interpretation
The replicated injective handover query remains "cannot be proved"; it is not reported as verified. Concrete clock arithmetic, atomic locking, capacity, crash persistence and erasure are outside these models. CRT is an ideal constructor/destructor rather than integer arithmetic, and no result establishes concrete CRT residue confidentiality or lattice hardness. No forward-secrecy guarantee is claimed. See manuscript Section 5.4 and Appendix A, plus S2's finite numeric state checks.
False secrecy queries in deliberate disclosure models are expected boundary demonstrations, not a claim that every query succeeds.
