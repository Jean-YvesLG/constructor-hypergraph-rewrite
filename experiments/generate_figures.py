
import sys
from pathlib import Path
import matplotlib.pyplot as plt
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = PROJECT_ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT_ROOT))


from core.hypergraph_core import (
    enumerate_reachable,
    compute_delta,
    normalise,
    depth_counter,
)

# Initial seed
S0 = frozenset({frozenset({3, 4}), frozenset({3, 5})})

# Run both regimes
visited_free, depths_free, _ = enumerate_reachable(S0, include_rc=False)
visited_gated, depths_gated, _ = enumerate_reachable(S0, include_rc=True)

delta = compute_delta(visited_free, visited_gated)

# Global max depth
global_max = max(max(depths_free.values()), max(depths_gated.values()))

norm_free = normalise(depths_free, global_max)
norm_gated = normalise(depths_gated, global_max)
norm_delta = [norm_gated[k] for k in delta]

# -----------------------------
# Figure 1: Reachability counts
# -----------------------------
plt.figure()

labels = [
    r"$\left|\mathrm{Reach}_{\mathrm{free}}\right|$",
    r"$\left|\mathrm{Reach}_{\mathrm{gated}}\right|$",
    r"$\left|\Delta\right|$",
]

values = [len(visited_free), len(visited_gated), len(delta)]

bars = plt.bar(labels, values)

plt.ylim(0, max(values) * 1.15)

for bar, value in zip(bars, values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + max(values) * 0.02,
        str(value),
        ha="center",
        va="bottom",
        fontsize=10,
    )

    
plt.title("Reachable configuration counts", fontsize=14)
plt.ylabel("Count of configurations containing motif", fontsize=12)

plt.tight_layout()
plt.savefig(FIG_DIR / "figure1_reachability_counts_1.png", dpi=300)
plt.close()

# -----------------------------
# Figure 2: AI distribution
# -----------------------------
plt.figure()

plt.hist(norm_free.values(), bins=12, alpha=0.7, label="Free")
plt.hist(norm_delta, bins=12, alpha=0.7, label="Δ")

plt.title("Assembly index distribution across reachable configurations")
plt.xlabel("Normalized Assembly Index")
plt.ylabel("Frequency")
plt.legend()

plt.tight_layout()
plt.savefig(FIG_DIR / "figure2_ai_distribution.png", dpi=300)
plt.close()

# -----------------------------
# Figure 3: Δ dominance
# -----------------------------
plt.figure()

labels = ["Baseline", "Δ"]
values = [len(visited_free), len(delta)]

plt.bar(labels, values)
plt.title("Composition of the constructor-gated reachable space")
plt.ylabel("Number of configurations")

plt.tight_layout()
plt.savefig(FIG_DIR / "figure3_delta_dominance_1.png", dpi=300)
plt.close()

# -----------------------------
# Figure 4: Depth-conditioned motif persistence
# -----------------------------

def has_target_motif(cfg):
    return frozenset({3, 4, 6}) in cfg

depth_counts = {}

for key, depth in depths_gated.items():
    cfg = visited_gated[key]
    if has_target_motif(cfg):
        depth_counts[depth] = depth_counts.get(depth, 0) + 1

depths = sorted(depth_counts.keys())
counts = [depth_counts[d] for d in depths]


plt.figure()
plt.plot(depths, counts, marker='o')

plt.title("Depth-conditioned motif persistence")
plt.xlabel("Depth")
plt.ylabel("Number of configurations containing motif")

plt.tight_layout()
plt.savefig(FIG_DIR / "figure4_depth_conditioned_reuse.png", dpi=300)
plt.close()

print("Figures generated successfully.")
