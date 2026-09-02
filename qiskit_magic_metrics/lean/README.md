# Lean-verified core

**Status: not started.** This directory is a placeholder for the v0.2 milestone (see
[ROADMAP.md](../../ROADMAP.md)).

## Target identity

Now that v0.1 is implemented, the concrete candidate is the correctness of the GF(2)
null-space/rank shortcuts actually in use, rather than the more abstract purity-reduction
formula originally sketched here:

- `MeyerWallachMeasure._compute_stabilizer` claims: qubit k's reduced state is pure (tr(rho_k^2)
  = 1) iff the stabilizer generator matrix, restricted to columns for every qubit except k, has
  a nonzero GF(2) null space; otherwise tr(rho_k^2) = 1/2. This is the identity worth verifying
  first, since the whole fast path's correctness rests on it.
- `EntanglementEntropy._compute_stabilizer` claims the Fattal et al. rank formula
  `S(A) = rank_GF2(M_B) - |B|`. This is already a published, cited result (arXiv:quant-ph/0406168)
  rather than something derived here, so verifying it in Lean is lower priority than the
  Meyer-Wallach claim above, which is this package's own derivation from that same family of
  results and hasn't been independently checked anywhere else.

Plan: formalize the Meyer-Wallach null-space claim for the finite case family (Bell pairs, GHZ
states, small graph states), `#eval`-checked against the Python implementation, following the
spider-fusion proof structure in `qiskit-zx-verified` (small enumerable case space, no Mathlib
dependency beyond `propext` if achievable).

## Cross-check bridge (planned)

Following the `qiskit-zx-verified` / `qiskit-lean-bridge` pattern:
1. Lean's `#eval` computes the identity's value across every case in the finite family.
2. A Python script independently computes the same values using the `qiskit_magic_metrics`
   implementation.
3. CI diffs the two outputs and fails on any mismatch.

## Known risks (fill in as encountered)

- Naming collisions with existing Lean quantum libraries (LeanQuantum/inQWIRE), as previously hit
  in `qiskit-lean-bridge` (`π`-notation collision, `λ` as a reserved identifier) — check early.
- If the identity requires facts not cheaply provable without Mathlib, decide explicitly whether
  to take the Mathlib dependency or scope the identity down further. Don't let this stall v0.2
  silently — document the decision here once made.
