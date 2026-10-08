#!/usr/bin/env python3
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import json
import re
from collections import Counter
from package_release import canonical_release_root_name, is_transient_release_path
from restart_mirror_family import extract_generated_restart_mirror_block, render_generated_restart_mirror_block

root = Path(__file__).resolve().parents[1]
required = [
    'README.md',
    'START_HERE.md',
    'ARCHIVE_INDEX.md',
    'RELEASE-MANIFEST.json',
    'REVISION-RECEIPT.json',
    'context-pack.json',
    'docs/00-meta/bibliography.md',
    'docs/10-method/router-economy-and-demotion-rules.md',
    'docs/20-constitution/claim-registry.md',
    'docs/20-constitution/open-question-registry.md',
    'ROUTER-TOPOLOGY.json',
]

errors = []




def extract_markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    capture = False
    out = []
    for line in lines:
        if line.strip() == heading:
            capture = True
            continue
        if capture and line.startswith('## '):
            break
        if capture:
            out.append(line)
    return "\n".join(out)

def check_markdown_ordered_list_integrity(path: Path, label: str, errors: list[str]) -> None:
    lines = path.read_text().splitlines()
    current_numbers = []
    block_start = None

    def flush() -> None:
        nonlocal current_numbers, block_start
        if current_numbers:
            expected = list(range(current_numbers[0], current_numbers[0] + len(current_numbers)))
            if current_numbers != expected:
                errors.append(f"{label} has non-sequential ordered-list numbering near line {block_start}")
        current_numbers = []
        block_start = None

    for lineno, line in enumerate(lines, start=1):
        m = re.match(r'^(\d+)\.\s', line.strip())
        if m:
            if block_start is None:
                block_start = lineno
            current_numbers.append(int(m.group(1)))
        else:
            flush()
    flush()



for rel in required:
    if not (root / rel).exists():
        errors.append(f'missing required file: {rel}')

if (root / 'docs/README.md').exists():
    errors.append('redundant manual docs index retained: docs/README.md; keep ARCHIVE_INDEX.md as the sole curated navigator')

archive_index_text = (root / 'ARCHIVE_INDEX.md').read_text()
archive_index_doc40_section = ''
in_doc40 = False
for line in archive_index_text.splitlines():
    if line.strip() == '### `docs/40-model`':
        in_doc40 = True
        continue
    if in_doc40 and line.startswith('### '):
        break
    if in_doc40:
        archive_index_doc40_section += line + '\n'
if archive_index_doc40_section.count('`') > 20:
    errors.append('ARCHIVE_INDEX.md regrew into a per-file model index; keep it at compact section/router level and leave exact coverage to ARCHIVE_INDEX.generated.md')

for bad in root.rglob('*.pdf'):
    errors.append(f'pdf retained in archive: {bad.relative_to(root)}')

for bad in root.rglob('*'):
    if bad.is_file() and is_transient_release_path(bad, root):
        errors.append(f'transient build artifact retained in archive tree: {bad.relative_to(root)}')

stable_entry_surfaces = [
    'README.md',
    'docs/00-meta/archive-policy.md',
    'docs/00-meta/llm-runbook.md',
]
release_name_pattern = re.compile(r'Theory-of-Everything-rev\d{4}-\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}-')

revisionless_durable_surfaces = [
    'ASSUMPTION-LEDGER.json',
    'WITNESS-VOCABULARY.json',
    'DATACUBE-TRANSFER-LEDGER.json',
    'FOREIGN-PRESSURE-LEDGER.json',
]
for rel in stable_entry_surfaces:
    text = (root / rel).read_text()
    if release_name_pattern.search(text):
        errors.append(f'hardcoded bundle identity found in stable surface: {rel}')

start_here_text = (root / 'START_HERE.md').read_text()
start_here_release_identity = extract_markdown_section(start_here_text, '## Current release identity')
start_here_without_release_identity = start_here_text.replace(start_here_release_identity, '')
if release_name_pattern.search(start_here_without_release_identity):
    errors.append('hardcoded bundle identity found outside START_HERE current release identity mirror')

for rel in ['docs/00-meta/archive-policy.md', 'docs/00-meta/llm-runbook.md']:
    check_markdown_ordered_list_integrity(root / rel, rel, errors)

archive_policy_text = (root / 'docs/00-meta/archive-policy.md').read_text()
release_discipline = extract_markdown_section(archive_policy_text, '## Release discipline')
if 'keep wedge ownership sharp:' in release_discipline.lower() or re.search(r'^\d+\.\s+If a lane is standby-only', release_discipline, flags=re.MULTILINE):
    errors.append('archive-policy release-discipline section regrew malformed tail rules; keep those control-tail lines out of the release checklist')

llm_runbook_text = (root / 'docs/00-meta/llm-runbook.md').read_text()
research_posture = extract_markdown_section(llm_runbook_text, '## Research posture')

compression_protocol_text = (root / 'docs/10-method/compression-and-deduping-protocol.md').read_text()
router_economy_text = (root / 'docs/10-method/router-economy-and-demotion-rules.md').read_text()
router_topology_text = (root / 'docs/00-meta/router-topology-and-scope-map.md').read_text()
router_topology_ledger = json.loads((root / 'ROUTER-TOPOLOGY.json').read_text())

router_nodes = set(router_topology_ledger.get('routers', {}))
root_router = router_topology_ledger.get('root_router')
if root_router not in router_nodes:
    errors.append('ROUTER-TOPOLOGY.json root_router must name a router present in the ledger')
parent_child_router_pairs = []
for router, meta in router_topology_ledger.get('routers', {}).items():
    parent = meta.get('parent')
    if parent is not None and parent not in router_nodes:
        errors.append(f'ROUTER-TOPOLOGY.json names unknown parent router for {router}: {parent}')
    for child in meta.get('children', []):
        if child in router_nodes:
            parent_child_router_pairs.append((router, child))

router_economy_required_refs = {
    'docs/00-meta/canonical-homes.md': 'docs/10-method/router-economy-and-demotion-rules.md',
    'docs/00-meta/archive-policy.md': 'docs/10-method/router-economy-and-demotion-rules.md',
    'docs/00-meta/llm-runbook.md': 'docs/10-method/router-economy-and-demotion-rules.md',
    'ARCHIVE_INDEX.md': 'router-economy-and-demotion-rules.md',
}
for rel, needle in router_economy_required_refs.items():
    if needle not in (root / rel).read_text():
        errors.append(f'{rel} does not wire the router-economy method surface into the archive-control path')

if 'absorbs **at least two already-live subordinate surfaces**' not in router_economy_text or 'Demotion rule' not in router_economy_text:
    errors.append('router-economy-and-demotion-rules.md lost its admission/demotion core tests')

router_topology_required_refs = {
    'README.md': 'docs/00-meta/router-topology-and-scope-map.md',
    'docs/00-meta/canonical-homes.md': 'docs/00-meta/router-topology-and-scope-map.md',
    'docs/00-meta/archive-policy.md': 'docs/00-meta/router-topology-and-scope-map.md',
    'docs/00-meta/llm-runbook.md': 'docs/00-meta/router-topology-and-scope-map.md',
    'ARCHIVE_INDEX.md': 'router-topology-and-scope-map.md',
    'docs/40-model/current-head-control-router.md': 'docs/00-meta/router-topology-and-scope-map.md',
    'docs/40-model/broad-toe-credit-router.md': 'docs/00-meta/router-topology-and-scope-map.md',
    'docs/40-model/empirical-contact-burden-router.md': 'docs/00-meta/router-topology-and-scope-map.md',
    'docs/40-model/current-family-readout-router.md': 'docs/00-meta/router-topology-and-scope-map.md',
}

router_topology_ledger_required_refs = {
    'README.md': 'ROUTER-TOPOLOGY.json',
    'docs/00-meta/canonical-homes.md': 'ROUTER-TOPOLOGY.json',
    'docs/00-meta/archive-policy.md': 'ROUTER-TOPOLOGY.json',
    'docs/00-meta/llm-runbook.md': 'ROUTER-TOPOLOGY.json',
    'docs/00-meta/router-topology-and-scope-map.md': 'ROUTER-TOPOLOGY.json',
}
for rel, needle in router_topology_required_refs.items():
    if needle not in (root / rel).read_text():
        errors.append(f'{rel} does not wire the router-topology map into the archive-control path')

for rel, needle in router_topology_ledger_required_refs.items():
    if needle not in (root / rel).read_text():
        errors.append(f'{rel} does not wire the machine-readable router-topology ledger into the archive-control path')

if router_topology_ledger.get('machine_source_for') != 'docs/00-meta/router-topology-and-scope-map.md':
    errors.append('ROUTER-TOPOLOGY.json machine_source_for must point to docs/00-meta/router-topology-and-scope-map.md')


def extract_markdown_section_body(text: str, heading: str) -> str:
    pattern = rf'^{re.escape(heading)}\n\n(.*?)(?=^##\s|\Z)'
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ''


def parse_topology_bullet_tree(section_text: str):
    tree = {}
    stack = []
    saw_any = False
    for raw_line in section_text.splitlines():
        if not raw_line.strip():
            continue
        m = re.match(r'^(?P<indent>\s*)-\s+`(?P<path>[^`]+)`\s*$', raw_line)
        if not m:
            continue
        saw_any = True
        indent = len(m.group('indent'))
        if indent % 2 != 0:
            raise ValueError('topology tree indentation must use multiples of two spaces')
        level = indent // 2
        path = m.group('path')
        while stack and stack[-1][0] >= level:
            stack.pop()
        if level > 0 and not stack:
            raise ValueError('topology tree contains an indented child without a parent')
        if stack and level > stack[-1][0] + 1:
            raise ValueError('topology tree skipped an indentation level')
        if stack:
            parent = stack[-1][1]
            tree.setdefault(parent, []).append(path)
        tree.setdefault(path, [])
        stack.append((level, path))
    if not saw_any:
        raise ValueError('topology tree did not contain any bullet nodes')
    return tree

for needle in (
    'docs/40-model/current-head-control-router.md',
    'docs/40-model/broad-toe-credit-router.md',
    'docs/40-model/empirical-contact-burden-router.md',
    'docs/40-model/current-family-readout-router.md',
    'highest matching router',
    'Deepen only the directly touched child surface',
    'Ordered route',
    'mirror ROUTER-TOPOLOGY.json exactly',
):
    if needle not in router_topology_text:
        errors.append('router-topology-and-scope-map.md lost required hierarchy or scope guidance')
        break

topology_body = extract_markdown_section_body(router_topology_text, '## Topology')
try:
    topology_tree = parse_topology_bullet_tree(topology_body)
except ValueError as exc:
    errors.append(f'router-topology-and-scope-map.md has malformed Topology tree: {exc}')
    topology_tree = None

if topology_tree is not None:
    if root_router not in topology_tree:
        errors.append('router-topology-and-scope-map.md Topology tree lost the root router')
    for router, meta in router_topology_ledger.get('routers', {}).items():
        tree_children = topology_tree.get(router)
        if tree_children is None:
            errors.append(f'router-topology-and-scope-map.md Topology tree lost router node {router}')
            continue
        if tree_children != meta.get('children', []):
            errors.append(f'router-topology-and-scope-map.md Topology tree drifted from ROUTER-TOPOLOGY.json children for {router}')

for router, meta in router_topology_ledger.get('routers', {}).items():
    router_path = root / router
    router_text = router_path.read_text()
    ordered_match = re.search(r'## Ordered route\n\n((?:\d+\. .*\n)+)', router_text)
    if not ordered_match:
        errors.append(f'{router} is missing an Ordered route block')
        continue
    ordered_lines = []
    for raw_line in ordered_match.group(1).strip().splitlines():
        m = re.match(r'^\d+\.\s+`([^`]+)`\s*$', raw_line.strip())
        if not m:
            errors.append(f'{router} has malformed Ordered route line: {raw_line.strip()}')
            ordered_lines = None
            break
        ordered_lines.append(m.group(1))
    if ordered_lines is None:
        continue
    ledger_children = meta.get('children', [])
    if ordered_lines != ledger_children:
        errors.append(f'{router} Ordered route drifted from ROUTER-TOPOLOGY.json children')

for needle in (
    'docs/40-model/current-head-control-router.md',
    'docs/40-model/cross-family-pressure-router.md',
    'docs/40-model/empirical-contact-burden-router.md',
    'docs/40-model/broad-toe-credit-router.md',
):
    if needle not in router_topology_ledger.get('routers', {}):
        errors.append('ROUTER-TOPOLOGY.json lost a required top-level router node')
        break

if router_topology_ledger.get('routers', {}).get(root_router, {}).get('parent') is not None:
    errors.append('ROUTER-TOPOLOGY.json root_router must not itself name a parent')

compression_restart_parity_headings = re.findall(r'^## Restart-.* parity rule$', compression_protocol_text, flags=re.MULTILINE)
if len(compression_restart_parity_headings) > 1:
    errors.append('compression-and-deduping-protocol regrew into per-mirror restart-parity headings; keep one shared restart-mirror family rule plus the archive-control growth parity rule')

claim_ladder_text = (root / 'docs/10-method/claim-ladder-and-promotion-rules.md').read_text()
claim_ladder_restart_parity_headings = re.findall(r'^## Restart-.* parity rules$', claim_ladder_text, flags=re.MULTILINE)
if len(claim_ladder_restart_parity_headings) > 1:
    errors.append('claim-ladder-and-promotion-rules regrew into per-mirror restart-parity sections; keep one shared restart-mirror family rule plus the archive-control restart-surface parity rule')

runbook_restart_parity_headings = re.findall(r'^## Restart-.* parity rule$', llm_runbook_text, flags=re.MULTILINE)
if runbook_restart_parity_headings:
    errors.append('llm-runbook regrew standalone per-mirror restart-parity sections; keep restart-mirror family guidance in one shared rule')
if 'keep wedge ownership sharp:' in research_posture.lower():
    errors.append('llm-runbook research-posture section regrew a stray control-tail bullet; keep wedge-ownership rules in the numbered revision pattern only if needed, not as a dangling tail')

claim_registry_lines = (root / 'docs/20-constitution/claim-registry.md').read_text().splitlines()
wired_lines = [line for line in claim_registry_lines if line.startswith('  - Wired docs:')]
for line, count in Counter(wired_lines).items():
    if count > 4:
        errors.append('claim registry repeats an identical wired-doc stack too many times; hoist shared lane routing into one shared note')
        break

fixed_scaffold_phrase = 'support window, proxy family, xerographic family, nearby prior freedom, tail discipline, entry weighting, evidence floor, and objectivity requirement'
claim_registry_text = '\n'.join(claim_registry_lines)
if claim_registry_text.count(fixed_scaffold_phrase) > 1:
    errors.append('claim registry repeats the same heavy fixed-condition scaffold too many times; hoist it into one shared lane note and keep each claim at delta level')


shared_basis_tail = '`REF-0015`, `REF-0016`, `REF-0031`, `REF-0032`'
if claim_registry_text.count(shared_basis_tail) > 2:
    errors.append('claim registry repeats the same shared reference-basis tail too many times; hoist it into one shared lane note and keep each claim basis incremental')


bib = (root / 'docs/00-meta/bibliography.md').read_text()
ids = [line.split('`')[1] for line in bib.splitlines() if line.startswith('- `REF-')]
if len(ids) != len(set(ids)):
    errors.append('duplicate bibliography ids found')

bib_entries = []
current_entry = None
for line in bib.splitlines():
    header = re.match(r'- `(REF-\d+)` — (.+?), \*\*(.+?)\*\* \((.+)\)', line)
    if header:
        current_entry = {
            'rid': header.group(1),
            'authors': header.group(2),
            'title': header.group(3),
            'url': ''
        }
        bib_entries.append(current_entry)
        continue
    if current_entry and line.strip().startswith('- URL:'):
        current_entry['url'] = line.split('URL:', 1)[1].strip()

def normalize_bib_token(value: str) -> str:
    return ' '.join(value.lower().split())

seen_source_keys = {}
for entry in bib_entries:
    source_key = (normalize_bib_token(entry['authors']), normalize_bib_token(entry['title']))
    if source_key in seen_source_keys and seen_source_keys[source_key] != entry['rid']:
        errors.append(f'duplicate bibliography source found for {entry["rid"]} and {seen_source_keys[source_key]}: merge same-source parallel REF ids')
        break
    seen_source_keys[source_key] = entry['rid']

seen_urls = {}
for entry in bib_entries:
    url = entry['url']
    if not url:
        continue
    if url in seen_urls and seen_urls[url] != entry['rid']:
        errors.append(f'duplicate bibliography url found for {entry["rid"]} and {seen_urls[url]}: merge same-source parallel REF ids')
        break
    seen_urls[url] = entry['rid']

try:
    manifest = json.loads((root / 'RELEASE-MANIFEST.json').read_text())
    receipt = json.loads((root / 'REVISION-RECEIPT.json').read_text())
    context = json.loads((root / 'context-pack.json').read_text())
    status = json.loads((root / 'SURFACE-STATUS.json').read_text())
    if manifest['revision'] != receipt['revision']:
        errors.append('manifest and receipt revision mismatch')
    if manifest['revision'] != context['revision']:
        errors.append('manifest and context revision mismatch')
    if manifest['revision'] != status['revision']:
        errors.append('manifest and surface-status revision mismatch')

    broad_summary_sections = {
        'README current posture': extract_markdown_section((root / 'README.md').read_text(), '## Current posture'),
        'trajectory current spine': extract_markdown_section((root / 'docs/00-meta/trajectory-map.md').read_text(), '## Current spine'),
        'context current_posture': '\n'.join(context.get('current_posture', [])),
    }
    for label, section in broad_summary_sections.items():
        for parent_router, child_router in parent_child_router_pairs:
            if parent_router in section and child_router in section:
                errors.append(f'{label} stacks parent and child routers in a broad summary: {parent_router} + {child_router}')

    allowed_receipt_keys = {
        'project', 'revision', 'previous_revision', 'summary', 'revision_kind',
        'move_classes', 'packaged_release', 'scope_state', 'upstream_bundle'
    }
    extra_receipt_keys = set(receipt) - allowed_receipt_keys
    if extra_receipt_keys:
        errors.append(f'revision receipt contains non-durable extra keys: {sorted(extra_receipt_keys)}')
    if 'scope_witness' in receipt:
        errors.append('revision receipt still carries scope_witness; keep one top-level scope_state instead of nested request echo')
    for legacy_key in ('canon_additions', 'refs_used', 'checks_passed', 'touched_surfaces'):
        if legacy_key in receipt:
            errors.append(f'revision receipt still carries legacy task-log field: {legacy_key}')
    if str(receipt.get('scope_state', '')) not in {'exact', 'approximate'}:
        errors.append('revision receipt scope_state must be one of: exact, approximate')
    if 'foreign_pressure_witness' in receipt:
        errors.append('revision receipt still uses foreign_pressure_witness; use one upstream_bundle anchor instead')
    upstream_bundle = str(receipt.get('upstream_bundle', ''))
    expected_upstream_prefix = f"Theory-of-Everything-{receipt.get('previous_revision', '')}-"
    if not upstream_bundle.startswith(expected_upstream_prefix) or not upstream_bundle.endswith('.zip'):
        errors.append('revision receipt upstream_bundle does not point to the previous revision bundle')
    expected_prefix = f"Theory-of-Everything-{manifest['revision']}-{manifest['timestamp']}-"
    if not manifest['bundle'].startswith(expected_prefix):
        errors.append('bundle name does not match manifest revision/timestamp prefix')
    bundle_stem = manifest['bundle'][:-4] if manifest['bundle'].endswith('.zip') else manifest['bundle']
    slug_prefix = expected_prefix
    manifest_slug = str(manifest.get('slug', ''))
    bundle_slug = bundle_stem[len(slug_prefix):] if bundle_stem.startswith(slug_prefix) else ''
    if manifest_slug != bundle_slug:
        errors.append('manifest slug drifted from the bundle suffix')
    if manifest.get('previous_revision') != receipt.get('previous_revision'):
        errors.append('manifest previous_revision drifted from revision receipt previous_revision')
    expected_root_name = canonical_release_root_name(manifest)
    if root.name != expected_root_name:
        errors.append('working-tree root directory drifted from manifest-derived canonical release root')
    for rel in revisionless_durable_surfaces:
        data = json.loads((root / rel).read_text())
        if 'revision' in data:
            errors.append(f'durable surface should be revisionless: {rel}')
    followthrough = json.loads((root / 'FOLLOWTHROUGH-QUEUE.json').read_text())
    for item in followthrough:
        if item.get('state') != 'active':
            errors.append(f'followthrough queue contains non-active item: {item.get("id", "<missing-id>")}')
        title = str(item.get('title', ''))
        next_point = str(item.get('next_proof_point', ''))
        if title.startswith('Reopen ') and ('only if' in title.lower() or 'unless' in title.lower() or 'only if' in next_point.lower() or 'unless' in next_point.lower()):
            errors.append(f'followthrough queue contains trigger-only reopen residue: {item.get("id", "<missing-id>")}')

    assumption_ledger = json.loads((root / 'ASSUMPTION-LEDGER.json').read_text())
    allowed_assumption_states = {'active', 'retired-by-revision', 'standby-threshold'}
    retired_detailed = []
    for item in assumption_ledger.get('assumptions', []):
        state = item.get('state')
        if state not in allowed_assumption_states:
            errors.append(f'assumption ledger contains unknown state: {item.get("id", "<missing-id>")} -> {state}')
        statement = str(item.get('statement', '')).lower()
        if state == 'active' and 'reopen' in statement and ('only if' in statement or 'unless' in statement):
            errors.append(f'assumption ledger contains trigger-only reopen assumption marked active: {item.get("id", "<missing-id>")}')
        if state == 'retired-by-revision':
            retired_detailed.append(item.get('id', '<missing-id>'))
    if len(retired_detailed) > 3:
        errors.append('assumption ledger carries too many detailed retired assumptions; compress older chains into grouped retired phase history')
    if status.get('active_followthrough_count') == 0:
        tactical_markers = ('next useful move', 'next highest-leverage move', 'next best')
        for item in assumption_ledger.get('assumptions', []):
            if item.get('state') != 'active':
                continue
            statement = str(item.get('statement', '')).lower()
            if statement.startswith('after ') or any(marker in statement for marker in tactical_markers):
                errors.append(f'assumption ledger keeps tactical next-move guidance active while the queue is empty: {item.get("id", "<missing-id>")}')
    for item in assumption_ledger.get('retired_phase_history', []):
        if item.get('state') != 'grouped-retired-history':
            errors.append(f'assumption ledger contains malformed retired phase history entry: {item.get("id_range", "<missing-range>")}')


    start_here_text = (root / 'START_HERE.md').read_text()
    expected_generated_block = render_generated_restart_mirror_block({
        'manifest': manifest,
        'receipt': receipt,
        'context': context,
        'status': status,
    })
    try:
        actual_generated_block = extract_generated_restart_mirror_block(start_here_text)
    except ValueError as exc:
        errors.append(str(exc))
        actual_generated_block = None
    if actual_generated_block is not None and actual_generated_block != expected_generated_block:
        errors.append('START_HERE generated restart mirror family block drifted from canonical sources')

    meta_expectations = {
        'current_posture_human_mirror': 'START_HERE.md',
        'current_posture_source': 'canonical-machine-source',
        'priority_open_question_human_mirror': 'START_HERE.md',
        'priority_open_question_source': 'canonical-machine-source',
        'operator_warning_human_mirror': 'START_HERE.md',
        'operator_warning_source': 'canonical-machine-source',
        'queue_and_standby_human_mirror': 'START_HERE.md',
        'queue_and_standby_source': 'canonical-machine-source',
        'command_human_mirror': 'START_HERE.md',
        'command_source': 'canonical-machine-source',
        'assumption_state_human_mirror': 'START_HERE.md',
        'assumption_state_source': 'canonical-machine-source',
        'entry_surface_human_mirror': 'START_HERE.md',
        'entry_surface_source': 'canonical-machine-source',
    }
    for key, expected in meta_expectations.items():
        if context.get(key) != expected:
            errors.append(f'context-pack {key} must remain {expected} for the restart-mirror family')

    entry_surfaces = context.get('entry_surfaces', {})

    assumption_summary = context.get('assumption_state_summary', {})
    expected_active_assumption_count = sum(1 for item in assumption_ledger.get('assumptions', []) if item.get('state') == 'active')
    expected_standby_ids = [item.get('id') for item in assumption_ledger.get('assumptions', []) if item.get('state') == 'standby-threshold']
    if context.get('active_followthrough_count') != len(followthrough):
        errors.append('context-pack active_followthrough_count drifted from FOLLOWTHROUGH-QUEUE.json')
    if assumption_summary.get('active_count') != expected_active_assumption_count:
        errors.append('context-pack assumption_state_summary active_count drifted from ASSUMPTION-LEDGER.json')
    if assumption_summary.get('standby_threshold_count') != len(expected_standby_ids):
        errors.append('context-pack assumption_state_summary standby_threshold_count drifted from ASSUMPTION-LEDGER.json')
    if assumption_summary.get('standby_threshold_ids', []) != expected_standby_ids:
        errors.append('context-pack assumption_state_summary standby_threshold_ids drifted from ASSUMPTION-LEDGER.json')
    if status.get('active_assumption_count') != expected_active_assumption_count:
        errors.append('SURFACE-STATUS active_assumption_count drifted from ASSUMPTION-LEDGER.json')
    if status.get('standby_threshold_assumption_ids', []) != expected_standby_ids:
        errors.append('SURFACE-STATUS standby_threshold_assumption_ids drifted from ASSUMPTION-LEDGER.json')

    registry_text = (root / 'docs/20-constitution/open-question-registry.md').read_text()
    registry_question_ids = re.findall(r'`(OQ-\d{4})`', registry_text)
    if 'open_questions' in context:
        errors.append('context-pack still uses ambiguous open_questions; label restart-priority subsets explicitly and anchor them to the canonical registry')
    priority_open_question_ids = context.get('priority_open_question_ids', [])
    open_question_registry_path = root / 'docs/20-constitution/open-question-registry.md'
    for lineno, line in enumerate(open_question_registry_path.read_text().splitlines(), start=1):
        if line.strip().startswith('- Current posture:') and len(line.strip()) > 260:
            errors.append(f'open-question registry current posture regrew into mini-history near line {lineno}; keep mature-lane posture at claim-level summary plus canonical anchors')

    if priority_open_question_ids:
        if context.get('open_question_registry_anchor') != 'docs/20-constitution/open-question-registry.md':
            errors.append('context-pack priority_open_question_ids lost the canonical open-question registry anchor')
        if not str(context.get('priority_open_question_basis', '')).strip():
            errors.append('context-pack priority_open_question_ids require a basis describing why the list is a subset')
        missing_priority_ids = [qid for qid in priority_open_question_ids if qid not in registry_question_ids]
        if missing_priority_ids:
            errors.append(f'context-pack priority_open_question_ids contain ids not present in the registry: {missing_priority_ids}')
        standby_only_priority_ids = {'OQ-0018', 'OQ-0019', 'OQ-0020', 'OQ-0021'}
        if status.get('active_followthrough_count') == 0 and status.get('state_class') == 'closed-lane-standby':
            leaked_priority_ids = sorted(standby_only_priority_ids & set(priority_open_question_ids))
            if leaked_priority_ids:
                errors.append(f'context-pack priority_open_question_ids still include mature standby cosmology / measure questions while the lane is closed-under-threshold: {leaked_priority_ids}')

    wedges_text = (root / 'docs/40-model/discriminator-wedges.md').read_text()
    w5_match = re.search(r'## W-0005.*?(?=\n## W-0006)', wedges_text, re.S)
    if w5_match:
        w5_text = w5_match.group(0)
        if 'sign-only timing wedge' in w5_text or 'relative-ordering discriminator sketch' in w5_text:
            errors.append('W-0005 replayed closed local-measure residue details; keep that lane routed through W-0006 / CL-0049 instead')

    def extract_makefile_commands(makefile_text):
        cmds = []
        for line in makefile_text.splitlines():
            m = re.match(r'^([A-Za-z0-9_-]+):\s*$', line.strip())
            if m:
                cmds.append(f'make {m.group(1)}')
        return cmds

    operator_warnings = context.get('operator_warnings', [])
    if len(operator_warnings) > 6:
        errors.append('context-pack operator_warnings regrew beyond a compact high-risk subset; route the full rule set to archive-policy.md instead')
    if operator_warnings and context.get('operator_warning_anchor') != 'docs/00-meta/archive-policy.md':
        errors.append('context-pack operator_warning_anchor must point to docs/00-meta/archive-policy.md when warnings are present')

    commands = context.get('commands', [])
    makefile_commands = extract_makefile_commands((root / 'Makefile').read_text())
    if commands and context.get('command_anchor') != 'Makefile':
        errors.append('context-pack command_anchor must point to Makefile when commands are present')
    if commands != makefile_commands:
        errors.append('context-pack commands drifted from Makefile targets')

    standby_thresholds = context.get('standby_thresholds', [])
    standby_assumption_ids = [item.get('assumption_id') for item in standby_thresholds]
    if standby_assumption_ids != expected_standby_ids:
        errors.append('context-pack standby_thresholds drifted from ASSUMPTION-LEDGER.json standby-threshold assumptions')

    closed_lane_default_docs = {
        'docs/40-model/discriminator-wedges.md',
        'docs/40-model/measure-population-typicality-audit.md',
    }
    if status.get('active_followthrough_count') == 0 and status.get('state_class') == 'closed-lane-standby':
        continued = set(context.get('restart_tiers', {}).get('continuation_30min', []))
        closed_in_default = sorted(closed_lane_default_docs & continued)
        if closed_in_default:
            errors.append('closed-lane standby docs still sit in the default 30-minute continuation tier; route them through targeted deepen notes instead')
        start_text = (root / 'START_HERE.md').read_text()
        explicit_measure_note = 'If you are touching the closed measure / population / typicality residue directly'
        if explicit_measure_note not in start_text:
            errors.append('START_HERE lost the explicit targeted note for the closed measure lane')
        for doc in sorted(closed_lane_default_docs):
            lines_with_doc = [line.strip() for line in start_text.splitlines() if doc in line]
            if any(explicit_measure_note not in line for line in lines_with_doc):
                errors.append('START_HERE lets closed-lane standby docs hitchhike through a broad deepen bucket; route them only through the explicit targeted note')
        readme_text = (root / 'README.md').read_text()
        closed_lane_markers = [
            'docs/40-model/discriminator-wedges.md',
            'docs/40-model/measure-population-typicality-audit.md',
        ]
        if any(marker in readme_text for marker in closed_lane_markers):
            errors.append('stable README still contains closed-lane file-path routing detail while the queue is empty; keep it at claim-and-threshold level and route through targeted deepen notes instead')
        warning = status.get('warning', '')
        if 'docs/40-model/' in warning or '30-minute continuation' in warning:
            errors.append('SURFACE-STATUS warning still contains closed-lane routing detail while the queue is empty; keep it at claim-and-threshold level')

        for rel in ['docs/30-program/workstreams.md', 'docs/30-program/bridge-experiments.md', 'docs/30-program/research-frontiers.md']:
            for line in (root / rel).read_text().splitlines():
                if 'CL-0049' in line and 'docs/40-model/' in line:
                    errors.append(f'{rel} still mixes closed-lane claim-level summary with file-path routing while the queue is empty; keep routing in canonical lane homes or targeted deepen notes instead')
        workstreams_text = (root / 'docs/30-program/workstreams.md').read_text()
        if 'docs/40-model/measure-population-typicality-audit.md' in workstreams_text:
            errors.append('workstreams still list the closed measure / population / typicality audit as a direct key surface while the lane is standby-only; keep that routing in canonical lane homes or targeted deepen notes instead')

    witness_stage_markers = [
        'asymptotic or observer-relative observable',
        'cross-frame witness portability',
        'public reference standard',
        'diachronic witness lineage',
        'cross-site reproducibility',
        'intervention-grade control',
        'drift-resilient autonomy',
        'public auditability',
        'assertibility',
        'public adjudication',
        'public evidence custody',
        'fresh-host reinstantiation',
        'independent implementation',
        'independent evidence-generation',
        'candidate-native witness closure',
        'candidate-native intervention closure',
        'candidate-native counterfactual closure',
        'candidate-native threshold closure',
        'candidate-native identifiability closure',
    ]
    for rel, max_hits in [
        ('docs/00-meta/trajectory-map.md', 12),
        ('docs/30-program/bridge-experiments.md', 16),
        ('docs/40-model/spine.md', 8),
        ('docs/00-meta/canonical-homes.md', 6),
        ('README.md', 6),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in witness_stage_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the witness-package subgate stack; name the stack and route to spine / witness-borrowing ladder / newest unpaid gate instead')


    continuation_30min = context.get('restart_tiers', {}).get('continuation_30min', [])
    witness_stack_paths = {
        'docs/40-model/asymptotic-access-vs-local-witness-closure-gate.md',
        'docs/40-model/single-frame-access-vs-cross-frame-witness-portability-gate.md',
        'docs/40-model/cross-frame-portability-vs-public-reference-standard-closure-gate.md',
        'docs/40-model/public-reference-standard-vs-diachronic-witness-lineage-closure-gate.md',
        'docs/40-model/diachronic-witness-lineage-vs-cross-site-reproducibility-closure-gate.md',
        'docs/40-model/cross-site-reproducibility-vs-intervention-grade-control-closure-gate.md',
        'docs/40-model/intervention-grade-control-vs-drift-resilient-autonomy-closure-gate.md',
        'docs/40-model/drift-resilient-autonomy-vs-public-auditability-closure-gate.md',
        'docs/40-model/public-auditability-vs-assertibility-closure-gate.md',
        'docs/40-model/assertibility-vs-public-adjudication-closure-gate.md',
        'docs/40-model/public-adjudication-vs-public-evidence-custody-closure-gate.md',
        'docs/40-model/public-evidence-custody-vs-fresh-host-reinstantiation-closure-gate.md',
        'docs/40-model/fresh-host-reinstantiation-vs-independent-implementation-closure-gate.md',
        'docs/40-model/independent-implementation-vs-independent-evidence-generation-closure-gate.md',
        'docs/40-model/independent-evidence-generation-vs-candidate-native-witness-closure-gate.md',
        'docs/40-model/candidate-native-witness-vs-candidate-native-intervention-closure-gate.md',
        'docs/40-model/candidate-native-intervention-vs-candidate-native-counterfactual-closure-gate.md',
        'docs/40-model/candidate-native-counterfactual-vs-candidate-native-threshold-closure-gate.md',
        'docs/40-model/candidate-native-threshold-vs-candidate-native-identifiability-closure-gate.md',
    }
    continuation_witness_paths = [p for p in continuation_30min if p in witness_stack_paths]
    if len(continuation_witness_paths) > 4:
        errors.append('context-pack continuation_30min replays too much of the witness-package gate ladder; route default restart through witness-package-subgate-stack.md and only the few directly relevant frontier surfaces')


    cross_family_router = 'docs/40-model/cross-family-pressure-router.md'
    cross_family_markers = [
        'candidate-bridges.md',
        'invariant-matrix.md',
        'discriminator-wedges.md',
    ]
    for rel, max_hits in [
        ('README.md', 2),
        ('docs/40-model/spine.md', 2),
        ('docs/30-program/workstreams.md', 3),
        ('docs/30-program/bridge-experiments.md', 3),
        ('START_HERE.md', 1),
        ('context-pack.json', 1),
        ('docs/00-meta/archive-policy.md', 3),
        ('docs/00-meta/llm-runbook.md', 3),
        ('docs/00-meta/trajectory-map.md', 2),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in cross_family_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the broad cross-family pressure trio; name cross-family-pressure-router.md instead')

    for rel in [
        'README.md',
        'docs/40-model/spine.md',
        'docs/30-program/workstreams.md',
        'docs/30-program/bridge-experiments.md',
        'docs/00-meta/archive-policy.md',
        'docs/00-meta/llm-runbook.md',
        'docs/00-meta/trajectory-map.md',
    ]:
        if cross_family_router not in (root / rel).read_text() and 'docs/40-model/current-head-control-router.md' not in (root / rel).read_text():
            errors.append(f'{rel} does not route broad cross-family pressure through cross-family-pressure-router.md or current-head-control-router.md')

    cross_family_router_text = (root / cross_family_router).read_text()
    for marker in [
        'docs/40-model/candidate-bridges.md',
        'docs/40-model/invariant-matrix.md',
        'docs/40-model/discriminator-wedges.md',
    ]:
        if marker not in cross_family_router_text:
            errors.append('cross-family pressure router does not point to the full subordinate cross-family route')

    for rel in [
        'docs/40-model/candidate-bridges.md',
        'docs/40-model/invariant-matrix.md',
        'docs/40-model/discriminator-wedges.md',
    ]:
        if cross_family_router not in (root / rel).read_text():
            errors.append(f'{rel} does not route broad cross-family pressure through cross-family-pressure-router.md')

    current_head_router = 'docs/40-model/current-head-control-router.md'
    current_head_markers = [
        'docs/40-model/spine.md',
        'docs/40-model/empirical-contact-burden-router.md',
        'docs/40-model/broad-toe-credit-router.md',
    ]
    current_head_required_markers = [
        'docs/40-model/spine.md',
        'docs/40-model/cross-family-pressure-router.md',
        'docs/40-model/empirical-contact-burden-router.md',
        'docs/40-model/broad-toe-credit-router.md',
    ]
    continuation_head_paths = [p for p in continuation_30min if p in current_head_markers]
    if len(continuation_head_paths) > 2:
        errors.append('context-pack continuation_30min replays too much of the current-head control quartet; route default restart through current-head-control-router.md instead')
    if current_head_router not in continuation_30min:
        errors.append('context-pack continuation_30min does not route default head control through current-head-control-router.md')

    for rel, max_hits in [
        ('README.md', 1),
        ('START_HERE.md', 5),
        ('context-pack.json', 1),
        ('docs/00-meta/archive-policy.md', 5),
        ('docs/00-meta/llm-runbook.md', 4),
        ('docs/00-meta/trajectory-map.md', 2),
        ('docs/30-program/workstreams.md', 8),
        ('docs/30-program/bridge-experiments.md', 2),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in current_head_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the current-head control quartet; name current-head-control-router.md instead')

    for rel in [
        'README.md',
        'START_HERE.md',
        'context-pack.json',
        'docs/00-meta/archive-policy.md',
        'docs/00-meta/llm-runbook.md',
        'docs/00-meta/trajectory-map.md',
        'docs/30-program/workstreams.md',
        'docs/30-program/bridge-experiments.md',
    ]:
        if current_head_router not in (root / rel).read_text():
            errors.append(f'{rel} does not route default current-head control through current-head-control-router.md')

    current_head_router_text = (root / current_head_router).read_text()
    for marker in current_head_required_markers:
        if marker not in current_head_router_text:
            errors.append('current-head control router does not point to the full subordinate head route')

    empirical_contact_markers = [
        'observer-record-minimum.md',
        'witness-borrowing-ladder.md',
        'witness-package-burden-router.md',
    ]
    for rel, max_hits in [
        ('README.md', 2),
        ('docs/40-model/spine.md', 2),
        ('docs/30-program/workstreams.md', 8),
        ('docs/30-program/bridge-experiments.md', 2),
        ('START_HERE.md', 5),
        ('context-pack.json', 2),
        ('docs/00-meta/archive-policy.md', 3),
        ('docs/00-meta/llm-runbook.md', 3),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in empirical_contact_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the broad empirical-contact control trio; name empirical-contact-burden-router.md instead')

    empirical_contact_router_text = (root / 'docs/40-model/empirical-contact-burden-router.md').read_text()
    for marker in [
        'docs/40-model/observer-record-minimum.md',
        'docs/40-model/witness-borrowing-ladder.md',
        'docs/40-model/witness-package-burden-router.md',
    ]:
        if marker not in empirical_contact_router_text:
            errors.append('empirical-contact burden router does not point to the full subordinate empirical-contact route')

    for rel in [
        'docs/40-model/observer-record-minimum.md',
        'docs/40-model/witness-borrowing-ladder.md',
        'docs/40-model/witness-package-burden-router.md',
    ]:
        if 'docs/40-model/empirical-contact-burden-router.md' not in (root / rel).read_text():
            errors.append(f'{rel} does not route broad empirical-contact control through empirical-contact-burden-router.md')

    witness_gate_path_markers = [
        'asymptotic-access-vs-local-witness-closure-gate.md',
        'single-frame-access-vs-cross-frame-witness-portability-gate.md',
        'cross-frame-portability-vs-public-reference-standard-closure-gate.md',
        'public-reference-standard-vs-diachronic-witness-lineage-closure-gate.md',
        'diachronic-witness-lineage-vs-cross-site-reproducibility-closure-gate.md',
        'cross-site-reproducibility-vs-intervention-grade-control-closure-gate.md',
        'intervention-grade-control-vs-drift-resilient-autonomy-closure-gate.md',
        'drift-resilient-autonomy-vs-public-auditability-closure-gate.md',
        'public-auditability-vs-assertibility-closure-gate.md',
        'assertibility-vs-public-adjudication-closure-gate.md',
        'public-adjudication-vs-public-evidence-custody-closure-gate.md',
        'public-evidence-custody-vs-fresh-host-reinstantiation-closure-gate.md',
        'fresh-host-reinstantiation-vs-independent-implementation-closure-gate.md',
        'independent-implementation-vs-independent-evidence-generation-closure-gate.md',
        'independent-evidence-generation-vs-candidate-native-witness-closure-gate.md',
        'candidate-native-witness-vs-candidate-native-intervention-closure-gate.md',
        'candidate-native-intervention-vs-candidate-native-counterfactual-closure-gate.md',
        'candidate-native-counterfactual-vs-candidate-native-threshold-closure-gate.md',
        'candidate-native-threshold-vs-candidate-native-identifiability-closure-gate.md',
    ]
    three_book_split_text = (root / 'docs/40-model/local-law-vs-cosmological-package-vs-witness-package-split.md').read_text()
    if 'docs/40-model/witness-package-burden-router.md' not in three_book_split_text:
        errors.append('local-law-vs-cosmological-package-vs-witness-package-split.md does not route witness-stage detail through witness-package-burden-router.md')
    witness_gate_hits = sum(three_book_split_text.count(marker) for marker in witness_gate_path_markers)
    if witness_gate_hits > 0:
        errors.append('local-law-vs-cosmological-package-vs-witness-package-split.md still replays explicit witness gate filepaths; route that ladder through witness-package-burden-router.md instead')

    workstreams_text = (root / 'docs/30-program/workstreams.md').read_text()
    if workstreams_text.count('subgate preventing') > 4:
        errors.append('docs/30-program/workstreams.md replays too much of the witness-stage ladder in prose; route that summary through witness-package-burden-router.md instead')

    witness_credit_markers = [
        'witness-borrowing-ladder.md',
        'witness-package-subgate-stack.md',
        'witness-closure-gate-family-frame.md',
    ]
    for rel, max_hits in [
        ('README.md', 1),
        ('docs/40-model/spine.md', 1),
        ('docs/30-program/bridge-experiments.md', 1),
        ('docs/00-meta/trajectory-map.md', 1),
        ('START_HERE.md', 1),
        ('context-pack.json', 1),
        ('docs/00-meta/archive-policy.md', 1),
        ('docs/00-meta/llm-runbook.md', 4),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in witness_credit_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the broad witness-package control trio; name witness-package-burden-router.md instead')

    for rel in [
        'docs/40-model/witness-borrowing-ladder.md',
        'docs/40-model/witness-package-subgate-stack.md',
        'docs/40-model/witness-closure-gate-family-frame.md',
        'docs/40-model/cross-family-candidate-native-identifiability-audit.md',
    ]:
        if 'docs/40-model/witness-package-burden-router.md' not in (root / rel).read_text():
            errors.append(f'{rel} does not route broad witness-package control through witness-package-burden-router.md')

    for rel in [
        'docs/40-model/witness-package-subgate-stack.md',
        'docs/40-model/witness-closure-gate-family-frame.md',
    ]:
        if 'docs/40-model/empirical-contact-burden-router.md' not in (root / rel).read_text():
            errors.append(f'{rel} does not route broad empirical-contact prerequisites through empirical-contact-burden-router.md')

    witness_gate_files = [root / rel for rel in witness_stack_paths if (root / rel).exists()]
    shared_frame_ref_count = 0
    empirical_contact_ref_count = 0
    direct_prereq_hits = 0
    gate_scaffold_hits = 0
    for gate_path in witness_gate_files:
        gate_text = gate_path.read_text()
        if 'docs/40-model/witness-closure-gate-family-frame.md' in gate_text:
            shared_frame_ref_count += 1
        if 'docs/40-model/empirical-contact-burden-router.md' in gate_text:
            empirical_contact_ref_count += 1
        direct_prereq_hits += gate_text.count('docs/40-model/observer-record-minimum.md')
        direct_prereq_hits += gate_text.count('docs/40-model/witness-borrowing-ladder.md')
        gate_scaffold_hits += gate_text.count('The archive already had:')
        gate_scaffold_hits += gate_text.count('What it still lacked was one compact warning against')
    witness_router_text = (root / 'docs/40-model/witness-package-burden-router.md').read_text()
    if 'docs/40-model/witness-borrowing-ladder.md' not in witness_router_text or 'docs/40-model/witness-package-subgate-stack.md' not in witness_router_text or 'docs/40-model/witness-closure-gate-family-frame.md' not in witness_router_text:
        errors.append('witness-package burden router does not point to the borrowing ladder, stage stack, and shared gate frame')

    if witness_gate_files and shared_frame_ref_count < len(witness_gate_files):
        errors.append('not all pairwise witness-package gates route shared scaffolding through witness-closure-gate-family-frame.md')
    if witness_gate_files and empirical_contact_ref_count < len(witness_gate_files):
        errors.append('not all pairwise witness-package gates route shared empirical-contact prerequisites through empirical-contact-burden-router.md')
    if direct_prereq_hits > 0:
        errors.append('pairwise witness-package gates still replay observer-record-minimum.md or witness-borrowing-ladder.md directly; route those prerequisites through empirical-contact-burden-router.md instead')
    if gate_scaffold_hits > 4:
        errors.append('witness-package gate family still replays too much shared boilerplate; route archive-level scaffolding through witness-closure-gate-family-frame.md and keep each gate at pair-specific delta')


    family_b_broad_markers = [
        'thermodynamic-gravity-assumption-audit.md',
        'non-equilibrium-observable-record-map.md',
        'family-b-witness-climb-audit.md',
        'family-b-beyond-equilibrium-gate.md',
    ]
    for rel, max_hits in [
        ('docs/40-model/spine.md', 2),
        ('docs/30-program/workstreams.md', 2),
        ('docs/30-program/bridge-experiments.md', 2),
        ('docs/40-model/candidate-bridges.md', 2),
        ('START_HERE.md', 5),
        ('README.md', 1),
        ('docs/00-meta/archive-policy.md', 5),
        ('docs/00-meta/llm-runbook.md', 2),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in family_b_broad_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the broad family-B control lane; name family-b-burden-router.md instead')
    for rel in [
        'docs/30-program/workstreams.md',
        'docs/30-program/bridge-experiments.md',
        'docs/40-model/candidate-bridges.md',
    ]:
        if 'docs/40-model/family-b-burden-router.md' not in (root / rel).read_text():
            errors.append(f'{rel} does not route broad family-B control through family-b-burden-router.md')
    for rel in [
        'START_HERE.md',
    ]:
        text = (root / rel).read_text()
        if 'docs/40-model/family-b-burden-router.md' not in text and 'docs/40-model/current-family-readout-router.md' not in text and 'docs/40-model/current-head-control-router.md' not in text:
            errors.append(f'{rel} does not route broad family-B control through family-b-burden-router.md, current-family-readout-router.md, or current-head-control-router.md')
    spine_text = (root / 'docs/40-model/spine.md').read_text()
    if 'docs/40-model/family-b-burden-router.md' not in spine_text and 'docs/40-model/current-family-readout-router.md' not in spine_text:
        errors.append('docs/40-model/spine.md does not route broad family-B control through family-b-burden-router.md or current-family-readout-router.md')

    for rel in [
        'docs/40-model/thermodynamic-gravity-assumption-audit.md',
        'docs/40-model/non-equilibrium-observable-record-map.md',
        'docs/40-model/family-b-witness-climb-audit.md',
        'docs/40-model/family-b-beyond-equilibrium-gate.md',
    ]:
        if 'docs/40-model/family-b-burden-router.md' not in (root / rel).read_text():
            errors.append(f'{rel} does not route broad family-B control through family-b-burden-router.md')

    family_c_broad_markers = [
        'family-c-witness-closure-gate.md',
        'family-c-identifiability-stack.md',
        'cross-family-candidate-native-identifiability-audit.md',
    ]
    for rel, max_hits in [
        ('docs/40-model/spine.md', 2),
        ('docs/30-program/workstreams.md', 2),
        ('context-pack.json', 2),
        ('START_HERE.md', 5),
        ('docs/00-meta/archive-policy.md', 2),
        ('docs/00-meta/llm-runbook.md', 2),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in family_c_broad_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the broad family-C control lane; name family-c-burden-router.md instead')
    for rel in [
        'docs/30-program/workstreams.md',
    ]:
        if 'docs/40-model/family-c-burden-router.md' not in (root / rel).read_text():
            errors.append(f'{rel} does not route broad family-C control through family-c-burden-router.md')
    for rel in [
        'context-pack.json',
        'START_HERE.md',
    ]:
        text = (root / rel).read_text()
        if 'docs/40-model/family-c-burden-router.md' not in text and 'docs/40-model/current-family-readout-router.md' not in text and 'docs/40-model/current-head-control-router.md' not in text:
            errors.append(f'{rel} does not route broad family-C control through family-c-burden-router.md, current-family-readout-router.md, or current-head-control-router.md')
    spine_text = (root / 'docs/40-model/spine.md').read_text()
    if 'docs/40-model/family-c-burden-router.md' not in spine_text and 'docs/40-model/current-family-readout-router.md' not in spine_text:
        errors.append('docs/40-model/spine.md does not route broad family-C control through family-c-burden-router.md or current-family-readout-router.md')

    current_family_markers = [
        'family-b-burden-router.md',
        'family-c-burden-router.md',
    ]
    for rel, max_hits in [
        ('README.md', 1),
        ('docs/40-model/spine.md', 1),
        ('context-pack.json', 2),
        ('START_HERE.md', 5),
        ('docs/00-meta/archive-policy.md', 5),
        ('docs/00-meta/llm-runbook.md', 4),
        ('docs/00-meta/trajectory-map.md', 2),
        ('docs/30-program/workstreams.md', 8),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in current_family_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the broad current-family readout lane; name current-family-readout-router.md instead')
    for rel in [
        'README.md',
        'docs/40-model/spine.md',
        'context-pack.json',
        'START_HERE.md',
        'docs/00-meta/archive-policy.md',
        'docs/00-meta/llm-runbook.md',
        'docs/00-meta/trajectory-map.md',
    ]:
        text = (root / rel).read_text()
        if 'docs/40-model/current-family-readout-router.md' not in text and 'docs/40-model/current-head-control-router.md' not in text:
            errors.append(f'{rel} does not route broad current-family readout through current-family-readout-router.md or current-head-control-router.md')

    family_c_stack_markers = [
        'family-c-partial-identification-audit.md',
        'family-c-inverse-portability-screen.md',
        'family-c-nonuniqueness-triage.md',
        'family-c-overlap-class-screen.md',
        'family-c-thin-data-vs-acquirable-witness-screen.md',
        'family-c-inverse-stability-and-regularization-screen.md',
        'family-c-recoverand-vs-surrogate-screen.md',
        'family-c-point-estimate-vs-calibrated-solution-bundle-screen.md',
        'family-c-abstention-competence-vs-soft-confidence-screen.md',
        'family-c-selective-safety-vs-discriminator-coverage-screen.md',
        'family-c-policy-choice-vs-candidate-order-stability-screen.md',
        'family-c-order-stability-vs-separation-margin-screen.md',
    ]
    for rel, max_hits in [
        ('docs/40-model/spine.md', 4),
        ('docs/30-program/workstreams.md', 8),
        ('context-pack.json', 3),
        ('START_HERE.md', 3),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in family_c_stack_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the family-C identifiability chain; name the stack and route to family-c-identifiability-stack.md instead')

    family_c_stack_files = [root / rel for rel in family_c_stack_markers if (root / rel).exists()]
    family_c_stack_ref_count = 0
    for p in family_c_stack_files:
        if 'docs/40-model/family-c-identifiability-stack.md' in p.read_text():
            family_c_stack_ref_count += 1
    if family_c_stack_files and family_c_stack_ref_count < len(family_c_stack_files):
        errors.append('not all family-C chain docs route shared order / stack cautions through family-c-identifiability-stack.md')
    for rel in [
        'docs/40-model/family-c-identifiability-stack.md',
        'docs/40-model/family-c-witness-closure-gate.md',
        'docs/40-model/cross-family-candidate-native-identifiability-audit.md',
    ]:
        if 'docs/40-model/family-c-burden-router.md' not in (root / rel).read_text():
            errors.append(f'{rel} does not route broad family-C control through family-c-burden-router.md')


    current_family_router_text = (root / 'docs/40-model/current-family-readout-router.md').read_text()
    for marker in [
        'docs/40-model/family-b-burden-router.md',
        'docs/40-model/family-c-burden-router.md',
    ]:
        if marker not in current_family_router_text:
            errors.append('current-family readout router does not point to family-B and family-C burden routers')

    vacuum_stack_markers = [
        'cosmological-constant-debt-split-audit.md',
        'unimodular-integration-constant-audit.md',
        'sequestering-global-constraint-audit.md',
        'self-tuning-relaxation-audit.md',
        'anthropic-landscape-selection-audit.md',
        'measure-population-typicality-audit.md',
    ]
    for rel, max_hits in [
        ('README.md', 1),
        ('docs/30-program/workstreams.md', 2),
        ('START_HERE.md', 1),
        ('docs/40-model/spine.md', 2),
        ('docs/00-meta/archive-policy.md', 2),
        ('docs/00-meta/llm-runbook.md', 2),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in vacuum_stack_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the broad vacuum-energy control lane; name vacuum-energy-burden-router.md instead')

    completion_credit_markers = [
        'uv-completion-atlas.md',
        'completion-bid-cashout-sieve.md',
        'completion-bid-comparison-stack.md',
        'completion-bid-comparison-gate-family-frame.md',
    ]
    for rel, max_hits in [
        ('README.md', 2),
        ('docs/40-model/spine.md', 2),
        ('docs/30-program/workstreams.md', 2),
        ('docs/30-program/bridge-experiments.md', 2),
        ('START_HERE.md', 5),
        ('context-pack.json', 2),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in completion_credit_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the broad completion-bid control quartet; name completion-bid-credit-stack.md instead')

    for rel in [
        'docs/40-model/uv-completion-atlas.md',
        'docs/40-model/completion-bid-cashout-sieve.md',
        'docs/40-model/completion-bid-comparison-stack.md',
        'docs/40-model/completion-bid-comparison-gate-family-frame.md',
    ]:
        if 'docs/40-model/completion-bid-credit-stack.md' not in (root / rel).read_text():
            errors.append(f'{rel} does not route broad completion-bid control through completion-bid-credit-stack.md')

    broad_toe_markers = [
        'completion-bid-credit-stack.md',
        'local-law-vs-cosmological-package-vs-witness-package-split.md',
        'vacuum-energy-burden-router.md',
        'witness-package-burden-router.md',
        'current-family-readout-router.md',
    ]
    for rel, max_hits in [
        ('README.md', 2),
        ('docs/40-model/spine.md', 2),
        ('context-pack.json', 3),
        ('docs/00-meta/archive-policy.md', 5),
        ('docs/00-meta/llm-runbook.md', 5),
        ('docs/00-meta/trajectory-map.md', 4),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in broad_toe_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the broad ToE control quintet; name broad-toe-credit-router.md instead')

    for rel in [
        'docs/40-model/spine.md',
        'docs/00-meta/archive-policy.md',
        'docs/00-meta/llm-runbook.md',
    ]:
        if 'docs/40-model/broad-toe-credit-router.md' not in (root / rel).read_text():
            errors.append(f'{rel} does not route broad ToE credit through broad-toe-credit-router.md')
    for rel in [
        'README.md',
        'START_HERE.md',
        'context-pack.json',
        'docs/00-meta/trajectory-map.md',
    ]:
        text = (root / rel).read_text()
        if 'docs/40-model/broad-toe-credit-router.md' not in text and 'docs/40-model/current-head-control-router.md' not in text:
            errors.append(f'{rel} does not route broad ToE credit through broad-toe-credit-router.md or current-head-control-router.md')

    for rel in [
        'docs/40-model/completion-bid-credit-stack.md',
        'docs/40-model/local-law-vs-cosmological-package-vs-witness-package-split.md',
        'docs/40-model/vacuum-energy-burden-router.md',
        'docs/40-model/witness-package-burden-router.md',
        'docs/40-model/current-family-readout-router.md',
    ]:
        if 'docs/40-model/broad-toe-credit-router.md' not in (root / rel).read_text():
            errors.append(f'{rel} does not route integrated broad ToE control through broad-toe-credit-router.md')

    broad_router_text = (root / 'docs/40-model/broad-toe-credit-router.md').read_text()
    for marker in [
        'docs/40-model/completion-bid-credit-stack.md',
        'docs/40-model/local-law-vs-cosmological-package-vs-witness-package-split.md',
        'docs/40-model/vacuum-energy-burden-router.md',
        'docs/40-model/witness-package-burden-router.md',
        'docs/40-model/current-family-readout-router.md',
    ]:
        if marker not in broad_router_text:
            errors.append('broad ToE credit router does not point to the full subordinate control route')

    completion_stack_markers = [
        'matter-sector-recovery-gate.md',
        'parameter-fixation-gate.md',
        'benchmark-portability-gate.md',
        'fit-vs-prediction-gate.md',
        'prediction-vs-discrimination-gate.md',
        'discrimination-vs-acquisition-gate.md',
        'acquisition-vs-attribution-gate.md',
        'attribution-vs-ranking-gate.md',
        'ranking-vs-allocation-gate.md',
        'allocation-vs-retirement-gate.md',
        'retirement-vs-exclusion-gate.md',
        'exclusion-vs-salvage-gate.md',
        'salvage-vs-import-gate.md',
        'import-vs-assimilation-gate.md',
        'assimilation-vs-convergence-gate.md',
        'convergence-vs-closure-gate.md',
    ]
    for rel, max_hits in [
        ('docs/40-model/spine.md', 4),
        ('docs/00-meta/canonical-homes.md', 3),
        ('README.md', 3),
        ('START_HERE.md', 5),
        ('docs/30-program/bridge-experiments.md', 4),
    ]:
        text = (root / rel).read_text()
        marker_hits = sum(text.count(marker) for marker in completion_stack_markers)
        if marker_hits > max_hits:
            errors.append(f'{rel} replays too much of the post-cash-out completion-bid comparison ladder; name the stack and route to completion-bid-comparison-stack.md instead')

    if 'docs/40-model/completion-bid-comparison-stack.md' not in (root / 'docs/40-model/completion-bid-cashout-sieve.md').read_text():
        errors.append('completion-bid cash-out sieve does not route ordered post-cash-out stage handling through completion-bid-comparison-stack.md')

    completion_gate_files = [root / ('docs/40-model/' + rel) for rel in completion_stack_markers if (root / ('docs/40-model/' + rel)).exists()]
    completion_frame_ref_count = 0
    completion_gate_scaffold_hits = 0
    for gate_path in completion_gate_files:
        gate_text = gate_path.read_text()
        if 'docs/40-model/completion-bid-comparison-gate-family-frame.md' in gate_text:
            completion_frame_ref_count += 1
        completion_gate_scaffold_hits += gate_text.count('Those are related, but they are not the same achievement.')
        completion_gate_scaffold_hits += gate_text.count('Those are related achievements, but they are not the same achievement.')
        completion_gate_scaffold_hits += gate_text.count('Those are not the same decision.')
        completion_gate_scaffold_hits += gate_text.count('Those are not the same verdict.')
        completion_gate_scaffold_hits += gate_text.count('This gate preserves a compact distinction the atlas now needs:')
        completion_gate_scaffold_hits += gate_text.count('This gate preserves one more compact distinction the atlas now needs:')
    if completion_gate_files and completion_frame_ref_count < len(completion_gate_files):
        errors.append('not all pairwise completion-comparison gates route shared scaffolding through completion-bid-comparison-gate-family-frame.md')
    if completion_gate_scaffold_hits > 4:
        errors.append('completion-comparison gate family still replays too much shared boilerplate; route archive-level scaffolding through completion-bid-comparison-gate-family-frame.md and keep each gate at pair-specific delta')
    if 'docs/40-model/completion-bid-comparison-gate-family-frame.md' not in (root / 'docs/40-model/completion-bid-comparison-stack.md').read_text():
        errors.append('completion-bid comparison stack does not route shared gate scaffolding through completion-bid-comparison-gate-family-frame.md')

    vacuum_stack_files = [root / ('docs/40-model/' + rel) for rel in vacuum_stack_markers if (root / ('docs/40-model/' + rel)).exists()]
    vacuum_stack_ref_count = 0
    vacuum_frame_ref_count = 0
    vacuum_router_ref_count = 0
    vacuum_family_scaffold_hits = 0
    for p in vacuum_stack_files:
        vacuum_text = p.read_text()
        if 'docs/40-model/vacuum-energy-proposal-class-stack.md' in vacuum_text:
            vacuum_stack_ref_count += 1
        if 'docs/40-model/vacuum-energy-proposal-class-family-frame.md' in vacuum_text:
            vacuum_frame_ref_count += 1
        if 'docs/40-model/vacuum-energy-burden-router.md' in vacuum_text:
            vacuum_router_ref_count += 1
        vacuum_family_scaffold_hits += vacuum_text.count('Its job is not to')
        vacuum_family_scaffold_hits += vacuum_text.count('Its job is to stop the archive from')
        vacuum_family_scaffold_hits += vacuum_text.count('This document is the **')
    if vacuum_stack_files and vacuum_stack_ref_count < len(vacuum_stack_files):
        errors.append('not all vacuum-energy proposal-class docs route shared order / stack cautions through vacuum-energy-proposal-class-stack.md')
    if vacuum_stack_files and vacuum_frame_ref_count < len(vacuum_stack_files):
        errors.append('not all vacuum-energy proposal-class docs route shared family scaffolding through vacuum-energy-proposal-class-family-frame.md')
    if vacuum_stack_files and vacuum_router_ref_count < len(vacuum_stack_files):
        errors.append('not all vacuum-energy proposal-class docs route broad control through vacuum-energy-burden-router.md')
    if vacuum_family_scaffold_hits > 3:
        errors.append('vacuum-energy proposal-class audit family still replays too much shared boilerplate; route archive-level burden scaffolding through vacuum-energy-proposal-class-family-frame.md and keep each audit at proposal-class delta')
    if 'docs/40-model/vacuum-energy-proposal-class-family-frame.md' not in (root / 'docs/40-model/vacuum-energy-proposal-class-stack.md').read_text():
        errors.append('vacuum-energy proposal-class stack does not route shared audit scaffolding through vacuum-energy-proposal-class-family-frame.md')
    if 'docs/40-model/vacuum-energy-burden-router.md' not in (root / 'docs/40-model/vacuum-energy-proposal-class-stack.md').read_text():
        errors.append('vacuum-energy proposal-class stack does not route broad control through vacuum-energy-burden-router.md')
    if 'docs/40-model/vacuum-energy-burden-router.md' not in (root / 'docs/40-model/vacuum-energy-proposal-class-family-frame.md').read_text():
        errors.append('vacuum-energy proposal-class family frame does not route broad control through vacuum-energy-burden-router.md')
    if 'docs/40-model/vacuum-energy-burden-router.md' not in (root / 'docs/40-model/cosmological-constant-debt-split-audit.md').read_text():
        errors.append('cosmological-constant debt split audit does not route broad control through vacuum-energy-burden-router.md')
    vacuum_router_text = (root / 'docs/40-model/vacuum-energy-burden-router.md').read_text()
    if 'docs/40-model/vacuum-energy-proposal-class-stack.md' not in vacuum_router_text or 'docs/40-model/vacuum-energy-proposal-class-family-frame.md' not in vacuum_router_text:
        errors.append('vacuum-energy burden router does not point to both the proposal-class stack and shared family frame')

    repeated_cosmo_stack = 'unimodular, sequestering, self-tuning / relaxation, anthropic / landscape-selection'
    repeated_cosmo_count = 0
    for rel in ['docs/30-program/workstreams.md', 'docs/30-program/bridge-experiments.md', 'docs/30-program/research-frontiers.md']:
        repeated_cosmo_count += (root / rel).read_text().count(repeated_cosmo_stack)
    if repeated_cosmo_count > 1:
        errors.append('program surfaces keep re-listing the mature cosmological proposal-class stack; summarize it once at burden-split / claim level instead')

    trajectory_text = (root / 'docs/00-meta/trajectory-map.md').read_text()
    trajectory_lines = trajectory_text.splitlines()
    in_spine = False
    spine_bullets = []
    for line in trajectory_lines:
        stripped = line.strip()
        if stripped == '## Current spine':
            in_spine = True
            continue
        if in_spine and line.startswith('## '):
            break
        if in_spine and stripped.startswith('- '):
            spine_bullets.append(stripped)
    if len(spine_bullets) > 18:
        errors.append('trajectory map current spine is overgrown; compress absorbed micro-history into grouped backbone statements')

    trajectory_heading = None
    in_priorities = False
    seen_numbers = []
    for line in trajectory_lines:
        stripped = line.strip()
        if stripped in {'## Near-term priorities', '## Current preservation priorities (while the queue is empty)'}:
            trajectory_heading = stripped
            in_priorities = True
            continue
        if in_priorities and line.startswith('## '):
            break
        if in_priorities and re.match(r'^\d+\. ', line):
            seen_numbers.append(int(line.split('.', 1)[0]))
    if seen_numbers:
        expected = list(range(seen_numbers[0], seen_numbers[0] + len(seen_numbers)))
        if seen_numbers != expected:
            errors.append('trajectory priority numbering drifted out of sequence')
    if status.get('active_followthrough_count') == 0 and '## Near-term priorities' in trajectory_text:
        errors.append('trajectory map still uses `Near-term priorities` while the active queue is empty; switch to preservation / standby language')

    changelog_text = (root / 'CHANGELOG.md').read_text()
    if '## Current head' in changelog_text:
        errors.append('changelog still contains stale Current head marker')
    detailed_heads = re.findall(r'^### rev\d{4}\b', changelog_text, flags=re.MULTILINE)
    if len(detailed_heads) > 6:
        errors.append('changelog carries too many detailed revision closeouts; compress older history into phase summaries')
    wedges_text = (root / 'docs/40-model/discriminator-wedges.md').read_text()
    if status.get('active_followthrough_count') == 0 and 'W-0006' in wedges_text and 'The next best move is' in wedges_text:
        errors.append("closed discriminator wedge surface still carries faux-forward `The next best move` narration while the active queue is empty")
    if status.get('active_followthrough_count') == 0 and ('no active followthrough item' in wedges_text.lower() or 'live followthrough queue' in wedges_text.lower()):
        errors.append('closed discriminator wedge surface still narrates global queue state while the active queue is empty; keep only admissibility, stop rule, and reopen threshold')
    if status.get('active_followthrough_count') == 0:
        measure_audit_text = (root / 'docs/40-model/measure-population-typicality-audit.md').read_text()
        if 'closes the next queue item' in measure_audit_text:
            errors.append('closed measure audit still carries stale queue-closing narration while the active queue is empty; keep the substantive tests but remove old task voice')

    if status.get('active_followthrough_count') == 0:
        for rel in ['docs/30-program/workstreams.md', 'docs/30-program/research-frontiers.md', 'docs/30-program/bridge-experiments.md']:
            text = (root / rel).read_text().lower()
            if 'no active followthrough item' in text or 'no active queue item' in text:
                errors.append(f'{rel} still narrates global queue state inside a lane summary while the active queue is empty; keep program mirrors at claim/threshhold level')


    for label, payload in [('manifest', manifest), ('surface-status', status)]:
        state_class = str(payload.get('state_class', ''))
        if any(token in state_class for token in ('W-000', 'CL-00', 'AS-00')):
            errors.append(f'{label} state_class should be generic archive state, not a specific scientific id')
except Exception as e:
    errors.append(f'json parse failure: {e}')

if errors:
    print('LINT FAILED')
    for e in errors:
        print('-', e)
    sys.exit(1)

print('LINT OK')

