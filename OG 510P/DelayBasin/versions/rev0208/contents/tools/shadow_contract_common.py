from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]


def _as_surface_specs(extra_required: Iterable[tuple[str, Sequence[str], str]] | None):
    if not extra_required:
        return []
    specs = []
    for rel, needles, label in extra_required:
        specs.append((ROOT / rel, list(needles), label))
    return specs


def require_shadow_contract(*, kind: str, doc_required: list[str], prompt_required: list[str], runbook_required: list[str], trajectory_required: list[str], open_question_required: list[str], quarantine_required: list[str], extra_required: list[tuple[str, list[str], str]] | None = None) -> None:
    required = [
        ROOT / "docs/10-method/external-optimizer-loops-public-slow-weights-and-archive-write-gates.md",
        ROOT / "docs/50-promptcraft/prompt-pairs.md",
        ROOT / "docs/00-meta/llm-runbook.md",
        ROOT / "docs/00-meta/trajectory-map.md",
        ROOT / "docs/20-constitution/open-question-registry.md",
        ROOT / "docs/90-quarantine/wild-speculations-2026-03-08.md",
    ]
    labels = [
        (required[0], doc_required, "external-optimizer doc"),
        (required[1], prompt_required, "prompt pairs"),
        (required[2], runbook_required, "runbook"),
        (required[3], trajectory_required, "trajectory map"),
        (required[4], open_question_required, "open-question registry"),
        (required[5], quarantine_required, "quarantine"),
        *_as_surface_specs(extra_required),
    ]
    for path, _, _ in labels:
        if not path.exists():
            raise SystemExit(f"missing required shadow-{kind} surface: {path}")

    for path, needles, label in labels:
        text = path.read_text(encoding="utf-8")
        missing = [needle for needle in needles if needle not in text]
        if missing:
            raise SystemExit(f"shadow-{kind} contract missing from {label}: " + ", ".join(missing))

    print(f"check_shadow_{kind}_contract: OK")
