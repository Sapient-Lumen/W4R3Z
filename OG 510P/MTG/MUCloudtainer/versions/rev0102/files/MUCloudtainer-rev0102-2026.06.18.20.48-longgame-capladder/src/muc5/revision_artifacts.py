from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ArtifactAuditReport:
    revision: str
    passed: bool
    expected_count: int
    missing: tuple[str, ...]
    forbidden_present: tuple[str, ...]
    row_limit_violations: tuple[dict[str, object], ...]
    checked_row_limits: tuple[dict[str, object], ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def count_csv_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as f:
        return max(0, sum(1 for _ in csv.reader(f)) - 1)


def latest_revision_entry(log_path: str | Path) -> Mapping[str, object]:
    payload = json.loads(Path(log_path).read_text(encoding="utf-8"))
    revisions = payload.get("revisions", []) if isinstance(payload, Mapping) else []
    if not revisions:
        raise ValueError(f"revision log has no revisions: {log_path}")
    return revisions[-1]


def audit_revision_artifacts(
    root: str | Path,
    *,
    revision: str,
    expected_paths: Sequence[str],
    forbidden_globs: Sequence[str] = (),
    max_csv_rows: Mapping[str, int] | None = None,
) -> ArtifactAuditReport:
    """Check that a revision ships the intended evidence and avoids known ballast.

    This intentionally stays small and revision-agnostic.  The legacy monolithic
    ``audit_cube.py`` is a broad inheritance audit; this helper is for the live
    revision's own artifact contract, especially when raw transition ballast must
    not be packaged by accident.
    """

    base = Path(root)
    missing = tuple(path for path in expected_paths if not (base / path).exists())
    forbidden: list[str] = []
    for pattern in forbidden_globs:
        forbidden.extend(str(p.relative_to(base)) for p in sorted(base.glob(pattern)) if p.is_file())

    checked: list[dict[str, object]] = []
    violations: list[dict[str, object]] = []
    for rel, limit in (max_csv_rows or {}).items():
        path = base / rel
        if not path.exists():
            continue
        rows = count_csv_rows(path)
        item = {"path": rel, "rows": rows, "limit": int(limit)}
        checked.append(item)
        if rows > int(limit):
            violations.append(item)

    return ArtifactAuditReport(
        revision=revision,
        passed=not missing and not forbidden and not violations,
        expected_count=len(expected_paths),
        missing=tuple(missing),
        forbidden_present=tuple(forbidden),
        row_limit_violations=tuple(violations),
        checked_row_limits=tuple(checked),
    )
