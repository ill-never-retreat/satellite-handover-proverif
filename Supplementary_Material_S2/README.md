# Supplementary Material S2: software and numerical evaluation
Title: Proactive Key Distribution for 0-RTT Handover Authentication in 6G Integrated Satellite-Terrestrial Networks

## Reproduction
Recorded data are in recorded_results/. All measurements use Windows 11, Intel Core i9-12900H and Python 3.12.14. Arithmetic and endpoint timings use cryptography 50.0.1. Gateway preparation was measured separately using the specified authenticated encoding and cryptography 50.0.2; its environment and nine raw batch means per configuration are in gateway_prepare_refresh.json. Only gateway_prepare entries in results.json refer to that separate cohort; platform describes the retained arithmetic/endpoint results and gateway_prepare_measurement describes preparation. This is not a before/after experiment attributing timing differences to encoding alone.
To reproduce the specified preparation workload and functional checks, install: python -m pip install cryptography==50.0.2
Run: python refresh_gateway_prepare.py
Then: python validate_protocol.py
To rerun every benchmark and the synthetic study rather than only preparation, run python evaluate.py and then python validate_protocol.py. For the recorded arithmetic/endpoint measurement environment, use cryptography==50.0.1. Results should be interpreted using the environment actually reported by each run.
New data are written to reproduced_results/, not over the recorded data. To check the recorded results without rerunning timings, run: python validate_protocol.py --recorded
No real credentials, satellite traces, private keys or deployment data are included.

## Methods
Sixteen microbenchmark rows cover tag widths 128/80 bits and m=2,3,4,5,6,8,10,16; moduli have tag width + 32 bits. Timers report nine batch means, their median and range. Modular reduction uses 20,000 iterations/batch, uncached CRT construction 300, gateway preparation 100 and endpoint crypto 1,000. Fixed representative valid operands are used within a timing series, not an arithmetic worst-case search. Random secrets/seeds/IVs are freshly sampled; reproduction is methodological, not bit-identical, and timing changes with machine load.

The 72 synthetic cells each contain 20,000 episodes. Candidate availability a is 0.3/0.6/0.9, and independent packet loss p is 0/0.05/0.10. Four-hop preparation retries after a first failed hop. Each hop uses 10 ms propagation and 1 Mbit/s serialization. The timeout is 50 ms; a successful protected return opportunity adds 20 ms. A lost handover or return opportunity consumes the candidate. Exhaustion incurs online initial-access/bundle preparation, assuming a reachable gateway and subsequent reliable confirmation. No finite bound is claimed without this availability assumption.
Control bits count transmissions across both hops, exclude application payload and return traffic, and include unsuccessful preparation attempts. A 256-byte service payload contributes to handover serialization delay, not control-bit totals. Microbenchmarked computation is reported separately, not inserted into the synthetic timing study.

## Checks and boundaries
functional_checks.json records:
- CRT residue round trip and valid decryption;
- rejection of modified ciphertext/MAC;
- identity substitution by a valid credential holder who recomputes the MAC;
- a deliberately vulnerable identity-unbound control;
- key-role/target separation and principal cost accounting;
- satellite-downlink MAC input N_R || CT_Sj || M_R independently reconstructed for both profiles and all eight pool sizes, with valid satellite decryption and router-bundle consistency;
- rejection of modified nonce, satellite ciphertext, router ciphertext/tag, final tag, role label, and a tag computed with the alternative N_R || M_R || CT_Sj order;
- 23-state/51-transition finite replay-state exploration, with non-atomic and lost-on-reboot negative controls;
- exact equal-tail binomial tests of analytic fallback probability [1-a(1-p)^2]^m over 72 cells, with Bonferroni familywise 0.05 threshold.
A normal approximation is unsuitable when expected fallback counts are very small; the exact tests are used instead. Failure to reject a formula is a consistency check, not proof of the simulator or real deployment calibration.

This is not flight-hardware testing, an orbital/link-budget/Doppler simulation, a standards-stack implementation, a physical-erasure experiment, or a complete cryptographic/timed-protocol proof. Neither recovery-tag width nor modulus width is a standalone measure of session-key security.
