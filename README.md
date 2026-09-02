# Qiskit Magic Metrics

Exact, stabilizer-accelerated resource and entanglement metrics for Qiskit circuits, exposed as
composable `PassManager` passes.

Qiskit Magic Metrics computes quantities that describe *how nonclassical* a quantum state is —
how much multipartite entanglement it carries, and how much "magic" (nonstabilizerness) it
contains — directly from a `QuantumCircuit`, `Statevector`, or `Clifford`/stabilizer tableau. It
targets algorithm designers and researchers characterizing ansätze, error-correcting code states,
and NISQ circuit outputs.

**Status: v0.1 — core metrics implemented.** All three metrics below are implemented and
tested (23 passing tests), each with both a general (statevector) path and a stabilizer fast
path. See [ROADMAP.md](ROADMAP.md) for what's next (Lean-verified core, docs site, Ecosystem
submission) and [CHANGELOG.md](CHANGELOG.md) for what shipped in this pass.

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

## Metrics

| Metric | Class | Exact method | Stabilizer fast path |
|---|---|---|---|
| Stabilizer Rényi entropy (magic) | `StabilizerRenyiEntropy` | Pauli-expectation sampling, `P_2α(ψ) = (1/d) Σ_P ⟨ψ|P|ψ⟩^{2α}` | Zero by construction for stabilizer states; O(1), no enumeration |
| Meyer-Wallach measure | `MeyerWallachMeasure` | `Q(ψ) = 2(1 - (1/n) Σ tr(ρ_k²))` from single-qubit RDMs | GF(2) null-space test on the stabilizer tableau, per qubit |
| Multipartite entanglement entropy | `EntanglementEntropy` | Von Neumann entropy across a user-specified bipartition | Fattal et al. GF(2) rank formula |

## Installation

```bash
pip install qiskit-magic-metrics
```

(Not yet published to PyPI — clone and `pip install -e .` for now. See
[CONTRIBUTING.md](CONTRIBUTING.md).)

## Quick start

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

**Not started** (v0.2, see [ROADMAP.md](ROADMAP.md)). `lean/` will contain a Lean 4
formalization of the GF(2) null-space claim underlying `MeyerWallachMeasure`'s stabilizer fast
path — this package's own derivation, not a result copied from elsewhere, so it's the one worth
independently verifying first. See
[lean/README.md](qiskit_magic_metrics/lean/README.md) for the current target and how the
cross-check bridge will work.

## Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — pass design, `ResourceMetric` base class, property_set keys
- [ROADMAP.md](ROADMAP.md) — what's built vs. planned
- [PRIOR_ART.md](docs/PRIOR_ART.md) — full writeup of the Qurrium/qLEET/`qiskit.quantum_info` landscape and where this package sits relative to each
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CHANGELOG.md](CHANGELOG.md)

## License

Apache License 2.0 — see [LICENSE](LICENSE).
