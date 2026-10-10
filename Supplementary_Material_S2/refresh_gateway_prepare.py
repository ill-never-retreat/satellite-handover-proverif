"""Remeasure only the corrected gateway preparation workload.

Recorded results remain read-only. Updated gateway rows and a composed result
file are written to reproduced_results/. No synthetic episodes or unaffected
microbenchmark components are rerun by this script.
"""
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import cryptography
import evaluate as e

def cpu_name():
    if sys.platform == "win32":
        cmd = ["powershell.exe", "-NoProfile", "-Command",
               "(Get-CimInstance Win32_Processor).Name"]
        return subprocess.check_output(cmd, text=True).strip()
    return platform.processor() or "not available"

def main():
    baseline = e.ROOT / "recorded_results/results.json"
    original_bytes = baseline.read_bytes()
    result = json.loads(original_bytes)
    rows = []
    e.RNG.seed(20260924)
    for tagbits in (128, 80):
        for m in (2, 3, 4, 5, 6, 8, 10, 16):
            ns = e.moduli(tagbits + 32, m)
            ltks = [os.urandom(16) for _ in ns]
            kr, ks = os.urandom(16), os.urandom(16)
            measured = e.timing(lambda: e.prepare(ns, tagbits, ltks, kr, ks), 100)
            row = {"tag_bits": tagbits, "m": m, "gateway_prepare": measured}
            rows.append(row)
            existing = next(x for x in result["benchmark"]
                            if x["tag_bits"] == tagbits and x["m"] == m)
            existing["gateway_prepare"] = measured
            print(json.dumps(row), flush=True)
    environment = {
        "python": sys.version, "os": platform.platform(),
        "machine": platform.machine(), "cpu": cpu_name(),
        "cryptography": cryptography.__version__, "clock": "perf_counter_ns",
        "batches": 9, "loops_per_batch": 100, "warmup_calls": 20,
        "measured_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "authenticated_input": "PREFIX || satellite-down || N_R || CT_Sj || CT_R || tag_R",
        "limitations": "desktop batch throughput, not flight hardware or network latency"
    }
    refresh = {"platform": environment, "benchmark": rows,
               "baseline_results_sha256": hashlib.sha256(original_bytes).hexdigest().upper(),
               "script_sha256": hashlib.sha256((e.ROOT / "evaluate.py").read_bytes()).hexdigest().upper(),
               "preserved": ["mod", "crt", "router_packet", "target_accept_crypto",
                             "state", "assertions", "simulation", "simulation_assumptions"],
               "interpretation": "Gateway preparation is a separate corrected-encoding measurement cohort. Differences from earlier timings cannot be attributed to encoding alone."}
    result["gateway_prepare_measurement"] = environment
    result["measurement_scope"] = "Only gateway_prepare entries use the separate gateway_prepare_measurement platform. Other benchmark components and synthetic data retain the original platform and results."
    (e.OUT / "gateway_prepare_refresh.json").write_text(json.dumps(refresh, indent=2), encoding="utf-8")
    (e.OUT / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    assert baseline.read_bytes() == original_bytes
    print(json.dumps({"gateway_rows": len(rows), "other_components_rerun": False,
                      "simulation_rerun": False, "platform": environment}), flush=True)

if __name__ == "__main__":
    main()
