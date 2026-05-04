
"""
hypergraph_core.py

Shared deterministic core for the AT/CT hypergraph model.

This module factors the typed-edge deterministic semantics out of the
paper-facing scripts so both the static and stochastic layers consume a
single source of truth.

Key properties preserved from simulation_final.py:
- typed constructor/substrate separation
- canonicalization over active substrate nodes only
- β determinism via v = min(hyperedge - {w})
- δ canonical split via sorted sliding window [0:3], [1:4]
- R_c gating by non-empty intersection with constructor neighbourhood
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from itertools import permutations
from typing import FrozenSet, Iterable, Optional

# =====================================================
# CONSTANTS
# =====================================================

Hyperedge = FrozenSet[int]
Config = FrozenSet[Hyperedge]

ALL_NODES: FrozenSet[int] = frozenset(range(7))
C_CORE_NODES: FrozenSet[int] = frozenset({0, 1, 2, 3})
SUB_NODES: FrozenSet[int] = frozenset({3, 4, 5, 6})
MAX_RANK = 4
ABORT_LIMIT = 500
INTERFACE_NODE = 3

C_EDGES: Config = frozenset({
    frozenset({0, 1, 2}),
    frozenset({0, 2}),
    frozenset({2, 3}),
})

S0: Config = frozenset({
    frozenset({3, 4}),
    frozenset({3, 5}),
})

_CANON_CACHE: dict[Config, str] = {}


# =====================================================
# BASIC UTILITIES
# =====================================================

def active_sub_nodes(s_edges: Config) -> FrozenSet[int]:
    nodes: set[int] = set()
    for edge in s_edges:
        nodes.update(edge)
    return frozenset(nodes & SUB_NODES)


def inactive_sub_nodes(s_edges: Config) -> FrozenSet[int]:
    return SUB_NODES - active_sub_nodes(s_edges)


def validate_s_edges(s_edges: Config) -> None:
    for edge in s_edges:
        assert 2 <= len(edge) <= MAX_RANK, f"Rank violation: {sorted(edge)}"
        assert edge.issubset(SUB_NODES), (
            f"S-edge contains non-substrate node: {sorted(edge)}"
        )


def canonical(s_edges: Config) -> str:
    """
    Canonicalize by permuting active substrate nodes only.

    This follows simulation_final.py exactly, including the fact that the
    interface node 3 is *not* held fixed if it is among the active substrate
    nodes.
    """
    if s_edges in _CANON_CACHE:
        return _CANON_CACHE[s_edges]

    active = sorted(active_sub_nodes(s_edges))
    n = len(active)

    if n == 0:
        _CANON_CACHE[s_edges] = "empty"
        return "empty"

    best: Optional[str] = None
    for perm in permutations(range(n)):
        mapping = {active[i]: perm[i] for i in range(n)}
        mapped = frozenset(
            frozenset(mapping[nd] for nd in edge)
            for edge in s_edges
        )
        rep = str(sorted(sorted(list(e)) for e in mapped))
        if best is None or rep < best:
            best = rep

    assert best is not None
    _CANON_CACHE[s_edges] = best
    return best


def clear_canonical_cache() -> None:
    _CANON_CACHE.clear()


def c_neighbourhood_sub(s_edges: Config) -> FrozenSet[int]:
    """
    Substrate nodes within graph distance 1 of interface node 3.
    """
    nbhd = {INTERFACE_NODE}
    for edge in s_edges:
        if INTERFACE_NODE in edge:
            nbhd.update(edge & SUB_NODES)
    return frozenset(nbhd)


# =====================================================
# EXACT SUCCESSOR GENERATORS
# =====================================================

def alpha_successors(s_edges: Config) -> list[tuple[tuple[str, tuple[int, int], int], Config]]:
    inactive = inactive_sub_nodes(s_edges)
    if not inactive:
        return []

    results: list[tuple[tuple[str, tuple[int, int], int], Config]] = []
    for edge in [e for e in s_edges if len(e) == 2]:
        u, v = sorted(edge)
        for w in sorted(inactive):
            new_s = (s_edges - {edge}) | {edge | frozenset({w})}
            validate_s_edges(new_s)
            results.append((("alpha", (u, v), w), new_s))
    return results


def beta_successors(s_edges: Config) -> list[tuple[tuple[str, tuple[int, ...], tuple[int, int], int, int, int], Config]]:
    results = []
    threes = [e for e in s_edges if len(e) == 3]
    twos = [e for e in s_edges if len(e) == 2]

    for hedge in threes:
        hn = set(hedge)
        for tedge in twos:
            shared = hn & set(tedge)
            if len(shared) != 1:
                continue
            w = next(iter(shared))
            x = next(iter(set(tedge) - {w}))
            if x in hn:
                continue
            v = min(hn - {w})  # exact deterministic choice from simulation_final.py
            new_edge = frozenset({w, x, v})
            if new_edge in s_edges:
                continue
            if not new_edge.issubset(SUB_NODES):
                continue
            new_s = s_edges | {new_edge}
            validate_s_edges(new_s)
            results.append((("beta", tuple(sorted(hedge)), tuple(sorted(tedge)), w, x, v), new_s))
    return results


def gamma_successors(
    s_edges: Config,
    neighbourhood: Optional[FrozenSet[int]] = None,
) -> list[tuple[tuple[str, tuple[int, ...], tuple[int, ...]], Config]]:
    results = []
    threes = [e for e in s_edges if len(e) == 3]
    for i in range(len(threes)):
        for j in range(i + 1, len(threes)):
            e1, e2 = threes[i], threes[j]
            if len(e1 & e2) != 2:
                continue
            merged = e1 | e2
            if len(merged) != 4:
                continue
            if neighbourhood is not None and not (merged & neighbourhood):
                continue
            if not merged.issubset(SUB_NODES):
                continue
            new_s = (s_edges - {e1, e2}) | {merged}
            validate_s_edges(new_s)
            results.append((("gamma", tuple(sorted(e1)), tuple(sorted(e2))), new_s))
    return results


def delta_successors(
    s_edges: Config,
    neighbourhood: Optional[FrozenSet[int]] = None,
) -> list[tuple[tuple[str, tuple[int, ...]], Config]]:
    results = []
    fours = [e for e in s_edges if len(e) == 4]
    for fedge in fours:
        if neighbourhood is not None and not (fedge & neighbourhood):
            continue
        nodes = sorted(fedge)
        t1 = frozenset(nodes[0:3])
        t2 = frozenset(nodes[1:4])
        if t1 == t2:
            continue
        new_s = (s_edges - {fedge}) | {t1, t2}
        validate_s_edges(new_s)
        results.append((("delta", tuple(nodes)), new_s))
    return results


def epsilon_successors(
    s_edges: Config,
    neighbourhood: Optional[FrozenSet[int]] = None,
) -> list[tuple[tuple[str, tuple[int, ...], tuple[int, ...], int, int], Config]]:
    results = []
    threes = [e for e in s_edges if len(e) == 3]
    for i in range(len(threes)):
        for j in range(i + 1, len(threes)):
            e1, e2 = threes[i], threes[j]
            shared = e1 & e2
            if len(shared) != 2:
                continue
            u_set = e1 - shared
            x_set = e2 - shared
            if len(u_set) != 1 or len(x_set) != 1:
                continue
            u = next(iter(u_set))
            x = next(iter(x_set))
            new_edge = frozenset({u, x})
            if new_edge in s_edges:
                continue
            if not new_edge.issubset(SUB_NODES):
                continue
            match_nodes = e1 | e2
            if neighbourhood is not None and not (match_nodes & neighbourhood):
                continue
            new_s = s_edges | {new_edge}
            validate_s_edges(new_s)
            results.append((("epsilon", tuple(sorted(e1)), tuple(sorted(e2)), u, x), new_s))
    return results


# Thin compatibility wrappers matching simulation_final.py semantics.
def apply_alpha(s_edges: Config) -> list[Config]:
    return [succ for _, succ in alpha_successors(s_edges)]


def apply_beta(s_edges: Config) -> list[Config]:
    return [succ for _, succ in beta_successors(s_edges)]


def apply_gamma(s_edges: Config, neighbourhood: Optional[FrozenSet[int]] = None) -> list[Config]:
    return [succ for _, succ in gamma_successors(s_edges, neighbourhood)]


def apply_delta(s_edges: Config, neighbourhood: Optional[FrozenSet[int]] = None) -> list[Config]:
    return [succ for _, succ in delta_successors(s_edges, neighbourhood)]


def apply_epsilon(s_edges: Config, neighbourhood: Optional[FrozenSet[int]] = None) -> list[Config]:
    return [succ for _, succ in epsilon_successors(s_edges, neighbourhood)]


def apply_all_rules(s_edges: Config, include_rc: bool = False) -> list[Config]:
    results = apply_alpha(s_edges) + apply_beta(s_edges)
    if include_rc:
        nbhd = c_neighbourhood_sub(s_edges)
        results += apply_gamma(s_edges, nbhd)
        results += apply_delta(s_edges, nbhd)
        results += apply_epsilon(s_edges, nbhd)
    return results


def enumerate_reachable(
    s0: Config,
    include_rc: bool = False,
    abort_limit: int = ABORT_LIMIT,
) -> tuple[dict[str, Config], dict[str, int], bool]:
    clear_canonical_cache()
    c0 = canonical(s0)
    visited = {c0: s0}
    depths = {c0: 0}
    queue = deque([s0])

    while queue:
        s_edges = queue.popleft()
        c_current = canonical(s_edges)

        if len(visited) >= abort_limit:
            return visited, depths, True

        for succ in apply_all_rules(s_edges, include_rc=include_rc):
            c_succ = canonical(succ)
            if c_succ not in visited:
                visited[c_succ] = succ
                depths[c_succ] = depths[c_current] + 1
                queue.append(succ)

    return visited, depths, False


# =====================================================
# ANALYSIS HELPERS
# =====================================================

def compute_delta(visited_1: dict[str, Config], visited_2: dict[str, Config]) -> dict[str, Config]:
    return {k: v for k, v in visited_2.items() if k not in visited_1}


def normalise(depths: dict[str, int], global_max: int) -> dict[str, float]:
    if global_max == 0:
        return {k: 0.0 for k in depths}
    return {k: v / global_max for k, v in depths.items()}


def stats(values: Iterable[float]) -> tuple[float, float, float]:
    vals = sorted(values)
    if not vals:
        return 0.0, 0.0, 0.0
    mean = sum(vals) / len(vals)
    mid = len(vals) // 2
    median = vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2
    return mean, median, vals[-1]


def count_selfrep_pattern(config: Config) -> int:
    """
    Count 3-edge + 2-edge patterns sharing two nodes.
    """
    threes = [e for e in config if len(e) == 3]
    twos = [e for e in config if len(e) == 2]
    count = 0
    for h in threes:
        for t in twos:
            if len(h & t) == 2:
                count += 1
    return count


def has_selfrep_pattern(config: Config) -> bool:
    return count_selfrep_pattern(config) > 0


def depth_counter(depths: dict[str, int]) -> Counter:
    return Counter(depths.values())


def static_summary() -> dict[str, object]:
    visited_1, depths_1, abort_1 = enumerate_reachable(S0, include_rc=False)
    visited_2, depths_2, abort_2 = enumerate_reachable(S0, include_rc=True)
    if abort_1 or abort_2:
        raise RuntimeError("Enumeration aborted unexpectedly.")
    delta = compute_delta(visited_1, visited_2)
    global_max = max(max(depths_1.values()), max(depths_2.values()))
    norm_1 = normalise(depths_1, global_max)
    norm_2 = normalise(depths_2, global_max)
    norm_delta = {k: norm_2[k] for k in delta}
    repro_in_delta = {k: cfg for k, cfg in delta.items() if has_selfrep_pattern(cfg)}

    return {
        "visited_1": visited_1,
        "depths_1": depths_1,
        "visited_2": visited_2,
        "depths_2": depths_2,
        "delta": delta,
        "global_max": global_max,
        "mean_norm_free": stats(norm_1.values())[0],
        "mean_norm_delta": stats(norm_delta.values())[0],
        "repro_in_delta": repro_in_delta,
    }
