# Prior art

This document exists so that anyone evaluating this package — including its own maintainer —
has an honest, checkable account of what already exists, rather than a marketing claim that
"no equivalent exists." Last reviewed: 2026-09-01.

## `qiskit.quantum_info` (built into Qiskit)

Provides:
- `entropy()` — von Neumann entropy of a `Statevector`/`DensityMatrix`
- `entanglement_of_formation(state)` — restricted to a 2-qubit density matrix or bipartite
  statevector
- `mutual_information(state, base=2)` — bipartite only: `I(ρ_AB) = S(ρ_A) + S(ρ_B) - S(ρ_AB)`

Gap: no multipartite entanglement measure (Meyer-Wallach or otherwise), no configurable
bipartition beyond the trivial 2-party split, and no magic/nonstabilizerness measure of any
kind. This package's `EntanglementEntropy` pass generalizes the bipartite case to arbitrary
user-specified partitions; `MeyerWallachMeasure` and `StabilizerRenyiEntropy` cover territory
`quantum_info` doesn't touch at all.

## Qurrium / Qurry (PyPI: `qurrium`)

Actively maintained. Measures quantum Rényi entropy, Loschmidt echo, and magnetization-squared
via **randomized measurement protocols** (Hadamard test and Haar-randomized measurement), with
direct `qiskit-ibm-runtime` integration for job submission, recall, and postprocessing, plus
error mitigation features.

This is real, mature prior art on the Rényi-entropy/magic-adjacent front and should not be
undersold. The distinction that justifies a separate package:

- Qurrium is built around **executing circuits** (on a simulator or real backend) and
  statistically estimating a quantity from shots. It's the right tool when you have hardware
  access and want an experimental estimate.
- This package computes the **exact** value from a statevector or, for Clifford circuits, the
  stabilizer tableau — no execution, no shot noise, and (via the stabilizer fast path) no
  exponential Pauli enumeration for the common case. It's the right tool during circuit design,
  in CI, or anywhere you want a deterministic answer instantly.

If a user needs a hardware-validated magic estimate, Qurrium is likely the better choice, not
this package. Worth linking to from this package's docs rather than pretending it doesn't exist.

## qLEET (PyPI: `qLEET`, GitHub: `QLemma/qleet`)

Implements expressibility and entangling capability (Meyer-Wallach-based) plus loss-landscape
and training-trajectory visualization, for Qiskit/Cirq/pyQuil circuits. Apache-2.0, Unitary
Fund–supported.

Status as of this review: 35 GitHub stars, 118 commits total, no visible recent activity, and a
`python_requires` floor (3.7+) suggesting it predates several Qiskit major-version changes. It
may not run cleanly against current Qiskit without patching. Confirm current install/import
health before citing it as a working alternative in any submission materials — this assessment
is based on repo metadata, not a fresh install test.

This package deliberately does **not** reimplement expressibility or loss-landscape tooling.
If that functionality is wanted, the more honest path is contributing fixes/updates upstream to
qLEET (or forking it explicitly as a revival, clearly labeled as such) rather than quietly
duplicating it under a new name.

## Net scoping decision

Given the above, this package's differentiated territory is:
1. Exact (not sampled) computation of magic and multipartite entanglement measures
2. Stabilizer-tableau fast paths for the Clifford case
3. `PassManager`-native composability
4. A formally verified core identity

None of the three prior-art projects combine all four. That's the actual gap being filled —
narrower than "no ecosystem equivalent exists for entanglement/complexity metrics," which is not
an accurate claim once Qurrium and qLEET are accounted for.
