#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "cooperation_benchmark_card.schema.json"
FREEZE_RECEIPT_SCHEMA_PATH = ROOT / "schemas" / "cooperation_benchmark_card_freeze_receipt.schema.json"
DELTA_RECEIPT_SCHEMA_PATH = ROOT / "schemas" / "cooperation_benchmark_card_delta_receipt.schema.json"
DEFAULT_NOTES = (
    "TODO: optional notes; keep explicit 'not applicable: ...' strings for intentionally "
    "inapplicable fields rather than omitting required rows."
)
SECTION_ORDER = [
    "comparison_license",
    "lane_contract",
    "score_construction",
    "metric_governance",
    "uncertainty_and_dependence",
    "variant_selection",
    "evaluated_subject",
    "environment_and_knowledge",
    "execution_budget",
    "scenario_sampling",
    "failure_handling",
    "adjudication",
]
SECTION_TITLES = {
    "comparison_license": "Comparison license",
    "lane_contract": "Lane contract",
    "score_construction": "Score construction",
    "metric_governance": "Metric governance",
    "uncertainty_and_dependence": "Uncertainty and dependence",
    "variant_selection": "Variant selection",
    "evaluated_subject": "Evaluated subject",
    "environment_and_knowledge": "Environment and knowledge",
    "execution_budget": "Execution budget",
    "scenario_sampling": "Scenario sampling",
    "failure_handling": "Failure handling",
    "adjudication": "Adjudication",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))



def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()



def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()



def path_for_receipt(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()

def scalar_field_map(obj: Any, path: tuple[str, ...] = ()) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            out.update(scalar_field_map(value, path + (str(key),)))
        return out
    if isinstance(obj, list):
        for idx, value in enumerate(obj):
            out.update(scalar_field_map(value, path + (str(idx),)))
        return out
    out['.'.join(path)] = obj
    return out


METADATA_ONLY_PATHS = {'schema_version', 'id', 'benchmark_name', 'notes'}


def classify_changed_paths(paths: list[str]) -> tuple[list[str], list[str]]:
    claim_surface = [path for path in paths if path not in METADATA_ONLY_PATHS]
    metadata_only = [path for path in paths if path in METADATA_ONLY_PATHS]
    return claim_surface, metadata_only



def try_validate(obj: Any, schema: dict[str, Any]) -> bool:
    try:
        jsonschema.validate(obj, schema)
    except jsonschema.ValidationError:
        return False
    return True


def collect_card_inventory_snapshot() -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    card_schema = load_json(SCHEMA_PATH)
    delta_schema = load_json(DELTA_RECEIPT_SCHEMA_PATH)
    cards: dict[str, dict[str, Any]] = {}
    delta_receipts: list[dict[str, Any]] = []

    for path in sorted(ROOT.rglob('*.json')):
        rel = path_for_receipt(path)
        if rel.startswith('.git/'):
            continue
        obj = load_json(path)
        if try_validate(obj, card_schema):
            issues = list(readiness_issues(obj))
            cards[rel] = {
                'id': obj['id'],
                'path': rel,
                'claim_ready': not issues,
                'predecessor_card_ids': [],
                'successor_card_ids': [],
            }
            continue
        if try_validate(obj, delta_schema):
            delta_receipts.append({
                'old_card_id': obj['old_card_id'],
                'new_card_id': obj['new_card_id'],
                'old_card_path': obj['old_card_path'],
                'new_card_path': obj['new_card_path'],
            })

    for receipt in delta_receipts:
        old_card = cards.get(receipt['old_card_path'])
        new_card = cards.get(receipt['new_card_path'])
        if old_card is None or new_card is None:
            continue
        if old_card['id'] != receipt['old_card_id'] or new_card['id'] != receipt['new_card_id']:
            continue
        old_card['successor_card_ids'].append(receipt['new_card_id'])
        new_card['predecessor_card_ids'].append(receipt['old_card_id'])

    for row in cards.values():
        row['predecessor_card_ids'].sort()
        row['successor_card_ids'].sort()
        row['latest_known'] = not row['successor_card_ids']
    return cards, delta_receipts


def guarded_freeze_context(input_path: Path, card_id: str) -> dict[str, Any]:
    cards, _ = collect_card_inventory_snapshot()
    rel = path_for_receipt(input_path)
    row = cards.get(rel)
    if row is None or row['id'] != card_id:
        raise RuntimeError('card not found in repository inventory snapshot')

    by_id = {entry['id']: entry for entry in cards.values()}
    neighbors: dict[str, set[str]] = {entry['id']: set() for entry in cards.values()}
    for entry in cards.values():
        for other in entry['predecessor_card_ids'] + entry['successor_card_ids']:
            if other in by_id:
                neighbors[entry['id']].add(other)
                neighbors[other].add(entry['id'])

    seen = {card_id}
    queue = deque([card_id])
    component_ids: list[str] = []
    while queue:
        cur = queue.popleft()
        component_ids.append(cur)
        for nxt in sorted(neighbors.get(cur, set())):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)

    component = [by_id[cur] for cur in sorted(component_ids)]
    roots = sorted(entry['id'] for entry in component if not entry['predecessor_card_ids'])
    lineage_id = roots[0] if roots else card_id
    operational_heads = sorted(entry['id'] for entry in component if entry['claim_ready'] and entry['latest_known'])
    if len(operational_heads) != 1:
        raise RuntimeError(
            'guarded freeze requires exactly one current operational head; '
            f'lineage {lineage_id} has {len(operational_heads)} ({", ".join(operational_heads) or "none"})'
        )
    if operational_heads[0] != card_id:
        raise RuntimeError(
            'guarded freeze refused: '
            f'{card_id} is not the current operational head for lineage {lineage_id} '
            f'(current: {operational_heads[0]})'
        )
    return {
        'guard_kind': 'require_unique_operational_head',
        'lineage_id': lineage_id,
        'observed_operational_head_card_ids': operational_heads,
        'matched_card_id': card_id,
    }

def resolve_ref(ref: str, root_schema: dict[str, Any]) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported $ref: {ref}")
    node: Any = root_schema
    for part in ref[2:].split("/"):
        node = node[part]
    if not isinstance(node, dict):
        raise ValueError(f"expected dict at $ref {ref}")
    return node


def scaffold_value(schema: dict[str, Any], root_schema: dict[str, Any], path: tuple[str, ...]) -> Any:
    if "$ref" in schema:
        return scaffold_value(resolve_ref(schema["$ref"], root_schema), root_schema, path)
    if "const" in schema:
        return schema["const"]
    enum = schema.get("enum")
    if path == ("result_kind",):
        return "comparative"
    if path == ("id",):
        return "TODO: benchmark-card-id"
    if path == ("benchmark_name",):
        return "TODO: benchmark name"
    if schema.get("type") == "object":
        required = list(schema.get("required", []))
        out: dict[str, Any] = {}
        props = schema.get("properties", {})
        for key in required:
            out[key] = scaffold_value(props[key], root_schema, path + (key,))
        if path == () and "notes" in props:
            out["notes"] = DEFAULT_NOTES
        return out
    if enum:
        return enum[0]
    if schema.get("type") == "string":
        dotted = ".".join(path)
        return f"TODO: fill {dotted} or write 'not applicable: ...'"
    if schema.get("type") == "integer":
        return 0
    raise ValueError(f"unsupported schema fragment at {'.'.join(path) or '<root>'}")



def apply_overrides(card: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    if args.id:
        card["id"] = args.id
    if args.benchmark_name:
        card["benchmark_name"] = args.benchmark_name
    if args.result_kind:
        card["result_kind"] = args.result_kind
    if args.notes:
        card["notes"] = args.notes
    return card



def validate_card(card: dict[str, Any], schema: dict[str, Any]) -> None:
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(card, schema)



def slug_to_label(key: str) -> str:
    return key.replace("_", " ")



def walk_string_fields(obj: Any, path: tuple[str, ...] = ()):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from walk_string_fields(value, path + (str(key),))
        return
    if isinstance(obj, list):
        for idx, value in enumerate(obj):
            yield from walk_string_fields(value, path + (str(idx),))
        return
    if isinstance(obj, str):
        yield path, obj



def readiness_issues(card: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for path, value in walk_string_fields(card):
        lowered = value.strip().lower()
        dotted = '.'.join(path)
        if 'todo:' in lowered or lowered.startswith('todo'):
            issues.append(f"{dotted}: unresolved TODO placeholder")
        if lowered == 'not applicable' or lowered == 'n/a':
            issues.append(f"{dotted}: bare not-applicable marker; add a short reason")
        elif lowered.startswith('not applicable') and ':' not in lowered and ' because ' not in lowered:
            issues.append(f"{dotted}: not-applicable marker should include a reason")
    return issues



def render_card(card: dict[str, Any]) -> str:
    lines = [
        f"# Cooperation Benchmark Card — {card['benchmark_name']}",
        "",
        f"- id: `{card['id']}`",
        f"- result_kind: `{card['result_kind']}`",
        f"- schema_version: `{card['schema_version']}`",
    ]
    notes = str(card.get("notes", "")).strip()
    if notes:
        lines.append(f"- notes: {notes}")
    lines.append("")
    for section_key in SECTION_ORDER:
        section = card[section_key]
        lines.append(f"## {SECTION_TITLES[section_key]}")
        lines.append("")
        for field, value in section.items():
            lines.append(f"- **{slug_to_label(field)}**: {value}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"



def write_text(output_path: Path | None, text: str) -> None:
    if output_path is None:
        sys.stdout.write(text)
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")



def cmd_scaffold(args: argparse.Namespace) -> int:
    schema = load_json(SCHEMA_PATH)
    card = scaffold_value(schema, schema, ())
    assert isinstance(card, dict)
    card = apply_overrides(card, args)
    validate_card(card, schema)
    write_text(Path(args.output) if args.output else None, json.dumps(card, indent=2, sort_keys=False) + "\n")
    return 0



def cmd_render(args: argparse.Namespace) -> int:
    schema = load_json(SCHEMA_PATH)
    input_path = Path(args.input)
    card = load_json(input_path)
    validate_card(card, schema)
    write_text(Path(args.output) if args.output else None, render_card(card))
    return 0



def cmd_lint(args: argparse.Namespace) -> int:
    schema = load_json(SCHEMA_PATH)
    input_path = Path(args.input)
    card = load_json(input_path)
    validate_card(card, schema)
    issues = readiness_issues(card)
    if issues:
        for issue in issues:
            print(f"cooperation-benchmark-card-lint: {issue}", file=sys.stderr)
        return 1
    field_count = sum(1 for _ in walk_string_fields(card))
    print(f"cooperation-benchmark-card-lint: ok ({field_count} string fields checked)")
    print(f"cooperation-benchmark-card-lint: claim-ready {input_path}")
    return 0




def cmd_freeze(args: argparse.Namespace) -> int:
    card_schema = load_json(SCHEMA_PATH)
    receipt_schema = load_json(FREEZE_RECEIPT_SCHEMA_PATH)
    input_path = Path(args.input)
    card = load_json(input_path)
    validate_card(card, card_schema)
    issues = readiness_issues(card)
    if issues:
        for issue in issues:
            print(f"cooperation-benchmark-card-freeze: {issue}", file=sys.stderr)
        return 1

    render_path = Path(args.render_output) if args.render_output else input_path.with_suffix('.md')
    receipt_path = Path(args.receipt_output) if args.receipt_output else input_path.with_suffix('.freeze_receipt.json')

    rendered = render_card(card)
    write_text(render_path, rendered)

    lineage_guard = None
    if args.require_current_operational_head:
        try:
            lineage_guard = guarded_freeze_context(input_path, card["id"])
        except RuntimeError as exc:
            print(f"cooperation-benchmark-card-freeze: {exc}", file=sys.stderr)
            return 1

    receipt = {
        "schema_version": 1,
        "receipt_kind": "cooperation_benchmark_card_freeze_receipt",
        "card_id": card["id"],
        "benchmark_name": card["benchmark_name"],
        "result_kind": card["result_kind"],
        "card_path": path_for_receipt(input_path),
        "card_sha256": sha256_file(input_path),
        "rendered_markdown_path": path_for_receipt(render_path),
        "rendered_markdown_sha256": sha256_text(rendered),
        "card_schema_path": path_for_receipt(SCHEMA_PATH),
        "card_schema_sha256": sha256_file(SCHEMA_PATH),
        "freeze_tool_path": path_for_receipt(Path(__file__)),
        "freeze_tool_sha256": sha256_file(Path(__file__)),
        "claim_ready": True,
    }
    if lineage_guard is not None:
        receipt["lineage_guard"] = lineage_guard
    jsonschema.Draft202012Validator.check_schema(receipt_schema)
    jsonschema.validate(receipt, receipt_schema)
    write_text(receipt_path, json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(f"cooperation-benchmark-card-freeze: claim-ready {input_path}")
    print(f"cooperation-benchmark-card-freeze: wrote {path_for_receipt(render_path)}")
    print(f"cooperation-benchmark-card-freeze: wrote {path_for_receipt(receipt_path)}")
    return 0



def cmd_compare(args: argparse.Namespace) -> int:
    card_schema = load_json(SCHEMA_PATH)
    receipt_schema = load_json(DELTA_RECEIPT_SCHEMA_PATH)
    old_input = Path(args.old_input)
    new_input = Path(args.new_input)
    old_card = load_json(old_input)
    new_card = load_json(new_input)
    validate_card(old_card, card_schema)
    validate_card(new_card, card_schema)

    old_issues = readiness_issues(old_card)
    new_issues = readiness_issues(new_card)
    if old_issues or new_issues:
        for issue in old_issues:
            print(f"cooperation-benchmark-card-compare: old card {issue}", file=sys.stderr)
        for issue in new_issues:
            print(f"cooperation-benchmark-card-compare: new card {issue}", file=sys.stderr)
        return 1

    old_map = scalar_field_map(old_card)
    new_map = scalar_field_map(new_card)
    changed = sorted(path for path in sorted(set(old_map) | set(new_map)) if old_map.get(path) != new_map.get(path))
    claim_surface_changed, metadata_only_changed = classify_changed_paths(changed)

    receipt = {
        "schema_version": 1,
        "receipt_kind": "cooperation_benchmark_card_delta_receipt",
        "old_card_id": old_card["id"],
        "new_card_id": new_card["id"],
        "old_card_path": path_for_receipt(old_input),
        "old_card_sha256": sha256_file(old_input),
        "new_card_path": path_for_receipt(new_input),
        "new_card_sha256": sha256_file(new_input),
        "changed_field_paths": changed,
        "claim_surface_changed_field_paths": claim_surface_changed,
        "metadata_only_changed_field_paths": metadata_only_changed,
        "claim_surface_changed": bool(claim_surface_changed),
        "delta_tool_path": path_for_receipt(Path(__file__)),
        "delta_tool_sha256": sha256_file(Path(__file__)),
    }
    jsonschema.Draft202012Validator.check_schema(receipt_schema)
    jsonschema.validate(receipt, receipt_schema)
    receipt_path = Path(args.receipt_output) if args.receipt_output else new_input.with_suffix('.delta_receipt.json')
    write_text(receipt_path, json.dumps(receipt, indent=2, sort_keys=False) + "\n")
    print(f"cooperation-benchmark-card-compare: compared {path_for_receipt(old_input)} -> {path_for_receipt(new_input)}")
    print(
        "cooperation-benchmark-card-compare: "
        f"{len(changed)} changed fields; "
        f"claim-surface={len(claim_surface_changed)} metadata-only={len(metadata_only_changed)}"
    )
    print(f"cooperation-benchmark-card-compare: wrote {path_for_receipt(receipt_path)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scaffold or render cooperation benchmark cards.")
    sub = parser.add_subparsers(dest="command", required=True)

    scaffold = sub.add_parser("scaffold", help="Emit a compact valid scaffold JSON card.")
    scaffold.add_argument("--id", help="Card id override.")
    scaffold.add_argument("--benchmark-name", help="Benchmark name override.")
    scaffold.add_argument(
        "--result-kind",
        choices=["comparative", "descriptive", "method_note"],
        help="Result kind override.",
    )
    scaffold.add_argument("--notes", help="Optional notes override.")
    scaffold.add_argument("--output", help="Write scaffold JSON to a file instead of stdout.")
    scaffold.set_defaults(func=cmd_scaffold)

    render = sub.add_parser("render", help="Render a valid JSON card to compact markdown.")
    render.add_argument("input", help="Path to a JSON cooperation benchmark card.")
    render.add_argument("--output", help="Write markdown output to a file instead of stdout.")
    render.set_defaults(func=cmd_render)

    lint = sub.add_parser("lint", help="Check that a valid card is claim-ready rather than scaffold-draft only.")
    lint.add_argument("input", help="Path to a JSON cooperation benchmark card.")
    lint.set_defaults(func=cmd_lint)

    freeze = sub.add_parser("freeze", help="Validate, lint, render, and emit a compact freeze receipt for a claim-ready card.")
    freeze.add_argument("input", help="Path to a JSON cooperation benchmark card.")
    freeze.add_argument("--render-output", help="Write canonical markdown render to this path (default: sibling .md).")
    freeze.add_argument("--receipt-output", help="Write compact freeze receipt JSON to this path (default: sibling .freeze_receipt.json).")
    freeze.add_argument(
        "--require-current-operational-head",
        action="store_true",
        help="Fail closed unless this card is still the unique current claim-ready operational head of its retained lineage.",
    )
    freeze.set_defaults(func=cmd_freeze)

    compare = sub.add_parser("compare", help="Validate, lint, and emit a compact delta receipt between two claim-ready cards.")
    compare.add_argument("old_input", help="Path to the older JSON cooperation benchmark card.")
    compare.add_argument("new_input", help="Path to the newer JSON cooperation benchmark card.")
    compare.add_argument("--receipt-output", help="Write compact delta receipt JSON to this path (default: sibling .delta_receipt.json next to new_input).")
    compare.set_defaults(func=cmd_compare)
    return parser



def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
