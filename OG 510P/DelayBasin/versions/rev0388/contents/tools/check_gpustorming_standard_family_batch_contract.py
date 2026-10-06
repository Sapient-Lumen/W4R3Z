import pathlib
import sys
from collections import Counter
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from gpustorming_contract_lib import derived_variant_forms, ensure_needles, standard_family_contract_map
from gpustorming_standard_contract_specs import iter_gpustorming_standard_contract_specs

EXPECTED_STANDARD_GPUSTORMING_CONTRACTS = 40
ALLOWED_MODES = {"needle_map", "standard_family", "phrase_family"}


def _contract_map(row: dict[str, Any]) -> dict[str, list[str]]:
    mode = row.get("mode")
    family = row.get("family")
    if mode == "needle_map":
        mapping = row.get("needles")
        if not isinstance(mapping, dict) or not mapping:
            raise SystemExit(f"{family}: needle_map spec must contain a non-empty needles map")
        return mapping
    if mode == "standard_family":
        kwargs = row.get("kwargs")
        if not isinstance(kwargs, dict) or not kwargs:
            raise SystemExit(f"{family}: standard_family spec must contain kwargs")
        return standard_family_contract_map(**kwargs)
    if mode == "phrase_family":
        kwargs = dict(row.get("kwargs") or {})
        operator_variant = kwargs.pop("operator_variant", None)
        if not isinstance(operator_variant, str) or not operator_variant:
            raise SystemExit(f"{family}: phrase_family spec must contain operator_variant")
        variants = derived_variant_forms(operator_variant)
        return standard_family_contract_map(
            family=kwargs["family"],
            operator_variant=variants["operator"],
            privileges=kwargs["privileges"],
            crosswalk_text=kwargs["crosswalk_text"],
            trajectory_intro=kwargs.get("trajectory_intro"),
            oq_variant=variants["oq"],
            prompt_variant=variants["prompt"],
            runbook_variant=variants["runbook"],
            quarantine_id=kwargs["quarantine_id"],
            quarantine_text=kwargs["quarantine_text"],
            changelog_text=kwargs["changelog_text"],
            archive_index_text=kwargs["archive_index_text"],
        )
    raise SystemExit(f"{family}: unsupported standard GPustorming spec mode: {mode!r}")


rows = list(iter_gpustorming_standard_contract_specs())
if len(rows) != EXPECTED_STANDARD_GPUSTORMING_CONTRACTS:
    raise SystemExit(
        f"expected {EXPECTED_STANDARD_GPUSTORMING_CONTRACTS} standard GPustorming specs, "
        f"found {len(rows)}"
    )

seen_sources: set[str] = set()
seen_families: set[str] = set()
by_segment = Counter(segment for segment, _row in rows)
for segment, row in rows:
    source_checker = row.get("source_checker")
    family = row.get("family")
    mode = row.get("mode")
    if "source" in row:
        raise SystemExit(f"{source_checker} [{segment}]: stored executable source payloads are forbidden in standard batch specs")
    if mode not in ALLOWED_MODES:
        raise SystemExit(f"{source_checker} [{segment}]: unsupported standard GPustorming spec mode {mode!r}")
    if not isinstance(source_checker, str) or not source_checker.startswith("check_gpustorming_"):
        raise SystemExit(f"bad source checker in standard GPustorming spec {segment}: {source_checker!r}")
    if source_checker in seen_sources:
        raise SystemExit(f"duplicate standard GPustorming source checker {source_checker} in {segment}")
    seen_sources.add(source_checker)
    if not isinstance(family, str) or not family:
        raise SystemExit(f"bad family in standard GPustorming spec {source_checker} [{segment}]")
    if family in seen_families:
        raise SystemExit(f"duplicate standard GPustorming family {family} in {segment}")
    seen_families.add(family)
    if family not in source_checker:
        raise SystemExit(f"{source_checker} [{segment}]: family/source mismatch for {family}")
    try:
        ensure_needles(ROOT, f"gpustorming-{family}", _contract_map(row))
    except SystemExit as exc:
        raise SystemExit(f"{source_checker} [{segment}] failed: {exc}") from exc

print(
    "check_gpustorming_standard_family_batch_contract: OK "
    f"({len(rows)} contracts across {len(by_segment)} segments, no exec)"
)
