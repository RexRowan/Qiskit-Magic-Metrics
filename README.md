# Qiskit Magic Metrics

Exact, stabilizer-accelerated resource and entanglement metrics for Qiskit circuits, exposed as
composable `PassManager` passes.

Qiskit Magic Metrics computes quantities that describe *how nonclassical* a quantum state is —
how much multipartite entanglement it carries, and how much "magic" (nonstabilizerness) it
contains — directly from a `QuantumCircuit`, `Statevector`, or `Clifford`/stabilizer tableau. It
targets algorithm designers and researchers characterizing ansätze, error-correcting code states,
and NISQ circuit outputs.

**Status: early scaffold.** Interfaces below are the design target; see [ROADMAP.md](ROADMAP.md)
for what's implemented today.

## Why this exists

`qiskit.quantum_info` ships von Neumann entropy, `entanglement_of_formation` (restricted to
2-qubit states), and `mutual_information` (bipartite only) — it has no multipartite entanglement
measures and no magic/nonstabilizerness measures at all. Existing third-party tools fill *part*
of this gap but not this way:

- [Qurrium/Qurry](https://pypi.org/project/qurrium/) measures Rényi entropy and magic-adjacent
  quantities via **randomized measurement protocols on real or simulated hardware** — it's built
  for experiment execution and job orchestration, not for exact, in-process statevector/tableau
  analysis during circuit design.
- [qLEET](https://github.com/QLemma/qleet) implements expressibility and Meyer-Wallach entangling
  capability, but appears unmaintained (no `PassManager` integration, last active years ago) and
  doesn't cover magic measures at all.

Qiskit Magic Metrics is scoped narrowly and deliberately around what neither covers:

1. **Exact computation**, not hardware-sampled estimation — you get the same answer every time
   for a given circuit, no shot noise, no backend required.
2. **Stabilizer fast paths** — for Clifford circuits, metrics that would naively require
   exponential Pauli enumeration or full statevector construction are instead computed directly
   from the stabilizer tableau in polynomial time.
3. **`PassManager`-native** — every metric is an `AnalysisPass` that writes into `property_set`,
   so it composes into existing transpilation/analysis pipelines instead of living in a
   standalone notebook function.
4. **A formally verified core** — at least one nontrivial closed-form identity underlying these
   metrics is proved in Lean 4 and cross-checked against the Python implementation, following the
   same pattern as [qiskit-zx-verified](https://github.com/RexRowan/qiskit-zx-verified) and
   [qiskit-lean-bridge](https://github.com/RexRowan/qiskit-lean-bridge).

Explicitly **out of scope**: expressibility/loss-landscape/training-trajectory tooling (qLEET's
territory) and randomized-measurement hardware execution (Qurrium's territory). If those get
built, they belong in a separate package or as contributions upstream, not bolted on here.

## Planned metrics

| Metric | Class | Exact method | Stabilizer fast path |
|---|---|---|---|
| Stabilizer Rényi entropy (magic) | `StabilizerRenyiEntropy` | Pauli-expectation sampling, `P_2α(ψ) = (1/d) Σ_P ⟨ψ|P|ψ⟩^{2α}` | Zero by construction for stabilizer states; tableau-derived, no enumeration |
| Meyer-Wallach measure | `MeyerWallachMeasure` | `Q(ψ) = 2(1 - (1/n) Σ tr(ρ_k²))` from single-qubit RDMs | Purities read directly from the stabilizer tableau |
| Multipartite entanglement entropy | `EntanglementEntropy` | Von Neumann entropy across a user-specified bipartition | Rank/purity shortcuts for stabilizer states |

## Installation

```bash
pip install qiskit-magic-metrics
```

(Not yet published — this is a local scaffold. See [CONTRIBUTING.md](CONTRIBUTING.md).)

## Quick start (target API)

```python
from qiskit import QuantumCircuit
from qiskit_magic_metrics import StabilizerRenyiEntropy, MeyerWallachMeasure

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)  # GHZ state — a stabilizer state, so magic should be exactly zero

magic = StabilizerRenyiEntropy(alpha=2)
print(magic.compute(qc))  # 0.0, via the stabilizer fast path

mw = MeyerWallachMeasure()
print(mw.compute(qc))  # 1.0 for GHZ
```

As `AnalysisPass`es inside a `PassManager`:

```python
from qiskit.transpiler import PassManager
from qiskit_magic_metrics import StabilizerRenyiEntropy, MeyerWallachMeasure

pm = PassManager([StabilizerRenyiEntropy(alpha=2), MeyerWallachMeasure()])
pm.run(qc)
print(pm.property_set["stabilizer_renyi_entropy"])
print(pm.property_set["meyer_wallach_measure"])
```

## The Lean-verified core

`lean/` contains a Lean 4 formalization of one closed-form identity underlying these metrics
(target: the reduction of the Meyer-Wallach measure to average single-qubit purity, checked
against the stabilizer-tableau shortcut for the Bell/GHZ/graph-state family). See
[lean/README.md](qiskit_magic_metrics/lean/README.md) for status and how the cross-check bridge
works.

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — pass design, `ResourceMetric` base class, property_set keys
- [ROADMAP.md](ROADMAP.md) — what's built vs. planned
- [PRIOR_ART.md](docs/PRIOR_ART.md) — full writeup of the Qurrium/qLEET/`qiskit.quantum_info` landscape and where this package sits relative to each
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CHANGELOG.md](CHANGELOG.md)

## License

Apache License 2.0 — see [LICENSE](LICENSE).
