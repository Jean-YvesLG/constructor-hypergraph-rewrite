
"""
simulation_final_refactored.py

Refactored deterministic entry point that delegates to hypergraph_core.py.
This preserves the exact static semantics while making the deterministic core
importable by other scripts.
"""

from __future__ import annotations

from core.hypergraph_core import (
    S0,
    static_summary,
    depth_counter,
    count_selfrep_pattern,
)

def main() -> None:
    summary = static_summary()
    visited_1 = summary["visited_1"]
    depths_1 = summary["depths_1"]
    visited_2 = summary["visited_2"]
    depths_2 = summary["depths_2"]
    delta = summary["delta"]
    repro_in_delta = summary["repro_in_delta"]

    print("AT_CT_Hypergraph — Refactored Deterministic Simulation")
    print("=" * 60)
    print(f"S0 = {[sorted(e) for e in S0]}")
    print()
    print("Run 1 (R_free only)")
    print(f"  |Reach| = {len(visited_1)}")
    print(f"  max depth = {max(depths_1.values())}")
    print(f"  depth distribution = {dict(sorted(depth_counter(depths_1).items()))}")
    print()
    print("Run 2 (R_free + R_c)")
    print(f"  |Reach| = {len(visited_2)}")
    print(f"  max depth = {max(depths_2.values())}")
    print(f"  depth distribution = {dict(sorted(depth_counter(depths_2).items()))}")
    print()
    print("Δ and Assembly Index Summary")
    print(f"  |Δ| = {len(delta)}")
    print(f"  mean normalized AI — R_free = {summary['mean_norm_free']:.4f}")
    print(f"  mean normalized AI — Δ      = {summary['mean_norm_delta']:.4f}")
    print(f"  asymmetry                   = {summary['mean_norm_delta'] - summary['mean_norm_free']:+.4f}")
    print(f"  repro-pattern configs in Δ  = {len(repro_in_delta)}")
    print()
    print("Acceptance checks")
    print(f"  Δ non-empty                : {'PASS' if len(delta) >= 1 else 'FAIL'}")
    print(f"  mean(Δ) > mean(R_free)     : {'PASS' if summary['mean_norm_delta'] > summary['mean_norm_free'] else 'FAIL'}")
    print(f"  repro-pattern exists in Δ  : {'PASS' if len(repro_in_delta) >= 1 else 'FAIL'}")

if __name__ == "__main__":
    main()
