# Constructor-Gated Reachability and Assembly Complexity in Hypergraph Rewrite Systems — Reference Implementation

## Overview

This repository contains the deterministic reference implementation for the model described in:

> *Constructor-Defined Possibility Boundaries in Hypergraph Rewrite Systems*

The implementation provides an exact, finite realization of a typed hypergraph rewrite system in which a constructor gates a subset of rewrite rules, inducing a sharp reachability boundary Δ.

---

## Model Summary

The system consists of:

* A finite substrate node set (|SUB| = 4 in reported results)
* Substrate hyperedges (S-edges) of rank 2–4
* Typed constructor edges (C-edges), which are inert and excluded from rule matching

### Rewrite Rules

* **Free rules**:
  α (activation), β (propagation)

* **Constructor-gated rules**:
  γ (merge), δ (split), ε (loop closing)

Gated rules apply only within the constructor’s substrate-side neighbourhood.

---

## What This Code Reproduces

Running the deterministic simulation reproduces the main results reported in the paper:

* |Reach_free| = 3
* |Reach_gated| = 106
* Δ = 103
* Elevated mean normalized Assembly Index (AI) in the gated-only region

The repository also includes a complete evaluation over all 15 two-edge seeds for |SUB| = 4, confirming that:

* connected seeds exhibit constructor-gated reachability expansion
* disconnected seeds yield trivial dynamics

---

## Repository Structure

core/

* rules.py — implementation of α–ε
* hypergraph.py — data structures
* bfs.py — reachability enumeration
* canonicalization.py — isomorphism handling

experiments/

* run_deterministic.py — reproduces main results
* seed_sweep.py — evaluates all two-edge seeds

outputs/

* (generated result files)

---

## Installation

Python 3.10+ recommended.

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

### Reproduce main results

```bash
python experiments/run_deterministic.py
```

This computes:

* reachable configuration counts
* reachability boundary Δ
* Assembly Index statistics

---

### Evaluate seed dependence

```bash
python experiments/seed_sweep.py
```

This evaluates all 15 two-edge seeds over |SUB| = 4 and reports:

* reachability sizes
* Δ per seed
* qualitative classification (connected vs disconnected)

---

## Key Concepts

### Reachability Boundary (Δ)

Δ is the set of configurations reachable only when constructor-gated rules are enabled.

---

### Assembly Index (AI)

Defined as the shortest-path depth from the initial configuration in the BFS reachability graph.

This is a model-internal measure and does not correspond to chemical assembly metrics.

---

### Canonicalization

Configurations are canonicalized under isomorphism over active substrate nodes to ensure unique counting.

---

## Reproducibility

All results reported in the associated paper are:

* deterministic
* exactly enumerable
* reproducible from this implementation

Implementation details are described in the Supplementary Material of the paper.

---

## Scope Notes

* The system is finite and non-stochastic
* Causal invariance is not evaluated
* Results depend on structurally productive initial conditions (connected seeds)

---

## License

This code is released under the MIT License for reproducibility and research use.

---

## Citation

If you use this code, please cite:

*Constructor-Defined Possibility Boundaries in Hypergraph Rewrite Systems*

---

## Related Work

For ongoing extensions of this model, including stochastic dynamics and scaling behaviour, see the companion research repository (to be provided).
