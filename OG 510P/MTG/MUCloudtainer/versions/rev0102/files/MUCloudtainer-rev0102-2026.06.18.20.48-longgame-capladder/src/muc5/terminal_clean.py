from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, Mapping, Sequence


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


@dataclass(frozen=True)
class TerminalCleanSummary:
    """Summary for payoff panels intended to be used as promotion/evaluation tables.

    Earlier revisions allowed smoke panels with nonterminal max-decision draws as
    diagnostics.  rev0049 makes the preferred evaluation contract explicit:
    terminal-clean panels use a high enough decision ceiling that every row ends
    in a real terminal game, or else the panel is labelled non-clean and should
    not be used for policy promotion.
    """

    revision: str
    rows: int
    max_decisions: int
    terminal_rows: int
    truncation_rows: int
    terminal_clean: bool
    terminal_rate: float
    truncation_rate: float

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def mark_terminal_clean_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    revision: str,
    max_decisions: int,
    strict: bool = False,
) -> list[dict[str, Any]]:
    """Annotate payoff rows with an explicit terminal-clean contract.

    The function does not alter scores.  It makes truncation status visible on
    every row and allows scripts/audits to distinguish:

    * terminal-clean evaluation rows, suitable for normal standings; and
    * smoke/diagnostic rows with max-decision truncations.
    """

    out: list[dict[str, Any]] = []
    for src in rows:
        row = dict(src)
        is_trunc = truthy(row.get("is_truncation")) or str(row.get("loss_reason", "")).strip() == "max_decisions_reached"
        row["simulator_revision"] = revision
        row["terminal_clean_max_decisions"] = int(max_decisions)
        row["terminal_clean_game"] = bool(not is_trunc)
        row["terminal_clean_status"] = "terminal" if not is_trunc else "truncated_nonterminal"
        out.append(row)
    if strict and any(not truthy(r.get("terminal_clean_game")) for r in out):
        bad = sum(1 for r in out if not truthy(r.get("terminal_clean_game")))
        raise ValueError(f"terminal-clean strict mode saw {bad} truncated rows")
    return out


def summarize_terminal_clean_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    revision: str,
    max_decisions: int,
) -> TerminalCleanSummary:
    n = len(rows)
    trunc = sum(
        1
        for r in rows
        if truthy(r.get("is_truncation"))
        or truthy(r.get("final_is_truncation"))
        or not truthy(r.get("terminal_clean_game", True))
        or str(r.get("loss_reason", "")).strip() == "max_decisions_reached"
    )
    terminal = n - trunc
    return TerminalCleanSummary(
        revision=revision,
        rows=int(n),
        max_decisions=int(max_decisions),
        terminal_rows=int(terminal),
        truncation_rows=int(trunc),
        terminal_clean=bool(n > 0 and trunc == 0),
        terminal_rate=terminal / n if n else 0.0,
        truncation_rate=trunc / n if n else 0.0,
    )


def terminal_clean_by_strategy(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Seat-symmetric truncation/terminal counts by strategy."""

    buckets: dict[str, dict[str, float]] = {}
    for row in rows:
        for key in ("strategy0", "strategy1"):
            sid = str(row.get(key, ""))
            if sid not in buckets:
                buckets[sid] = {"seat_games": 0, "terminal_games": 0, "truncations": 0}
            b = buckets[sid]
            b["seat_games"] += 1
            terminal = truthy(row.get("terminal_clean_game", True)) and not truthy(row.get("is_truncation"))
            b["terminal_games"] += 1 if terminal else 0
            b["truncations"] += 0 if terminal else 1
    out = []
    for strategy, b in buckets.items():
        games = int(b["seat_games"])
        out.append({
            "strategy": strategy,
            "seat_games": games,
            "terminal_games": int(b["terminal_games"]),
            "truncations": int(b["truncations"]),
            "terminal_rate": b["terminal_games"] / games if games else 0.0,
            "truncation_rate": b["truncations"] / games if games else 0.0,
        })
    out.sort(key=lambda r: (r["truncation_rate"], r["strategy"]), reverse=True)
    return out
