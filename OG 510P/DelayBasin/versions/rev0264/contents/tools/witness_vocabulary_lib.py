import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "WITNESS-VOCABULARY.json"


def load_families() -> dict:
    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    families = vocab.get("families")
    if not isinstance(families, dict) or not families:
        raise SystemExit("WITNESS-VOCABULARY families must be a non-empty object")
    return families


def expect_allowed(families: dict, family: str, value: str, where: str) -> None:
    allowed = families.get(family, {}).get("allowed", [])
    if value not in allowed:
        raise SystemExit(f"{where} value {value!r} not allowed by family {family}")


def expect_family(families: dict, family: str, *, allowed: list[str] | None = None, surfaces: list[str] | None = None, excluded: list[str] | None = None) -> dict:
    meta = families.get(family)
    if not isinstance(meta, dict):
        raise SystemExit(f"{family} family missing")
    if allowed is not None and meta.get("allowed") != allowed:
        raise SystemExit(f"{family} allowed tokens drifted")
    if surfaces is not None and meta.get("surfaces") != surfaces:
        raise SystemExit(f"{family} surfaces drifted")
    if excluded is not None:
        actual = set(meta.get("excluded_synonyms", []))
        for needle in excluded:
            if needle not in actual:
                raise SystemExit(f"{family} excluded_synonyms missing {needle}")
    return meta
