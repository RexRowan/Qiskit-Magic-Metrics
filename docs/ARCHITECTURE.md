# Architecture

## `ResourceMetric` base class

Every metric implements a common interface so it can be used standalone or wired into a
`PassManager`:

```python
class ResourceMetric:
    """Base class for an exact resource/entanglement metric.

    Subclasses implement `_compute_statevector` (general path) and, where a closed form
    exists, `_compute_stabilizer` (fast path for Clifford circuits). `compute()` dispatches
    between them automatically by checking whether the input is/reduces to a Clifford circuit.
    """

    property_set_key: str  # e.g. "stabilizer_renyi_entropy"

    def compute(self, circuit_or_state) -> float:
        ...

    def _compute_stabilizer(self, clifford) -> float:
        raise NotImplementedError  # not every metric has a fast path

    def _compute_statevector(self, statevector) -> float:
        raise NotImplementedError
```

Each concrete metric (`StabilizerRenyiEntropy`, `MeyerWallachMeasure`, `EntanglementEntropy`)
subclasses this and additionally subclasses Qiskit's `AnalysisPass`, so:

```python
class StabilizerRenyiEntropy(ResourceMetric, AnalysisPass):
    def run(self, dag):
        circuit = dag_to_circuit(dag)
        self.property_set[self.property_set_key] = self.compute(circuit)
```

## Stabilizer detection and the fast path

Dispatch logic (in `_dispatch.py`):

1. If the input is already a `Clifford` object, or a `QuantumCircuit` composed entirely of gates
   in Qiskit's Clifford gate set (checked via `Clifford.from_circuit`, which raises on
   non-Clifford gates), use the stabilizer fast path.
2. Otherwise fall back to full statevector simulation. This is exact but exponential in qubit
   count — fine for the small-to-medium circuits this package targets (ansatz design,
   error-correcting code state characterization), not intended for large-scale simulation.
3. A future extension point (not in v0.1/v0.2 scope): a "mostly-Clifford" path using stabilizer
   rank decomposition for circuits with a small number of non-Clifford (e.g. T) gates. Tracked
   as a roadmap idea, not a commitment.

## `property_set` keys

| Pass | Key | Type |
|---|---|---|
| `StabilizerRenyiEntropy` | `stabilizer_renyi_entropy` | `float` |
| `MeyerWallachMeasure` | `meyer_wallach_measure` | `float` |
| `EntanglementEntropy` | `entanglement_entropy` | `float` (or `dict` keyed by partition, if multiple partitions are requested in one pass instance — TBD during implementation) |

## Directory layout

```
qiskit_magic_metrics/
  __init__.py              # public API exports
  base.py                  # ResourceMetric
  _dispatch.py             # Clifford-vs-statevector dispatch logic
  passes/
    stabilizer_renyi_entropy.py
    meyer_wallach.py
    entanglement_entropy.py
  lean/
    README.md              # verification status, cross-check instructions
    *.lean                 # Lean 4 source (added in v0.2)
tests/
  test_stabilizer_renyi_entropy.py
  test_meyer_wallach.py
  test_entanglement_entropy.py
  test_regression_known_states.py   # GHZ, W, Bell, product-state closed-form checks
docs/
  ARCHITECTURE.md   (this file)
  PRIOR_ART.md
```

## Testing philosophy

Every metric gets regression tests against states with known closed-form values:
- Product states → all metrics should read zero entanglement/magic
- Bell pairs → maximal 2-qubit entanglement, zero magic
- GHZ / W states → known Meyer-Wallach values, zero magic (both are stabilizer states for GHZ;
  W-state is *not* a stabilizer state, so it exercises the general statevector path and is a
  useful edge case)
- A non-Clifford ansatz (e.g. containing a T gate) with a hand-computed or literature-sourced
  expected magic value, to validate the general path independent of the fast path

Following the pattern used in `qiskit-graph-walks`: any real bug found during development gets
turned into a permanent regression test documenting the failure mode, not just fixed silently.
