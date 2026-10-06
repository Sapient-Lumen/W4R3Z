import json
import pathlib
from typing import Iterable

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_json(rel: str, *, root: pathlib.Path = ROOT):
    return json.loads((pathlib.Path(root) / rel).read_text(encoding="utf-8"))


def assert_surface_exists(rel: str) -> None:
    base = rel.split('#', 1)[0]
    if base and not (ROOT / base).exists():
        raise SystemExit(f"missing referenced surface: {rel}")


def assert_tokens(text: str, tokens: Iterable[str], *, label: str) -> None:
    for token in tokens:
        if token not in text:
            raise SystemExit(f"{label} missing {token}")


def metric_ids(assay: dict) -> set[str]:
    return {row.get("id") for row in assay.get("metrics", [])}


def assert_metric_contract(assay: dict, *, required: set[str] | None = None, count: int | None = None, two_point: bool = True) -> set[str]:
    metrics = assay.get("metrics", [])
    if not isinstance(metrics, list) or not metrics:
        raise SystemExit("Priority-0 assay metrics must be a non-empty list")
    if count is not None and len(metrics) != count:
        raise SystemExit(f"Priority-0 assay must carry exactly {count} metrics")
    observed = metric_ids(assay)
    if len(observed) != len(metrics):
        raise SystemExit("Priority-0 assay metric ids must be unique")
    if required is not None and observed != required:
        raise SystemExit(f"Priority-0 assay metric id set drifted: {sorted(observed)}")
    if two_point and any(row.get("max") != 2 for row in metrics):
        raise SystemExit("Priority-0 assay metrics must be two-point metrics")
    return observed


def variants_by_id(assay: dict, required: set[str] | None = None) -> dict[str, dict]:
    rows = assay.get("variants", [])
    if not isinstance(rows, list) or not rows:
        raise SystemExit("Priority-0 assay variants must be a non-empty list")
    variants: dict[str, dict] = {}
    for row in rows:
        vid = row.get("id")
        if not vid or vid in variants:
            raise SystemExit("Priority-0 assay variant ids must be present and unique")
        variants[vid] = row
    if required is not None and set(variants) != required:
        raise SystemExit(f"Priority-0 assay variants drifted: {sorted(variants)}")
    return variants


def assert_variant_score_integrity(assay: dict, *, required_variants: set[str] | None = None, exact_metric_scores: bool = True) -> dict[str, dict]:
    metrics = assay.get("metrics", [])
    ids = metric_ids(assay)
    max_total = sum(metric.get("max", 0) for metric in metrics)
    variants = variants_by_id(assay, required_variants)
    for vid, row in variants.items():
        for key in ["score", "max", "operator_cost_minutes", "observed", "metric_scores"]:
            if key not in row:
                raise SystemExit(f"Priority-0 assay variant {vid} missing {key}")
        scores = row.get("metric_scores", {})
        if exact_metric_scores and set(scores) != ids:
            raise SystemExit(f"Priority-0 assay variant {vid} metric scores drifted")
        if not set(scores).issubset(ids):
            raise SystemExit(f"Priority-0 assay variant {vid} has unknown metric scores")
        if row.get("score") != sum(scores.values()):
            raise SystemExit(f"Priority-0 assay variant {vid} score must equal metric-score sum")
        if row.get("max") != max_total:
            raise SystemExit(f"Priority-0 assay variant {vid} max must equal metric max sum")
        if not isinstance(row.get("operator_cost_minutes"), (int, float)) or row["operator_cost_minutes"] <= 0:
            raise SystemExit(f"Priority-0 assay variant {vid} operator cost must be positive")
        if row["score"] < 0 or row["score"] > row["max"]:
            raise SystemExit(f"Priority-0 assay variant {vid} score out of range")
    return variants


def assert_scorecard_integrity(assay: dict, variants: dict[str, dict] | None = None) -> dict:
    variants = variants or variants_by_id(assay)
    scorecard = assay.get("scorecard", {})
    if scorecard.get("state") != "scored-canary":
        raise SystemExit("Priority-0 assay scorecard must be scored-canary")
    if scorecard.get("observed_score") != sum(row["score"] for row in variants.values()):
        raise SystemExit("Priority-0 assay observed score sum drift")
    if scorecard.get("max_score") != sum(row["max"] for row in variants.values()):
        raise SystemExit("Priority-0 assay max score sum drift")
    return scorecard


def assert_negative_canaries(assay: dict, required: Iterable[str], *, minimum: int = 0) -> None:
    canaries = assay.get("negative_canaries", [])
    if not isinstance(canaries, list) or len(canaries) < minimum:
        raise SystemExit("Priority-0 assay negative canaries too thin")
    for canary in required:
        if canary not in canaries:
            raise SystemExit(f"Priority-0 assay missing negative canary {canary}")


def file_sha256(rel: str, *, root: pathlib.Path = ROOT) -> str:
    base = rel.split('#', 1)[0]
    root = pathlib.Path(root)
    if not base or not (root / base).exists():
        raise SystemExit(f"missing file for sha256: {rel}")
    import hashlib
    return hashlib.sha256((root / base).read_bytes()).hexdigest()


def assert_no_tokens(text: str, tokens: Iterable[str], *, label: str) -> None:
    for token in tokens:
        if token in text:
            raise SystemExit(f"{label} leaked forbidden token: {token}")
