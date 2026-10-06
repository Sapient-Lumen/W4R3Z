import pathlib
import re
import sys
from collections import Counter
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from method_doc_ratchet_contract_specs import iter_method_doc_ratchet_contract_specs

PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
EXPECTED_METHOD_DOC_RATCHET_CONTRACTS = 18
ALLOWED_ROW_KEYS = {"source_checker", "doc_path", "doc_needles", "prompt_runbook_needles"}
WORD_RE = re.compile(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*")
MIN_SOURCE_DOC_WORDS = 900
MAX_DOC_NEEDLES = 16
MAX_PROMPT_RUNBOOK_NEEDLES = 5
MAX_NEEDLE_CHAR_FRACTION = 0.20


def _require_text(path: pathlib.Path, label: str) -> str:
    if not path.exists():
        raise SystemExit(f"{label}: missing surface {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def _check_needles(segment: str, source: str, label: str, text: str, needles: list[str]) -> None:
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"{source} [{segment}] missing {label}: " + ", ".join(missing))


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


rows = list(iter_method_doc_ratchet_contract_specs())
if len(rows) != EXPECTED_METHOD_DOC_RATCHET_CONTRACTS:
    raise SystemExit(
        f"method-doc ratchet batch expected {EXPECTED_METHOD_DOC_RATCHET_CONTRACTS} contracts, found {len(rows)}"
    )

prompt_text = _require_text(PROMPTS, "method-doc ratchet batch")
runbook_text = _require_text(RUNBOOK, "method-doc ratchet batch")
seen_sources: set[str] = set()
by_segment = Counter(segment for segment, _row in rows)
for segment, row in rows:
    if set(row) != ALLOWED_ROW_KEYS:
        raise SystemExit(f"method-doc ratchet spec has unsupported keys in {segment}: {sorted(row)}")
    source = row.get("source_checker")
    doc_path = row.get("doc_path")
    doc_needles = row.get("doc_needles")
    ratchet_needles = row.get("prompt_runbook_needles")
    if not isinstance(source, str) or not source.startswith("check_") or not source.endswith("_contract.py"):
        raise SystemExit(f"method-doc ratchet spec has invalid source checker in {segment}: {source!r}")
    if source in seen_sources:
        raise SystemExit(f"method-doc ratchet spec duplicates source checker: {source}")
    seen_sources.add(source)
    if not isinstance(doc_path, str) or not doc_path.startswith("docs/10-method/"):
        raise SystemExit(f"{source} [{segment}] has invalid doc_path: {doc_path!r}")
    if not isinstance(doc_needles, list) or not 4 <= len(doc_needles) <= MAX_DOC_NEEDLES or not all(isinstance(item, str) and item for item in doc_needles):
        raise SystemExit(f"{source} [{segment}] has invalid doc needles")
    if not isinstance(ratchet_needles, list) or not 3 <= len(ratchet_needles) <= MAX_PROMPT_RUNBOOK_NEEDLES or not all(isinstance(item, str) and item for item in ratchet_needles):
        raise SystemExit(f"{source} [{segment}] has invalid prompt/runbook ratchet needles")
    if (ROOT / "tools" / source).exists():
        raise SystemExit(f"former method-doc ratchet wrapper still exists: tools/{source}")
    doc_text = _require_text(ROOT / doc_path, source)
    if _word_count(doc_text) < MIN_SOURCE_DOC_WORDS:
        raise SystemExit(f"{source} [{segment}] source document is too small to remain the semantic source")
    if sum(len(needle) for needle in doc_needles) > len(doc_text) * MAX_NEEDLE_CHAR_FRACTION:
        raise SystemExit(f"{source} [{segment}] doc needles are too large; spec is drifting toward semantic substitution")
    _check_needles(segment, source, "doc needles", doc_text, doc_needles)
    _check_needles(segment, source, "prompt ratchet needles", prompt_text, ratchet_needles)
    _check_needles(segment, source, "runbook ratchet needles", runbook_text, ratchet_needles)

print(
    "check_method_doc_ratchet_batch_contract: OK "
    f"({len(rows)} contracts across {len(by_segment)} segments; source docs remain semantic surfaces)"
)
