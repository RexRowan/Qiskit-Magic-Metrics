"""Minimal GF(2) linear algebra used by the stabilizer fast paths.

Both `MeyerWallachMeasure` and `EntanglementEntropy` reduce, on Clifford circuits, to rank/
null-space computations over the binary field on the stabilizer tableau's symplectic (X|Z)
representation. Kept separate from the passes themselves so the underlying algorithm is easy to
unit-test on its own and easy to point a future Lean proof at.
"""

from __future__ import annotations

import numpy as np


def gf2_rank(matrix: np.ndarray) -> int:
    """Rank of a binary matrix over GF(2), via Gaussian elimination mod 2.

    Args:
        matrix: a 2D integer array; entries are reduced mod 2 before elimination, so any
            integer dtype is accepted.

    Returns:
        The rank of `matrix` over GF(2). `matrix` itself is not modified — elimination runs on
        a local copy.
    """
    mat = matrix.copy().astype(np.uint8) % 2
    rows, cols = mat.shape
    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if mat[row, col]:
                pivot = row
                break
        if pivot is None:
            continue
        mat[[rank, pivot]] = mat[[pivot, rank]]
        for row in range(rows):
            if row != rank and mat[row, col]:
                mat[row] ^= mat[rank]
        rank += 1
        if rank == rows:
            break
    return rank


def gf2_nullspace(matrix: np.ndarray) -> np.ndarray:
    """Basis for the null space of a binary matrix over GF(2), taken over its rows.

    Used to find combinations of stabilizer generators (the matrix's rows) that cancel out on a
    chosen set of columns (see `MeyerWallachMeasure`'s stabilizer fast path) — hence the null
    space is computed over row-combinations, not the more usual column null space.

    Args:
        matrix: a 2D integer array of shape `(rows, cols)`; entries are reduced mod 2.

    Returns:
        An array of shape `(k, rows)`, where `k` is the nullity and each row `v` satisfies
        `v @ matrix ≡ 0 (mod 2)` — i.e. each `v` is a combination of `matrix`'s rows that sums
        to the all-zero row.
    """
    mat = matrix.copy().astype(np.uint8) % 2
    rows, cols = mat.shape
    # Track which combination of original rows produced each row of the reduced matrix, via an
    # augmented identity block, so we can recover null-space vectors over the *rows* (generator
    # combinations) rather than the columns.
    aug = np.concatenate([mat, np.eye(rows, dtype=np.uint8)], axis=1)

    rank = 0
    for col in range(cols):
        pivot = None
        for row in range(rank, rows):
            if aug[row, col]:
                pivot = row
                break
        if pivot is None:
            continue
        aug[[rank, pivot]] = aug[[pivot, rank]]
        for row in range(rows):
            if row != rank and aug[row, col]:
                aug[row] ^= aug[rank]
        rank += 1
        if rank == rows:
            break

    # Rows rank..rows-1 of `aug` are all-zero in the original `cols` columns (they're linear
    # combinations of the original rows, recorded in the trailing identity block, that vanish
    # on every column). Those trailing entries are exactly the null-space basis over the rows.
    return aug[rank:, cols:]
