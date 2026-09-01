# Lean-verified core

**Status: not started.** This directory is a placeholder for the v0.2 milestone (see
[ROADMAP.md](../../ROADMAP.md)).

## Target identity

Default plan: formally verify that the Meyer-Wallach measure's closed form,

```
Q(ψ) = 2 (1 - (1/n) Σ_k tr(ρ_k²))
```

agrees with the stabilizer-tableau-derived shortcut (single-qubit purities read directly off the
tableau rather than computed via full reduced-density-matrix construction) for the finite case
family: Bell pairs, GHZ states, and small graph states. This mirrors the scope and structure of
the spider-fusion proof in `qiskit-zx-verified` — a small, enumerable case space, checked with
`#eval`, no dependency on Mathlib beyond `propext` if that constraint turns out to be achievable
here too (not guaranteed; revisit once the proof is drafted).

This target may change once the implementation work in `passes/` surfaces a more natural or more
valuable identity to verify — e.g., the stabilizer Rényi entropy's exact-zero property for
stabilizer states might be the more interesting claim, since it's the thing the fast path
actually depends on for correctness. Decide after v0.1 lands, not before.

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
