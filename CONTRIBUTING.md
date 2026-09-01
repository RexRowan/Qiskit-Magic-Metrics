# Contributing

## Setup

```bash
git clone https://github.com/RexRowan/qiskit-magic-metrics.git
cd qiskit-magic-metrics
pip install -e ".[test,lint]"
```

## Before opening a PR

- Run `pytest` — all tests must pass.
- Run `ruff check .` and `black --check .`.
- If your change touches a metric's core formula, add a regression test against a
  known-closed-form state (see `docs/ARCHITECTURE.md`, "Testing philosophy") — don't just assert
  the new behavior matches the new code.
- If you find a real bug, add a regression test that documents the failure mode, not just a fix.
  This project follows that convention throughout (see `qiskit-graph-walks`,
  `qiskit-lean-bridge` for precedent).

## Scope boundaries

Before proposing a new metric or feature, check `docs/PRIOR_ART.md` and the "Why this exists" /
"Explicitly out of scope" sections of `README.md`. This package deliberately does not include
expressibility/loss-landscape tooling (see qLEET) or randomized-measurement hardware execution
(see Qurrium). PRs adding those will likely be declined in favor of contributing upstream instead
— raise an issue first if you think an exception is warranted.

## Lean changes

Changes to `qiskit_magic_metrics/lean/` require the cross-check bridge script to pass (diffing
Lean's `#eval` output against the Python implementation). See
`qiskit_magic_metrics/lean/README.md` for current status — this component doesn't exist yet as
of v0.1.

## Code of conduct

Be direct, be kind, cite your sources. Standard open-source courtesy applies; no separate CoC
document yet — added if/when the contributor base grows past one person.
