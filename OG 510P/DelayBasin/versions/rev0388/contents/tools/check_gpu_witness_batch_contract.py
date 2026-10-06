from collections import Counter

from gpu_witness_contract_specs import iter_gpu_witness_contract_specs
from packet_contract_common import require_standard_packet_and_vocabulary

EXPECTED_GPU_WITNESS_CONTRACTS = 54

rows = list(iter_gpu_witness_contract_specs())
if len(rows) != EXPECTED_GPU_WITNESS_CONTRACTS:
    raise SystemExit(
        f"GPU witness batch expected {EXPECTED_GPU_WITNESS_CONTRACTS} contracts, "
        f"found {len(rows)}"
    )

seen_kinds: set[str] = set()
seen_sources: set[str] = set()
by_segment = Counter(segment for segment, _row in rows)
for segment, row in rows:
    source = row.get("source_checker")
    kwargs = row.get("kwargs")
    if not isinstance(source, str) or not source.startswith("check_gpu_") or not source.endswith("_contract.py"):
        raise SystemExit(f"GPU witness batch has invalid source checker in {segment}: {source!r}")
    if source in seen_sources:
        raise SystemExit(f"GPU witness batch duplicates source checker {source} in {segment}")
    seen_sources.add(source)
    if not isinstance(kwargs, dict):
        raise SystemExit(f"GPU witness batch missing kwargs for {source} in {segment}")
    kind = kwargs.get("kind")
    if not isinstance(kind, str) or not kind.endswith("_witness_contract"):
        raise SystemExit(f"GPU witness batch has invalid kind for {source} in {segment}: {kind!r}")
    if kind in seen_kinds:
        raise SystemExit(f"GPU witness batch duplicates contract kind {kind} in {segment}")
    seen_kinds.add(kind)
    changelog_needles = kwargs.get("changelog_needles", [])
    if source not in changelog_needles:
        raise SystemExit(f"GPU witness batch must preserve historical changelog needle for {source} in {segment}")
    try:
        require_standard_packet_and_vocabulary(**kwargs)
    except SystemExit as exc:
        raise SystemExit(f"{source} [{segment}] failed: {exc}") from exc

print(
    "check_gpu_witness_batch_contract: OK "
    f"({len(rows)} contracts across {len(by_segment)} segments)"
)
