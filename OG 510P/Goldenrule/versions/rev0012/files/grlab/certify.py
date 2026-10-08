from __future__ import annotations

from typing import Any, Mapping


class CertifyError(ValueError):
    pass


_MEMORY_ONE_KEYS = ("p_cc", "p_cd", "p_dc", "p_dd")


def _as_prob(name: str, value: Any) -> float:
    if not isinstance(value, (int, float)):
        raise CertifyError(f"{name} must be numeric")
    p = float(value)
    if p < 0.0 or p > 1.0:
        raise CertifyError(f"{name} must be in [0, 1], got {p}")
    return p


def _extract_memory_one_probabilities(strategy: Mapping[str, Any], label: str) -> list[float]:
    family = strategy.get("family")
    if family != "memory_one":
        raise CertifyError(f"{label} is not memory_one (family={family!r})")
    return [_as_prob(f"{label}.{k}", strategy.get(k)) for k in _MEMORY_ONE_KEYS]


def _build_transition_matrix_memory_one(p: list[float], q: list[float]) -> list[list[float]]:
    matrix: list[list[float]] = []
    for i in range(4):
        row = [
            p[i] * q[i],
            p[i] * (1.0 - q[i]),
            (1.0 - p[i]) * q[i],
            (1.0 - p[i]) * (1.0 - q[i]),
        ]
        matrix.append(row)
    return matrix


def _solve_linear_4x4(a: list[list[float]], b: list[float]) -> list[float]:
    eps = 1e-12
    if len(a) != 4 or any(len(row) != 4 for row in a) or len(b) != 4:
        raise CertifyError("expected a 4x4 linear system")

    aug = [row[:] + [rhs] for row, rhs in zip(a, b)]

    for col in range(4):
        pivot = max(range(col, 4), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < eps:
            raise CertifyError("stationary system is singular or ill-conditioned")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]

        pivot_val = aug[col][col]
        for j in range(col, 5):
            aug[col][j] /= pivot_val

        for r in range(4):
            if r == col:
                continue
            factor = aug[r][col]
            if abs(factor) < eps:
                continue
            for j in range(col, 5):
                aug[r][j] -= factor * aug[col][j]

    return [aug[i][4] for i in range(4)]


def _stationary_distribution(matrix: list[list[float]]) -> list[float]:
    # Solve (P^T - I)v = 0 with sum(v) = 1.
    a = [[matrix[i][j] - (1.0 if i == j else 0.0) for i in range(4)] for j in range(4)]
    b = [0.0, 0.0, 0.0, 0.0]

    # Replace one equation with normalization to get a full-rank system.
    a[3] = [1.0, 1.0, 1.0, 1.0]
    b[3] = 1.0

    v = _solve_linear_4x4(a, b)

    cleaned = [0.0 if abs(x) < 1e-12 else float(x) for x in v]
    if any(x < -1e-9 for x in cleaned):
        raise CertifyError(f"computed invalid stationary distribution: {cleaned}")

    non_negative = [max(0.0, x) for x in cleaned]
    total = sum(non_negative)
    if total <= 0.0:
        raise CertifyError("computed zero-mass stationary distribution")
    return [x / total for x in non_negative]


def certify_memory_one_pair(strategy_a: Mapping[str, Any], strategy_b: Mapping[str, Any]) -> dict[str, Any]:
    p = _extract_memory_one_probabilities(strategy_a, "strategy_a")
    q_raw = _extract_memory_one_probabilities(strategy_b, "strategy_b")
    # Mirror B's conditional states so both players use [CC, CD, DC, DD] from A's viewpoint.
    q = [q_raw[0], q_raw[2], q_raw[1], q_raw[3]]

    matrix = _build_transition_matrix_memory_one(p, q)
    v = _stationary_distribution(matrix)

    payoffs_a = [3.0, 0.0, 5.0, 1.0]
    payoffs_b = [3.0, 5.0, 0.0, 1.0]

    avg_a = sum(v[i] * payoffs_a[i] for i in range(4))
    avg_b = sum(v[i] * payoffs_b[i] for i in range(4))

    return {
        "strategy_a": strategy_a.get("id"),
        "strategy_b": strategy_b.get("id"),
        "steady_state_distribution": [float(x) for x in v],
        "avg_payoff_a": float(avg_a),
        "avg_payoff_b": float(avg_b),
        "payoff_diff": float(abs(avg_a - avg_b)),
    }
