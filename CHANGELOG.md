# Changelog

All notable changes to this project are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- Docstring/API pass: `Args`/`Returns`/`Raises` sections on every public method, usage examples
  on all three concrete metric classes (previously only `MeyerWallachMeasure` had one),
  `__repr__` on `StabilizerRenyiEntropy` and `EntanglementEntropy`, module-level public-API
  summary in `qiskit_magic_metrics/__init__.py`, `py.typed` marker for PEP 561 compliance.

### Fixed
- `StabilizerRenyiEntropy` now rejects `alpha <= 0` (previously only `alpha == 1` was rejected;
  non-positive alpha raises a divergence in the underlying sum whenever any Pauli expectation
  value is exactly zero, which is the common case, not an edge case).
- `gf2_nullspace` had an unused `pivot_cols` variable and an imprecise docstring (said
  `matrix @ v` when the actual returned vectors satisfy `v @ matrix`); both fixed, with the
  correct semantics verified against a worked example.

### Added
- `ResourceMetric` base class with automatic Clifford/statevector dispatch (`_dispatch.py`).
- `StabilizerRenyiEntropy`: exact magic measure, statevector path via Pauli-expectation
  enumeration, O(1) Clifford fast path (always exactly 0.0).
- `MeyerWallachMeasure`: exact global multipartite entanglement, statevector path via
  single-qubit reduced-density-matrix purities, Clifford fast path via a GF(2) null-space test
  on the stabilizer tableau (`_gf2.py`).
- `EntanglementEntropy`: von Neumann entropy across an arbitrary user-specified bipartition
  (generalizing `qiskit.quantum_info.mutual_information`'s fixed bipartite split), Clifford fast
  path via the Fattal et al. GF(2) rank formula.
- All three metrics work standalone (`.compute(circuit)`) and as `AnalysisPass`es composable in
  a `PassManager`.
- 20 tests: per-metric regression tests against known closed-form states (GHZ, Bell pairs,
  product states, W-state), fast-path-vs-general-path agreement checks, and a cross-metric/
  `PassManager` integration test.
- Repository scaffold: packaging (`pyproject.toml`, `qiskit>=2,<3`), docs (`README.md`,
  `ARCHITECTURE.md`, `PRIOR_ART.md`, `ROADMAP.md`), CI skeleton.
- Prior-art assessment covering `qiskit.quantum_info`, Qurrium/Qurry, and qLEET.

v0.1 core metrics are implemented; see `ROADMAP.md` for what's next (Lean-verified core, docs
site, Ecosystem submission).
