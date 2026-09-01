# Roadmap

Honest status tracker. Nothing below is marked done until it has tests and, where applicable,
a passing Lean cross-check.

## v0.1 — scaffold (current)

- [x] Repo structure, packaging, CI skeleton
- [x] Prior-art writeup (`docs/PRIOR_ART.md`)
- [ ] `ResourceMetric` base class
- [ ] `StabilizerRenyiEntropy` — statevector/Pauli-enumeration path (small circuits only)
- [ ] `StabilizerRenyiEntropy` — Clifford fast path (tableau-based, returns exact 0)
- [ ] `MeyerWallachMeasure` — statevector path
- [ ] `MeyerWallachMeasure` — Clifford fast path (tableau-derived purities)
- [ ] `EntanglementEntropy` — arbitrary bipartition, statevector path
- [ ] Each metric usable both standalone (`.compute(circuit)`) and as an `AnalysisPass`
- [ ] Regression tests against known closed-form values (GHZ, W-state, Bell pairs, product states)

## v0.2 — Lean-verified core

- [ ] Pick the target identity (default plan: Meyer-Wallach purity reduction on the
      Bell/GHZ/graph-state family — see `qiskit_magic_metrics/lean/README.md`)
- [ ] Lean 4 formalization, zero `sorry`s if feasible; document any that remain, following the
      precedent set in `qiskit-lean-bridge` (open items are fine if disclosed, not hidden)
- [ ] `#eval`-based cross-check script diffing Lean's evaluation against the Python
      implementation across the finite case space
- [ ] CI job running the Lean build + cross-check on every PR touching the verified identity

## v0.3 — Ecosystem submission prep

- [ ] Docs site (readthedocs or GitHub Pages)
- [ ] Ecosystem submission checklist review
- [ ] PyPI v0.1.0 release

## Explicitly not planned (see README "Why this exists")

- Expressibility / loss-landscape / training-trajectory tooling — qLEET's territory
- Randomized-measurement hardware execution / shot-based estimation — Qurrium's territory
- Non-Clifford magic-state distillation cost estimates (a different, much larger project)
