from __future__ import annotations

from itertools import combinations

from core.hypergraph_core import (
    SUB_NODES,
    enumerate_reachable,
    compute_delta,
    normalise,
    stats,
)


def is_connected_seed(seed):
    nodes = set()
    for edge in seed:
        nodes.update(edge)

    start = next(iter(nodes))
    seen = {start}
    changed = True

    while changed:
        changed = False
        for edge in seed:
            if seen & set(edge):
                before = len(seen)
                seen.update(edge)
                changed = changed or len(seen) > before

    return seen == nodes


def main():
    two_edges = [frozenset(e) for e in combinations(sorted(SUB_NODES), 2)]

    rows = []

    for e1, e2 in combinations(two_edges, 2):
        seed = frozenset({e1, e2})

        visited_free, depths_free, abort_free = enumerate_reachable(seed, include_rc=False)
        visited_gated, depths_gated, abort_gated = enumerate_reachable(seed, include_rc=True)

        if abort_free or abort_gated:
            status = "aborted"
            mean_ai_delta = None
        else:
            delta = compute_delta(visited_free, visited_gated)
            global_max = max(max(depths_free.values()), max(depths_gated.values()))
            norm_gated = normalise(depths_gated, global_max)
            norm_delta = [norm_gated[k] for k in delta]
            mean_ai_delta = stats(norm_delta)[0] if norm_delta else None
            status = "connected" if is_connected_seed(seed) else "disconnected"

        rows.append({
            "seed": seed,
            "status": status,
            "reach_free": len(visited_free),
            "reach_gated": len(visited_gated),
            "delta": len(visited_gated) - len(visited_free),
            "mean_ai_delta": mean_ai_delta,
        })

    print("Seed sweep over all 15 two-edge seeds for |SUB| = 4")
    print("=" * 72)
    print(f"{'Seed':28s} {'Status':13s} {'Free':>5s} {'Gated':>6s} {'Delta':>6s} {'Mean AI Δ':>10s}")

    for row in rows:
        seed_str = "{" + ",".join(
            "{" + ",".join(map(str, sorted(e))) + "}"
            for e in sorted(row["seed"], key=lambda x: sorted(x))
            ) + "}"
        mean_str = "—" if row["mean_ai_delta"] is None else f"{row['mean_ai_delta']:.3f}"
        print(
            f"{seed_str:28s} "
            f"{row['status']:13s} "
            f"{row['reach_free']:5d} "
            f"{row['reach_gated']:6d} "
            f"{row['delta']:6d} "
            f"{mean_str:>10s}"
        )


if __name__ == "__main__":
    main()
