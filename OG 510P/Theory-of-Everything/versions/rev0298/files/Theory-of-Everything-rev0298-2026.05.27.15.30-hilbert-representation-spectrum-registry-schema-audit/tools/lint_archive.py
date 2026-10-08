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

changelog_text = (root / 'CHANGELOG.md').read_text()
changelog_first_nonempty = next((line.strip() for line in changelog_text.splitlines() if line.strip()), '')
if changelog_first_nonempty != '# Changelog':
    errors.append('CHANGELOG.md must begin with # Changelog as its first nonempty line')

claim_registry_raw_for_boundary = (root / 'docs/20-constitution/claim-registry.md').read_text()
if re.search(r'[^\n]- `CL-\d{4}`', claim_registry_raw_for_boundary):
    errors.append('claim-registry has a CL entry that does not begin on its own line')
if re.search(r'[^\n]- `OQ-\d{4}`', (root / 'docs/20-constitution/open-question-registry.md').read_text()):
    errors.append('open-question-registry has an OQ entry that does not begin on its own line')

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

witness_vocab = json.loads((root / 'WITNESS-VOCABULARY.json').read_text())
allowed_claim_statuses = set(witness_vocab.get('status_labels', []))
for lineno, line in enumerate(claim_registry_lines, start=1):
    m = re.match(r'^  - Status: (.+)$', line)
    if m and m.group(1).strip() not in allowed_claim_statuses:
        errors.append(f'claim registry status not present in WITNESS-VOCABULARY.json near line {lineno}: {m.group(1).strip()}')


bib = (root / 'docs/00-meta/bibliography.md').read_text()
ids = [line.split('`')[1] for line in bib.splitlines() if line.startswith('- `REF-')]
if len(ids) != len(set(ids)):
    errors.append('duplicate bibliography ids found')
ref_numbers = sorted(int(rid.split('-')[1]) for rid in ids)
if ref_numbers:
    missing_ref_ids = [f'REF-{n:04d}' for n in range(ref_numbers[0], ref_numbers[-1] + 1) if n not in set(ref_numbers)]
    ref_gap_ledger_path = root / 'docs/00-meta/ref-id-retirement-ledger.md'
    if missing_ref_ids and not ref_gap_ledger_path.exists():
        errors.append('bibliography has REF id gaps but docs/00-meta/ref-id-retirement-ledger.md is missing')
    elif missing_ref_ids:
        ref_gap_ledger_text = ref_gap_ledger_path.read_text()
        unaccounted_ref_gaps = [rid for rid in missing_ref_ids if f'`{rid}`' not in ref_gap_ledger_text]
        if unaccounted_ref_gaps:
            errors.append(f'bibliography REF id gaps are not accounted for in ref-id-retirement-ledger.md: {unaccounted_ref_gaps}')

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
    required_head_fields = ['bundle_head', 'scientific_current_head', 'release_control_head', 'operational_head', 'citation_head', 'head_semantics_surface']
    missing_head_fields = [field for field in required_head_fields if field not in status]
    if missing_head_fields:
        errors.append(f'SURFACE-STATUS missing explicit head-semantics fields: {missing_head_fields}')
    if status.get('bundle_head') != manifest['revision']:
        errors.append('SURFACE-STATUS bundle_head must match the manifest revision')
    if status.get('head_semantics_surface') != 'docs/00-meta/head-semantics-and-citation-policy.md':
        errors.append('SURFACE-STATUS head_semantics_surface must point to docs/00-meta/head-semantics-and-citation-policy.md')
    if f"## {manifest['revision']}" not in changelog_text:
        errors.append('CHANGELOG.md does not contain an entry for the current manifest revision')
    if f"## {manifest['previous_revision']}" not in changelog_text:
        errors.append('CHANGELOG.md does not contain an entry for the manifest previous_revision')

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
    for tier_name, tier_paths in context.get('restart_tiers', {}).items():
        for tier_path in tier_paths:
            if not (root / tier_path).exists():
                errors.append(f'context-pack restart_tiers {tier_name} references missing surface: {tier_path}')

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
    registered_question_ids = set(re.findall(r'^- `(OQ-\d{4})`', registry_text, flags=re.MULTILINE))
    all_text_for_oq_refs = []
    for qpath in root.rglob('*'):
        if qpath.is_file() and qpath.suffix in {'.md', '.json'} and not is_transient_release_path(qpath, root):
            all_text_for_oq_refs.append(qpath.read_text(errors='ignore'))
    referenced_question_ids = set(re.findall(r'\bOQ-\d{4}\b', '\n'.join(all_text_for_oq_refs)))
    unknown_question_refs = sorted(referenced_question_ids - registered_question_ids)
    if unknown_question_refs:
        errors.append(f'archive references OQ ids that are not registered: {unknown_question_refs}')
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


    # Executable route-ledger and empirical-delta checks added in rev0261.
    required_executable_surfaces = [
        'schemas/record-denominator.schema.json',
        'schemas/candidate-route-state-ledger.schema.json',
        'schemas/negative-control-ledger.schema.json',
        'schemas/empirical-delta-ledger.schema.json',
        'schemas/promotion-gate-ledger.schema.json',
        'schemas/observed-sector-recovery-ledger.schema.json',
        'schemas/discriminator-forecast-ledger.schema.json',
        'schemas/decision-experiment-ledger.schema.json',
        'schemas/public-record-carrier-ledger.schema.json',
        'schemas/acquisition-protocol-ledger.schema.json',
        'schemas/claim-route-binding-ledger.schema.json',
        'schemas/epistemic-defeater-ledger.schema.json',
        'schemas/rollback-propagation-ledger.schema.json',
        'schemas/evidence-severity-ledger.schema.json',
        'schemas/authority-dependency-graph.schema.json',
        'schemas/evidence-unit-ledger.schema.json',
        'schemas/independence-assumption-ledger.schema.json',
        'schemas/credit-allocation-ledger.schema.json',
        'schemas/contrast-class-ledger.schema.json',
        'schemas/likelihood-update-ledger.schema.json',
        'schemas/prior-sensitivity-ledger.schema.json',
        'schemas/measurement-model-ledger.schema.json',
        'schemas/systematic-uncertainty-ledger.schema.json',
        'schemas/calibration-traceability-ledger.schema.json',
        'schemas/domain-of-validity-ledger.schema.json',
        'schemas/transportability-ledger.schema.json',
        'schemas/extrapolation-fence-ledger.schema.json',
        'schemas/causal-mechanism-ledger.schema.json',
        'schemas/intervention-protocol-ledger.schema.json',
        'schemas/counterfactual-robustness-ledger.schema.json',
        'schemas/selection-function-ledger.schema.json',
        'schemas/multiplicity-control-ledger.schema.json',
        'schemas/reporting-bias-ledger.schema.json',
        'schemas/model-capacity-ledger.schema.json',
        'schemas/complexity-penalty-ledger.schema.json',
        'schemas/predictive-generalization-ledger.schema.json',
        'schemas/social-authority-ledger.schema.json',
        'schemas/review-replication-ledger.schema.json',
        'schemas/consensus-elicitation-ledger.schema.json',
        'schemas/computational-reproducibility-ledger.schema.json',
        'schemas/numerical-stability-ledger.schema.json',
        'schemas/software-supply-chain-ledger.schema.json',
        'schemas/idealization-ledger.schema.json',
        'schemas/approximation-error-ledger.schema.json',
        'schemas/limit-interchange-ledger.schema.json',
        'schemas/boundary-condition-ledger.schema.json',
        'schemas/initial-data-ledger.schema.json',
        'schemas/sector-selection-ledger.schema.json',
        'schemas/gauge-symmetry-ledger.schema.json',
        'schemas/constraint-closure-ledger.schema.json',
        'schemas/observable-quotient-ledger.schema.json',
        'CANDIDATE-ROUTE-STATE-LEDGER.json',
        'NEGATIVE-CONTROL-LEDGER.json',
        'RECORD-DENOMINATOR-TEMPLATES.json',
        'EMPIRICAL-DELTA-LEDGER.json',
        'PROMOTION-GATE-LEDGER.json',
        'OBSERVED-SECTOR-RECOVERY-LEDGER.json',
        'DISCRIMINATOR-FORECAST-LEDGER.json',
        'DECISION-EXPERIMENT-LEDGER.json',
        'PUBLIC-RECORD-CARRIER-LEDGER.json',
        'ACQUISITION-PROTOCOL-LEDGER.json',
        'CLAIM-ROUTE-BINDING-LEDGER.json',
        'EPISTEMIC-DEFEATER-LEDGER.json',
        'ROLLBACK-PROPAGATION-LEDGER.json',
        'EVIDENCE-SEVERITY-LEDGER.json',
        'AUTHORITY-DEPENDENCY-GRAPH.json',
        'EVIDENCE-UNIT-LEDGER.json',
        'INDEPENDENCE-ASSUMPTION-LEDGER.json',
        'CREDIT-ALLOCATION-LEDGER.json',
        'CONTRAST-CLASS-LEDGER.json',
        'LIKELIHOOD-UPDATE-LEDGER.json',
        'PRIOR-SENSITIVITY-LEDGER.json',
        'MEASUREMENT-MODEL-LEDGER.json',
        'SYSTEMATIC-UNCERTAINTY-LEDGER.json',
        'CALIBRATION-TRACEABILITY-LEDGER.json',
        'DOMAIN-OF-VALIDITY-LEDGER.json',
        'TRANSPORTABILITY-LEDGER.json',
        'EXTRAPOLATION-FENCE-LEDGER.json',
        'CAUSAL-MECHANISM-LEDGER.json',
        'INTERVENTION-PROTOCOL-LEDGER.json',
        'COUNTERFACTUAL-ROBUSTNESS-LEDGER.json',
        'SELECTION-FUNCTION-LEDGER.json',
        'MULTIPLICITY-CONTROL-LEDGER.json',
        'REPORTING-BIAS-LEDGER.json',
        'MODEL-CAPACITY-LEDGER.json',
        'COMPLEXITY-PENALTY-LEDGER.json',
        'PREDICTIVE-GENERALIZATION-LEDGER.json',
        'SEMANTIC-TERM-LEDGER.json',
        'ONTOLOGY-COMMITMENT-LEDGER.json',
        'CLAIM-LANGUAGE-PERMISSION-LEDGER.json',
        'SOCIAL-AUTHORITY-LEDGER.json',
        'REVIEW-REPLICATION-LEDGER.json',
        'CONSENSUS-ELICITATION-LEDGER.json',
        'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json',
        'NUMERICAL-STABILITY-LEDGER.json',
        'SOFTWARE-SUPPLY-CHAIN-LEDGER.json',
        'BOUNDARY-CONDITION-LEDGER.json',
        'INITIAL-DATA-LEDGER.json',
        'SECTOR-SELECTION-LEDGER.json',
        'GAUGE-SYMMETRY-LEDGER.json',
        'CONSTRAINT-CLOSURE-LEDGER.json',
        'OBSERVABLE-QUOTIENT-LEDGER.json',
        'docs/10-method/record-denominator-and-route-ledger-schema.md',
        'docs/10-method/residual-deficiency-scorecard.md',
        'docs/10-method/duality-and-underdetermination-adjudication.md',
        'docs/30-program/executable-route-ledger.md',
        'docs/30-program/empirical-delta-roadmap.md',
        'docs/30-program/route-state-summary.generated.md',
        'docs/30-program/promotion-and-recovery-summary.generated.md',
        'docs/10-method/promotion-gate-ledger-and-no-compensation-rule.md',
        'docs/10-method/observed-sector-recovery-burden.md',
        'docs/30-program/discriminator-forecast-ledger.md',
        'docs/30-program/decision-experiment-ledger.md',
        'docs/30-program/decision-experiment-summary.generated.md',
        'docs/10-method/public-record-carrier-and-acquisition-protocol.md',
        'docs/10-method/claim-route-binding-and-authority-propagation.md',
        'docs/30-program/public-record-carrier-ledger.md',
        'docs/30-program/acquisition-protocol-ledger.md',
        'docs/30-program/claim-route-binding-ledger.md',
        'docs/30-program/record-replay-harness.md',
        'docs/30-program/record-carrier-and-acquisition-summary.generated.md',
        'docs/40-model/public-record-carrier-crosswalk.md',
        'docs/40-model/acquisition-pipeline-risk-taxonomy.md',
        'docs/10-method/nonmonotonic-defeat-and-rollback-propagation.md',
        'docs/10-method/evidence-severity-and-severe-test-discipline.md',
        'docs/30-program/epistemic-defeater-ledger.md',
        'docs/30-program/rollback-propagation-ledger.md',
        'docs/30-program/evidence-severity-ledger.md',
        'docs/30-program/authority-dependency-graph.md',
        'docs/30-program/defeat-rollback-summary.generated.md',
        'docs/40-model/candidate-route-defeater-taxonomy.md',
        'docs/40-model/positive-evidence-versus-severe-test-audit.md',
        'docs/10-method/evidence-unit-and-credit-accounting.md',
        'docs/10-method/independence-and-double-counting-control.md',
        'docs/30-program/evidence-unit-ledger.md',
        'docs/30-program/independence-assumption-ledger.md',
        'docs/30-program/credit-allocation-ledger.md',
        'docs/30-program/evidence-credit-summary.generated.md',
        'docs/40-model/evidence-aggregation-risk-taxonomy.md',
        'docs/10-method/contrast-class-and-update-denominator.md',
        'docs/10-method/prior-sensitivity-and-likelihood-update-discipline.md',
        'docs/30-program/contrast-class-ledger.md',
        'docs/30-program/likelihood-update-ledger.md',
        'docs/30-program/prior-sensitivity-ledger.md',
        'docs/30-program/contrast-update-summary.generated.md',
        'docs/40-model/contrastive-evidence-risk-taxonomy.md',
        'docs/40-model/cosmology-prior-sensitivity-audit.md',
        'docs/10-method/measurement-model-and-measurand-discipline.md',
        'docs/10-method/systematic-uncertainty-and-calibration-traceability.md',
        'docs/30-program/measurement-model-ledger.md',
        'docs/30-program/systematic-uncertainty-ledger.md',
        'docs/30-program/calibration-traceability-ledger.md',
        'docs/30-program/measurement-systematics-summary.generated.md',
        'docs/40-model/measurement-model-risk-taxonomy.md',
        'docs/40-model/calibration-traceability-crosswalk.md',
        'docs/40-model/raw-record-to-likelihood-audit.md',
        'docs/10-method/validity-domain-and-transportability-discipline.md',
        'docs/10-method/extrapolation-fence-and-domain-shift-control.md',
        'docs/30-program/domain-of-validity-ledger.md',
        'docs/30-program/transportability-ledger.md',
        'docs/30-program/extrapolation-fence-ledger.md',
        'docs/30-program/validity-transport-summary.generated.md',
        'docs/40-model/domain-shift-and-extrapolation-risk-taxonomy.md',
        'docs/40-model/eft-domain-of-validity-and-cutoff-audit.md',
        'docs/10-method/causal-mechanism-and-intervention-discipline.md',
        'docs/10-method/counterfactual-robustness-and-mechanism-transfer.md',
        'docs/30-program/causal-mechanism-ledger.md',
        'docs/30-program/intervention-protocol-ledger.md',
        'docs/30-program/counterfactual-robustness-ledger.md',
        'docs/30-program/causal-mechanism-summary.generated.md',
        'docs/40-model/causal-mechanism-risk-taxonomy.md',
        'docs/40-model/intervention-versus-observation-audit.md',
        'docs/40-model/counterfactual-robustness-crosswalk.md',
        'docs/10-method/selection-function-and-multiplicity-discipline.md',
        'docs/10-method/reporting-bias-and-survivorship-control.md',
        'docs/30-program/selection-function-ledger.md',
        'docs/30-program/multiplicity-control-ledger.md',
        'docs/30-program/reporting-bias-ledger.md',
        'docs/30-program/selection-bias-summary.generated.md',
        'docs/40-model/selection-multiplicity-risk-taxonomy.md',
        'docs/40-model/look-elsewhere-and-survivorship-audit.md',
        'docs/10-method/model-capacity-and-complexity-discipline.md',
        'docs/10-method/predictive-generalization-and-holdout-discipline.md',
        'docs/30-program/model-capacity-ledger.md',
        'docs/30-program/complexity-penalty-ledger.md',
        'docs/30-program/predictive-generalization-ledger.md',
        'docs/30-program/model-capacity-summary.generated.md',
        'docs/40-model/model-capacity-risk-taxonomy.md',
        'docs/40-model/fit-compression-generalization-audit.md',
        'docs/10-method/semantic-binding-and-term-stability-discipline.md',
        'docs/10-method/ontology-commitment-and-claim-language-permission.md',
        'docs/30-program/semantic-term-ledger.md',
        'docs/30-program/ontology-commitment-ledger.md',
        'docs/30-program/claim-language-permission-ledger.md',
        'docs/30-program/semantic-binding-summary.generated.md',
        'docs/40-model/semantic-drift-and-equivocation-risk-taxonomy.md',
        'docs/40-model/ontology-identity-versus-structural-equivalence-audit.md',
        'docs/10-method/social-authority-and-review-boundaries.md',
        'docs/10-method/consensus-elicitation-and-testimony-discipline.md',
        'docs/30-program/social-authority-ledger.md',
        'docs/30-program/review-replication-ledger.md',
        'docs/30-program/consensus-elicitation-ledger.md',
        'docs/30-program/social-authority-summary.generated.md',
        'docs/40-model/social-authority-risk-taxonomy.md',
        'docs/40-model/review-consensus-versus-evidence-audit.md',
        'docs/10-method/computational-reproducibility-and-artifact-replay.md',
        'docs/10-method/numerical-stability-and-solver-tolerance-discipline.md',
        'docs/10-method/software-supply-chain-and-provenance-discipline.md',
        'docs/30-program/computational-reproducibility-ledger.md',
        'docs/30-program/numerical-stability-ledger.md',
        'docs/30-program/software-supply-chain-ledger.md',
        'docs/30-program/computational-reproducibility-summary.generated.md',
        'docs/10-method/idealization-and-approximation-error-discipline.md',
        'docs/10-method/limit-interchange-and-singular-limit-control.md',
        'docs/30-program/idealization-ledger.md',
        'docs/30-program/approximation-error-ledger.md',
        'docs/30-program/limit-interchange-ledger.md',
        'docs/30-program/idealization-limit-summary.generated.md',
        'docs/10-method/boundary-initial-sector-discipline.md',
        'docs/10-method/solution-sector-and-background-selection-control.md',
        'docs/30-program/boundary-condition-ledger.md',
        'docs/30-program/initial-data-ledger.md',
        'docs/30-program/sector-selection-ledger.md',
        'docs/30-program/boundary-sector-summary.generated.md',
        'docs/40-model/boundary-initial-sector-risk-taxonomy.md',
        'docs/40-model/background-independence-versus-selected-sector-audit.md',
        'docs/10-method/gauge-constraint-observable-quotient-discipline.md',
        'docs/10-method/constraint-closure-and-anomaly-control.md',
        'docs/30-program/gauge-symmetry-ledger.md',
        'docs/30-program/constraint-closure-ledger.md',
        'docs/30-program/observable-quotient-ledger.md',
        'docs/30-program/gauge-constraint-summary.generated.md',
        'docs/40-model/gauge-constraint-risk-taxonomy.md',
        'docs/40-model/physical-observable-versus-gauge-representative-audit.md',
        'docs/40-model/idealization-and-limit-risk-taxonomy.md',
        'docs/40-model/exact-limit-versus-finite-target-audit.md',
        'docs/40-model/computational-artifact-risk-taxonomy.md',
        'docs/40-model/numerical-stability-and-solver-risk-audit.md',
        'docs/40-model/causal-set-qsg-causality-computability-audit.md',
        'docs/40-model/forecast-to-update-discipline.md',
        'docs/40-model/cosmology-dark-energy-discriminator-roadmap.md',
        'docs/40-model/primordial-tensor-discriminator-roadmap.md',
        'docs/40-model/single-graviton-statistics-discriminator-roadmap.md',
        'docs/40-model/observed-sector-recovery-crosswalk.md',
        'docs/40-model/gravity-observable-and-witness-taxonomy.md',
        'docs/40-model/lab-quantum-gravity-discriminator-roadmap.md',
        'docs/40-model/cross-family-identifiability-scorecards.md',
        'docs/40-model/duality-equivalence-versus-candidate-identity-audit.md',
    ]
    for rel in required_executable_surfaces:
        if not (root / rel).exists():
            errors.append(f'missing rev0261 executable route surface: {rel}')

    route_ledger = json.loads((root / 'CANDIDATE-ROUTE-STATE-LEDGER.json').read_text())
    negative_control_ledger = json.loads((root / 'NEGATIVE-CONTROL-LEDGER.json').read_text())
    empirical_delta_ledger = json.loads((root / 'EMPIRICAL-DELTA-LEDGER.json').read_text())
    record_templates = json.loads((root / 'RECORD-DENOMINATOR-TEMPLATES.json').read_text())
    promotion_gate_ledger = json.loads((root / 'PROMOTION-GATE-LEDGER.json').read_text())
    observed_sector_ledger = json.loads((root / 'OBSERVED-SECTOR-RECOVERY-LEDGER.json').read_text())
    forecast_ledger = json.loads((root / 'DISCRIMINATOR-FORECAST-LEDGER.json').read_text())
    decision_ledger = json.loads((root / 'DECISION-EXPERIMENT-LEDGER.json').read_text())
    carrier_ledger = json.loads((root / 'PUBLIC-RECORD-CARRIER-LEDGER.json').read_text())
    acquisition_ledger = json.loads((root / 'ACQUISITION-PROTOCOL-LEDGER.json').read_text())
    claim_binding_ledger = json.loads((root / 'CLAIM-ROUTE-BINDING-LEDGER.json').read_text())
    defeater_ledger = json.loads((root / 'EPISTEMIC-DEFEATER-LEDGER.json').read_text())
    rollback_ledger = json.loads((root / 'ROLLBACK-PROPAGATION-LEDGER.json').read_text())
    severity_ledger = json.loads((root / 'EVIDENCE-SEVERITY-LEDGER.json').read_text())
    dependency_graph = json.loads((root / 'AUTHORITY-DEPENDENCY-GRAPH.json').read_text())
    evidence_unit_ledger = json.loads((root / 'EVIDENCE-UNIT-LEDGER.json').read_text())
    independence_ledger = json.loads((root / 'INDEPENDENCE-ASSUMPTION-LEDGER.json').read_text())
    credit_allocation_ledger = json.loads((root / 'CREDIT-ALLOCATION-LEDGER.json').read_text())
    contrast_class_ledger = json.loads((root / 'CONTRAST-CLASS-LEDGER.json').read_text())
    likelihood_update_ledger = json.loads((root / 'LIKELIHOOD-UPDATE-LEDGER.json').read_text())
    prior_sensitivity_ledger = json.loads((root / 'PRIOR-SENSITIVITY-LEDGER.json').read_text())
    measurement_model_ledger = json.loads((root / 'MEASUREMENT-MODEL-LEDGER.json').read_text())
    systematic_uncertainty_ledger = json.loads((root / 'SYSTEMATIC-UNCERTAINTY-LEDGER.json').read_text())
    calibration_traceability_ledger = json.loads((root / 'CALIBRATION-TRACEABILITY-LEDGER.json').read_text())
    domain_validity_ledger = json.loads((root / 'DOMAIN-OF-VALIDITY-LEDGER.json').read_text())
    transportability_ledger = json.loads((root / 'TRANSPORTABILITY-LEDGER.json').read_text())
    extrapolation_fence_ledger = json.loads((root / 'EXTRAPOLATION-FENCE-LEDGER.json').read_text())
    causal_mechanism_ledger = json.loads((root / 'CAUSAL-MECHANISM-LEDGER.json').read_text())
    intervention_protocol_ledger = json.loads((root / 'INTERVENTION-PROTOCOL-LEDGER.json').read_text())
    counterfactual_robustness_ledger = json.loads((root / 'COUNTERFACTUAL-ROBUSTNESS-LEDGER.json').read_text())
    selection_function_ledger = json.loads((root / 'SELECTION-FUNCTION-LEDGER.json').read_text())
    multiplicity_control_ledger = json.loads((root / 'MULTIPLICITY-CONTROL-LEDGER.json').read_text())
    reporting_bias_ledger = json.loads((root / 'REPORTING-BIAS-LEDGER.json').read_text())
    model_capacity_ledger = json.loads((root / 'MODEL-CAPACITY-LEDGER.json').read_text())
    complexity_penalty_ledger = json.loads((root / 'COMPLEXITY-PENALTY-LEDGER.json').read_text())
    predictive_generalization_ledger = json.loads((root / 'PREDICTIVE-GENERALIZATION-LEDGER.json').read_text())
    semantic_term_ledger = json.loads((root / 'SEMANTIC-TERM-LEDGER.json').read_text())
    ontology_commitment_ledger = json.loads((root / 'ONTOLOGY-COMMITMENT-LEDGER.json').read_text())
    claim_language_permission_ledger = json.loads((root / 'CLAIM-LANGUAGE-PERMISSION-LEDGER.json').read_text())
    social_authority_ledger = json.loads((root / 'SOCIAL-AUTHORITY-LEDGER.json').read_text())
    review_replication_ledger = json.loads((root / 'REVIEW-REPLICATION-LEDGER.json').read_text())
    consensus_elicitation_ledger = json.loads((root / 'CONSENSUS-ELICITATION-LEDGER.json').read_text())
    computational_reproducibility_ledger = json.loads((root / 'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json').read_text())
    numerical_stability_ledger = json.loads((root / 'NUMERICAL-STABILITY-LEDGER.json').read_text())
    software_supply_chain_ledger = json.loads((root / 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json').read_text())
    boundary_condition_ledger = json.loads((root / 'BOUNDARY-CONDITION-LEDGER.json').read_text())
    initial_data_ledger = json.loads((root / 'INITIAL-DATA-LEDGER.json').read_text())
    sector_selection_ledger = json.loads((root / 'SECTOR-SELECTION-LEDGER.json').read_text())

    route_summary_text = (root / 'docs/30-program/route-state-summary.generated.md').read_text()
    if f"- Revision: `{manifest['revision']}`" not in route_summary_text:
        errors.append('route-state generated summary revision drifted from manifest; run make index')

    promotion_summary_text = (root / 'docs/30-program/promotion-and-recovery-summary.generated.md').read_text()
    decision_summary_text = (root / 'docs/30-program/decision-experiment-summary.generated.md').read_text()
    carrier_summary_text = (root / 'docs/30-program/record-carrier-and-acquisition-summary.generated.md').read_text()
    defeat_summary_text = (root / 'docs/30-program/defeat-rollback-summary.generated.md').read_text()
    evidence_credit_summary_text = (root / 'docs/30-program/evidence-credit-summary.generated.md').read_text()
    contrast_update_summary_text = (root / 'docs/30-program/contrast-update-summary.generated.md').read_text()
    measurement_systematics_summary_text = (root / 'docs/30-program/measurement-systematics-summary.generated.md').read_text()
    validity_transport_summary_text = (root / 'docs/30-program/validity-transport-summary.generated.md').read_text()
    causal_mechanism_summary_text = (root / 'docs/30-program/causal-mechanism-summary.generated.md').read_text()
    selection_bias_summary_text = (root / 'docs/30-program/selection-bias-summary.generated.md').read_text()
    model_capacity_summary_text = (root / 'docs/30-program/model-capacity-summary.generated.md').read_text()
    semantic_binding_summary_text = (root / 'docs/30-program/semantic-binding-summary.generated.md').read_text()
    social_authority_summary_text = (root / 'docs/30-program/social-authority-summary.generated.md').read_text()
    computational_reproducibility_summary_text = (root / 'docs/30-program/computational-reproducibility-summary.generated.md').read_text()
    boundary_sector_summary_text = (root / 'docs/30-program/boundary-sector-summary.generated.md').read_text()
    if f"- Revision: `{manifest['revision']}`" not in promotion_summary_text:
        errors.append('promotion/recovery generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in decision_summary_text:
        errors.append('decision-experiment generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in carrier_summary_text:
        errors.append('record-carrier/acquisition generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in defeat_summary_text:
        errors.append('defeat/rollback generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in evidence_credit_summary_text:
        errors.append('evidence-credit generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in contrast_update_summary_text:
        errors.append('contrast/update generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in measurement_systematics_summary_text:
        errors.append('measurement/systematics generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in validity_transport_summary_text:
        errors.append('validity/transport generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in causal_mechanism_summary_text:
        errors.append('causal-mechanism generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in selection_bias_summary_text:
        errors.append('selection/multiplicity/reporting-bias generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in model_capacity_summary_text:
        errors.append('model-capacity generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in semantic_binding_summary_text:
        errors.append('semantic-binding generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in social_authority_summary_text:
        errors.append('social-authority generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in computational_reproducibility_summary_text:
        errors.append('computational-reproducibility generated summary revision drifted from manifest; run make index')
    if f"- Revision: `{manifest['revision']}`" not in boundary_sector_summary_text:
        errors.append('boundary-sector generated summary revision drifted from manifest; run make index')

    if route_ledger.get('revision') != manifest['revision']:
        errors.append('CANDIDATE-ROUTE-STATE-LEDGER revision drifted from manifest')
    if negative_control_ledger.get('revision') != manifest['revision']:
        errors.append('NEGATIVE-CONTROL-LEDGER revision drifted from manifest')
    if empirical_delta_ledger.get('revision') != manifest['revision']:
        errors.append('EMPIRICAL-DELTA-LEDGER revision drifted from manifest')
    if record_templates.get('revision') != manifest['revision']:
        errors.append('RECORD-DENOMINATOR-TEMPLATES revision drifted from manifest')

    if promotion_gate_ledger.get('revision') != manifest['revision']:
        errors.append('PROMOTION-GATE-LEDGER revision drifted from manifest')
    if observed_sector_ledger.get('revision') != manifest['revision']:
        errors.append('OBSERVED-SECTOR-RECOVERY-LEDGER revision drifted from manifest')
    if forecast_ledger.get('revision') != manifest['revision']:
        errors.append('DISCRIMINATOR-FORECAST-LEDGER revision drifted from manifest')
    if decision_ledger.get('revision') != manifest['revision']:
        errors.append('DECISION-EXPERIMENT-LEDGER revision drifted from manifest')
    if carrier_ledger.get('revision') != manifest['revision']:
        errors.append('PUBLIC-RECORD-CARRIER-LEDGER revision drifted from manifest')
    if acquisition_ledger.get('revision') != manifest['revision']:
        errors.append('ACQUISITION-PROTOCOL-LEDGER revision drifted from manifest')
    if claim_binding_ledger.get('revision') != manifest['revision']:
        errors.append('CLAIM-ROUTE-BINDING-LEDGER revision drifted from manifest')
    if defeater_ledger.get('revision') != manifest['revision']:
        errors.append('EPISTEMIC-DEFEATER-LEDGER revision drifted from manifest')
    if rollback_ledger.get('revision') != manifest['revision']:
        errors.append('ROLLBACK-PROPAGATION-LEDGER revision drifted from manifest')
    if severity_ledger.get('revision') != manifest['revision']:
        errors.append('EVIDENCE-SEVERITY-LEDGER revision drifted from manifest')
    if dependency_graph.get('revision') != manifest['revision']:
        errors.append('AUTHORITY-DEPENDENCY-GRAPH revision drifted from manifest')
    if evidence_unit_ledger.get('revision') != manifest['revision']:
        errors.append('EVIDENCE-UNIT-LEDGER revision drifted from manifest')
    if independence_ledger.get('revision') != manifest['revision']:
        errors.append('INDEPENDENCE-ASSUMPTION-LEDGER revision drifted from manifest')
    if credit_allocation_ledger.get('revision') != manifest['revision']:
        errors.append('CREDIT-ALLOCATION-LEDGER revision drifted from manifest')
    if contrast_class_ledger.get('revision') != manifest['revision']:
        errors.append('CONTRAST-CLASS-LEDGER revision drifted from manifest')
    if likelihood_update_ledger.get('revision') != manifest['revision']:
        errors.append('LIKELIHOOD-UPDATE-LEDGER revision drifted from manifest')
    if prior_sensitivity_ledger.get('revision') != manifest['revision']:
        errors.append('PRIOR-SENSITIVITY-LEDGER revision drifted from manifest')
    if measurement_model_ledger.get('revision') != manifest['revision']:
        errors.append('MEASUREMENT-MODEL-LEDGER revision drifted from manifest')
    if systematic_uncertainty_ledger.get('revision') != manifest['revision']:
        errors.append('SYSTEMATIC-UNCERTAINTY-LEDGER revision drifted from manifest')
    if calibration_traceability_ledger.get('revision') != manifest['revision']:
        errors.append('CALIBRATION-TRACEABILITY-LEDGER revision drifted from manifest')
    if domain_validity_ledger.get('revision') != manifest['revision']:
        errors.append('DOMAIN-OF-VALIDITY-LEDGER revision drifted from manifest')
    if transportability_ledger.get('revision') != manifest['revision']:
        errors.append('TRANSPORTABILITY-LEDGER revision drifted from manifest')
    if extrapolation_fence_ledger.get('revision') != manifest['revision']:
        errors.append('EXTRAPOLATION-FENCE-LEDGER revision drifted from manifest')
    if causal_mechanism_ledger.get('revision') != manifest['revision']:
        errors.append('CAUSAL-MECHANISM-LEDGER revision drifted from manifest')
    if intervention_protocol_ledger.get('revision') != manifest['revision']:
        errors.append('INTERVENTION-PROTOCOL-LEDGER revision drifted from manifest')
    if counterfactual_robustness_ledger.get('revision') != manifest['revision']:
        errors.append('COUNTERFACTUAL-ROBUSTNESS-LEDGER revision drifted from manifest')
    if selection_function_ledger.get('revision') != manifest['revision']:
        errors.append('SELECTION-FUNCTION-LEDGER revision drifted from manifest')
    if multiplicity_control_ledger.get('revision') != manifest['revision']:
        errors.append('MULTIPLICITY-CONTROL-LEDGER revision drifted from manifest')
    if reporting_bias_ledger.get('revision') != manifest['revision']:
        errors.append('REPORTING-BIAS-LEDGER revision drifted from manifest')
    if semantic_term_ledger.get('revision') != manifest['revision']:
        errors.append('SEMANTIC-TERM-LEDGER revision drifted from manifest')
    if ontology_commitment_ledger.get('revision') != manifest['revision']:
        errors.append('ONTOLOGY-COMMITMENT-LEDGER revision drifted from manifest')
    if claim_language_permission_ledger.get('revision') != manifest['revision']:
        errors.append('CLAIM-LANGUAGE-PERMISSION-LEDGER revision drifted from manifest')
    if social_authority_ledger.get('revision') != manifest['revision']:
        errors.append('SOCIAL-AUTHORITY-LEDGER revision drifted from manifest')
    if review_replication_ledger.get('revision') != manifest['revision']:
        errors.append('REVIEW-REPLICATION-LEDGER revision drifted from manifest')
    if consensus_elicitation_ledger.get('revision') != manifest['revision']:
        errors.append('CONSENSUS-ELICITATION-LEDGER revision drifted from manifest')
    if computational_reproducibility_ledger.get('revision') != manifest['revision']:
        errors.append('COMPUTATIONAL-REPRODUCIBILITY-LEDGER revision drifted from manifest')
    if numerical_stability_ledger.get('revision') != manifest['revision']:
        errors.append('NUMERICAL-STABILITY-LEDGER revision drifted from manifest')
    if software_supply_chain_ledger.get('revision') != manifest['revision']:
        errors.append('SOFTWARE-SUPPLY-CHAIN-LEDGER revision drifted from manifest')
    if boundary_condition_ledger.get('revision') != manifest['revision']:
        errors.append('BOUNDARY-CONDITION-LEDGER revision drifted from manifest')
    if initial_data_ledger.get('revision') != manifest['revision']:
        errors.append('INITIAL-DATA-LEDGER revision drifted from manifest')
    if sector_selection_ledger.get('revision') != manifest['revision']:
        errors.append('SECTOR-SELECTION-LEDGER revision drifted from manifest')
    if (root / 'SYMMETRY-REALIZATION-LEDGER.json').exists() and json.loads((root / 'SYMMETRY-REALIZATION-LEDGER.json').read_text()).get('revision') != manifest['revision']:
        errors.append('SYMMETRY-REALIZATION-LEDGER revision drifted from manifest')
    if (root / 'ANOMALY-MATCHING-LEDGER.json').exists() and json.loads((root / 'ANOMALY-MATCHING-LEDGER.json').read_text()).get('revision') != manifest['revision']:
        errors.append('ANOMALY-MATCHING-LEDGER revision drifted from manifest')
    if (root / 'CONSERVATION-LAW-LEDGER.json').exists() and json.loads((root / 'CONSERVATION-LAW-LEDGER.json').read_text()).get('revision') != manifest['revision']:
        errors.append('CONSERVATION-LAW-LEDGER revision drifted from manifest')

    route_required_fields = [
        'route_id', 'authority_state', 'owner_surface', 'earliest_blocker', 'score_codes',
        'record_id', 'candidate_family', 'target_claim', 'target_grain', 'record_object',
        'record_production_process', 'observer_or_frame', 'public_access_mode',
        'candidate_native_definition', 'borrowed_bridge_fields', 'equivalence_relation',
        'forward_acquisition_map', 'inverse_map', 'inverse_deficiency', 'stability_margin',
        'abstention_or_no_verdict_rule', 'adversarial_countermodels', 'residual_cap',
        'promotion_ceiling', 'rollback_or_quarantine_handle', 'promotion_gate_ids',
        'observed_sector_obligations', 'public_record_carrier_ids', 'acquisition_protocol_ids',
        'defeater_ids', 'rollback_rule_ids', 'severity_test_ids',
        'evidence_unit_ids', 'independence_assumption_ids', 'credit_allocation_ids',
        'contrast_class_ids', 'likelihood_update_ids', 'prior_sensitivity_ids',
        'measurement_model_ids', 'systematic_uncertainty_ids', 'calibration_traceability_ids',
        'validity_domain_ids', 'transportability_ids', 'extrapolation_fence_ids',
        'causal_mechanism_ids', 'intervention_protocol_ids', 'counterfactual_robustness_ids',
        'selection_function_ids', 'multiplicity_control_ids', 'reporting_bias_ids',
        'model_capacity_ids', 'complexity_penalty_ids', 'generalization_validation_ids',
        'semantic_term_ids', 'ontology_commitment_ids', 'claim_language_permission_ids',
        'social_authority_ids', 'review_replication_ids', 'consensus_elicitation_ids',
        'computational_reproducibility_ids', 'numerical_stability_ids', 'software_supply_chain_ids',
        'symmetry_realization_ids', 'anomaly_matching_ids', 'conservation_law_ids',
    ]
    allowed_states = set(witness_vocab.get('authority_state_labels', []))
    allowed_score_atoms = {'N', 'P', 'B', 'M'}
    route_rows = route_ledger.get('route_rows', [])
    route_ids = []
    for row in route_rows:
        missing = [field for field in route_required_fields if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'route row {row.get("route_id", "<missing>")} missing required fields: {missing}')
        route_id = row.get('route_id', '')
        route_ids.append(route_id)
        if row.get('authority_state') not in allowed_states:
            errors.append(f'route row {route_id} has unknown authority_state: {row.get("authority_state")}')
        if row.get('promotion_ceiling') not in allowed_states:
            errors.append(f'route row {route_id} has unknown promotion_ceiling: {row.get("promotion_ceiling")}')
        state_order = {'S0':0,'S1':1,'S2':2,'S3':3,'S4':4,'S5':5}
        if row.get('authority_state') in state_order and row.get('promotion_ceiling') in state_order and state_order[row.get('authority_state')] > state_order[row.get('promotion_ceiling')]:
            errors.append(f'route row {route_id} authority_state exceeds promotion_ceiling')
        owner_surface = row.get('owner_surface', '')
        if owner_surface and not (root / owner_surface).exists():
            errors.append(f'route row {route_id} owner_surface does not exist: {owner_surface}')
        if not isinstance(row.get('borrowed_bridge_fields'), list):
            errors.append(f'route row {route_id} borrowed_bridge_fields must be a list')
        if not isinstance(row.get('adversarial_countermodels'), list):
            errors.append(f'route row {route_id} adversarial_countermodels must be a list')
        if not isinstance(row.get('promotion_gate_ids'), list) or not row.get('promotion_gate_ids'):
            errors.append(f'route row {route_id} promotion_gate_ids must be a nonempty list')
        if not isinstance(row.get('observed_sector_obligations'), list) or not row.get('observed_sector_obligations'):
            errors.append(f'route row {route_id} observed_sector_obligations must be a nonempty list')
        for list_field in ['defeater_ids', 'rollback_rule_ids', 'severity_test_ids', 'evidence_unit_ids', 'independence_assumption_ids', 'credit_allocation_ids', 'contrast_class_ids', 'likelihood_update_ids', 'prior_sensitivity_ids', 'measurement_model_ids', 'systematic_uncertainty_ids', 'calibration_traceability_ids', 'validity_domain_ids', 'transportability_ids', 'extrapolation_fence_ids', 'causal_mechanism_ids', 'intervention_protocol_ids', 'counterfactual_robustness_ids', 'selection_function_ids', 'multiplicity_control_ids', 'reporting_bias_ids', 'model_capacity_ids', 'complexity_penalty_ids', 'generalization_validation_ids', 'semantic_term_ids', 'ontology_commitment_ids', 'claim_language_permission_ids', 'social_authority_ids', 'review_replication_ids', 'consensus_elicitation_ids', 'computational_reproducibility_ids', 'numerical_stability_ids', 'software_supply_chain_ids', 'symmetry_realization_ids', 'anomaly_matching_ids', 'conservation_law_ids', 'spacetime_topology_ids', 'dimension_realization_ids', 'signature_structure_ids', 'algebraic_locality_ids', 'subsystem_factorization_ids', 'edge_mode_center_ids', 'measure_definition_ids', 'ensemble_sampling_ids', 'typicality_weighting_ids', 'particle_spectrum_ids', 'interaction_coupling_ids', 'mass_hierarchy_ids']:
            if not isinstance(row.get(list_field), list) or not row.get(list_field):
                errors.append(f'route row {route_id} {list_field} must be a nonempty list')
        for key, value in row.get('score_codes', {}).items():
            atoms = str(value).split('/')
            if not atoms or any(atom not in allowed_score_atoms for atom in atoms):
                errors.append(f'route row {route_id} score code {key} has unknown value: {value}')
    if len(route_ids) != len(set(route_ids)):
        errors.append('CANDIDATE-ROUTE-STATE-LEDGER contains duplicate route_id values')
    if len(route_rows) < 8:
        errors.append('CANDIDATE-ROUTE-STATE-LEDGER should preserve at least the major current route rows')
    known_route_ids = set(route_ids)
    if f"- Route rows: `{len(route_rows)}`" not in route_summary_text:
        errors.append('route-state generated summary row count drifted from route ledger; run make index')



    # Public-record carrier, acquisition protocol, and claim-route binding checks added in rev0263.
    carrier_rows = carrier_ledger.get('carrier_rows', [])
    carrier_required_fields = ['carrier_id','route_ids','carrier_class','publicness_level','record_object','custody_object','locator_or_access_class','metadata_standard','provenance_requirements','replay_requirements','challenge_route','versioning_or_freeze_rule','known_failure_modes','maximum_authority_credit','source_refs']
    carrier_ids = [item.get('carrier_id', '') for item in carrier_rows]
    if len(carrier_ids) != len(set(carrier_ids)):
        errors.append('PUBLIC-RECORD-CARRIER-LEDGER contains duplicate carrier_id values')
    known_carrier_ids = set(carrier_ids)
    for carrier in carrier_rows:
        cid = carrier.get('carrier_id', '')
        missing = [field for field in carrier_required_fields if field not in carrier or carrier.get(field) in ('', [], None)]
        if missing:
            errors.append(f'public record carrier {cid or "<missing>"} missing required fields: {missing}')
        if carrier.get('maximum_authority_credit') not in allowed_states:
            errors.append(f'public record carrier {cid} has unknown maximum_authority_credit: {carrier.get("maximum_authority_credit")}')
        for rid in carrier.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'public record carrier {cid} references unknown route_id: {rid}')
        for ref in carrier.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'public record carrier {cid} references unknown REF id: {ref}')
        if not isinstance(carrier.get('known_failure_modes'), list):
            errors.append(f'public record carrier {cid} known_failure_modes must be a list')

    protocol_rows = acquisition_ledger.get('protocol_rows', [])
    protocol_required_fields = ['protocol_id','route_ids','carrier_ids','acquisition_stage','required_operations','minimum_public_artifacts','calibration_or_metadata_requirements','nuisance_controls','replay_harness','intervention_grade','fresh_host_reinstantiation_requirement','failure_to_record_effect','maximum_route_effect','source_refs']
    protocol_ids = [item.get('protocol_id', '') for item in protocol_rows]
    if len(protocol_ids) != len(set(protocol_ids)):
        errors.append('ACQUISITION-PROTOCOL-LEDGER contains duplicate protocol_id values')
    known_protocol_ids = set(protocol_ids)
    for protocol in protocol_rows:
        pid = protocol.get('protocol_id', '')
        missing = [field for field in protocol_required_fields if field not in protocol or protocol.get(field) in ('', [], None)]
        if missing:
            errors.append(f'acquisition protocol {pid or "<missing>"} missing required fields: {missing}')
        if protocol.get('maximum_route_effect') not in allowed_states:
            errors.append(f'acquisition protocol {pid} has unknown maximum_route_effect: {protocol.get("maximum_route_effect")}')
        for rid in protocol.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'acquisition protocol {pid} references unknown route_id: {rid}')
        for cid in protocol.get('carrier_ids', []):
            if cid not in known_carrier_ids:
                errors.append(f'acquisition protocol {pid} references unknown carrier_id: {cid}')
        for ref in protocol.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'acquisition protocol {pid} references unknown REF id: {ref}')

    for row in route_rows:
        rid = row.get('route_id', '')
        for cid in row.get('public_record_carrier_ids', []):
            if cid not in known_carrier_ids:
                errors.append(f'route row {rid} references unknown public-record carrier: {cid}')
        for pid in row.get('acquisition_protocol_ids', []):
            if pid not in known_protocol_ids:
                errors.append(f'route row {rid} references unknown acquisition protocol: {pid}')
        if row.get('authority_state') in {'S3','S4','S5'}:
            if len(row.get('public_record_carrier_ids', [])) < 1 or len(row.get('acquisition_protocol_ids', [])) < 1:
                errors.append(f'route row {rid} at {row.get("authority_state")} needs carrier/protocol coverage')

    # Ledger rows should be bidirectionally coherent enough to catch typos.
    for cid, carrier in {item.get('carrier_id',''): item for item in carrier_rows}.items():
        for rid in carrier.get('route_ids', []):
            route = next((r for r in route_rows if r.get('route_id') == rid), None)
            if route and cid not in route.get('public_record_carrier_ids', []):
                errors.append(f'carrier {cid} names route {rid}, but route row does not name carrier')
    for pid, protocol in {item.get('protocol_id',''): item for item in protocol_rows}.items():
        for rid in protocol.get('route_ids', []):
            route = next((r for r in route_rows if r.get('route_id') == rid), None)
            if route and pid not in route.get('acquisition_protocol_ids', []):
                errors.append(f'protocol {pid} names route {rid}, but route row does not name protocol')

    binding_rows = claim_binding_ledger.get('binding_rows', [])
    binding_required_fields = ['binding_id','claim_or_oq_id','route_ids','controlling_ledgers','carrier_ids','protocol_ids','allowed_claim_language','forbidden_claim_language','authority_propagation_rule','rollback_if_missing']
    binding_ids = [item.get('binding_id', '') for item in binding_rows]
    if len(binding_ids) != len(set(binding_ids)):
        errors.append('CLAIM-ROUTE-BINDING-LEDGER contains duplicate binding_id values')
    registered_claim_ids = set(re.findall(r'^- `(CL-\d{4})`', claim_registry_raw_for_boundary, flags=re.MULTILINE))
    for binding in binding_rows:
        bid = binding.get('binding_id', '')
        missing = [field for field in binding_required_fields if field not in binding or binding.get(field) in ('', [], None)]
        if missing:
            errors.append(f'claim-route binding {bid or "<missing>"} missing required fields: {missing}')
        cqid = binding.get('claim_or_oq_id', '')
        if cqid.startswith('OQ-') and cqid not in registered_question_ids:
            errors.append(f'claim-route binding {bid} references unknown OQ id: {cqid}')
        if cqid.startswith('CL-') and cqid not in registered_claim_ids:
            errors.append(f'claim-route binding {bid} references unknown CL id: {cqid}')
        if not (cqid.startswith('OQ-') or cqid.startswith('CL-')):
            errors.append(f'claim-route binding {bid} claim_or_oq_id must be CL-#### or OQ-####: {cqid}')
        for rid in binding.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'claim-route binding {bid} references unknown route_id: {rid}')
        for cid in binding.get('carrier_ids', []):
            if cid not in known_carrier_ids:
                errors.append(f'claim-route binding {bid} references unknown carrier_id: {cid}')
        for pid in binding.get('protocol_ids', []):
            if pid not in known_protocol_ids:
                errors.append(f'claim-route binding {bid} references unknown protocol_id: {pid}')
        for rel in binding.get('controlling_ledgers', []):
            if not (root / rel).exists():
                errors.append(f'claim-route binding {bid} references missing controlling ledger: {rel}')

    if f"- Public-record carriers: `{len(carrier_rows)}`" not in carrier_summary_text:
        errors.append('record-carrier/acquisition generated summary carrier count drifted; run make index')
    if f"- Acquisition protocols: `{len(protocol_rows)}`" not in carrier_summary_text:
        errors.append('record-carrier/acquisition generated summary protocol count drifted; run make index')
    if f"- Claim-route bindings: `{len(binding_rows)}`" not in carrier_summary_text:
        errors.append('record-carrier/acquisition generated summary binding count drifted; run make index')

    controls = negative_control_ledger.get('controls', [])
    control_ids = [item.get('control_id', '') for item in controls]
    if len(control_ids) != len(set(control_ids)):
        errors.append('NEGATIVE-CONTROL-LEDGER contains duplicate control_id values')
    control_required_fields = [
        'control_id', 'route_id', 'positive_pattern_mimicked', 'missing_target_property',
        'borrowed_support_or_surrogate', 'expected_failure_mode', 'public_record_similarity',
        'candidate_native_difference', 'required_discriminator', 'state_machine_effect',
    ]
    known_route_ids = set(route_ids)
    for control in controls:
        cid = control.get('control_id', '')
        missing = [field for field in control_required_fields if field not in control or control.get(field) in ('', [], None)]
        if missing:
            errors.append(f'negative control {cid or "<missing>"} missing required fields: {missing}')
        if control.get('route_id') not in known_route_ids:
            errors.append(f'negative control {cid} references unknown route_id: {control.get("route_id")}')
    known_control_ids = set(control_ids)
    for row in route_rows:
        for cid in row.get('adversarial_countermodels', []):
            if cid not in known_control_ids:
                errors.append(f'route row {row.get("route_id")} references unknown negative control: {cid}')

    empirical_required_fields = ['delta_id', 'source_refs', 'route_ids', 'record_delta', 'candidate_native_effect', 'state_effect', 'promotion_ceiling', 'residual_cap', 'evidence_unit_ids']
    seen_delta_ids = []
    for delta in empirical_delta_ledger.get('empirical_deltas', []):
        did = delta.get('delta_id', '')
        seen_delta_ids.append(did)
        missing = [field for field in empirical_required_fields if field not in delta or delta.get(field) in ('', [], None)]
        if missing:
            errors.append(f'empirical delta {did or "<missing>"} missing required fields: {missing}')
        for rid in delta.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'empirical delta {did} references unknown route_id: {rid}')
        for ref in delta.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'empirical delta {did} references unknown REF id: {ref}')
        if delta.get('promotion_ceiling') not in allowed_states:
            errors.append(f'empirical delta {did} has unknown promotion_ceiling: {delta.get("promotion_ceiling")}')
    if len(seen_delta_ids) != len(set(seen_delta_ids)):
        errors.append('EMPIRICAL-DELTA-LEDGER contains duplicate delta_id values')

    gate_rows = promotion_gate_ledger.get('gate_rows', [])
    gate_ids = [item.get('gate_id', '') for item in gate_rows]
    required_gate_ids = {'PG-S1-TO-S2','PG-S2-TO-S3','PG-S3-TO-S4','PG-S4-TO-S5','PG-ANY-TO-Q','PG-ANY-TO-AR'}
    if set(gate_ids) != required_gate_ids:
        errors.append('PROMOTION-GATE-LEDGER must contain exactly the required promotion/rollback gate ids')
    if len(gate_ids) != len(set(gate_ids)):
        errors.append('PROMOTION-GATE-LEDGER contains duplicate gate_id values')
    gate_required_fields = ['gate_id','from_state','to_state','minimum_condition','required_route_fields','required_external_ledgers','blocking_if_missing','no_compensation_clause','observed_sector_condition','allowed_result','forbidden_result']
    known_gate_ids = set(gate_ids)
    for gate in gate_rows:
        gid = gate.get('gate_id', '')
        missing = [field for field in gate_required_fields if field not in gate or gate.get(field) in ('', [], None)]
        if missing:
            errors.append(f'promotion gate {gid or "<missing>"} missing required fields: {missing}')
        for rel in gate.get('required_external_ledgers', []):
            if not (root / rel).exists():
                errors.append(f'promotion gate {gid} references missing external ledger/surface: {rel}')
    for row in route_rows:
        route_id = row.get('route_id', '')
        for gid in row.get('promotion_gate_ids', []):
            if gid not in known_gate_ids:
                errors.append(f'route row {route_id} references unknown promotion gate: {gid}')
        if row.get('authority_state') in {'S3','S4','S5'} and len(row.get('adversarial_countermodels', [])) < 2:
            errors.append(f'route row {route_id} at {row.get("authority_state")} needs at least two negative controls')
        if row.get('authority_state') in {'S3','S4','S5'}:
            route_delta_count = sum(1 for delta in empirical_delta_ledger.get('empirical_deltas', []) if route_id in delta.get('route_ids', []))
            if route_delta_count < 1:
                errors.append(f'route row {route_id} at {row.get("authority_state")} needs at least one empirical delta')

    obligations = observed_sector_ledger.get('obligations', [])
    obligation_ids = [item.get('obligation_id', '') for item in obligations]
    if len(obligation_ids) != len(set(obligation_ids)):
        errors.append('OBSERVED-SECTOR-RECOVERY-LEDGER contains duplicate obligation_id values')
    obligation_required_fields = ['obligation_id','target_sector','minimum_for_S4','minimum_for_S5','current_archive_state','route_ids_touching','decisive_missing_piece','negative_controls','residual_cap']
    known_obligation_ids = set(obligation_ids)
    for obligation in obligations:
        oid = obligation.get('obligation_id', '')
        missing = [field for field in obligation_required_fields if field not in obligation or obligation.get(field) in ('', [], None)]
        if missing:
            errors.append(f'observed-sector obligation {oid or "<missing>"} missing required fields: {missing}')
        for rid in obligation.get('route_ids_touching', []):
            if rid not in known_route_ids:
                errors.append(f'observed-sector obligation {oid} references unknown route_id: {rid}')
        for cid in obligation.get('negative_controls', []):
            if cid not in known_control_ids:
                errors.append(f'observed-sector obligation {oid} references unknown negative control: {cid}')
    for row in route_rows:
        for oid in row.get('observed_sector_obligations', []):
            if oid not in known_obligation_ids:
                errors.append(f'route row {row.get("route_id")} references unknown observed-sector obligation: {oid}')
        if row.get('authority_state') in {'S4','S5'}:
            if not row.get('observed_sector_obligations'):
                errors.append(f'route row {row.get("route_id")} at {row.get("authority_state")} lacks observed-sector obligations')
    if any(row.get('authority_state') in {'S4','S5'} for row in route_rows) and observed_sector_ledger.get('no_obligation_closed_for_s5'):
        errors.append('route ledger contains S4/S5 while observed-sector ledger still declares no S5-obligation closure')

    forecast_rows = forecast_ledger.get('forecast_rows', [])
    forecast_ids = [item.get('forecast_id', '') for item in forecast_rows]
    known_forecast_ids = set(forecast_ids)
    if len(forecast_ids) != len(set(forecast_ids)):
        errors.append('DISCRIMINATOR-FORECAST-LEDGER contains duplicate forecast_id values')
    forecast_required_fields = ['forecast_id','route_id','artifact_type','required_public_record','positive_result_credit','negative_result_credit','underdetermination_controls','current_maximum_credit','non_promotion_warning','public_record_carrier_ids','acquisition_protocol_ids','evidence_unit_ids']
    for row in forecast_rows:
        fid = row.get('forecast_id', '')
        missing = [field for field in forecast_required_fields if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'discriminator forecast {fid or "<missing>"} missing required fields: {missing}')
        if row.get('route_id') not in known_route_ids:
            errors.append(f'discriminator forecast {fid} references unknown route_id: {row.get("route_id")}')
        if row.get('current_maximum_credit') not in allowed_states:
            errors.append(f'discriminator forecast {fid} has unknown current_maximum_credit: {row.get("current_maximum_credit")}')
        for cid in row.get('underdetermination_controls', []):
            if cid not in known_control_ids:
                errors.append(f'discriminator forecast {fid} references unknown negative control: {cid}')
        for carrier_id in row.get('public_record_carrier_ids', []):
            if carrier_id not in known_carrier_ids:
                errors.append(f'discriminator forecast {fid} references unknown public-record carrier: {carrier_id}')
        for protocol_id in row.get('acquisition_protocol_ids', []):
            if protocol_id not in known_protocol_ids:
                errors.append(f'discriminator forecast {fid} references unknown acquisition protocol: {protocol_id}')
    if f"- Promotion gates: `{len(gate_rows)}`" not in promotion_summary_text:
        errors.append('promotion/recovery generated summary gate count drifted; run make index')
    if f"- Observed-sector obligations: `{len(obligations)}`" not in promotion_summary_text:
        errors.append('promotion/recovery generated summary obligation count drifted; run make index')
    if f"- Forecast rows: `{len(forecast_rows)}`" not in promotion_summary_text:
        errors.append('promotion/recovery generated summary forecast count drifted; run make index')


    decision_experiments = decision_ledger.get('decision_experiments', [])
    decision_ids = [item.get('experiment_id', '') for item in decision_experiments]
    if len(decision_ids) != len(set(decision_ids)):
        errors.append('DECISION-EXPERIMENT-LEDGER contains duplicate experiment_id values')
    if len(decision_experiments) < 5:
        errors.append('DECISION-EXPERIMENT-LEDGER should preserve the current discriminator/cosmology/reconstruction decision rows')
    decision_required_fields = ['experiment_id','route_ids','target_question','public_record','decision_stage','minimum_public_artifact','source_refs','negative_controls','empirical_delta_hooks','outcome_effects','non_promotion_clause','public_record_carrier_ids','acquisition_protocol_ids','evidence_unit_ids']
    known_delta_ids = set(seen_delta_ids)
    for exp in decision_experiments:
        eid = exp.get('experiment_id', '')
        missing = [field for field in decision_required_fields if field not in exp or exp.get(field) in ('', [], None)]
        if missing:
            errors.append(f'decision experiment {eid or "<missing>"} missing required fields: {missing}')
        for rid in exp.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'decision experiment {eid} references unknown route_id: {rid}')
        for ref in exp.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'decision experiment {eid} references unknown REF id: {ref}')
        for cid in exp.get('negative_controls', []):
            if cid not in known_control_ids:
                errors.append(f'decision experiment {eid} references unknown negative control: {cid}')
        for did in exp.get('empirical_delta_hooks', []):
            if did not in known_delta_ids:
                errors.append(f'decision experiment {eid} references unknown empirical delta hook: {did}')
        for carrier_id in exp.get('public_record_carrier_ids', []):
            if carrier_id not in known_carrier_ids:
                errors.append(f'decision experiment {eid} references unknown public-record carrier: {carrier_id}')
        for protocol_id in exp.get('acquisition_protocol_ids', []):
            if protocol_id not in known_protocol_ids:
                errors.append(f'decision experiment {eid} references unknown acquisition protocol: {protocol_id}')
        for outcome in exp.get('outcome_effects', []):
            outcome_missing = [field for field in ['outcome_class','record_result','route_state_effect','promotion_ceiling','residual_cap','rollback_trigger'] if field not in outcome or outcome.get(field) in ('', [], None)]
            if outcome_missing:
                errors.append(f'decision experiment {eid} has outcome missing fields: {outcome_missing}')
            if outcome.get('promotion_ceiling') not in allowed_states:
                errors.append(f'decision experiment {eid} has unknown outcome promotion ceiling: {outcome.get("promotion_ceiling")}')
            if outcome.get('promotion_ceiling') in {'S4','S5'}:
                errors.append(f'decision experiment {eid} outcome tries to pre-authorize {outcome.get("promotion_ceiling")}; route promotion must use promotion gates after a realized empirical delta')
    if f"- Decision experiments: `{len(decision_experiments)}`" not in decision_summary_text:
        errors.append('decision-experiment generated summary count drifted; run make index')



    # Defeater, rollback, severity, and authority-dependency checks added in rev0264.
    defeater_rows = defeater_ledger.get('defeater_rows', [])
    defeater_ids = [item.get('defeater_id', '') for item in defeater_rows]
    if len(defeater_ids) != len(set(defeater_ids)):
        errors.append('EPISTEMIC-DEFEATER-LEDGER contains duplicate defeater_id values')
    if len(defeater_rows) < 10:
        errors.append('EPISTEMIC-DEFEATER-LEDGER should preserve the current source/custody/replay/control/quotient/forecast defeaters')
    known_defeater_ids = set(defeater_ids)
    allowed_defeater_types = set(witness_vocab.get('defeater_type_labels', []))
    defeater_required_keys = ['defeater_id','defeater_type','target_scope','route_ids','carrier_ids','protocol_ids','claim_or_oq_ids','negative_control_ids','triggering_condition','positive_surface_at_risk','defeated_authority','minimum_evidence_to_activate','adjudication_artifacts','propagation_action','rollback_rule_ids','source_refs']
    defeater_nonempty_fields = ['defeater_id','defeater_type','target_scope','triggering_condition','positive_surface_at_risk','defeated_authority','minimum_evidence_to_activate','adjudication_artifacts','propagation_action','rollback_rule_ids','source_refs']
    for defeater in defeater_rows:
        did = defeater.get('defeater_id', '')
        missing_keys = [field for field in defeater_required_keys if field not in defeater]
        if missing_keys:
            errors.append(f'defeater row {did or "<missing>"} missing required keys: {missing_keys}')
        missing_nonempty = [field for field in defeater_nonempty_fields if field not in defeater or defeater.get(field) in ('', [], None)]
        if missing_nonempty:
            errors.append(f'defeater row {did or "<missing>"} missing nonempty fields: {missing_nonempty}')
        if defeater.get('defeater_type') not in allowed_defeater_types:
            errors.append(f'defeater row {did} has unknown defeater_type: {defeater.get("defeater_type")}')
        for rid in defeater.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'defeater row {did} references unknown route_id: {rid}')
        for cid in defeater.get('carrier_ids', []):
            if cid not in known_carrier_ids:
                errors.append(f'defeater row {did} references unknown carrier_id: {cid}')
        for pid in defeater.get('protocol_ids', []):
            if pid not in known_protocol_ids:
                errors.append(f'defeater row {did} references unknown protocol_id: {pid}')
        for ncid in defeater.get('negative_control_ids', []):
            if ncid not in known_control_ids:
                errors.append(f'defeater row {did} references unknown negative control: {ncid}')
        for target in defeater.get('claim_or_oq_ids', []):
            if target.startswith('OQ-') and target not in registered_question_ids:
                errors.append(f'defeater row {did} references unknown OQ id: {target}')
            if target.startswith('CL-') and target not in registered_claim_ids:
                errors.append(f'defeater row {did} references unknown CL id: {target}')
        for ref in defeater.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'defeater row {did} references unknown REF id: {ref}')

    rollback_rows = rollback_ledger.get('rollback_rows', [])
    rollback_ids = [item.get('rollback_id', '') for item in rollback_rows]
    if len(rollback_ids) != len(set(rollback_ids)):
        errors.append('ROLLBACK-PROPAGATION-LEDGER contains duplicate rollback_id values')
    known_rollback_ids = set(rollback_ids)
    rollback_required_keys = ['rollback_id','defeater_ids','trigger_scope','affected_route_ids','affected_claim_or_oq_ids','affected_carrier_ids','affected_protocol_ids','trigger_condition','dependency_scope','immediate_state_effect','target_floor','public_notice','repair_conditions','no_silent_repromotion_rule']
    rollback_nonempty_fields = ['rollback_id','defeater_ids','trigger_scope','affected_route_ids','affected_claim_or_oq_ids','trigger_condition','dependency_scope','immediate_state_effect','target_floor','public_notice','repair_conditions','no_silent_repromotion_rule']
    for row in rollback_rows:
        rbid = row.get('rollback_id', '')
        missing_keys = [field for field in rollback_required_keys if field not in row]
        if missing_keys:
            errors.append(f'rollback row {rbid or "<missing>"} missing required keys: {missing_keys}')
        missing_nonempty = [field for field in rollback_nonempty_fields if field not in row or row.get(field) in ('', [], None)]
        if missing_nonempty:
            errors.append(f'rollback row {rbid or "<missing>"} missing nonempty fields: {missing_nonempty}')
        if row.get('target_floor') not in allowed_states:
            errors.append(f'rollback row {rbid} has unknown target_floor: {row.get("target_floor")}')
        for did in row.get('defeater_ids', []):
            if did not in known_defeater_ids:
                errors.append(f'rollback row {rbid} references unknown defeater_id: {did}')
        for rid in row.get('affected_route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'rollback row {rbid} references unknown route_id: {rid}')
        for cid in row.get('affected_carrier_ids', []):
            if cid not in known_carrier_ids:
                errors.append(f'rollback row {rbid} references unknown carrier_id: {cid}')
        for pid in row.get('affected_protocol_ids', []):
            if pid not in known_protocol_ids:
                errors.append(f'rollback row {rbid} references unknown protocol_id: {pid}')
        for target in row.get('affected_claim_or_oq_ids', []):
            if target.startswith('OQ-') and target not in registered_question_ids:
                errors.append(f'rollback row {rbid} references unknown OQ id: {target}')
            if target.startswith('CL-') and target not in registered_claim_ids:
                errors.append(f'rollback row {rbid} references unknown CL id: {target}')

    # All defeater rollback hooks must be backed by live rollback rows.
    for defeater in defeater_rows:
        for rbid in defeater.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'defeater row {defeater.get("defeater_id")} references unknown rollback rule: {rbid}')

    severity_rows = severity_ledger.get('severity_rows', [])
    severity_ids = [item.get('severity_id', '') for item in severity_rows]
    if len(severity_ids) != len(set(severity_ids)):
        errors.append('EVIDENCE-SEVERITY-LEDGER contains duplicate severity_id values')
    known_severity_ids = set(severity_ids)
    known_decision_ids = set(decision_ids)
    severity_required_keys = ['severity_id','route_ids','decision_experiment_ids','protocol_ids','carrier_ids','negative_control_ids','evidence_unit_ids','hypothesis_under_test','alternatives_or_failure_modes','pass_condition','severity_condition','public_artifact','maximum_credit_if_passed','defeat_if_failed','source_refs']
    severity_nonempty_fields = ['severity_id','route_ids','protocol_ids','carrier_ids','negative_control_ids','evidence_unit_ids','hypothesis_under_test','alternatives_or_failure_modes','pass_condition','severity_condition','public_artifact','maximum_credit_if_passed','defeat_if_failed','source_refs']
    for row in severity_rows:
        sid = row.get('severity_id', '')
        missing_keys = [field for field in severity_required_keys if field not in row]
        if missing_keys:
            errors.append(f'severity row {sid or "<missing>"} missing required keys: {missing_keys}')
        missing_nonempty = [field for field in severity_nonempty_fields if field not in row or row.get(field) in ('', [], None)]
        if missing_nonempty:
            errors.append(f'severity row {sid or "<missing>"} missing nonempty fields: {missing_nonempty}')
        if row.get('maximum_credit_if_passed') not in allowed_states:
            errors.append(f'severity row {sid} has unknown maximum_credit_if_passed: {row.get("maximum_credit_if_passed")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'severity row {sid} references unknown route_id: {rid}')
        for dxid in row.get('decision_experiment_ids', []):
            if dxid not in known_decision_ids:
                errors.append(f'severity row {sid} references unknown decision experiment: {dxid}')
        for pid in row.get('protocol_ids', []):
            if pid not in known_protocol_ids:
                errors.append(f'severity row {sid} references unknown protocol_id: {pid}')
        for cid in row.get('carrier_ids', []):
            if cid not in known_carrier_ids:
                errors.append(f'severity row {sid} references unknown carrier_id: {cid}')
        for ncid in row.get('negative_control_ids', []):
            if ncid not in known_control_ids:
                errors.append(f'severity row {sid} references unknown negative control: {ncid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'severity row {sid} references unknown REF id: {ref}')
        for rbid in re.findall(r'RB-\d{4}[A-Z0-9-]*', str(row.get('defeat_if_failed',''))):
            if rbid not in known_rollback_ids:
                errors.append(f'severity row {sid} defeat_if_failed references unknown rollback rule: {rbid}')

    for row in route_rows:
        rid = row.get('route_id', '')
        for did in row.get('defeater_ids', []):
            if did not in known_defeater_ids:
                errors.append(f'route row {rid} references unknown defeater: {did}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'route row {rid} references unknown rollback rule: {rbid}')
        for sid in row.get('severity_test_ids', []):
            if sid not in known_severity_ids:
                errors.append(f'route row {rid} references unknown severity test: {sid}')


    # Evidence-unit, independence-assumption, and credit-allocation checks added in rev0265.
    evidence_units = evidence_unit_ledger.get('evidence_units', [])
    evidence_unit_ids = [item.get('evidence_unit_id', '') for item in evidence_units]
    if len(evidence_unit_ids) != len(set(evidence_unit_ids)):
        errors.append('EVIDENCE-UNIT-LEDGER contains duplicate evidence_unit_id values')
    if len(evidence_units) < len(route_rows):
        errors.append('EVIDENCE-UNIT-LEDGER should preserve at least one route-touching evidence unit per current route')
    known_evidence_unit_ids = set(evidence_unit_ids)
    allowed_evidence_statuses = set(witness_vocab.get('evidence_unit_status_labels', []))
    allowed_credit_roles = set(witness_vocab.get('evidence_credit_role_labels', []))
    evidence_required_keys = ['evidence_unit_id','route_ids','support_kind','record_status','record_description','carrier_ids','protocol_ids','empirical_delta_ids','severity_test_ids','negative_control_ids','independence_assumption_ids','shared_support_cluster','credit_role','maximum_credit','double_counting_risk','credit_spend_rule','rollback_if_compromised','source_refs']
    evidence_nonempty_keys = ['evidence_unit_id','route_ids','support_kind','record_status','record_description','carrier_ids','protocol_ids','independence_assumption_ids','shared_support_cluster','credit_role','maximum_credit','double_counting_risk','credit_spend_rule','rollback_if_compromised','source_refs']
    for unit in evidence_units:
        uid = unit.get('evidence_unit_id', '')
        missing_keys = [field for field in evidence_required_keys if field not in unit]
        missing_nonempty = [field for field in evidence_nonempty_keys if unit.get(field) in ('', [], None)]
        if missing_keys or missing_nonempty:
            errors.append(f'evidence unit {uid or "<missing>"} missing required fields: keys={missing_keys}, nonempty={missing_nonempty}')
        if unit.get('record_status') not in allowed_evidence_statuses:
            errors.append(f'evidence unit {uid} has unknown record_status: {unit.get("record_status")}')
        if unit.get('credit_role') not in allowed_credit_roles:
            errors.append(f'evidence unit {uid} has unknown credit_role: {unit.get("credit_role")}')
        if unit.get('maximum_credit') not in allowed_states:
            errors.append(f'evidence unit {uid} has unknown maximum_credit: {unit.get("maximum_credit")}')
        for rid in unit.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'evidence unit {uid} references unknown route_id: {rid}')
        for cid in unit.get('carrier_ids', []):
            if cid not in known_carrier_ids:
                errors.append(f'evidence unit {uid} references unknown carrier_id: {cid}')
        for pid in unit.get('protocol_ids', []):
            if pid not in known_protocol_ids:
                errors.append(f'evidence unit {uid} references unknown protocol_id: {pid}')
        for did in unit.get('empirical_delta_ids', []):
            if did not in known_delta_ids:
                errors.append(f'evidence unit {uid} references unknown empirical delta: {did}')
        for sid in unit.get('severity_test_ids', []):
            if sid not in known_severity_ids:
                errors.append(f'evidence unit {uid} references unknown severity test: {sid}')
        for ncid in unit.get('negative_control_ids', []):
            if ncid not in known_control_ids:
                errors.append(f'evidence unit {uid} references unknown negative control: {ncid}')
        for ref in unit.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'evidence unit {uid} references unknown REF id: {ref}')

    independence_rows = independence_ledger.get('independence_rows', [])
    independence_ids = [item.get('independence_id', '') for item in independence_rows]
    if len(independence_ids) != len(set(independence_ids)):
        errors.append('INDEPENDENCE-ASSUMPTION-LEDGER contains duplicate independence_id values')
    known_independence_ids = set(independence_ids)
    allowed_independence_types = set(witness_vocab.get('independence_assumption_type_labels', []))
    independence_required_keys = ['independence_id','assumption_type','route_ids','evidence_unit_ids','independence_claim','failure_mode','stress_test','minimum_disclosure','aggregation_effect','defeater_ids','rollback_rule_ids','source_refs']
    for row in independence_rows:
        iid = row.get('independence_id', '')
        missing = [field for field in independence_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'independence assumption {iid or "<missing>"} missing required fields: {missing}')
        if row.get('assumption_type') not in allowed_independence_types:
            errors.append(f'independence assumption {iid} has unknown assumption_type: {row.get("assumption_type")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'independence assumption {iid} references unknown route_id: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'independence assumption {iid} references unknown evidence_unit_id: {uid}')
        for did in row.get('defeater_ids', []):
            if did not in known_defeater_ids:
                errors.append(f'independence assumption {iid} references unknown defeater_id: {did}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'independence assumption {iid} references unknown rollback rule: {rbid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'independence assumption {iid} references unknown REF id: {ref}')

    # Evidence units and independence assumptions should be bidirectionally coherent enough to catch typo drift.
    unit_by_id = {item.get('evidence_unit_id',''): item for item in evidence_units}
    independence_by_id = {item.get('independence_id',''): item for item in independence_rows}
    for unit in evidence_units:
        uid = unit.get('evidence_unit_id', '')
        for iid in unit.get('independence_assumption_ids', []):
            if iid not in known_independence_ids:
                errors.append(f'evidence unit {uid} references unknown independence assumption: {iid}')
            elif uid not in independence_by_id[iid].get('evidence_unit_ids', []):
                errors.append(f'evidence unit {uid} names independence assumption {iid}, but independence row does not name evidence unit')
    for row in independence_rows:
        iid = row.get('independence_id', '')
        for uid in row.get('evidence_unit_ids', []):
            if uid in unit_by_id and iid not in unit_by_id[uid].get('independence_assumption_ids', []):
                errors.append(f'independence assumption {iid} names evidence unit {uid}, but evidence unit does not name assumption')

    credit_rows = credit_allocation_ledger.get('credit_rows', [])
    credit_ids = [item.get('credit_id', '') for item in credit_rows]
    if len(credit_ids) != len(set(credit_ids)):
        errors.append('CREDIT-ALLOCATION-LEDGER contains duplicate credit_id values')
    known_credit_ids = set(credit_ids)
    credit_required_keys = ['credit_id','route_id','evidence_unit_ids','independence_assumption_ids','independence_clusters','aggregation_rule','current_credit_basis','maximum_authority_effect','no_double_counting_rule','cannot_compensate_for','claim_or_oq_ids','rollback_rule_ids','source_refs']
    for credit in credit_rows:
        caid = credit.get('credit_id', '')
        missing = [field for field in credit_required_keys if field not in credit or credit.get(field) in ('', [], None)]
        if missing:
            errors.append(f'credit allocation {caid or "<missing>"} missing required fields: {missing}')
        if credit.get('route_id') not in known_route_ids:
            errors.append(f'credit allocation {caid} references unknown route_id: {credit.get("route_id")}')
        if credit.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'credit allocation {caid} has unknown maximum_authority_effect: {credit.get("maximum_authority_effect")}')
        for uid in credit.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'credit allocation {caid} references unknown evidence_unit_id: {uid}')
        for iid in credit.get('independence_assumption_ids', []):
            if iid not in known_independence_ids:
                errors.append(f'credit allocation {caid} references unknown independence assumption: {iid}')
        for target in credit.get('claim_or_oq_ids', []):
            if target.startswith('OQ-') and target not in registered_question_ids:
                errors.append(f'credit allocation {caid} references unknown OQ id: {target}')
            if target.startswith('CL-') and target not in registered_claim_ids:
                errors.append(f'credit allocation {caid} references unknown CL id: {target}')
        for rbid in credit.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'credit allocation {caid} references unknown rollback rule: {rbid}')
        for ref in credit.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'credit allocation {caid} references unknown REF id: {ref}')

    for row in route_rows:
        rid = row.get('route_id', '')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'route row {rid} references unknown evidence unit: {uid}')
            elif rid not in unit_by_id[uid].get('route_ids', []):
                errors.append(f'route row {rid} names evidence unit {uid}, but evidence unit does not name route')
        for iid in row.get('independence_assumption_ids', []):
            if iid not in known_independence_ids:
                errors.append(f'route row {rid} references unknown independence assumption: {iid}')
            elif rid not in independence_by_id[iid].get('route_ids', []):
                errors.append(f'route row {rid} names independence assumption {iid}, but independence row does not name route')
        for caid in row.get('credit_allocation_ids', []):
            if caid not in known_credit_ids:
                errors.append(f'route row {rid} references unknown credit allocation: {caid}')


    # Contrast-class, likelihood/update, and prior-sensitivity checks added in rev0266.
    contrast_rows = contrast_class_ledger.get('contrast_rows', [])
    contrast_ids = [item.get('contrast_class_id', '') for item in contrast_rows]
    if len(contrast_ids) != len(set(contrast_ids)):
        errors.append('CONTRAST-CLASS-LEDGER contains duplicate contrast_class_id values')
    known_contrast_ids = set(contrast_ids)
    contrast_required_keys = ['contrast_class_id','route_ids','evidence_unit_ids','comparator_scope','target_question','live_alternatives','quotient_policy','contrast_completeness_status','current_update_ceiling','negative_control_ids','rollback_rule_ids','source_refs']
    for row in contrast_rows:
        cid = row.get('contrast_class_id', '')
        missing = [field for field in contrast_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'contrast class {cid or "<missing>"} missing required fields: {missing}')
        if row.get('current_update_ceiling') not in allowed_states:
            errors.append(f'contrast class {cid} has unknown current_update_ceiling: {row.get("current_update_ceiling")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'contrast class {cid} references unknown route_id: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'contrast class {cid} references unknown evidence_unit_id: {uid}')
        for control_id in row.get('negative_control_ids', []):
            if control_id not in known_control_ids:
                errors.append(f'contrast class {cid} references unknown negative control: {control_id}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'contrast class {cid} references unknown rollback rule: {rbid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'contrast class {cid} references unknown REF id: {ref}')

    update_rows = likelihood_update_ledger.get('update_rows', [])
    update_ids = [item.get('likelihood_update_id', '') for item in update_rows]
    if len(update_ids) != len(set(update_ids)):
        errors.append('LIKELIHOOD-UPDATE-LEDGER contains duplicate likelihood_update_id values')
    known_update_ids = set(update_ids)
    update_required_keys = ['likelihood_update_id','route_id','contrast_class_id','evidence_unit_ids','update_mode','likelihood_or_score_object','outcome_classes','prior_sensitivity_ids','current_update_status','maximum_authority_effect','no_update_if','rollback_rule_ids','source_refs']
    for row in update_rows:
        luid = row.get('likelihood_update_id', '')
        missing = [field for field in update_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'likelihood/update row {luid or "<missing>"} missing required fields: {missing}')
        rid = row.get('route_id')
        if rid != 'ALL-ROUTES-CUSTODY-ONLY' and rid not in known_route_ids:
            errors.append(f'likelihood/update row {luid} references unknown route_id: {rid}')
        if row.get('contrast_class_id') not in known_contrast_ids:
            errors.append(f'likelihood/update row {luid} references unknown contrast_class_id: {row.get("contrast_class_id")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'likelihood/update row {luid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'likelihood/update row {luid} references unknown evidence_unit_id: {uid}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'likelihood/update row {luid} references unknown rollback rule: {rbid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'likelihood/update row {luid} references unknown REF id: {ref}')

    prior_rows = prior_sensitivity_ledger.get('prior_rows', [])
    prior_ids = [item.get('prior_sensitivity_id', '') for item in prior_rows]
    if len(prior_ids) != len(set(prior_ids)):
        errors.append('PRIOR-SENSITIVITY-LEDGER contains duplicate prior_sensitivity_id values')
    known_prior_ids = set(prior_ids)
    prior_required_keys = ['prior_sensitivity_id','route_ids','contrast_class_ids','evidence_unit_ids','prior_family','sensitivity_dimensions','stress_test','current_status','maximum_authority_effect','likelihood_update_ids','rollback_rule_ids','source_refs']
    for row in prior_rows:
        psid = row.get('prior_sensitivity_id', '')
        missing = [field for field in prior_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'prior-sensitivity row {psid or "<missing>"} missing required fields: {missing}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'prior-sensitivity row {psid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'prior-sensitivity row {psid} references unknown route_id: {rid}')
        for cid in row.get('contrast_class_ids', []):
            if cid not in known_contrast_ids:
                errors.append(f'prior-sensitivity row {psid} references unknown contrast class: {cid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'prior-sensitivity row {psid} references unknown evidence unit: {uid}')
        for luid in row.get('likelihood_update_ids', []):
            if luid not in known_update_ids:
                errors.append(f'prior-sensitivity row {psid} references unknown likelihood/update row: {luid}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'prior-sensitivity row {psid} references unknown rollback rule: {rbid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'prior-sensitivity row {psid} references unknown REF id: {ref}')

    # Route/evidence/credit references to the new contrast/update/prior handles.
    contrast_by_id = {row.get('contrast_class_id',''): row for row in contrast_rows}
    prior_by_id = {row.get('prior_sensitivity_id',''): row for row in prior_rows}
    update_by_id = {row.get('likelihood_update_id',''): row for row in update_rows}
    for row in route_rows:
        rid = row.get('route_id', '')
        for cid in row.get('contrast_class_ids', []):
            if cid not in known_contrast_ids:
                errors.append(f'route row {rid} references unknown contrast class: {cid}')
            elif rid not in contrast_by_id[cid].get('route_ids', []):
                errors.append(f'route row {rid} names contrast class {cid}, but contrast row does not name route')
        for luid in row.get('likelihood_update_ids', []):
            if luid not in known_update_ids:
                errors.append(f'route row {rid} references unknown likelihood/update row: {luid}')
            elif update_by_id[luid].get('route_id') != rid:
                errors.append(f'route row {rid} names likelihood/update row {luid}, but update row does not name route')
        for psid in row.get('prior_sensitivity_ids', []):
            if psid not in known_prior_ids:
                errors.append(f'route row {rid} references unknown prior-sensitivity row: {psid}')
            elif rid not in prior_by_id[psid].get('route_ids', []):
                errors.append(f'route row {rid} names prior-sensitivity row {psid}, but prior row does not name route')
    for unit in evidence_units:
        uid = unit.get('evidence_unit_id', '')
        for cid in unit.get('contrast_class_ids', []):
            if cid not in known_contrast_ids:
                errors.append(f'evidence unit {uid} references unknown contrast class: {cid}')
        for luid in unit.get('likelihood_update_ids', []):
            if luid not in known_update_ids:
                errors.append(f'evidence unit {uid} references unknown likelihood/update row: {luid}')
        for psid in unit.get('prior_sensitivity_ids', []):
            if psid not in known_prior_ids:
                errors.append(f'evidence unit {uid} references unknown prior-sensitivity row: {psid}')
    for credit in credit_rows:
        caid = credit.get('credit_id', '')
        for cid in credit.get('contrast_class_ids', []):
            if cid not in known_contrast_ids:
                errors.append(f'credit allocation {caid} references unknown contrast class: {cid}')
        for luid in credit.get('likelihood_update_ids', []):
            if luid not in known_update_ids:
                errors.append(f'credit allocation {caid} references unknown likelihood/update row: {luid}')
        for psid in credit.get('prior_sensitivity_ids', []):
            if psid not in known_prior_ids:
                errors.append(f'credit allocation {caid} references unknown prior-sensitivity row: {psid}')


    # Measurement-model, systematic-uncertainty, and calibration/traceability checks added in rev0267.
    measurement_rows = measurement_model_ledger.get('measurement_model_rows', [])
    measurement_ids = [item.get('measurement_model_id', '') for item in measurement_rows]
    if len(measurement_ids) != len(set(measurement_ids)):
        errors.append('MEASUREMENT-MODEL-LEDGER contains duplicate measurement_model_id values')
    known_measurement_model_ids = set(measurement_ids)
    measurement_required_keys = ['measurement_model_id','route_ids','evidence_unit_ids','carrier_ids','protocol_ids','model_class','measurand_or_target','raw_record_inputs','transformation_model','correction_model','uncertainty_expression','candidate_native_gap','maximum_authority_effect','defeater_ids','rollback_rule_ids','source_refs']
    allowed_measurement_classes = set(witness_vocab.get('measurement_model_class_labels', []))
    for row in measurement_rows:
        mid = row.get('measurement_model_id', '')
        missing = [field for field in measurement_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'measurement model {mid or "<missing>"} missing required fields: {missing}')
        if row.get('model_class') not in allowed_measurement_classes:
            errors.append(f'measurement model {mid} has unknown model_class: {row.get("model_class")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'measurement model {mid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'measurement model {mid} references unknown route_id: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'measurement model {mid} references unknown evidence unit: {uid}')
        for cid in row.get('carrier_ids', []):
            if cid not in known_carrier_ids:
                errors.append(f'measurement model {mid} references unknown carrier: {cid}')
        for pid in row.get('protocol_ids', []):
            if pid not in known_protocol_ids:
                errors.append(f'measurement model {mid} references unknown protocol: {pid}')
        for did in row.get('defeater_ids', []):
            if did not in known_defeater_ids:
                errors.append(f'measurement model {mid} references unknown defeater: {did}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'measurement model {mid} references unknown rollback rule: {rbid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'measurement model {mid} references unknown REF id: {ref}')

    systematic_rows = systematic_uncertainty_ledger.get('systematic_rows', [])
    systematic_ids = [item.get('systematic_id', '') for item in systematic_rows]
    if len(systematic_ids) != len(set(systematic_ids)):
        errors.append('SYSTEMATIC-UNCERTAINTY-LEDGER contains duplicate systematic_id values')
    known_systematic_ids = set(systematic_ids)
    systematic_required_keys = ['systematic_id','route_ids','evidence_unit_ids','measurement_model_ids','systematic_class','uncertainty_source','bias_or_failure_mode','nuisance_parameters','stress_test','mitigation_or_bound','residual_effect','maximum_authority_effect','defeater_ids','rollback_rule_ids','source_refs']
    allowed_systematic_classes = set(witness_vocab.get('systematic_uncertainty_class_labels', []))
    for row in systematic_rows:
        sid = row.get('systematic_id', '')
        missing = [field for field in systematic_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'systematic uncertainty row {sid or "<missing>"} missing required fields: {missing}')
        if row.get('systematic_class') not in allowed_systematic_classes:
            errors.append(f'systematic uncertainty row {sid} has unknown systematic_class: {row.get("systematic_class")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'systematic uncertainty row {sid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'systematic uncertainty row {sid} references unknown route_id: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'systematic uncertainty row {sid} references unknown evidence unit: {uid}')
        for mid in row.get('measurement_model_ids', []):
            if mid not in known_measurement_model_ids:
                errors.append(f'systematic uncertainty row {sid} references unknown measurement model: {mid}')
        for did in row.get('defeater_ids', []):
            if did not in known_defeater_ids:
                errors.append(f'systematic uncertainty row {sid} references unknown defeater: {did}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'systematic uncertainty row {sid} references unknown rollback rule: {rbid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'systematic uncertainty row {sid} references unknown REF id: {ref}')

    calibration_rows = calibration_traceability_ledger.get('calibration_rows', [])
    calibration_ids = [item.get('calibration_id', '') for item in calibration_rows]
    if len(calibration_ids) != len(set(calibration_ids)):
        errors.append('CALIBRATION-TRACEABILITY-LEDGER contains duplicate calibration_id values')
    known_calibration_ids = set(calibration_ids)
    calibration_required_keys = ['calibration_id','route_ids','evidence_unit_ids','measurement_model_ids','systematic_ids','carrier_ids','protocol_ids','traceability_class','reference_object_or_standard','calibration_chain','uncertainty_budget','drift_control','replay_or_audit_artifact','failure_effect','maximum_authority_effect','source_refs']
    allowed_calibration_classes = set(witness_vocab.get('calibration_traceability_class_labels', []))
    for row in calibration_rows:
        calid = row.get('calibration_id', '')
        missing = [field for field in calibration_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'calibration/traceability row {calid or "<missing>"} missing required fields: {missing}')
        if row.get('traceability_class') not in allowed_calibration_classes:
            errors.append(f'calibration/traceability row {calid} has unknown traceability_class: {row.get("traceability_class")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'calibration/traceability row {calid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'calibration/traceability row {calid} references unknown route_id: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'calibration/traceability row {calid} references unknown evidence unit: {uid}')
        for mid in row.get('measurement_model_ids', []):
            if mid not in known_measurement_model_ids:
                errors.append(f'calibration/traceability row {calid} references unknown measurement model: {mid}')
        for sid in row.get('systematic_ids', []):
            if sid not in known_systematic_ids:
                errors.append(f'calibration/traceability row {calid} references unknown systematic row: {sid}')
        for cid in row.get('carrier_ids', []):
            if cid not in known_carrier_ids:
                errors.append(f'calibration/traceability row {calid} references unknown carrier: {cid}')
        for pid in row.get('protocol_ids', []):
            if pid not in known_protocol_ids:
                errors.append(f'calibration/traceability row {calid} references unknown protocol: {pid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'calibration/traceability row {calid} references unknown REF id: {ref}')

    measurement_by_id = {row.get('measurement_model_id',''): row for row in measurement_rows}
    systematic_by_id = {row.get('systematic_id',''): row for row in systematic_rows}
    calibration_by_id = {row.get('calibration_id',''): row for row in calibration_rows}
    for row in route_rows:
        rid = row.get('route_id', '')
        for mid in row.get('measurement_model_ids', []):
            if mid not in known_measurement_model_ids:
                errors.append(f'route row {rid} references unknown measurement model: {mid}')
            elif rid not in measurement_by_id[mid].get('route_ids', []):
                errors.append(f'route row {rid} names measurement model {mid}, but measurement row does not name route')
        for sid in row.get('systematic_uncertainty_ids', []):
            if sid not in known_systematic_ids:
                errors.append(f'route row {rid} references unknown systematic uncertainty row: {sid}')
            elif rid not in systematic_by_id[sid].get('route_ids', []):
                errors.append(f'route row {rid} names systematic row {sid}, but systematic row does not name route')
        for calid in row.get('calibration_traceability_ids', []):
            if calid not in known_calibration_ids:
                errors.append(f'route row {rid} references unknown calibration/traceability row: {calid}')
            elif rid not in calibration_by_id[calid].get('route_ids', []):
                errors.append(f'route row {rid} names calibration row {calid}, but calibration row does not name route')

    for unit in evidence_units:
        uid = unit.get('evidence_unit_id', '')
        for mid in unit.get('measurement_model_ids', []):
            if mid not in known_measurement_model_ids:
                errors.append(f'evidence unit {uid} references unknown measurement model: {mid}')
            elif uid not in measurement_by_id[mid].get('evidence_unit_ids', []):
                errors.append(f'evidence unit {uid} names measurement model {mid}, but measurement row does not name evidence unit')
        for sid in unit.get('systematic_uncertainty_ids', []):
            if sid not in known_systematic_ids:
                errors.append(f'evidence unit {uid} references unknown systematic uncertainty row: {sid}')
            elif uid not in systematic_by_id[sid].get('evidence_unit_ids', []):
                errors.append(f'evidence unit {uid} names systematic row {sid}, but systematic row does not name evidence unit')
        for calid in unit.get('calibration_traceability_ids', []):
            if calid not in known_calibration_ids:
                errors.append(f'evidence unit {uid} references unknown calibration/traceability row: {calid}')
            elif uid not in calibration_by_id[calid].get('evidence_unit_ids', []):
                errors.append(f'evidence unit {uid} names calibration row {calid}, but calibration row does not name evidence unit')

    for credit in credit_rows:
        caid = credit.get('credit_id', '')
        for mid in credit.get('measurement_model_ids', []):
            if mid not in known_measurement_model_ids:
                errors.append(f'credit allocation {caid} references unknown measurement model: {mid}')
        for sid in credit.get('systematic_uncertainty_ids', []):
            if sid not in known_systematic_ids:
                errors.append(f'credit allocation {caid} references unknown systematic uncertainty row: {sid}')
        for calid in credit.get('calibration_traceability_ids', []):
            if calid not in known_calibration_ids:
                errors.append(f'credit allocation {caid} references unknown calibration/traceability row: {calid}')

    for row in update_rows:
        luid = row.get('likelihood_update_id', '')
        for mid in row.get('measurement_model_ids', []):
            if mid not in known_measurement_model_ids:
                errors.append(f'likelihood/update row {luid} references unknown measurement model: {mid}')
        for sid in row.get('systematic_uncertainty_ids', []):
            if sid not in known_systematic_ids:
                errors.append(f'likelihood/update row {luid} references unknown systematic uncertainty row: {sid}')
        for calid in row.get('calibration_traceability_ids', []):
            if calid not in known_calibration_ids:
                errors.append(f'likelihood/update row {luid} references unknown calibration/traceability row: {calid}')

    for row in prior_rows:
        psid = row.get('prior_sensitivity_id', '')
        for mid in row.get('measurement_model_ids', []):
            if mid not in known_measurement_model_ids:
                errors.append(f'prior-sensitivity row {psid} references unknown measurement model: {mid}')
        for sid in row.get('systematic_uncertainty_ids', []):
            if sid not in known_systematic_ids:
                errors.append(f'prior-sensitivity row {psid} references unknown systematic uncertainty row: {sid}')
        for calid in row.get('calibration_traceability_ids', []):
            if calid not in known_calibration_ids:
                errors.append(f'prior-sensitivity row {psid} references unknown calibration/traceability row: {calid}')

    if f"- Measurement-model rows: `{len(measurement_rows)}`" not in measurement_systematics_summary_text:
        errors.append('measurement/systematics generated summary measurement-model count drifted; run make index')
    if f"- Systematic-uncertainty rows: `{len(systematic_rows)}`" not in measurement_systematics_summary_text:
        errors.append('measurement/systematics generated summary systematic count drifted; run make index')
    if f"- Calibration-traceability rows: `{len(calibration_rows)}`" not in measurement_systematics_summary_text:
        errors.append('measurement/systematics generated summary calibration count drifted; run make index')

    # Validity-domain, transportability, and extrapolation-fence checks added in rev0268.
    domain_rows = domain_validity_ledger.get('domain_rows', [])
    domain_ids = [item.get('domain_id', '') for item in domain_rows]
    if len(domain_ids) != len(set(domain_ids)):
        errors.append('DOMAIN-OF-VALIDITY-LEDGER contains duplicate domain_id values')
    known_domain_ids = set(domain_ids)
    allowed_domain_classes = set(witness_vocab.get('validity_domain_class_labels', []))
    domain_required_keys = ['domain_id','route_ids','evidence_unit_ids','measurement_model_ids','contrast_class_ids','domain_class','source_domain','target_domain','boundary_conditions','invariants_preserved','known_exclusions','domain_shift_watchlist','maximum_authority_effect','defeater_ids','rollback_rule_ids','source_refs']
    for row in domain_rows:
        did = row.get('domain_id', '')
        missing = [field for field in domain_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'validity-domain row {did or "<missing>"} missing required fields: {missing}')
        if row.get('domain_class') not in allowed_domain_classes:
            errors.append(f'validity-domain row {did} has unknown domain_class: {row.get("domain_class")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'validity-domain row {did} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'validity-domain row {did} references unknown route_id: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'validity-domain row {did} references unknown evidence unit: {uid}')
        for mid in row.get('measurement_model_ids', []):
            if mid not in known_measurement_model_ids:
                errors.append(f'validity-domain row {did} references unknown measurement model: {mid}')
        for cid in row.get('contrast_class_ids', []):
            if cid not in known_contrast_ids:
                errors.append(f'validity-domain row {did} references unknown contrast class: {cid}')
        for defeater_id in row.get('defeater_ids', []):
            if defeater_id not in known_defeater_ids:
                errors.append(f'validity-domain row {did} references unknown defeater: {defeater_id}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'validity-domain row {did} references unknown rollback rule: {rbid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'validity-domain row {did} references unknown REF id: {ref}')

    transport_rows = transportability_ledger.get('transport_rows', [])
    transport_ids = [item.get('transport_id', '') for item in transport_rows]
    if len(transport_ids) != len(set(transport_ids)):
        errors.append('TRANSPORTABILITY-LEDGER contains duplicate transport_id values')
    known_transport_ids = set(transport_ids)
    allowed_transport_statuses = set(witness_vocab.get('transportability_status_labels', []))
    transport_required_keys = ['transport_id','route_ids','domain_ids','evidence_unit_ids','contrast_class_ids','measurement_model_ids','transport_status','source_context','target_context','selection_or_domain_shift_variables','invariance_claim','transport_map_or_formula','stress_test','failure_effect','maximum_authority_effect','defeater_ids','rollback_rule_ids','source_refs']
    for row in transport_rows:
        tid = row.get('transport_id', '')
        missing = [field for field in transport_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'transportability row {tid or "<missing>"} missing required fields: {missing}')
        if row.get('transport_status') not in allowed_transport_statuses:
            errors.append(f'transportability row {tid} has unknown transport_status: {row.get("transport_status")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'transportability row {tid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'transportability row {tid} references unknown route_id: {rid}')
        for did in row.get('domain_ids', []):
            if did not in known_domain_ids:
                errors.append(f'transportability row {tid} references unknown validity-domain row: {did}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'transportability row {tid} references unknown evidence unit: {uid}')
        for cid in row.get('contrast_class_ids', []):
            if cid not in known_contrast_ids:
                errors.append(f'transportability row {tid} references unknown contrast class: {cid}')
        for mid in row.get('measurement_model_ids', []):
            if mid not in known_measurement_model_ids:
                errors.append(f'transportability row {tid} references unknown measurement model: {mid}')
        for defeater_id in row.get('defeater_ids', []):
            if defeater_id not in known_defeater_ids:
                errors.append(f'transportability row {tid} references unknown defeater: {defeater_id}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'transportability row {tid} references unknown rollback rule: {rbid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'transportability row {tid} references unknown REF id: {ref}')

    fence_rows = extrapolation_fence_ledger.get('fence_rows', [])
    fence_ids = [item.get('fence_id', '') for item in fence_rows]
    if len(fence_ids) != len(set(fence_ids)):
        errors.append('EXTRAPOLATION-FENCE-LEDGER contains duplicate fence_id values')
    known_fence_ids = set(fence_ids)
    allowed_fence_classes = set(witness_vocab.get('extrapolation_fence_class_labels', []))
    fence_required_keys = ['fence_id','route_ids','domain_ids','transport_ids','evidence_unit_ids','fence_class','forbidden_inference','allowed_inference','escalation_condition','target_floor_if_violated','maximum_authority_effect','rollback_rule_ids','source_refs']
    for row in fence_rows:
        xid = row.get('fence_id', '')
        missing = [field for field in fence_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'extrapolation-fence row {xid or "<missing>"} missing required fields: {missing}')
        if row.get('fence_class') not in allowed_fence_classes:
            errors.append(f'extrapolation-fence row {xid} has unknown fence_class: {row.get("fence_class")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'extrapolation-fence row {xid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        if row.get('target_floor_if_violated') not in allowed_states:
            errors.append(f'extrapolation-fence row {xid} has unknown target_floor_if_violated: {row.get("target_floor_if_violated")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'extrapolation-fence row {xid} references unknown route_id: {rid}')
        for did in row.get('domain_ids', []):
            if did not in known_domain_ids:
                errors.append(f'extrapolation-fence row {xid} references unknown validity-domain row: {did}')
        for tid in row.get('transport_ids', []):
            if tid not in known_transport_ids:
                errors.append(f'extrapolation-fence row {xid} references unknown transportability row: {tid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'extrapolation-fence row {xid} references unknown evidence unit: {uid}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'extrapolation-fence row {xid} references unknown rollback rule: {rbid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'extrapolation-fence row {xid} references unknown REF id: {ref}')

    domain_by_id = {row.get('domain_id',''): row for row in domain_rows}
    transport_by_id = {row.get('transport_id',''): row for row in transport_rows}
    fence_by_id = {row.get('fence_id',''): row for row in fence_rows}
    for row in route_rows:
        rid = row.get('route_id', '')
        for did in row.get('validity_domain_ids', []):
            if did not in known_domain_ids:
                errors.append(f'route row {rid} references unknown validity-domain row: {did}')
            elif rid not in domain_by_id[did].get('route_ids', []):
                errors.append(f'route row {rid} names validity-domain row {did}, but domain row does not name route')
        for tid in row.get('transportability_ids', []):
            if tid not in known_transport_ids:
                errors.append(f'route row {rid} references unknown transportability row: {tid}')
            elif rid not in transport_by_id[tid].get('route_ids', []):
                errors.append(f'route row {rid} names transportability row {tid}, but transportability row does not name route')
        for xid in row.get('extrapolation_fence_ids', []):
            if xid not in known_fence_ids:
                errors.append(f'route row {rid} references unknown extrapolation-fence row: {xid}')
            elif rid not in fence_by_id[xid].get('route_ids', []):
                errors.append(f'route row {rid} names extrapolation-fence row {xid}, but fence row does not name route')

    for unit in evidence_units:
        uid = unit.get('evidence_unit_id', '')
        for did in unit.get('validity_domain_ids', []):
            if did not in known_domain_ids:
                errors.append(f'evidence unit {uid} references unknown validity-domain row: {did}')
            elif uid not in domain_by_id[did].get('evidence_unit_ids', []):
                errors.append(f'evidence unit {uid} names validity-domain row {did}, but domain row does not name evidence unit')
        for tid in unit.get('transportability_ids', []):
            if tid not in known_transport_ids:
                errors.append(f'evidence unit {uid} references unknown transportability row: {tid}')
            elif uid not in transport_by_id[tid].get('evidence_unit_ids', []):
                errors.append(f'evidence unit {uid} names transportability row {tid}, but transportability row does not name evidence unit')
        for xid in unit.get('extrapolation_fence_ids', []):
            if xid not in known_fence_ids:
                errors.append(f'evidence unit {uid} references unknown extrapolation-fence row: {xid}')
            elif uid not in fence_by_id[xid].get('evidence_unit_ids', []):
                errors.append(f'evidence unit {uid} names extrapolation-fence row {xid}, but fence row does not name evidence unit')

    for credit in credit_rows:
        caid = credit.get('credit_id', '')
        for did in credit.get('validity_domain_ids', []):
            if did not in known_domain_ids:
                errors.append(f'credit allocation {caid} references unknown validity-domain row: {did}')
        for tid in credit.get('transportability_ids', []):
            if tid not in known_transport_ids:
                errors.append(f'credit allocation {caid} references unknown transportability row: {tid}')
        for xid in credit.get('extrapolation_fence_ids', []):
            if xid not in known_fence_ids:
                errors.append(f'credit allocation {caid} references unknown extrapolation-fence row: {xid}')

    for row in update_rows:
        luid = row.get('likelihood_update_id', '')
        for did in row.get('validity_domain_ids', []):
            if did not in known_domain_ids:
                errors.append(f'likelihood/update row {luid} references unknown validity-domain row: {did}')
        for tid in row.get('transportability_ids', []):
            if tid not in known_transport_ids:
                errors.append(f'likelihood/update row {luid} references unknown transportability row: {tid}')
        for xid in row.get('extrapolation_fence_ids', []):
            if xid not in known_fence_ids:
                errors.append(f'likelihood/update row {luid} references unknown extrapolation-fence row: {xid}')

    for row in prior_rows:
        psid = row.get('prior_sensitivity_id', '')
        for did in row.get('validity_domain_ids', []):
            if did not in known_domain_ids:
                errors.append(f'prior-sensitivity row {psid} references unknown validity-domain row: {did}')
        for tid in row.get('transportability_ids', []):
            if tid not in known_transport_ids:
                errors.append(f'prior-sensitivity row {psid} references unknown transportability row: {tid}')
        for xid in row.get('extrapolation_fence_ids', []):
            if xid not in known_fence_ids:
                errors.append(f'prior-sensitivity row {psid} references unknown extrapolation-fence row: {xid}')

    for row in measurement_rows:
        mid = row.get('measurement_model_id', '')
        for did in row.get('validity_domain_ids', []):
            if did not in known_domain_ids:
                errors.append(f'measurement model {mid} references unknown validity-domain row: {did}')
        for tid in row.get('transportability_ids', []):
            if tid not in known_transport_ids:
                errors.append(f'measurement model {mid} references unknown transportability row: {tid}')
        for xid in row.get('extrapolation_fence_ids', []):
            if xid not in known_fence_ids:
                errors.append(f'measurement model {mid} references unknown extrapolation-fence row: {xid}')

    if f"- Validity-domain rows: `{len(domain_rows)}`" not in validity_transport_summary_text:
        errors.append('validity/transport generated summary domain count drifted; run make index')
    if f"- Transportability rows: `{len(transport_rows)}`" not in validity_transport_summary_text:
        errors.append('validity/transport generated summary transport count drifted; run make index')
    if f"- Extrapolation-fence rows: `{len(fence_rows)}`" not in validity_transport_summary_text:
        errors.append('validity/transport generated summary fence count drifted; run make index')
    if f"- Validity-domain rows: `{len(domain_rows)}`" not in route_summary_text:
        errors.append('route-state generated summary validity-domain count drifted; run make index')
    if f"- Transportability rows: `{len(transport_rows)}`" not in route_summary_text:
        errors.append('route-state generated summary transportability count drifted; run make index')
    if f"- Extrapolation-fence rows: `{len(fence_rows)}`" not in route_summary_text:
        errors.append('route-state generated summary extrapolation-fence count drifted; run make index')

    # Delta, forecast, decision, and severity rows should now bind to evidence units.
    for delta in empirical_delta_ledger.get('empirical_deltas', []):
        did = delta.get('delta_id', '')
        for uid in delta.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'empirical delta {did} references unknown evidence unit: {uid}')
    for row in forecast_rows:
        fid = row.get('forecast_id', '')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'discriminator forecast {fid} references unknown evidence unit: {uid}')
    for exp in decision_experiments:
        eid = exp.get('experiment_id', '')
        for uid in exp.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'decision experiment {eid} references unknown evidence unit: {uid}')
    for row in severity_rows:
        sid = row.get('severity_id', '')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'severity row {sid} references unknown evidence unit: {uid}')

    if f"- Evidence units: `{len(evidence_units)}`" not in evidence_credit_summary_text:
        errors.append('evidence-credit generated summary evidence-unit count drifted; run make index')
    if f"- Independence assumptions: `{len(independence_rows)}`" not in evidence_credit_summary_text:
        errors.append('evidence-credit generated summary independence count drifted; run make index')
    if f"- Credit-allocation rows: `{len(credit_rows)}`" not in evidence_credit_summary_text:
        errors.append('evidence-credit generated summary credit count drifted; run make index')
    if f"- Contrast classes: `{len(contrast_rows)}`" not in contrast_update_summary_text:
        errors.append('contrast/update generated summary contrast count drifted; run make index')
    if f"- Likelihood/update rows: `{len(update_rows)}`" not in contrast_update_summary_text:
        errors.append('contrast/update generated summary update count drifted; run make index')
    if f"- Prior-sensitivity rows: `{len(prior_rows)}`" not in contrast_update_summary_text:
        errors.append('contrast/update generated summary prior count drifted; run make index')
    if f"- Measurement-model rows: `{len(measurement_rows)}`" not in route_summary_text:
        errors.append('route-state generated summary measurement count drifted; run make index')
    if f"- Systematic-uncertainty rows: `{len(systematic_rows)}`" not in route_summary_text:
        errors.append('route-state generated summary systematic count drifted; run make index')
    if f"- Calibration-traceability rows: `{len(calibration_rows)}`" not in route_summary_text:
        errors.append('route-state generated summary calibration count drifted; run make index')

    # Causal-mechanism, intervention-protocol, and counterfactual-robustness checks added in rev0269.
    mechanism_rows = causal_mechanism_ledger.get('mechanism_rows', [])
    mechanism_ids = [item.get('mechanism_id', '') for item in mechanism_rows]
    if len(mechanism_ids) != len(set(mechanism_ids)):
        errors.append('CAUSAL-MECHANISM-LEDGER contains duplicate mechanism_id values')
    known_mechanism_ids = set(mechanism_ids)
    allowed_mechanism_classes = set(witness_vocab.get('causal_mechanism_class_labels', []))
    mechanism_required_keys = ['mechanism_id','route_ids','evidence_unit_ids','contrast_class_ids','measurement_model_ids','validity_domain_ids','mechanism_class','causal_question','proposed_structure','causal_claim_grain','manipulability_or_intervention_gap','confounding_or_common_cause_controls','invariance_or_mechanism_stability_test','maximum_authority_effect','defeater_ids','rollback_rule_ids','source_refs']
    for row in mechanism_rows:
        mid = row.get('mechanism_id', '')
        missing = [field for field in mechanism_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'causal-mechanism row {mid or "<missing>"} missing required fields: {missing}')
        if row.get('mechanism_class') not in allowed_mechanism_classes:
            errors.append(f'causal-mechanism row {mid} has unknown mechanism_class: {row.get("mechanism_class")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'causal-mechanism row {mid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'causal-mechanism row {mid} references unknown route_id: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'causal-mechanism row {mid} references unknown evidence unit: {uid}')
        for cid in row.get('contrast_class_ids', []):
            if cid not in known_contrast_ids:
                errors.append(f'causal-mechanism row {mid} references unknown contrast class: {cid}')
        for mmid in row.get('measurement_model_ids', []):
            if mmid not in known_measurement_model_ids:
                errors.append(f'causal-mechanism row {mid} references unknown measurement model: {mmid}')
        for did in row.get('validity_domain_ids', []):
            if did not in known_domain_ids:
                errors.append(f'causal-mechanism row {mid} references unknown validity-domain row: {did}')
        for dfid in row.get('defeater_ids', []):
            if dfid not in known_defeater_ids:
                errors.append(f'causal-mechanism row {mid} references unknown defeater: {dfid}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'causal-mechanism row {mid} references unknown rollback rule: {rbid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'causal-mechanism row {mid} references unknown REF id: {ref}')

    intervention_rows = intervention_protocol_ledger.get('intervention_rows', [])
    intervention_ids = [item.get('intervention_id', '') for item in intervention_rows]
    if len(intervention_ids) != len(set(intervention_ids)):
        errors.append('INTERVENTION-PROTOCOL-LEDGER contains duplicate intervention_id values')
    known_intervention_ids = set(intervention_ids)
    allowed_intervention_statuses = set(witness_vocab.get('intervention_status_labels', []))
    intervention_required_keys = ['intervention_id','route_ids','mechanism_ids','evidence_unit_ids','protocol_ids','domain_ids','intervention_status','intervention_or_perturbation','intervention_target','isolation_assumptions','manipulability_gap','public_artifact','stress_test','maximum_authority_effect','defeater_ids','rollback_rule_ids','source_refs']
    for row in intervention_rows:
        iid = row.get('intervention_id', '')
        missing = [field for field in intervention_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'intervention-protocol row {iid or "<missing>"} missing required fields: {missing}')
        if row.get('intervention_status') not in allowed_intervention_statuses:
            errors.append(f'intervention-protocol row {iid} has unknown intervention_status: {row.get("intervention_status")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'intervention-protocol row {iid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'intervention-protocol row {iid} references unknown route_id: {rid}')
        for mid in row.get('mechanism_ids', []):
            if mid not in known_mechanism_ids:
                errors.append(f'intervention-protocol row {iid} references unknown causal mechanism: {mid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'intervention-protocol row {iid} references unknown evidence unit: {uid}')
        for pid in row.get('protocol_ids', []):
            if pid not in known_protocol_ids:
                errors.append(f'intervention-protocol row {iid} references unknown acquisition protocol: {pid}')
        for did in row.get('domain_ids', []):
            if did not in known_domain_ids:
                errors.append(f'intervention-protocol row {iid} references unknown validity-domain row: {did}')
        for dfid in row.get('defeater_ids', []):
            if dfid not in known_defeater_ids:
                errors.append(f'intervention-protocol row {iid} references unknown defeater: {dfid}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'intervention-protocol row {iid} references unknown rollback rule: {rbid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'intervention-protocol row {iid} references unknown REF id: {ref}')

    counterfactual_rows = counterfactual_robustness_ledger.get('counterfactual_rows', [])
    counterfactual_ids = [item.get('counterfactual_id', '') for item in counterfactual_rows]
    if len(counterfactual_ids) != len(set(counterfactual_ids)):
        errors.append('COUNTERFACTUAL-ROBUSTNESS-LEDGER contains duplicate counterfactual_id values')
    known_counterfactual_ids = set(counterfactual_ids)
    allowed_counterfactual_classes = set(witness_vocab.get('counterfactual_class_labels', []))
    allowed_counterfactual_statuses = set(witness_vocab.get('counterfactual_robustness_status_labels', []))
    counterfactual_required_keys = ['counterfactual_id','route_ids','mechanism_ids','intervention_ids','evidence_unit_ids','contrast_class_ids','transportability_ids','counterfactual_class','counterfactual_query','alternative_worlds_or_model_interventions','invariance_requirement','failure_modes','robustness_status','maximum_authority_effect','rollback_rule_ids','source_refs']
    for row in counterfactual_rows:
        cfid = row.get('counterfactual_id', '')
        missing = [field for field in counterfactual_required_keys if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'counterfactual-robustness row {cfid or "<missing>"} missing required fields: {missing}')
        if row.get('counterfactual_class') not in allowed_counterfactual_classes:
            errors.append(f'counterfactual-robustness row {cfid} has unknown counterfactual_class: {row.get("counterfactual_class")}')
        if row.get('robustness_status') not in allowed_counterfactual_statuses:
            errors.append(f'counterfactual-robustness row {cfid} has unknown robustness_status: {row.get("robustness_status")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'counterfactual-robustness row {cfid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'counterfactual-robustness row {cfid} references unknown route_id: {rid}')
        for mid in row.get('mechanism_ids', []):
            if mid not in known_mechanism_ids:
                errors.append(f'counterfactual-robustness row {cfid} references unknown causal mechanism: {mid}')
        for iid in row.get('intervention_ids', []):
            if iid not in known_intervention_ids:
                errors.append(f'counterfactual-robustness row {cfid} references unknown intervention protocol: {iid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'counterfactual-robustness row {cfid} references unknown evidence unit: {uid}')
        for cid in row.get('contrast_class_ids', []):
            if cid not in known_contrast_ids:
                errors.append(f'counterfactual-robustness row {cfid} references unknown contrast class: {cid}')
        for tid in row.get('transportability_ids', []):
            if tid not in known_transport_ids:
                errors.append(f'counterfactual-robustness row {cfid} references unknown transportability row: {tid}')
        for rbid in row.get('rollback_rule_ids', []):
            if rbid not in known_rollback_ids:
                errors.append(f'counterfactual-robustness row {cfid} references unknown rollback rule: {rbid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'counterfactual-robustness row {cfid} references unknown REF id: {ref}')

    mechanism_by_id = {row.get('mechanism_id',''): row for row in mechanism_rows}
    intervention_by_id = {row.get('intervention_id',''): row for row in intervention_rows}
    counterfactual_by_id = {row.get('counterfactual_id',''): row for row in counterfactual_rows}
    for row in route_rows:
        rid = row.get('route_id', '')
        for mid in row.get('causal_mechanism_ids', []):
            if mid not in known_mechanism_ids:
                errors.append(f'route row {rid} references unknown causal mechanism: {mid}')
            elif rid not in mechanism_by_id[mid].get('route_ids', []):
                errors.append(f'route row {rid} names causal mechanism {mid}, but mechanism row does not name route')
        for iid in row.get('intervention_protocol_ids', []):
            if iid not in known_intervention_ids:
                errors.append(f'route row {rid} references unknown intervention protocol: {iid}')
            elif rid not in intervention_by_id[iid].get('route_ids', []):
                errors.append(f'route row {rid} names intervention protocol {iid}, but intervention row does not name route')
        for cfid in row.get('counterfactual_robustness_ids', []):
            if cfid not in known_counterfactual_ids:
                errors.append(f'route row {rid} references unknown counterfactual robustness row: {cfid}')
            elif rid not in counterfactual_by_id[cfid].get('route_ids', []):
                errors.append(f'route row {rid} names counterfactual row {cfid}, but counterfactual row does not name route')

    for unit in evidence_units:
        uid = unit.get('evidence_unit_id', '')
        for mid in unit.get('causal_mechanism_ids', []):
            if mid not in known_mechanism_ids:
                errors.append(f'evidence unit {uid} references unknown causal mechanism: {mid}')
        for iid in unit.get('intervention_protocol_ids', []):
            if iid not in known_intervention_ids:
                errors.append(f'evidence unit {uid} references unknown intervention protocol: {iid}')
        for cfid in unit.get('counterfactual_robustness_ids', []):
            if cfid not in known_counterfactual_ids:
                errors.append(f'evidence unit {uid} references unknown counterfactual robustness row: {cfid}')

    for collection, label, idfield in [
        (credit_rows, 'credit allocation', 'credit_id'),
        (update_rows, 'likelihood/update row', 'likelihood_update_id'),
        (prior_rows, 'prior-sensitivity row', 'prior_sensitivity_id'),
        (measurement_rows, 'measurement model', 'measurement_model_id'),
        (systematic_rows, 'systematic uncertainty row', 'systematic_id'),
        (calibration_rows, 'calibration/traceability row', 'calibration_id'),
        (domain_rows, 'validity-domain row', 'domain_id'),
        (transport_rows, 'transportability row', 'transport_id'),
        (fence_rows, 'extrapolation-fence row', 'fence_id'),
    ]:
        for row in collection:
            label_id = row.get(idfield, '')
            for mid in row.get('causal_mechanism_ids', []):
                if mid not in known_mechanism_ids:
                    errors.append(f'{label} {label_id} references unknown causal mechanism: {mid}')
            for iid in row.get('intervention_protocol_ids', []):
                if iid not in known_intervention_ids:
                    errors.append(f'{label} {label_id} references unknown intervention protocol: {iid}')
            for cfid in row.get('counterfactual_robustness_ids', []):
                if cfid not in known_counterfactual_ids:
                    errors.append(f'{label} {label_id} references unknown counterfactual robustness row: {cfid}')

    for binding in binding_rows:
        bid = binding.get('binding_id', '')
        for mid in binding.get('causal_mechanism_ids', []):
            if mid not in known_mechanism_ids:
                errors.append(f'claim-route binding {bid} references unknown causal mechanism: {mid}')
        for iid in binding.get('intervention_protocol_ids', []):
            if iid not in known_intervention_ids:
                errors.append(f'claim-route binding {bid} references unknown intervention protocol: {iid}')
        for cfid in binding.get('counterfactual_robustness_ids', []):
            if cfid not in known_counterfactual_ids:
                errors.append(f'claim-route binding {bid} references unknown counterfactual robustness row: {cfid}')

    if f"- Causal-mechanism rows: `{len(mechanism_rows)}`" not in causal_mechanism_summary_text:
        errors.append('causal-mechanism generated summary mechanism count drifted; run make index')
    if f"- Intervention-protocol rows: `{len(intervention_rows)}`" not in causal_mechanism_summary_text:
        errors.append('causal-mechanism generated summary intervention count drifted; run make index')
    if f"- Counterfactual-robustness rows: `{len(counterfactual_rows)}`" not in causal_mechanism_summary_text:
        errors.append('causal-mechanism generated summary counterfactual count drifted; run make index')


    # Selection-function, multiplicity-control, and reporting-bias checks added in rev0270.
    selection_rows = selection_function_ledger.get('selection_rows', [])
    multiplicity_rows = multiplicity_control_ledger.get('multiplicity_rows', [])
    reporting_bias_rows = reporting_bias_ledger.get('bias_rows', [])
    selection_ids = [item.get('selection_function_id', '') for item in selection_rows]
    multiplicity_ids = [item.get('multiplicity_control_id', '') for item in multiplicity_rows]
    reporting_bias_ids = [item.get('reporting_bias_id', '') for item in reporting_bias_rows]
    if len(selection_ids) != len(set(selection_ids)):
        errors.append('SELECTION-FUNCTION-LEDGER contains duplicate selection_function_id values')
    if len(multiplicity_ids) != len(set(multiplicity_ids)):
        errors.append('MULTIPLICITY-CONTROL-LEDGER contains duplicate multiplicity_control_id values')
    if len(reporting_bias_ids) != len(set(reporting_bias_ids)):
        errors.append('REPORTING-BIAS-LEDGER contains duplicate reporting_bias_id values')
    known_selection_ids = set(selection_ids)
    known_multiplicity_ids = set(multiplicity_ids)
    known_reporting_bias_ids = set(reporting_bias_ids)
    allowed_selection_classes = set(witness_vocab.get('selection_function_class_labels', []))
    allowed_multiplicity_classes = set(witness_vocab.get('multiplicity_control_class_labels', []))
    allowed_reporting_bias_classes = set(witness_vocab.get('reporting_bias_class_labels', []))
    selection_required = ['selection_function_id','route_ids','evidence_unit_ids','contrast_class_ids','carrier_ids','protocol_ids','selection_class','sampling_or_search_frame','inclusion_rule','exclusion_or_missingness_rule','analyst_degrees_of_freedom','preregistration_or_freeze_status','selection_diagnostics','maximum_authority_effect','rollback_rule_ids','source_refs']
    multiplicity_required = ['multiplicity_control_id','route_ids','evidence_unit_ids','contrast_class_ids','likelihood_update_ids','prior_sensitivity_ids','selection_function_ids','control_class','search_space','effective_number_of_trials','correction_or_adjustment_rule','look_elsewhere_or_forking_paths_risk','discovery_language_allowed','maximum_authority_effect','rollback_rule_ids','source_refs']
    reporting_required = ['reporting_bias_id','route_ids','evidence_unit_ids','carrier_ids','protocol_ids','selection_function_ids','multiplicity_control_ids','bias_class','visibility_risk','null_or_failed_attempt_visibility','missing_record_risk','mitigation','authority_effect_if_unmitigated','maximum_authority_effect','rollback_rule_ids','source_refs']
    for row in selection_rows:
        sid = row.get('selection_function_id','')
        missing = [field for field in selection_required if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'selection-function row {sid or "<missing>"} missing required fields: {missing}')
        if row.get('selection_class') not in allowed_selection_classes:
            errors.append(f'selection-function row {sid} has unknown selection_class: {row.get("selection_class")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'selection-function row {sid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'selection-function row {sid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'selection-function row {sid} references unknown evidence unit: {uid}')
        for cid in row.get('contrast_class_ids', []):
            if cid not in known_contrast_ids:
                errors.append(f'selection-function row {sid} references unknown contrast class: {cid}')
        for cid in row.get('carrier_ids', []):
            if cid not in known_carrier_ids:
                errors.append(f'selection-function row {sid} references unknown carrier: {cid}')
        for pid in row.get('protocol_ids', []):
            if pid not in known_protocol_ids:
                errors.append(f'selection-function row {sid} references unknown protocol: {pid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids:
                errors.append(f'selection-function row {sid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'selection-function row {sid} references unknown REF id: {ref}')
    for row in multiplicity_rows:
        mid = row.get('multiplicity_control_id','')
        missing = [field for field in multiplicity_required if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'multiplicity-control row {mid or "<missing>"} missing required fields: {missing}')
        if row.get('control_class') not in allowed_multiplicity_classes:
            errors.append(f'multiplicity-control row {mid} has unknown control_class: {row.get("control_class")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'multiplicity-control row {mid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'multiplicity-control row {mid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'multiplicity-control row {mid} references unknown evidence unit: {uid}')
        for cid in row.get('contrast_class_ids', []):
            if cid not in known_contrast_ids:
                errors.append(f'multiplicity-control row {mid} references unknown contrast class: {cid}')
        for luid in row.get('likelihood_update_ids', []):
            if luid not in known_update_ids:
                errors.append(f'multiplicity-control row {mid} references unknown likelihood/update row: {luid}')
        for psid in row.get('prior_sensitivity_ids', []):
            if psid not in known_prior_ids:
                errors.append(f'multiplicity-control row {mid} references unknown prior-sensitivity row: {psid}')
        for sid in row.get('selection_function_ids', []):
            if sid not in known_selection_ids:
                errors.append(f'multiplicity-control row {mid} references unknown selection-function row: {sid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids:
                errors.append(f'multiplicity-control row {mid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'multiplicity-control row {mid} references unknown REF id: {ref}')
    for row in reporting_bias_rows:
        bid = row.get('reporting_bias_id','')
        missing = [field for field in reporting_required if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'reporting-bias row {bid or "<missing>"} missing required fields: {missing}')
        if row.get('bias_class') not in allowed_reporting_bias_classes:
            errors.append(f'reporting-bias row {bid} has unknown bias_class: {row.get("bias_class")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'reporting-bias row {bid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids:
                errors.append(f'reporting-bias row {bid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids:
                errors.append(f'reporting-bias row {bid} references unknown evidence unit: {uid}')
        for cid in row.get('carrier_ids', []):
            if cid not in known_carrier_ids:
                errors.append(f'reporting-bias row {bid} references unknown carrier: {cid}')
        for pid in row.get('protocol_ids', []):
            if pid not in known_protocol_ids:
                errors.append(f'reporting-bias row {bid} references unknown protocol: {pid}')
        for sid in row.get('selection_function_ids', []):
            if sid not in known_selection_ids:
                errors.append(f'reporting-bias row {bid} references unknown selection-function row: {sid}')
        for mid in row.get('multiplicity_control_ids', []):
            if mid not in known_multiplicity_ids:
                errors.append(f'reporting-bias row {bid} references unknown multiplicity-control row: {mid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids:
                errors.append(f'reporting-bias row {bid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib:
                errors.append(f'reporting-bias row {bid} references unknown REF id: {ref}')

    # Model-capacity, complexity-penalty, and predictive-generalization checks added in rev0271.
    capacity_rows = model_capacity_ledger.get('capacity_rows', [])
    complexity_rows = complexity_penalty_ledger.get('complexity_rows', [])
    generalization_rows = predictive_generalization_ledger.get('generalization_rows', [])
    capacity_ids = [item.get('model_capacity_id', '') for item in capacity_rows]
    complexity_ids = [item.get('complexity_penalty_id', '') for item in complexity_rows]
    generalization_ids = [item.get('generalization_id', '') for item in generalization_rows]
    if len(capacity_ids) != len(set(capacity_ids)):
        errors.append('MODEL-CAPACITY-LEDGER contains duplicate model_capacity_id values')
    if len(complexity_ids) != len(set(complexity_ids)):
        errors.append('COMPLEXITY-PENALTY-LEDGER contains duplicate complexity_penalty_id values')
    if len(generalization_ids) != len(set(generalization_ids)):
        errors.append('PREDICTIVE-GENERALIZATION-LEDGER contains duplicate generalization_id values')
    known_capacity_ids = set(capacity_ids)
    known_complexity_ids = set(complexity_ids)
    known_generalization_ids = set(generalization_ids)
    allowed_capacity_classes = set(witness_vocab.get('model_capacity_class_labels', []))
    allowed_complexity_classes = set(witness_vocab.get('complexity_penalty_class_labels', []))
    allowed_generalization_classes = set(witness_vocab.get('generalization_validation_class_labels', []))
    capacity_required = ['model_capacity_id','route_ids','evidence_unit_ids','contrast_class_ids','selection_function_ids','multiplicity_control_ids','capacity_class','adjustable_structure','effective_degrees_of_freedom','flexibility_source','capacity_diagnostic','maximum_authority_effect','rollback_rule_ids','source_refs']
    complexity_required = ['complexity_penalty_id','route_ids','evidence_unit_ids','likelihood_update_ids','prior_sensitivity_ids','model_capacity_ids','penalty_class','fit_term','complexity_term','penalty_or_regularizer','no_free_fit_rule','maximum_authority_effect','rollback_rule_ids','source_refs']
    generalization_required = ['generalization_id','route_ids','evidence_unit_ids','carrier_ids','protocol_ids','model_capacity_ids','complexity_penalty_ids','validation_class','train_or_construction_record','test_or_holdout_record','out_of_sample_or_out_of_domain_test','generalization_gap_risk','maximum_authority_effect','rollback_rule_ids','source_refs']
    for row in capacity_rows:
        cid = row.get('model_capacity_id','')
        missing = [field for field in capacity_required if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'model-capacity row {cid or "<missing>"} missing required fields: {missing}')
        if row.get('capacity_class') not in allowed_capacity_classes:
            errors.append(f'model-capacity row {cid} has unknown capacity_class: {row.get("capacity_class")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'model-capacity row {cid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'model-capacity row {cid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'model-capacity row {cid} references unknown evidence unit: {uid}')
        for ccid in row.get('contrast_class_ids', []):
            if ccid not in known_contrast_ids: errors.append(f'model-capacity row {cid} references unknown contrast class: {ccid}')
        for sid in row.get('selection_function_ids', []):
            if sid not in known_selection_ids: errors.append(f'model-capacity row {cid} references unknown selection-function row: {sid}')
        for mid in row.get('multiplicity_control_ids', []):
            if mid not in known_multiplicity_ids: errors.append(f'model-capacity row {cid} references unknown multiplicity-control row: {mid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'model-capacity row {cid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'model-capacity row {cid} references unknown REF id: {ref}')
    for row in complexity_rows:
        cid = row.get('complexity_penalty_id','')
        missing = [field for field in complexity_required if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'complexity-penalty row {cid or "<missing>"} missing required fields: {missing}')
        if row.get('penalty_class') not in allowed_complexity_classes:
            errors.append(f'complexity-penalty row {cid} has unknown penalty_class: {row.get("penalty_class")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'complexity-penalty row {cid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'complexity-penalty row {cid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'complexity-penalty row {cid} references unknown evidence unit: {uid}')
        for luid in row.get('likelihood_update_ids', []):
            if luid not in known_update_ids: errors.append(f'complexity-penalty row {cid} references unknown likelihood/update row: {luid}')
        for psid in row.get('prior_sensitivity_ids', []):
            if psid not in known_prior_ids: errors.append(f'complexity-penalty row {cid} references unknown prior-sensitivity row: {psid}')
        for capid in row.get('model_capacity_ids', []):
            if capid not in known_capacity_ids: errors.append(f'complexity-penalty row {cid} references unknown model-capacity row: {capid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'complexity-penalty row {cid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'complexity-penalty row {cid} references unknown REF id: {ref}')
    for row in generalization_rows:
        gid = row.get('generalization_id','')
        missing = [field for field in generalization_required if field not in row or row.get(field) in ('', [], None)]
        if missing:
            errors.append(f'generalization-validation row {gid or "<missing>"} missing required fields: {missing}')
        if row.get('validation_class') not in allowed_generalization_classes:
            errors.append(f'generalization-validation row {gid} has unknown validation_class: {row.get("validation_class")}')
        if row.get('maximum_authority_effect') not in allowed_states:
            errors.append(f'generalization-validation row {gid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'generalization-validation row {gid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'generalization-validation row {gid} references unknown evidence unit: {uid}')
        for cid in row.get('carrier_ids', []):
            if cid not in known_carrier_ids: errors.append(f'generalization-validation row {gid} references unknown carrier: {cid}')
        for pid in row.get('protocol_ids', []):
            if pid not in known_protocol_ids: errors.append(f'generalization-validation row {gid} references unknown protocol: {pid}')
        for capid in row.get('model_capacity_ids', []):
            if capid not in known_capacity_ids: errors.append(f'generalization-validation row {gid} references unknown model-capacity row: {capid}')
        for cpxid in row.get('complexity_penalty_ids', []):
            if cpxid not in known_complexity_ids: errors.append(f'generalization-validation row {gid} references unknown complexity-penalty row: {cpxid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'generalization-validation row {gid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'generalization-validation row {gid} references unknown REF id: {ref}')

    for row in route_rows:
        rid = row.get('route_id','')
        for sid in row.get('selection_function_ids', []):
            if sid not in known_selection_ids:
                errors.append(f'route row {rid} references unknown selection-function row: {sid}')
        for mid in row.get('multiplicity_control_ids', []):
            if mid not in known_multiplicity_ids:
                errors.append(f'route row {rid} references unknown multiplicity-control row: {mid}')
        for bid in row.get('reporting_bias_ids', []):
            if bid not in known_reporting_bias_ids:
                errors.append(f'route row {rid} references unknown reporting-bias row: {bid}')
        for capid in row.get('model_capacity_ids', []):
            if capid not in known_capacity_ids:
                errors.append(f'route row {rid} references unknown model-capacity row: {capid}')
        for cpxid in row.get('complexity_penalty_ids', []):
            if cpxid not in known_complexity_ids:
                errors.append(f'route row {rid} references unknown complexity-penalty row: {cpxid}')
        for genid in row.get('generalization_validation_ids', []):
            if genid not in known_generalization_ids:
                errors.append(f'route row {rid} references unknown generalization-validation row: {genid}')

    for collection, label, idfield in [
        (evidence_units, 'evidence unit', 'evidence_unit_id'),
        (credit_rows, 'credit allocation', 'credit_id'),
        (update_rows, 'likelihood/update row', 'likelihood_update_id'),
        (prior_rows, 'prior-sensitivity row', 'prior_sensitivity_id'),
        (measurement_rows, 'measurement model', 'measurement_model_id'),
        (systematic_rows, 'systematic uncertainty row', 'systematic_id'),
        (calibration_rows, 'calibration/traceability row', 'calibration_id'),
        (domain_rows, 'validity-domain row', 'domain_id'),
        (transport_rows, 'transportability row', 'transport_id'),
        (fence_rows, 'extrapolation-fence row', 'fence_id'),
        (mechanism_rows, 'causal mechanism', 'mechanism_id'),
        (intervention_rows, 'intervention protocol', 'intervention_id'),
        (counterfactual_rows, 'counterfactual robustness row', 'counterfactual_id'),
        (severity_rows, 'severity row', 'severity_id'),
        (decision_experiments, 'decision experiment', 'experiment_id'),
        (forecast_rows, 'forecast row', 'forecast_id'),
        (empirical_delta_ledger.get('empirical_deltas', []), 'empirical delta', 'delta_id'),
    ]:
        for item in collection:
            item_id = item.get(idfield, '')
            for sid in item.get('selection_function_ids', []):
                if sid not in known_selection_ids:
                    errors.append(f'{label} {item_id} references unknown selection-function row: {sid}')
            for mid in item.get('multiplicity_control_ids', []):
                if mid not in known_multiplicity_ids:
                    errors.append(f'{label} {item_id} references unknown multiplicity-control row: {mid}')
            for bid in item.get('reporting_bias_ids', []):
                if bid not in known_reporting_bias_ids:
                    errors.append(f'{label} {item_id} references unknown reporting-bias row: {bid}')
            for capid in item.get('model_capacity_ids', []):
                if capid not in known_capacity_ids:
                    errors.append(f'{label} {item_id} references unknown model-capacity row: {capid}')
            for cpxid in item.get('complexity_penalty_ids', []):
                if cpxid not in known_complexity_ids:
                    errors.append(f'{label} {item_id} references unknown complexity-penalty row: {cpxid}')
            for genid in item.get('generalization_validation_ids', []):
                if genid not in known_generalization_ids:
                    errors.append(f'{label} {item_id} references unknown generalization-validation row: {genid}')

    for binding in binding_rows:
        bid = binding.get('binding_id','')
        for sid in binding.get('selection_function_ids', []):
            if sid not in known_selection_ids:
                errors.append(f'claim-route binding {bid} references unknown selection-function row: {sid}')
        for mid in binding.get('multiplicity_control_ids', []):
            if mid not in known_multiplicity_ids:
                errors.append(f'claim-route binding {bid} references unknown multiplicity-control row: {mid}')
        for rbid in binding.get('reporting_bias_ids', []):
            if rbid not in known_reporting_bias_ids:
                errors.append(f'claim-route binding {bid} references unknown reporting-bias row: {rbid}')
        for capid in binding.get('model_capacity_ids', []):
            if capid not in known_capacity_ids:
                errors.append(f'claim-route binding {bid} references unknown model-capacity row: {capid}')
        for cpxid in binding.get('complexity_penalty_ids', []):
            if cpxid not in known_complexity_ids:
                errors.append(f'claim-route binding {bid} references unknown complexity-penalty row: {cpxid}')
        for genid in binding.get('generalization_validation_ids', []):
            if genid not in known_generalization_ids:
                errors.append(f'claim-route binding {bid} references unknown generalization-validation row: {genid}')

    if f"- Selection-function rows: `{len(selection_rows)}`" not in selection_bias_summary_text:
        errors.append('selection-bias generated summary selection count drifted; run make index')
    if f"- Multiplicity-control rows: `{len(multiplicity_rows)}`" not in selection_bias_summary_text:
        errors.append('selection-bias generated summary multiplicity count drifted; run make index')
    if f"- Reporting-bias rows: `{len(reporting_bias_rows)}`" not in selection_bias_summary_text:
        errors.append('selection-bias generated summary reporting-bias count drifted; run make index')
    if f"- Model-capacity rows: `{len(capacity_rows)}`" not in model_capacity_summary_text:
        errors.append('model-capacity generated summary capacity count drifted; run make index')
    if f"- Complexity-penalty rows: `{len(complexity_rows)}`" not in model_capacity_summary_text:
        errors.append('model-capacity generated summary complexity count drifted; run make index')
    if f"- Predictive-generalization rows: `{len(generalization_rows)}`" not in model_capacity_summary_text:
        errors.append('model-capacity generated summary generalization count drifted; run make index')

    # Semantic binding / ontology commitment / language permission checks added in rev0272.
    semantic_rows = semantic_term_ledger.get('semantic_rows', [])
    commitment_rows = ontology_commitment_ledger.get('commitment_rows', [])
    permission_rows = claim_language_permission_ledger.get('permission_rows', [])
    semantic_ids = [item.get('semantic_term_id', '') for item in semantic_rows]
    commitment_ids = [item.get('ontology_commitment_id', '') for item in commitment_rows]
    permission_ids = [item.get('language_permission_id', '') for item in permission_rows]
    if len(semantic_ids) != len(set(semantic_ids)):
        errors.append('SEMANTIC-TERM-LEDGER contains duplicate semantic_term_id values')
    if len(commitment_ids) != len(set(commitment_ids)):
        errors.append('ONTOLOGY-COMMITMENT-LEDGER contains duplicate ontology_commitment_id values')
    if len(permission_ids) != len(set(permission_ids)):
        errors.append('CLAIM-LANGUAGE-PERMISSION-LEDGER contains duplicate language_permission_id values')
    known_semantic_ids = set(semantic_ids)
    known_commitment_ids = set(commitment_ids)
    known_permission_ids = set(permission_ids)
    allowed_semantic_classes = set(witness_vocab.get('semantic_term_class_labels', []))
    allowed_commitment_classes = set(witness_vocab.get('ontology_commitment_class_labels', []))
    allowed_permission_classes = set(witness_vocab.get('claim_language_permission_class_labels', []))
    semantic_required = ['semantic_term_id','route_ids','evidence_unit_ids','term_class','controlled_terms','preferred_meaning','prohibited_equivocations','observational_bridge_terms','theory_internal_terms','semantic_stability_test','maximum_authority_effect','rollback_rule_ids','source_refs']
    commitment_required = ['ontology_commitment_id','route_ids','semantic_term_ids','commitment_class','ontic_target','structural_target','operational_target','noncommitments','equivalence_or_identity_rule','realist_status_ceiling','maximum_authority_effect','rollback_rule_ids','source_refs']
    permission_required = ['language_permission_id','route_ids','semantic_term_ids','ontology_commitment_ids','permission_class','allowed_language','forbidden_language','required_context','escalation_condition','maximum_authority_effect','rollback_rule_ids','source_refs']
    for row in semantic_rows:
        sid = row.get('semantic_term_id','')
        missing = [field for field in semantic_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'semantic-term row {sid or "<missing>"} missing required fields: {missing}')
        if row.get('term_class') not in allowed_semantic_classes: errors.append(f'semantic-term row {sid} has unknown term_class: {row.get("term_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'semantic-term row {sid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'semantic-term row {sid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'semantic-term row {sid} references unknown evidence unit: {uid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'semantic-term row {sid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'semantic-term row {sid} references unknown REF id: {ref}')
    for row in commitment_rows:
        oid = row.get('ontology_commitment_id','')
        missing = [field for field in commitment_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'ontology-commitment row {oid or "<missing>"} missing required fields: {missing}')
        if row.get('commitment_class') not in allowed_commitment_classes: errors.append(f'ontology-commitment row {oid} has unknown commitment_class: {row.get("commitment_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'ontology-commitment row {oid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        if row.get('realist_status_ceiling') not in allowed_states: errors.append(f'ontology-commitment row {oid} has unknown realist_status_ceiling: {row.get("realist_status_ceiling")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'ontology-commitment row {oid} references unknown route: {rid}')
        for sid in row.get('semantic_term_ids', []):
            if sid not in known_semantic_ids: errors.append(f'ontology-commitment row {oid} references unknown semantic term: {sid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'ontology-commitment row {oid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'ontology-commitment row {oid} references unknown REF id: {ref}')
    for row in permission_rows:
        pid = row.get('language_permission_id','')
        missing = [field for field in permission_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'claim-language-permission row {pid or "<missing>"} missing required fields: {missing}')
        if row.get('permission_class') not in allowed_permission_classes: errors.append(f'claim-language-permission row {pid} has unknown permission_class: {row.get("permission_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'claim-language-permission row {pid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'claim-language-permission row {pid} references unknown route: {rid}')
        for sid in row.get('semantic_term_ids', []):
            if sid not in known_semantic_ids: errors.append(f'claim-language-permission row {pid} references unknown semantic term: {sid}')
        for oid in row.get('ontology_commitment_ids', []):
            if oid not in known_commitment_ids: errors.append(f'claim-language-permission row {pid} references unknown ontology commitment: {oid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'claim-language-permission row {pid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'claim-language-permission row {pid} references unknown REF id: {ref}')

    for row in route_rows:
        rid = row.get('route_id','')
        for sid in row.get('semantic_term_ids', []):
            if sid not in known_semantic_ids: errors.append(f'route row {rid} references unknown semantic-term row: {sid}')
        for oid in row.get('ontology_commitment_ids', []):
            if oid not in known_commitment_ids: errors.append(f'route row {rid} references unknown ontology-commitment row: {oid}')
        for pid in row.get('claim_language_permission_ids', []):
            if pid not in known_permission_ids: errors.append(f'route row {rid} references unknown claim-language-permission row: {pid}')

    for collection, label, idfield in [
        (evidence_units, 'evidence unit', 'evidence_unit_id'),
        (credit_rows, 'credit allocation', 'credit_id'),
        (update_rows, 'likelihood/update row', 'likelihood_update_id'),
        (prior_rows, 'prior-sensitivity row', 'prior_sensitivity_id'),
        (measurement_rows, 'measurement model', 'measurement_model_id'),
        (systematic_rows, 'systematic uncertainty row', 'systematic_id'),
        (calibration_rows, 'calibration/traceability row', 'calibration_id'),
        (domain_rows, 'validity-domain row', 'domain_id'),
        (transport_rows, 'transportability row', 'transport_id'),
        (fence_rows, 'extrapolation-fence row', 'fence_id'),
        (mechanism_rows, 'causal mechanism', 'mechanism_id'),
        (intervention_rows, 'intervention protocol', 'intervention_id'),
        (counterfactual_rows, 'counterfactual robustness row', 'counterfactual_id'),
        (severity_rows, 'severity row', 'severity_id'),
        (decision_experiments, 'decision experiment', 'experiment_id'),
        (forecast_rows, 'forecast row', 'forecast_id'),
        (empirical_delta_ledger.get('empirical_deltas', []), 'empirical delta', 'delta_id'),
        (capacity_rows, 'model-capacity row', 'model_capacity_id'),
        (complexity_rows, 'complexity-penalty row', 'complexity_penalty_id'),
        (generalization_rows, 'generalization-validation row', 'generalization_id'),
    ]:
        for item in collection:
            item_id = item.get(idfield, '')
            for sid in item.get('semantic_term_ids', []):
                if sid not in known_semantic_ids: errors.append(f'{label} {item_id} references unknown semantic-term row: {sid}')
            for oid in item.get('ontology_commitment_ids', []):
                if oid not in known_commitment_ids: errors.append(f'{label} {item_id} references unknown ontology-commitment row: {oid}')
            for pid in item.get('claim_language_permission_ids', []):
                if pid not in known_permission_ids: errors.append(f'{label} {item_id} references unknown claim-language-permission row: {pid}')

    for binding in binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['SEMANTIC-TERM-LEDGER.json','ONTOLOGY-COMMITMENT-LEDGER.json','CLAIM-LANGUAGE-PERMISSION-LEDGER.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing semantic controlling ledger: {rel}')
        for sid in binding.get('semantic_term_ids', []):
            if sid not in known_semantic_ids: errors.append(f'claim-route binding {bid} references unknown semantic-term row: {sid}')
        for oid in binding.get('ontology_commitment_ids', []):
            if oid not in known_commitment_ids: errors.append(f'claim-route binding {bid} references unknown ontology-commitment row: {oid}')
        for pid in binding.get('claim_language_permission_ids', []):
            if pid not in known_permission_ids: errors.append(f'claim-route binding {bid} references unknown claim-language-permission row: {pid}')

    if f"- Semantic-term rows: `{len(semantic_rows)}`" not in semantic_binding_summary_text:
        errors.append('semantic-binding generated summary semantic-term count drifted; run make index')
    if f"- Ontology-commitment rows: `{len(commitment_rows)}`" not in semantic_binding_summary_text:
        errors.append('semantic-binding generated summary ontology-commitment count drifted; run make index')
    if f"- Claim-language-permission rows: `{len(permission_rows)}`" not in semantic_binding_summary_text:
        errors.append('semantic-binding generated summary permission count drifted; run make index')


    # Social authority / review-replication / consensus-elicitation checks added in rev0273.
    social_rows = social_authority_ledger.get('social_rows', [])
    review_rows = review_replication_ledger.get('review_rows', [])
    consensus_rows = consensus_elicitation_ledger.get('consensus_rows', [])
    social_ids = [item.get('social_authority_id', '') for item in social_rows]
    review_ids = [item.get('review_replication_id', '') for item in review_rows]
    consensus_ids = [item.get('consensus_elicitation_id', '') for item in consensus_rows]
    if len(social_ids) != len(set(social_ids)):
        errors.append('SOCIAL-AUTHORITY-LEDGER contains duplicate social_authority_id values')
    if len(review_ids) != len(set(review_ids)):
        errors.append('REVIEW-REPLICATION-LEDGER contains duplicate review_replication_id values')
    if len(consensus_ids) != len(set(consensus_ids)):
        errors.append('CONSENSUS-ELICITATION-LEDGER contains duplicate consensus_elicitation_id values')
    known_social_ids = set(social_ids)
    known_review_ids = set(review_ids)
    known_consensus_ids = set(consensus_ids)
    allowed_social_classes = set(witness_vocab.get('social_authority_class_labels', []))
    allowed_review_classes = set(witness_vocab.get('review_replication_class_labels', []))
    allowed_consensus_classes = set(witness_vocab.get('consensus_elicitation_class_labels', []))
    social_required = ['social_authority_id','route_ids','evidence_unit_ids','social_authority_class','authority_signal','authorized_use','forbidden_use','independence_requirements','conflict_or_deference_risk','maximum_authority_effect','rollback_rule_ids','source_refs']
    review_required = ['review_replication_id','route_ids','evidence_unit_ids','review_replication_class','review_object','review_stage','replication_target','failure_modes','maximum_authority_effect','rollback_rule_ids','source_refs']
    consensus_required = ['consensus_elicitation_id','route_ids','evidence_unit_ids','consensus_class','elicitation_object','panel_or_community_denominator','disagreement_visibility_rule','aggregation_rule','maximum_authority_effect','rollback_rule_ids','source_refs']
    for row in social_rows:
        sid = row.get('social_authority_id','')
        missing = [field for field in social_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'social-authority row {sid or "<missing>"} missing required fields: {missing}')
        if row.get('social_authority_class') not in allowed_social_classes: errors.append(f'social-authority row {sid} has unknown social_authority_class: {row.get("social_authority_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'social-authority row {sid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'social-authority row {sid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'social-authority row {sid} references unknown evidence unit: {uid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'social-authority row {sid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'social-authority row {sid} references unknown REF id: {ref}')
    for row in review_rows:
        rid2 = row.get('review_replication_id','')
        missing = [field for field in review_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'review-replication row {rid2 or "<missing>"} missing required fields: {missing}')
        if row.get('review_replication_class') not in allowed_review_classes: errors.append(f'review-replication row {rid2} has unknown review_replication_class: {row.get("review_replication_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'review-replication row {rid2} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'review-replication row {rid2} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'review-replication row {rid2} references unknown evidence unit: {uid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'review-replication row {rid2} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'review-replication row {rid2} references unknown REF id: {ref}')
    for row in consensus_rows:
        cid2 = row.get('consensus_elicitation_id','')
        missing = [field for field in consensus_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'consensus-elicitation row {cid2 or "<missing>"} missing required fields: {missing}')
        if row.get('consensus_class') not in allowed_consensus_classes: errors.append(f'consensus-elicitation row {cid2} has unknown consensus_class: {row.get("consensus_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'consensus-elicitation row {cid2} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'consensus-elicitation row {cid2} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'consensus-elicitation row {cid2} references unknown evidence unit: {uid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'consensus-elicitation row {cid2} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'consensus-elicitation row {cid2} references unknown REF id: {ref}')

    for row in route_rows:
        rid = row.get('route_id','')
        for sid in row.get('social_authority_ids', []):
            if sid not in known_social_ids: errors.append(f'route row {rid} references unknown social-authority row: {sid}')
        for rv in row.get('review_replication_ids', []):
            if rv not in known_review_ids: errors.append(f'route row {rid} references unknown review-replication row: {rv}')
        for cn in row.get('consensus_elicitation_ids', []):
            if cn not in known_consensus_ids: errors.append(f'route row {rid} references unknown consensus-elicitation row: {cn}')

    for collection, label, idfield in [
        (evidence_units, 'evidence unit', 'evidence_unit_id'),
        (credit_rows, 'credit allocation', 'credit_id'),
        (update_rows, 'likelihood/update row', 'likelihood_update_id'),
        (prior_rows, 'prior-sensitivity row', 'prior_sensitivity_id'),
        (measurement_rows, 'measurement model', 'measurement_model_id'),
        (systematic_rows, 'systematic uncertainty row', 'systematic_id'),
        (calibration_rows, 'calibration/traceability row', 'calibration_id'),
        (domain_rows, 'validity-domain row', 'domain_id'),
        (transport_rows, 'transportability row', 'transport_id'),
        (fence_rows, 'extrapolation-fence row', 'fence_id'),
        (mechanism_rows, 'causal mechanism', 'mechanism_id'),
        (intervention_rows, 'intervention protocol', 'intervention_id'),
        (counterfactual_rows, 'counterfactual robustness row', 'counterfactual_id'),
        (selection_rows, 'selection-function row', 'selection_id'),
        (multiplicity_rows, 'multiplicity-control row', 'multiplicity_id'),
        (reporting_bias_rows, 'reporting-bias row', 'bias_id'),
        (capacity_rows, 'model-capacity row', 'model_capacity_id'),
        (complexity_rows, 'complexity-penalty row', 'complexity_penalty_id'),
        (generalization_rows, 'generalization-validation row', 'generalization_id'),
        (severity_rows, 'severity row', 'severity_id'),
        (decision_experiments, 'decision experiment', 'experiment_id'),
        (forecast_rows, 'forecast row', 'forecast_id'),
        (empirical_delta_ledger.get('empirical_deltas', []), 'empirical delta', 'delta_id'),
        (semantic_rows, 'semantic-term row', 'semantic_term_id'),
        (commitment_rows, 'ontology-commitment row', 'ontology_commitment_id'),
        (permission_rows, 'claim-language-permission row', 'language_permission_id'),
    ]:
        for item in collection:
            item_id = item.get(idfield, '')
            for sid in item.get('social_authority_ids', []):
                if sid not in known_social_ids: errors.append(f'{label} {item_id} references unknown social-authority row: {sid}')
            for rv in item.get('review_replication_ids', []):
                if rv not in known_review_ids: errors.append(f'{label} {item_id} references unknown review-replication row: {rv}')
            for cn in item.get('consensus_elicitation_ids', []):
                if cn not in known_consensus_ids: errors.append(f'{label} {item_id} references unknown consensus-elicitation row: {cn}')

    for binding in binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['SOCIAL-AUTHORITY-LEDGER.json','REVIEW-REPLICATION-LEDGER.json','CONSENSUS-ELICITATION-LEDGER.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing social-authority controlling ledger: {rel}')
        for sid in binding.get('social_authority_ids', []):
            if sid not in known_social_ids: errors.append(f'claim-route binding {bid} references unknown social-authority row: {sid}')
        for rv in binding.get('review_replication_ids', []):
            if rv not in known_review_ids: errors.append(f'claim-route binding {bid} references unknown review-replication row: {rv}')
        for cn in binding.get('consensus_elicitation_ids', []):
            if cn not in known_consensus_ids: errors.append(f'claim-route binding {bid} references unknown consensus-elicitation row: {cn}')

    if f"- Social-authority rows: `{len(social_rows)}`" not in social_authority_summary_text:
        errors.append('social-authority generated summary social row count drifted; run make index')
    if f"- Review/replication rows: `{len(review_rows)}`" not in social_authority_summary_text:
        errors.append('social-authority generated summary review/replication count drifted; run make index')
    if f"- Consensus/elicitation rows: `{len(consensus_rows)}`" not in social_authority_summary_text:
        errors.append('social-authority generated summary consensus/elicitation count drifted; run make index')

    # Computational reproducibility / numerical stability / software supply-chain checks added in rev0274.
    computational_reproducibility_ledger = json.loads((root / 'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json').read_text())
    numerical_stability_ledger = json.loads((root / 'NUMERICAL-STABILITY-LEDGER.json').read_text())
    software_supply_chain_ledger = json.loads((root / 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json').read_text())
    computational_reproducibility_summary_text = (root / 'docs/30-program/computational-reproducibility-summary.generated.md').read_text()
    boundary_sector_summary_text = (root / 'docs/30-program/boundary-sector-summary.generated.md').read_text()
    crp_rows = computational_reproducibility_ledger.get('reproducibility_rows', [])
    nst_rows = numerical_stability_ledger.get('stability_rows', [])
    ssc_rows = software_supply_chain_ledger.get('supply_chain_rows', [])
    crp_ids = [item.get('computational_reproducibility_id', '') for item in crp_rows]
    nst_ids = [item.get('numerical_stability_id', '') for item in nst_rows]
    ssc_ids = [item.get('software_supply_chain_id', '') for item in ssc_rows]
    if computational_reproducibility_ledger.get('revision') != manifest['revision']:
        errors.append('COMPUTATIONAL-REPRODUCIBILITY-LEDGER revision drifted from manifest')
    if numerical_stability_ledger.get('revision') != manifest['revision']:
        errors.append('NUMERICAL-STABILITY-LEDGER revision drifted from manifest')
    if software_supply_chain_ledger.get('revision') != manifest['revision']:
        errors.append('SOFTWARE-SUPPLY-CHAIN-LEDGER revision drifted from manifest')
    if boundary_condition_ledger.get('revision') != manifest['revision']:
        errors.append('BOUNDARY-CONDITION-LEDGER revision drifted from manifest')
    if initial_data_ledger.get('revision') != manifest['revision']:
        errors.append('INITIAL-DATA-LEDGER revision drifted from manifest')
    if sector_selection_ledger.get('revision') != manifest['revision']:
        errors.append('SECTOR-SELECTION-LEDGER revision drifted from manifest')
    if (root / 'SYMMETRY-REALIZATION-LEDGER.json').exists() and json.loads((root / 'SYMMETRY-REALIZATION-LEDGER.json').read_text()).get('revision') != manifest['revision']:
        errors.append('SYMMETRY-REALIZATION-LEDGER revision drifted from manifest')
    if (root / 'ANOMALY-MATCHING-LEDGER.json').exists() and json.loads((root / 'ANOMALY-MATCHING-LEDGER.json').read_text()).get('revision') != manifest['revision']:
        errors.append('ANOMALY-MATCHING-LEDGER revision drifted from manifest')
    if (root / 'CONSERVATION-LAW-LEDGER.json').exists() and json.loads((root / 'CONSERVATION-LAW-LEDGER.json').read_text()).get('revision') != manifest['revision']:
        errors.append('CONSERVATION-LAW-LEDGER revision drifted from manifest')
    if len(crp_ids) != len(set(crp_ids)):
        errors.append('COMPUTATIONAL-REPRODUCIBILITY-LEDGER contains duplicate computational_reproducibility_id values')
    if len(nst_ids) != len(set(nst_ids)):
        errors.append('NUMERICAL-STABILITY-LEDGER contains duplicate numerical_stability_id values')
    if len(ssc_ids) != len(set(ssc_ids)):
        errors.append('SOFTWARE-SUPPLY-CHAIN-LEDGER contains duplicate software_supply_chain_id values')
    known_crp_ids = set(crp_ids)
    known_nst_ids = set(nst_ids)
    known_ssc_ids = set(ssc_ids)
    allowed_crp_classes = set(witness_vocab.get('computational_reproducibility_class_labels', []))
    allowed_nst_classes = set(witness_vocab.get('numerical_stability_class_labels', []))
    allowed_ssc_classes = set(witness_vocab.get('software_supply_chain_class_labels', []))
    crp_required = ['computational_reproducibility_id','route_ids','evidence_unit_ids','carrier_ids','protocol_ids','reproducibility_class','computational_artifact','execution_environment','dependency_lock','seed_or_randomness_control','replay_command','independent_reproduction_requirement','maximum_authority_effect','rollback_rule_ids','source_refs']
    nst_required = ['numerical_stability_id','route_ids','evidence_unit_ids','stability_class','numerical_object','precision_or_tolerance','convergence_or_solver_check','stochastic_variability_check','platform_sensitivity','maximum_authority_effect','rollback_rule_ids','source_refs']
    ssc_required = ['software_supply_chain_id','route_ids','carrier_ids','protocol_ids','computational_reproducibility_ids','supply_chain_class','source_control_or_archive','dependency_provenance','build_attestation','vulnerability_or_tamper_controls','release_freeze_rule','maximum_authority_effect','rollback_rule_ids','source_refs']
    for row in crp_rows:
        cid = row.get('computational_reproducibility_id','')
        missing = [field for field in crp_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'computational-reproducibility row {cid or "<missing>"} missing required fields: {missing}')
        if row.get('reproducibility_class') not in allowed_crp_classes: errors.append(f'computational-reproducibility row {cid} has unknown reproducibility_class: {row.get("reproducibility_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'computational-reproducibility row {cid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'computational-reproducibility row {cid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'computational-reproducibility row {cid} references unknown evidence unit: {uid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'computational-reproducibility row {cid} references unknown REF id: {ref}')
    for row in nst_rows:
        nid = row.get('numerical_stability_id','')
        missing = [field for field in nst_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'numerical-stability row {nid or "<missing>"} missing required fields: {missing}')
        if row.get('stability_class') not in allowed_nst_classes: errors.append(f'numerical-stability row {nid} has unknown stability_class: {row.get("stability_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'numerical-stability row {nid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'numerical-stability row {nid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'numerical-stability row {nid} references unknown evidence unit: {uid}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'numerical-stability row {nid} references unknown REF id: {ref}')
    for row in ssc_rows:
        sid = row.get('software_supply_chain_id','')
        missing = [field for field in ssc_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'software-supply-chain row {sid or "<missing>"} missing required fields: {missing}')
        if row.get('supply_chain_class') not in allowed_ssc_classes: errors.append(f'software-supply-chain row {sid} has unknown supply_chain_class: {row.get("supply_chain_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'software-supply-chain row {sid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'software-supply-chain row {sid} references unknown route: {rid}')
        for crp in row.get('computational_reproducibility_ids', []):
            if crp not in known_crp_ids: errors.append(f'software-supply-chain row {sid} references unknown computational-reproducibility row: {crp}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'software-supply-chain row {sid} references unknown REF id: {ref}')
    for row in route_rows:
        rid = row.get('route_id','')
        for cid in row.get('computational_reproducibility_ids', []):
            if cid not in known_crp_ids: errors.append(f'route row {rid} references unknown computational-reproducibility row: {cid}')
        for nid in row.get('numerical_stability_ids', []):
            if nid not in known_nst_ids: errors.append(f'route row {rid} references unknown numerical-stability row: {nid}')
        for sid in row.get('software_supply_chain_ids', []):
            if sid not in known_ssc_ids: errors.append(f'route row {rid} references unknown software-supply-chain row: {sid}')
    if f"- Computational-reproducibility rows: `{len(crp_rows)}`" not in computational_reproducibility_summary_text:
        errors.append('computational-reproducibility generated summary computational row count drifted; run make index')
    if f"- Numerical-stability rows: `{len(nst_rows)}`" not in computational_reproducibility_summary_text:
        errors.append('computational-reproducibility generated summary numerical-stability count drifted; run make index')
    if f"- Software-supply-chain rows: `{len(ssc_rows)}`" not in computational_reproducibility_summary_text:
        errors.append('computational-reproducibility generated summary software-supply-chain count drifted; run make index')


    computational_reproducibility_ledger = json.loads((root / 'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json').read_text()) if (root / 'COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json').exists() else {'reproducibility_rows': []}
    numerical_stability_ledger = json.loads((root / 'NUMERICAL-STABILITY-LEDGER.json').read_text()) if (root / 'NUMERICAL-STABILITY-LEDGER.json').exists() else {'stability_rows': []}
    software_supply_chain_ledger = json.loads((root / 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json').read_text()) if (root / 'SOFTWARE-SUPPLY-CHAIN-LEDGER.json').exists() else {'supply_chain_rows': []}
    comp_rows = computational_reproducibility_ledger.get('reproducibility_rows', [])
    num_rows = numerical_stability_ledger.get('stability_rows', [])
    sw_rows = software_supply_chain_ledger.get('supply_chain_rows', [])
    comp_ids = [item.get('computational_reproducibility_id', '') for item in comp_rows]
    num_ids = [item.get('numerical_stability_id', '') for item in num_rows]
    sw_ids = [item.get('software_supply_chain_id', '') for item in sw_rows]
    if len(comp_ids) != len(set(comp_ids)):
        errors.append('COMPUTATIONAL-REPRODUCIBILITY-LEDGER contains duplicate computational_reproducibility_id values')
    if len(num_ids) != len(set(num_ids)):
        errors.append('NUMERICAL-STABILITY-LEDGER contains duplicate numerical_stability_id values')
    if len(sw_ids) != len(set(sw_ids)):
        errors.append('SOFTWARE-SUPPLY-CHAIN-LEDGER contains duplicate software_supply_chain_id values')
    known_comp_ids = set(comp_ids)
    known_num_ids = set(num_ids)
    known_sw_ids = set(sw_ids)
    allowed_comp_classes = set(witness_vocab.get('computational_reproducibility_class_labels', []))
    allowed_num_classes = set(witness_vocab.get('numerical_stability_class_labels', []))
    allowed_sw_classes = set(witness_vocab.get('software_supply_chain_class_labels', []))
    comp_required = ['computational_reproducibility_id','route_ids','evidence_unit_ids','carrier_ids','protocol_ids','reproducibility_class','computational_artifact','execution_environment','dependency_lock','replay_command','maximum_authority_effect','rollback_rule_ids','source_refs']
    num_required = ['numerical_stability_id','route_ids','evidence_unit_ids','stability_class','numerical_object','precision_or_tolerance','convergence_or_solver_check','platform_sensitivity','maximum_authority_effect','rollback_rule_ids','source_refs']
    sw_required = ['software_supply_chain_id','route_ids','carrier_ids','protocol_ids','computational_reproducibility_ids','supply_chain_class','source_control_or_archive','dependency_provenance','build_attestation','maximum_authority_effect','rollback_rule_ids','source_refs']
    for row in comp_rows:
        cid = row.get('computational_reproducibility_id', '')
        missing = [field for field in comp_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'computational-reproducibility row {cid or "<missing>"} missing required fields: {missing}')
        if row.get('reproducibility_class') not in allowed_comp_classes: errors.append(f'computational-reproducibility row {cid} has unknown reproducibility_class: {row.get("reproducibility_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'computational-reproducibility row {cid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'computational-reproducibility row {cid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'computational-reproducibility row {cid} references unknown evidence unit: {uid}')
        for carrier in row.get('carrier_ids', []):
            if carrier not in known_carrier_ids: errors.append(f'computational-reproducibility row {cid} references unknown carrier: {carrier}')
        for protocol in row.get('protocol_ids', []):
            if protocol not in known_protocol_ids: errors.append(f'computational-reproducibility row {cid} references unknown protocol: {protocol}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'computational-reproducibility row {cid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'computational-reproducibility row {cid} references unknown REF id: {ref}')
    for row in num_rows:
        nid = row.get('numerical_stability_id', '')
        missing = [field for field in num_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'numerical-stability row {nid or "<missing>"} missing required fields: {missing}')
        if row.get('stability_class') not in allowed_num_classes: errors.append(f'numerical-stability row {nid} has unknown stability_class: {row.get("stability_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'numerical-stability row {nid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'numerical-stability row {nid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'numerical-stability row {nid} references unknown evidence unit: {uid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'numerical-stability row {nid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'numerical-stability row {nid} references unknown REF id: {ref}')
    for row in sw_rows:
        sid = row.get('software_supply_chain_id', '')
        missing = [field for field in sw_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'software-supply-chain row {sid or "<missing>"} missing required fields: {missing}')
        if row.get('supply_chain_class') not in allowed_sw_classes: errors.append(f'software-supply-chain row {sid} has unknown supply_chain_class: {row.get("supply_chain_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'software-supply-chain row {sid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'software-supply-chain row {sid} references unknown route: {rid}')
        for cid in row.get('computational_reproducibility_ids', []):
            if cid not in known_comp_ids: errors.append(f'software-supply-chain row {sid} references unknown computational-reproducibility row: {cid}')
        for carrier in row.get('carrier_ids', []):
            if carrier not in known_carrier_ids: errors.append(f'software-supply-chain row {sid} references unknown carrier: {carrier}')
        for protocol in row.get('protocol_ids', []):
            if protocol not in known_protocol_ids: errors.append(f'software-supply-chain row {sid} references unknown protocol: {protocol}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'software-supply-chain row {sid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'software-supply-chain row {sid} references unknown REF id: {ref}')
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('computational_reproducibility_ids') or not row.get('numerical_stability_ids') or not row.get('software_supply_chain_ids'):
            errors.append(f'route row {rid} missing computational / numerical / software handles')
        for cid in row.get('computational_reproducibility_ids', []):
            if cid not in known_comp_ids: errors.append(f'route row {rid} references unknown computational-reproducibility row: {cid}')
        for nid in row.get('numerical_stability_ids', []):
            if nid not in known_num_ids: errors.append(f'route row {rid} references unknown numerical-stability row: {nid}')
        for sid in row.get('software_supply_chain_ids', []):
            if sid not in known_sw_ids: errors.append(f'route row {rid} references unknown software-supply-chain row: {sid}')
    computational_summary_text = (root / 'docs/30-program/computational-reproducibility-summary.generated.md').read_text() if (root / 'docs/30-program/computational-reproducibility-summary.generated.md').exists() else ''
    if f"- Computational-reproducibility rows: `{len(comp_rows)}`" not in computational_summary_text:
        errors.append('computational generated summary reproducibility count drifted; run make index')
    if f"- Numerical-stability rows: `{len(num_rows)}`" not in computational_summary_text:
        errors.append('computational generated summary numerical count drifted; run make index')
    if f"- Software-supply-chain rows: `{len(sw_rows)}`" not in computational_summary_text:
        errors.append('computational generated summary software count drifted; run make index')


    # Preload rev0275 formal-proof node ids before dependency-graph validation.
    proof_obligation_ledger_for_edges = json.loads((root / 'PROOF-OBLIGATION-LEDGER.json').read_text())
    assumption_discharge_ledger_for_edges = json.loads((root / 'ASSUMPTION-DISCHARGE-LEDGER.json').read_text())
    formalization_coverage_ledger_for_edges = json.loads((root / 'FORMALIZATION-COVERAGE-LEDGER.json').read_text())
    known_pob_ids = set(item.get('proof_obligation_id', '') for item in proof_obligation_ledger_for_edges.get('proof_obligation_rows', []))
    known_asd_ids = set(item.get('assumption_discharge_id', '') for item in assumption_discharge_ledger_for_edges.get('assumption_discharge_rows', []))
    known_fcv_ids = set(item.get('formalization_coverage_id', '') for item in formalization_coverage_ledger_for_edges.get('formalization_rows', []))

    # Preload rev0276 idealization / approximation / limit node ids before dependency-graph validation.
    idealization_ledger_for_edges = json.loads((root / 'IDEALIZATION-LEDGER.json').read_text())
    approximation_error_ledger_for_edges = json.loads((root / 'APPROXIMATION-ERROR-LEDGER.json').read_text())
    limit_interchange_ledger_for_edges = json.loads((root / 'LIMIT-INTERCHANGE-LEDGER.json').read_text())
    known_idl_ids = set(item.get('idealization_id', '') for item in idealization_ledger_for_edges.get('idealization_rows', []))
    known_aer_ids = set(item.get('approximation_error_id', '') for item in approximation_error_ledger_for_edges.get('approximation_rows', []))
    known_lim_ids = set(item.get('limit_interchange_id', '') for item in limit_interchange_ledger_for_edges.get('limit_rows', []))

    # Preload rev0277 boundary / initial-data / sector-selection node ids before dependency-graph validation.
    boundary_condition_ledger_for_edges = json.loads((root / 'BOUNDARY-CONDITION-LEDGER.json').read_text())
    initial_data_ledger_for_edges = json.loads((root / 'INITIAL-DATA-LEDGER.json').read_text())
    sector_selection_ledger_for_edges = json.loads((root / 'SECTOR-SELECTION-LEDGER.json').read_text())
    known_bnd_ids = set(item.get('boundary_condition_id', '') for item in boundary_condition_ledger_for_edges.get('boundary_rows', []))
    known_ini_ids = set(item.get('initial_data_id', '') for item in initial_data_ledger_for_edges.get('initial_data_rows', []))
    known_sec_ids = set(item.get('sector_selection_id', '') for item in sector_selection_ledger_for_edges.get('sector_rows', []))

    # Preload rev0278 gauge-symmetry / constraint-closure / observable-quotient node ids before dependency-graph validation.
    gauge_symmetry_ledger_for_edges = json.loads((root / 'GAUGE-SYMMETRY-LEDGER.json').read_text())
    constraint_closure_ledger_for_edges = json.loads((root / 'CONSTRAINT-CLOSURE-LEDGER.json').read_text())
    observable_quotient_ledger_for_edges = json.loads((root / 'OBSERVABLE-QUOTIENT-LEDGER.json').read_text())
    known_gsy_ids = set(item.get('gauge_symmetry_id', '') for item in gauge_symmetry_ledger_for_edges.get('gauge_rows', []))
    known_ccl_ids = set(item.get('constraint_closure_id', '') for item in constraint_closure_ledger_for_edges.get('constraint_rows', []))
    known_obsq_ids = set(item.get('observable_quotient_id', '') for item in observable_quotient_ledger_for_edges.get('observable_rows', []))

    # Preload rev0279 regularization-scheme / renormalization-flow / matching-condition node ids before dependency-graph validation.
    regularization_scheme_ledger_for_edges = json.loads((root / 'REGULARIZATION-SCHEME-LEDGER.json').read_text())
    renormalization_flow_ledger_for_edges = json.loads((root / 'RENORMALIZATION-FLOW-LEDGER.json').read_text())
    matching_condition_ledger_for_edges = json.loads((root / 'MATCHING-CONDITION-LEDGER.json').read_text())
    known_reg_ids = set(item.get('regularization_scheme_id', '') for item in regularization_scheme_ledger_for_edges.get('regularization_rows', []))
    known_rgf_ids = set(item.get('renormalization_flow_id', '') for item in renormalization_flow_ledger_for_edges.get('flow_rows', []))
    known_mat_ids = set(item.get('matching_condition_id', '') for item in matching_condition_ledger_for_edges.get('matching_rows', []))

    # Preload rev0280 composition-law / interface-compatibility / global-consistency node ids before dependency-graph validation.
    composition_law_ledger_for_edges = json.loads((root / 'COMPOSITION-LAW-LEDGER.json').read_text())
    interface_compatibility_ledger_for_edges = json.loads((root / 'INTERFACE-COMPATIBILITY-LEDGER.json').read_text())
    global_consistency_ledger_for_edges = json.loads((root / 'GLOBAL-CONSISTENCY-LEDGER.json').read_text())
    known_cmp_ids = set(item.get('composition_law_id', '') for item in composition_law_ledger_for_edges.get('composition_rows', []))
    known_ifc_ids = set(item.get('interface_compatibility_id', '') for item in interface_compatibility_ledger_for_edges.get('interface_rows', []))
    known_glc_ids = set(item.get('global_consistency_id', '') for item in global_consistency_ledger_for_edges.get('global_rows', []))

    # Preload rev0281 unitarity-check / causality-cone / stability-positivity node ids before dependency-graph validation.
    unitarity_check_ledger_for_edges = json.loads((root / 'UNITARITY-CHECK-LEDGER.json').read_text())
    causality_cone_ledger_for_edges = json.loads((root / 'CAUSALITY-CONE-LEDGER.json').read_text())
    stability_positivity_ledger_for_edges = json.loads((root / 'STABILITY-POSITIVITY-LEDGER.json').read_text())
    known_uni_ids = set(item.get('unitarity_check_id', '') for item in unitarity_check_ledger_for_edges.get('unitarity_rows', []))
    known_cau_ids = set(item.get('causality_cone_id', '') for item in causality_cone_ledger_for_edges.get('causality_rows', []))
    known_stb_ids = set(item.get('stability_positivity_id', '') for item in stability_positivity_ledger_for_edges.get('stability_rows', []))

    # Preload rev0282 quantization-map / classical-limit / semiclassical-correspondence node ids before dependency-graph validation.
    quantization_map_ledger_for_edges = json.loads((root / 'QUANTIZATION-MAP-LEDGER.json').read_text())
    classical_limit_ledger_for_edges = json.loads((root / 'CLASSICAL-LIMIT-LEDGER.json').read_text())
    semiclassical_correspondence_ledger_for_edges = json.loads((root / 'SEMICLASSICAL-CORRESPONDENCE-LEDGER.json').read_text())
    known_qmap_ids = set(item.get('quantization_map_id', '') for item in quantization_map_ledger_for_edges.get('quantization_rows', []))
    known_clim_ids = set(item.get('classical_limit_id', '') for item in classical_limit_ledger_for_edges.get('classical_limit_rows', []))
    known_scor_ids = set(item.get('semiclassical_correspondence_id', '') for item in semiclassical_correspondence_ledger_for_edges.get('semiclassical_rows', []))


    # Preload rev0283 information-flow / entropy-accounting / no-go-compliance node ids before dependency-graph validation.
    information_flow_ledger_for_edges = json.loads((root / 'INFORMATION-FLOW-LEDGER.json').read_text())
    entropy_accounting_ledger_for_edges = json.loads((root / 'ENTROPY-ACCOUNTING-LEDGER.json').read_text())
    no_go_compliance_ledger_for_edges = json.loads((root / 'NO-GO-COMPLIANCE-LEDGER.json').read_text())
    known_ifl_ids = set(item.get('information_flow_id', '') for item in information_flow_ledger_for_edges.get('information_rows', []))
    known_ent_ids = set(item.get('entropy_accounting_id', '') for item in entropy_accounting_ledger_for_edges.get('entropy_rows', []))
    known_ngc_ids = set(item.get('no_go_compliance_id', '') for item in no_go_compliance_ledger_for_edges.get('no_go_rows', []))

    # Preload rev0284 symmetry-realization / anomaly-matching / conservation-law node ids before dependency-graph validation.
    symmetry_realization_ledger_for_edges = json.loads((root / 'SYMMETRY-REALIZATION-LEDGER.json').read_text())
    anomaly_matching_ledger_for_edges = json.loads((root / 'ANOMALY-MATCHING-LEDGER.json').read_text())
    conservation_law_ledger_for_edges = json.loads((root / 'CONSERVATION-LAW-LEDGER.json').read_text())
    known_sym_ids = set(item.get('symmetry_realization_id', '') for item in symmetry_realization_ledger_for_edges.get('symmetry_rows', []))
    known_anm_ids = set(item.get('anomaly_matching_id', '') for item in anomaly_matching_ledger_for_edges.get('anomaly_rows', []))
    known_con_ids = set(item.get('conservation_law_id', '') for item in conservation_law_ledger_for_edges.get('conservation_rows', []))

    # Preload rev0285 spacetime-topology / dimension-realization / signature-structure node ids before dependency-graph validation.
    spacetime_topology_ledger_for_edges = json.loads((root / 'SPACETIME-TOPOLOGY-LEDGER.json').read_text())
    dimension_realization_ledger_for_edges = json.loads((root / 'DIMENSION-REALIZATION-LEDGER.json').read_text())
    signature_structure_ledger_for_edges = json.loads((root / 'SIGNATURE-STRUCTURE-LEDGER.json').read_text())
    known_top_ids = set(item.get('spacetime_topology_id', '') for item in spacetime_topology_ledger_for_edges.get('topology_rows', []))
    known_dim_ids = set(item.get('dimension_realization_id', '') for item in dimension_realization_ledger_for_edges.get('dimension_rows', []))
    known_sig_ids = set(item.get('signature_structure_id', '') for item in signature_structure_ledger_for_edges.get('signature_rows', []))

    # Preload rev0286 algebraic-locality / subsystem-factorization / edge-mode-center node ids before dependency-graph validation.
    algebraic_locality_ledger_for_edges = json.loads((root / 'ALGEBRAIC-LOCALITY-LEDGER.json').read_text()) if (root / 'ALGEBRAIC-LOCALITY-LEDGER.json').exists() else {'algebraic_rows': []}
    subsystem_factorization_ledger_for_edges = json.loads((root / 'SUBSYSTEM-FACTORIZATION-LEDGER.json').read_text()) if (root / 'SUBSYSTEM-FACTORIZATION-LEDGER.json').exists() else {'factorization_rows': []}
    edge_mode_center_ledger_for_edges = json.loads((root / 'EDGE-MODE-CENTER-LEDGER.json').read_text()) if (root / 'EDGE-MODE-CENTER-LEDGER.json').exists() else {'edge_mode_rows': []}
    known_alg_ids = set(item.get('algebraic_locality_id', '') for item in algebraic_locality_ledger_for_edges.get('algebraic_rows', []))
    known_fac_ids = set(item.get('subsystem_factorization_id', '') for item in subsystem_factorization_ledger_for_edges.get('factorization_rows', []))
    known_edg_ids = set(item.get('edge_mode_center_id', '') for item in edge_mode_center_ledger_for_edges.get('edge_mode_rows', []))

    # Preload rev0286 measure-definition / ensemble-sampling / typicality-weighting node ids before dependency-graph validation.
    measure_definition_ledger_for_edges = json.loads((root / 'MEASURE-DEFINITION-LEDGER.json').read_text()) if (root / 'MEASURE-DEFINITION-LEDGER.json').exists() else {'measure_rows': []}
    ensemble_sampling_ledger_for_edges = json.loads((root / 'ENSEMBLE-SAMPLING-LEDGER.json').read_text()) if (root / 'ENSEMBLE-SAMPLING-LEDGER.json').exists() else {'ensemble_rows': []}
    typicality_weighting_ledger_for_edges = json.loads((root / 'TYPICALITY-WEIGHTING-LEDGER.json').read_text()) if (root / 'TYPICALITY-WEIGHTING-LEDGER.json').exists() else {'typicality_rows': []}
    known_mea_ids = set(item.get('measure_definition_id', '') for item in measure_definition_ledger_for_edges.get('measure_rows', []))
    known_ens_ids = set(item.get('ensemble_sampling_id', '') for item in ensemble_sampling_ledger_for_edges.get('ensemble_rows', []))
    known_typ_ids = set(item.get('typicality_weighting_id', '') for item in typicality_weighting_ledger_for_edges.get('typicality_rows', []))

    # Preload rev0287 matter-sector node ids before dependency-graph validation.
    particle_spectrum_ledger_for_edges = json.loads((root / 'PARTICLE-SPECTRUM-LEDGER.json').read_text()) if (root / 'PARTICLE-SPECTRUM-LEDGER.json').exists() else {'particle_spectrum_rows': []}
    interaction_coupling_ledger_for_edges = json.loads((root / 'INTERACTION-COUPLING-LEDGER.json').read_text()) if (root / 'INTERACTION-COUPLING-LEDGER.json').exists() else {'interaction_coupling_rows': []}
    mass_hierarchy_ledger_for_edges = json.loads((root / 'MASS-HIERARCHY-LEDGER.json').read_text()) if (root / 'MASS-HIERARCHY-LEDGER.json').exists() else {'mass_hierarchy_rows': []}
    known_psp_ids = set(item.get('particle_spectrum_id', '') for item in particle_spectrum_ledger_for_edges.get('particle_spectrum_rows', []))
    known_icg_ids = set(item.get('interaction_coupling_id', '') for item in interaction_coupling_ledger_for_edges.get('interaction_coupling_rows', []))
    known_mhg_ids = set(item.get('mass_hierarchy_id', '') for item in mass_hierarchy_ledger_for_edges.get('mass_hierarchy_rows', []))

    # Preload rev0288 cosmological-background / vacuum-energy / thermal-history node ids before dependency-graph validation.
    cosmological_background_ledger_for_edges = json.loads((root / 'COSMOLOGICAL-BACKGROUND-LEDGER.json').read_text()) if (root / 'COSMOLOGICAL-BACKGROUND-LEDGER.json').exists() else {'background_rows': []}
    vacuum_energy_ledger_for_edges = json.loads((root / 'VACUUM-ENERGY-LEDGER.json').read_text()) if (root / 'VACUUM-ENERGY-LEDGER.json').exists() else {'vacuum_energy_rows': []}
    thermal_history_ledger_for_edges = json.loads((root / 'THERMAL-HISTORY-LEDGER.json').read_text()) if (root / 'THERMAL-HISTORY-LEDGER.json').exists() else {'thermal_history_rows': []}
    known_cbg_ids = set(item.get('cosmological_background_id', '') for item in cosmological_background_ledger_for_edges.get('background_rows', []))
    known_ved_ids = set(item.get('vacuum_energy_id', '') for item in vacuum_energy_ledger_for_edges.get('vacuum_energy_rows', []))
    known_ths_ids = set(item.get('thermal_history_id', '') for item in thermal_history_ledger_for_edges.get('thermal_history_rows', []))

    # Preload rev0289 black-hole horizon / thermodynamics / evaporation node ids before dependency-graph validation.
    horizon_structure_ledger_for_edges = json.loads((root / 'HORIZON-STRUCTURE-LEDGER.json').read_text()) if (root / 'HORIZON-STRUCTURE-LEDGER.json').exists() else {'horizon_rows': []}
    black_hole_thermodynamics_ledger_for_edges = json.loads((root / 'BLACK-HOLE-THERMODYNAMICS-LEDGER.json').read_text()) if (root / 'BLACK-HOLE-THERMODYNAMICS-LEDGER.json').exists() else {'thermodynamics_rows': []}
    evaporation_radiation_ledger_for_edges = json.loads((root / 'EVAPORATION-RADIATION-LEDGER.json').read_text()) if (root / 'EVAPORATION-RADIATION-LEDGER.json').exists() else {'evaporation_rows': []}
    known_hzn_ids = set(item.get('horizon_structure_id', '') for item in horizon_structure_ledger_for_edges.get('horizon_rows', []))
    known_bht_ids = set(item.get('black_hole_thermodynamics_id', '') for item in black_hole_thermodynamics_ledger_for_edges.get('thermodynamics_rows', []))
    known_evr_ids = set(item.get('evaporation_radiation_id', '') for item in evaporation_radiation_ledger_for_edges.get('evaporation_rows', []))

    # Preload rev0290 curvature-regime / singularity-resolution / censorship-hyperbolicity node ids before dependency-graph validation.
    curvature_regime_ledger_for_edges = json.loads((root / 'CURVATURE-REGIME-LEDGER.json').read_text()) if (root / 'CURVATURE-REGIME-LEDGER.json').exists() else {'curvature_rows': []}
    singularity_resolution_ledger_for_edges = json.loads((root / 'SINGULARITY-RESOLUTION-LEDGER.json').read_text()) if (root / 'SINGULARITY-RESOLUTION-LEDGER.json').exists() else {'singularity_rows': []}
    censorship_hyperbolicity_ledger_for_edges = json.loads((root / 'CENSORSHIP-HYPERBOLICITY-LEDGER.json').read_text()) if (root / 'CENSORSHIP-HYPERBOLICITY-LEDGER.json').exists() else {'censorship_rows': []}
    known_crv_ids = set(item.get('curvature_regime_id', '') for item in curvature_regime_ledger_for_edges.get('curvature_rows', []))
    known_sng_ids = set(item.get('singularity_resolution_id', '') for item in singularity_resolution_ledger_for_edges.get('singularity_rows', []))
    known_chy_ids = set(item.get('censorship_hyperbolicity_id', '') for item in censorship_hyperbolicity_ledger_for_edges.get('censorship_rows', []))


    # Preload rev0291 stress-energy/source / backreaction / energy-condition node ids before dependency-graph validation.
    stress_energy_source_ledger_for_edges = json.loads((root / 'STRESS-ENERGY-SOURCE-LEDGER.json').read_text()) if (root / 'STRESS-ENERGY-SOURCE-LEDGER.json').exists() else {'source_rows': []}
    semiclassical_backreaction_ledger_for_edges = json.loads((root / 'SEMICLASSICAL-BACKREACTION-LEDGER.json').read_text()) if (root / 'SEMICLASSICAL-BACKREACTION-LEDGER.json').exists() else {'backreaction_rows': []}
    energy_condition_ledger_for_edges = json.loads((root / 'ENERGY-CONDITION-LEDGER.json').read_text()) if (root / 'ENERGY-CONDITION-LEDGER.json').exists() else {'energy_condition_rows': []}
    known_set_ids = set(item.get('stress_energy_source_id', '') for item in stress_energy_source_ledger_for_edges.get('source_rows', []))
    known_bkr_ids = set(item.get('backreaction_consistency_id', '') for item in semiclassical_backreaction_ledger_for_edges.get('backreaction_rows', []))
    known_enc_ids = set(item.get('energy_condition_id', '') for item in energy_condition_ledger_for_edges.get('energy_condition_rows', []))


    # Preload rev0292 classical-GR recovery node ids before dependency-graph validation.
    equivalence_principle_ledger_for_edges = json.loads((root / 'EQUIVALENCE-PRINCIPLE-LEDGER.json').read_text()) if (root / 'EQUIVALENCE-PRINCIPLE-LEDGER.json').exists() else {'equivalence_principle_rows': []}
    weak_field_ppn_ledger_for_edges = json.loads((root / 'WEAK-FIELD-PPN-LEDGER.json').read_text()) if (root / 'WEAK-FIELD-PPN-LEDGER.json').exists() else {'weak_field_ppn_rows': []}
    gravitational_radiation_ledger_for_edges = json.loads((root / 'GRAVITATIONAL-RADIATION-LEDGER.json').read_text()) if (root / 'GRAVITATIONAL-RADIATION-LEDGER.json').exists() else {'radiation_rows': []}
    known_epr_ids = set(item.get('equivalence_principle_id', '') for item in equivalence_principle_ledger_for_edges.get('equivalence_principle_rows', []))
    known_wfp_ids = set(item.get('weak_field_ppn_id', '') for item in weak_field_ppn_ledger_for_edges.get('weak_field_ppn_rows', []))
    known_grr_ids = set(item.get('gravitational_radiation_id', '') for item in gravitational_radiation_ledger_for_edges.get('radiation_rows', []))


    # Preload rev0293 state-preparation / detector-response / decoherence node ids before dependency-graph validation.
    state_preparation_ledger_for_edges = json.loads((root / 'STATE-PREPARATION-LEDGER.json').read_text()) if (root / 'STATE-PREPARATION-LEDGER.json').exists() else {'state_preparation_rows': []}
    detector_response_ledger_for_edges = json.loads((root / 'DETECTOR-RESPONSE-LEDGER.json').read_text()) if (root / 'DETECTOR-RESPONSE-LEDGER.json').exists() else {'detector_response_rows': []}
    decoherence_pointer_ledger_for_edges = json.loads((root / 'DECOHERENCE-POINTER-LEDGER.json').read_text()) if (root / 'DECOHERENCE-POINTER-LEDGER.json').exists() else {'decoherence_pointer_rows': []}
    known_spr_ids = set(item.get('state_preparation_id', '') for item in state_preparation_ledger_for_edges.get('state_preparation_rows', []))
    known_dre_ids = set(item.get('detector_response_id', '') for item in detector_response_ledger_for_edges.get('detector_response_rows', []))
    known_dcp_ids = set(item.get('decoherence_pointer_id', '') for item in decoherence_pointer_ledger_for_edges.get('decoherence_pointer_rows', []))


    # Preload rev0294 asymptotic-state / infrared-dressing / scattering-observable node ids before dependency-graph validation.
    asymptotic_state_ledger_for_edges = json.loads((root / 'ASYMPTOTIC-STATE-LEDGER.json').read_text()) if (root / 'ASYMPTOTIC-STATE-LEDGER.json').exists() else {'asymptotic_state_rows': []}
    infrared_dressing_ledger_for_edges = json.loads((root / 'INFRARED-DRESSING-LEDGER.json').read_text()) if (root / 'INFRARED-DRESSING-LEDGER.json').exists() else {'infrared_dressing_rows': []}
    scattering_observable_ledger_for_edges = json.loads((root / 'SCATTERING-OBSERVABLE-LEDGER.json').read_text()) if (root / 'SCATTERING-OBSERVABLE-LEDGER.json').exists() else {'scattering_observable_rows': []}
    known_asy_ids = set(item.get('asymptotic_state_id', '') for item in asymptotic_state_ledger_for_edges.get('asymptotic_state_rows', []))
    known_ird_ids = set(item.get('infrared_dressing_id', '') for item in infrared_dressing_ledger_for_edges.get('infrared_dressing_rows', []))
    known_sco_ids = set(item.get('scattering_observable_id', '') for item in scattering_observable_ledger_for_edges.get('scattering_observable_rows', []))


    # Preload rev0295 discretization-regime / finite-volume-scaling / continuum-extrapolation node ids before dependency-graph validation.
    discretization_regime_ledger_for_edges = json.loads((root / 'DISCRETIZATION-REGIME-LEDGER.json').read_text()) if (root / 'DISCRETIZATION-REGIME-LEDGER.json').exists() else {'discretization_rows': []}
    finite_volume_scaling_ledger_for_edges = json.loads((root / 'FINITE-VOLUME-SCALING-LEDGER.json').read_text()) if (root / 'FINITE-VOLUME-SCALING-LEDGER.json').exists() else {'finite_volume_rows': []}
    continuum_extrapolation_ledger_for_edges = json.loads((root / 'CONTINUUM-EXTRAPOLATION-LEDGER.json').read_text()) if (root / 'CONTINUUM-EXTRAPOLATION-LEDGER.json').exists() else {'continuum_extrapolation_rows': []}
    known_drg_ids = set(item.get('discretization_regime_id', '') for item in discretization_regime_ledger_for_edges.get('discretization_rows', []))
    known_fvs_ids = set(item.get('finite_volume_scaling_id', '') for item in finite_volume_scaling_ledger_for_edges.get('finite_volume_rows', []))
    known_cex_ids = set(item.get('continuum_extrapolation_id', '') for item in continuum_extrapolation_ledger_for_edges.get('continuum_extrapolation_rows', []))


    # Preload rev0296 correlation-function / operator-insertion / bootstrap-data node ids before dependency-graph validation.
    correlation_function_ledger_for_edges = json.loads((root / 'CORRELATION-FUNCTION-LEDGER.json').read_text()) if (root / 'CORRELATION-FUNCTION-LEDGER.json').exists() else {'correlation_function_rows': []}
    operator_insertion_ledger_for_edges = json.loads((root / 'OPERATOR-INSERTION-LEDGER.json').read_text()) if (root / 'OPERATOR-INSERTION-LEDGER.json').exists() else {'operator_insertion_rows': []}
    bootstrap_data_ledger_for_edges = json.loads((root / 'BOOTSTRAP-DATA-LEDGER.json').read_text()) if (root / 'BOOTSTRAP-DATA-LEDGER.json').exists() else {'bootstrap_data_rows': []}
    known_cfn_ids = set(item.get('correlation_function_id', '') for item in correlation_function_ledger_for_edges.get('correlation_function_rows', []))
    known_opi_ids = set(item.get('operator_insertion_id', '') for item in operator_insertion_ledger_for_edges.get('operator_insertion_rows', []))
    known_bsd_ids = set(item.get('bootstrap_data_id', '') for item in bootstrap_data_ledger_for_edges.get('bootstrap_data_rows', []))


    # Preload rev0297 phase-structure / order-parameter / universality-class node ids before dependency-graph validation.
    phase_structure_ledger_for_edges = json.loads((root / 'PHASE-STRUCTURE-LEDGER.json').read_text()) if (root / 'PHASE-STRUCTURE-LEDGER.json').exists() else {'phase_structure_rows': []}
    order_parameter_ledger_for_edges = json.loads((root / 'ORDER-PARAMETER-LEDGER.json').read_text()) if (root / 'ORDER-PARAMETER-LEDGER.json').exists() else {'order_parameter_rows': []}
    universality_class_ledger_for_edges = json.loads((root / 'UNIVERSALITY-CLASS-LEDGER.json').read_text()) if (root / 'UNIVERSALITY-CLASS-LEDGER.json').exists() else {'universality_class_rows': []}
    known_phs_ids = set(item.get('phase_structure_id', '') for item in phase_structure_ledger_for_edges.get('phase_structure_rows', []))
    known_opm_ids = set(item.get('order_parameter_id', '') for item in order_parameter_ledger_for_edges.get('order_parameter_rows', []))
    known_ucl_ids = set(item.get('universality_class_id', '') for item in universality_class_ledger_for_edges.get('universality_class_rows', []))


    # Preload rev0298 Hilbert-space / representation-map / spectral-reconstruction node ids before dependency-graph validation.
    hilbert_space_ledger_for_edges = json.loads((root / 'HILBERT-SPACE-LEDGER.json').read_text()) if (root / 'HILBERT-SPACE-LEDGER.json').exists() else {'hilbert_space_rows': []}
    representation_map_ledger_for_edges = json.loads((root / 'REPRESENTATION-MAP-LEDGER.json').read_text()) if (root / 'REPRESENTATION-MAP-LEDGER.json').exists() else {'representation_map_rows': []}
    spectral_reconstruction_ledger_for_edges = json.loads((root / 'SPECTRAL-RECONSTRUCTION-LEDGER.json').read_text()) if (root / 'SPECTRAL-RECONSTRUCTION-LEDGER.json').exists() else {'spectral_reconstruction_rows': []}
    known_hsp_ids = set(item.get('hilbert_space_id', '') for item in hilbert_space_ledger_for_edges.get('hilbert_space_rows', []))
    known_rmp_ids = set(item.get('representation_map_id', '') for item in representation_map_ledger_for_edges.get('representation_map_rows', []))
    known_src_ids = set(item.get('spectral_reconstruction_id', '') for item in spectral_reconstruction_ledger_for_edges.get('spectral_reconstruction_rows', []))

    edge_rows = dependency_graph.get('edge_rows', [])
    edge_ids = [item.get('edge_id', '') for item in edge_rows]
    if len(edge_ids) != len(set(edge_ids)):
        errors.append('AUTHORITY-DEPENDENCY-GRAPH contains duplicate edge_id values')
    allowed_dependency_kinds = set(witness_vocab.get('dependency_kind_labels', []))
    edge_required_fields = ['edge_id','source_kind','source_id','dependent_kind','dependent_id','dependency_kind','required_for','failure_effect','max_credit_transmitted']
    route_like_kind_to_known = {
        'route': known_route_ids,
        'empirical-delta': known_delta_ids,
        'forecast': known_forecast_ids,
        'carrier': known_carrier_ids,
        'protocol': known_protocol_ids,
        'negative-control': known_control_ids,
        'promotion-gate': known_gate_ids,
        'observed-sector-obligation': known_obligation_ids,
        'defeater': known_defeater_ids,
        'severity-test': known_severity_ids,
        'rollback-rule': known_rollback_ids,
        'evidence-unit': known_evidence_unit_ids,
        'independence-assumption': known_independence_ids,
        'credit-allocation': known_credit_ids,
        'contrast-class': known_contrast_ids,
        'likelihood-update': known_update_ids,
        'prior-sensitivity': known_prior_ids,
        'measurement-model': known_measurement_model_ids,
        'systematic-uncertainty': known_systematic_ids,
        'calibration-traceability': known_calibration_ids,
        'validity-domain': known_domain_ids,
        'transportability': known_transport_ids,
        'extrapolation-fence': known_fence_ids,
        'causal-mechanism': known_mechanism_ids,
        'intervention-protocol': known_intervention_ids,
        'counterfactual-robustness': known_counterfactual_ids,
        'selection-function': known_selection_ids,
        'multiplicity-control': known_multiplicity_ids,
        'reporting-bias': known_reporting_bias_ids,
        'model-capacity': known_capacity_ids,
        'complexity-penalty': known_complexity_ids,
        'generalization-validation': known_generalization_ids,
        'semantic-term': known_semantic_ids,
        'ontology-commitment': known_commitment_ids,
        'claim-language-permission': known_permission_ids,
        'social-authority': known_social_ids,
        'review-replication': known_review_ids,
        'consensus-elicitation': known_consensus_ids,
        'computational-reproducibility': known_crp_ids,
        'numerical-stability': known_nst_ids,
        'software-supply-chain': known_ssc_ids,
        'computational-reproducibility': known_crp_ids,
        'numerical-stability': known_nst_ids,
        'software-supply-chain': known_ssc_ids,
        'proof-obligation': known_pob_ids,
        'assumption-discharge': known_asd_ids,
        'formalization-coverage': known_fcv_ids,
        'idealization': known_idl_ids,
        'approximation-error': known_aer_ids,
        'limit-interchange': known_lim_ids,
        'boundary-condition': known_bnd_ids,
        'initial-data': known_ini_ids,
        'sector-selection': known_sec_ids,
        'gauge-symmetry': known_gsy_ids,
        'constraint-closure': known_ccl_ids,
        'observable-quotient': known_obsq_ids,
        'regularization-scheme': known_reg_ids,
        'renormalization-flow': known_rgf_ids,
        'matching-condition': known_mat_ids,
        'composition-law': known_cmp_ids,
        'interface-compatibility': known_ifc_ids,
        'global-consistency': known_glc_ids,
        'unitarity-check': known_uni_ids,
        'causality-cone': known_cau_ids,
        'stability-positivity': known_stb_ids,
        'quantization-map': known_qmap_ids,
        'classical-limit': known_clim_ids,
        'semiclassical-correspondence': known_scor_ids,
        'information-flow': known_ifl_ids,
        'entropy-accounting': known_ent_ids,
        'no-go-compliance': known_ngc_ids,
        'symmetry-realization': known_sym_ids,
        'anomaly-matching': known_anm_ids,
        'conservation-law': known_con_ids,
        'spacetime-topology': known_top_ids,
        'dimension-realization': known_dim_ids,
        'signature-structure': known_sig_ids,
        'algebraic-locality': known_alg_ids,
        'subsystem-factorization': known_fac_ids,
        'edge-mode-center': known_edg_ids,
        'measure-definition': known_mea_ids,
        'ensemble-sampling': known_ens_ids,
        'typicality-weighting': known_typ_ids,
        'particle-spectrum': known_psp_ids,
        'interaction-coupling': known_icg_ids,
        'mass-hierarchy': known_mhg_ids,
        'cosmological-background': known_cbg_ids,
        'vacuum-energy': known_ved_ids,
        'thermal-history': known_ths_ids,
        'horizon-structure': known_hzn_ids,
        'black-hole-thermodynamics': known_bht_ids,
        'evaporation-radiation': known_evr_ids,
        'curvature-regime': known_crv_ids,
        'singularity-resolution': known_sng_ids,
        'censorship-hyperbolicity': known_chy_ids,
        'stress-energy-source': known_set_ids,
        'semiclassical-backreaction': known_bkr_ids,
        'energy-condition': known_enc_ids,
        'equivalence-principle': known_epr_ids,
        'weak-field-ppn': known_wfp_ids,
        'gravitational-radiation': known_grr_ids,
        'state-preparation': known_spr_ids,
        'detector-response': known_dre_ids,
        'decoherence-pointer': known_dcp_ids,
        'asymptotic-state': known_asy_ids,
        'infrared-dressing': known_ird_ids,
        'scattering-observable': known_sco_ids,
        'discretization-regime': known_drg_ids,
        'finite-volume-scaling': known_fvs_ids,
        'continuum-extrapolation': known_cex_ids,
        'correlation-function': known_cfn_ids,
        'operator-insertion': known_opi_ids,
        'bootstrap-data': known_bsd_ids,
        'phase-structure': known_phs_ids,
        'order-parameter': known_opm_ids,
        'universality-class': known_ucl_ids,
        'hilbert-space': known_hsp_ids,
        'representation-map': known_rmp_ids,
        'spectral-reconstruction': known_src_ids,
        'decision-experiment': known_decision_ids,
        'claim': registered_claim_ids,
        'open-question': registered_question_ids,
    }
    edge_key_set = set()
    for edge in edge_rows:
        eid = edge.get('edge_id', '')
        missing = [field for field in edge_required_fields if field not in edge or edge.get(field) in ('', [], None)]
        if missing:
            errors.append(f'authority dependency edge {eid or "<missing>"} missing required fields: {missing}')
        if edge.get('dependency_kind') not in allowed_dependency_kinds:
            errors.append(f'authority dependency edge {eid} has unknown dependency_kind: {edge.get("dependency_kind")}')
        for kind_field, id_field in [('source_kind','source_id'), ('dependent_kind','dependent_id')]:
            kind = edge.get(kind_field)
            identifier = edge.get(id_field)
            known = route_like_kind_to_known.get(kind)
            if known is None:
                errors.append(f'authority dependency edge {eid} has unknown {kind_field}: {kind}')
            elif identifier not in known:
                errors.append(f'authority dependency edge {eid} references unknown {kind}: {identifier}')
        edge_key_set.add((edge.get('source_kind'), edge.get('source_id'), edge.get('dependent_kind'), edge.get('dependent_id'), edge.get('dependency_kind')))

    for row in route_rows:
        rid = row.get('route_id', '')
        for cid in row.get('public_record_carrier_ids', []):
            if ('carrier', cid, 'route', rid, 'record-carrier-requirement') not in edge_key_set:
                errors.append(f'authority dependency graph missing carrier→route edge for {cid} -> {rid}')
        for pid in row.get('acquisition_protocol_ids', []):
            if ('protocol', pid, 'route', rid, 'acquisition-protocol-requirement') not in edge_key_set:
                errors.append(f'authority dependency graph missing protocol→route edge for {pid} -> {rid}')
        for did in row.get('defeater_ids', []):
            if ('defeater', did, 'route', rid, 'defeater-attack') not in edge_key_set:
                errors.append(f'authority dependency graph missing defeater→route edge for {did} -> {rid}')
        for sid in row.get('severity_test_ids', []):
            if ('severity-test', sid, 'route', rid, 'severity-test-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing severity→route edge for {sid} -> {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if ('evidence-unit', uid, 'route', rid, 'evidence-unit-support') not in edge_key_set:
                errors.append(f'authority dependency graph missing evidence-unit→route edge for {uid} -> {rid}')
        for iid in row.get('independence_assumption_ids', []):
            if ('independence-assumption', iid, 'route', rid, 'independence-assumption-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing independence-assumption→route edge for {iid} -> {rid}')
        for caid in row.get('credit_allocation_ids', []):
            if ('credit-allocation', caid, 'route', rid, 'credit-allocation-rule') not in edge_key_set:
                errors.append(f'authority dependency graph missing credit-allocation→route edge for {caid} -> {rid}')
        for cid in row.get('contrast_class_ids', []):
            if ('contrast-class', cid, 'route', rid, 'contrast-class-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing contrast-class→route edge for {cid} -> {rid}')
        for luid in row.get('likelihood_update_ids', []):
            if ('likelihood-update', luid, 'route', rid, 'likelihood-update-rule') not in edge_key_set:
                errors.append(f'authority dependency graph missing likelihood-update→route edge for {luid} -> {rid}')
        for psid in row.get('prior_sensitivity_ids', []):
            if ('prior-sensitivity', psid, 'route', rid, 'prior-sensitivity-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing prior-sensitivity→route edge for {psid} -> {rid}')
        for mid in row.get('measurement_model_ids', []):
            if ('measurement-model', mid, 'route', rid, 'measurement-model-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing measurement-model→route edge for {mid} -> {rid}')
        for sid in row.get('systematic_uncertainty_ids', []):
            if ('systematic-uncertainty', sid, 'route', rid, 'systematic-uncertainty-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing systematic-uncertainty→route edge for {sid} -> {rid}')
        for calid in row.get('calibration_traceability_ids', []):
            if ('calibration-traceability', calid, 'route', rid, 'calibration-traceability-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing calibration-traceability→route edge for {calid} -> {rid}')
        for did in row.get('validity_domain_ids', []):
            if ('validity-domain', did, 'route', rid, 'validity-domain-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing validity-domain→route edge for {did} -> {rid}')
        for tid in row.get('transportability_ids', []):
            if ('transportability', tid, 'route', rid, 'transportability-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing transportability→route edge for {tid} -> {rid}')
        for xid in row.get('extrapolation_fence_ids', []):
            if ('extrapolation-fence', xid, 'route', rid, 'extrapolation-fence-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing extrapolation-fence→route edge for {xid} -> {rid}')
        for mid in row.get('causal_mechanism_ids', []):
            if ('causal-mechanism', mid, 'route', rid, 'causal-mechanism-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing causal-mechanism→route edge for {mid} -> {rid}')
        for iid in row.get('intervention_protocol_ids', []):
            if ('intervention-protocol', iid, 'route', rid, 'intervention-protocol-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing intervention-protocol→route edge for {iid} -> {rid}')
        for cfid in row.get('counterfactual_robustness_ids', []):
            if ('counterfactual-robustness', cfid, 'route', rid, 'counterfactual-robustness-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing counterfactual-robustness→route edge for {cfid} -> {rid}')
        for sid in row.get('selection_function_ids', []):
            if ('selection-function', sid, 'route', rid, 'selection-function-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing selection-function→route edge for {sid} -> {rid}')
        for mid in row.get('multiplicity_control_ids', []):
            if ('multiplicity-control', mid, 'route', rid, 'multiplicity-control-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing multiplicity-control→route edge for {mid} -> {rid}')
        for bid in row.get('reporting_bias_ids', []):
            if ('reporting-bias', bid, 'route', rid, 'reporting-bias-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing reporting-bias→route edge for {bid} -> {rid}')
        for capid in row.get('model_capacity_ids', []):
            if ('model-capacity', capid, 'route', rid, 'model-capacity-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing model-capacity→route edge for {capid} -> {rid}')
        for cpxid in row.get('complexity_penalty_ids', []):
            if ('complexity-penalty', cpxid, 'route', rid, 'complexity-penalty-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing complexity-penalty→route edge for {cpxid} -> {rid}')
        for genid in row.get('generalization_validation_ids', []):
            if ('generalization-validation', genid, 'route', rid, 'generalization-validation-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing generalization-validation→route edge for {genid} -> {rid}')
        for sid in row.get('semantic_term_ids', []):
            if ('semantic-term', sid, 'route', rid, 'semantic-term-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing semantic-term→route edge for {sid} -> {rid}')
        for oid in row.get('ontology_commitment_ids', []):
            if ('ontology-commitment', oid, 'route', rid, 'ontology-commitment-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing ontology-commitment→route edge for {oid} -> {rid}')
        for pid in row.get('claim_language_permission_ids', []):
            if ('claim-language-permission', pid, 'route', rid, 'claim-language-permission-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing claim-language-permission→route edge for {pid} -> {rid}')
        for sid in row.get('social_authority_ids', []):
            if ('social-authority', sid, 'route', rid, 'social-authority-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing social-authority→route edge for {sid} -> {rid}')
        for rv in row.get('review_replication_ids', []):
            if ('review-replication', rv, 'route', rid, 'review-replication-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing review-replication→route edge for {rv} -> {rid}')
        for cn in row.get('consensus_elicitation_ids', []):
            if ('consensus-elicitation', cn, 'route', rid, 'consensus-elicitation-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing consensus-elicitation→route edge for {cn} -> {rid}')
        for cid in row.get('computational_reproducibility_ids', []):
            if ('computational-reproducibility', cid, 'route', rid, 'computational-reproducibility-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing computational-reproducibility→route edge for {cid} -> {rid}')
        for nid in row.get('numerical_stability_ids', []):
            if ('numerical-stability', nid, 'route', rid, 'numerical-stability-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing numerical-stability→route edge for {nid} -> {rid}')
        for sid in row.get('software_supply_chain_ids', []):
            if ('software-supply-chain', sid, 'route', rid, 'software-supply-chain-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing software-supply-chain→route edge for {sid} -> {rid}')
        for crp in row.get('computational_reproducibility_ids', []):
            if ('computational-reproducibility', crp, 'route', rid, 'computational-reproducibility-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing computational-reproducibility→route edge for {crp} -> {rid}')
        for nst in row.get('numerical_stability_ids', []):
            if ('numerical-stability', nst, 'route', rid, 'numerical-stability-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing numerical-stability→route edge for {nst} -> {rid}')
        for ssc in row.get('software_supply_chain_ids', []):
            if ('software-supply-chain', ssc, 'route', rid, 'software-supply-chain-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing software-supply-chain→route edge for {ssc} -> {rid}')

    if f"- Defeaters: `{len(defeater_rows)}`" not in defeat_summary_text:
        errors.append('defeat/rollback generated summary defeater count drifted; run make index')
    if f"- Rollback rules: `{len(rollback_rows)}`" not in defeat_summary_text:
        errors.append('defeat/rollback generated summary rollback count drifted; run make index')
    if f"- Severity tests: `{len(severity_rows)}`" not in defeat_summary_text:
        errors.append('defeat/rollback generated summary severity count drifted; run make index')
    if f"- Dependency edges: `{len(edge_rows)}`" not in defeat_summary_text:
        errors.append('defeat/rollback generated summary dependency-edge count drifted; run make index')



    # Formal proof obligation / assumption discharge / formalization coverage checks added in rev0275.
    proof_obligation_ledger = json.loads((root / 'PROOF-OBLIGATION-LEDGER.json').read_text())
    assumption_discharge_ledger = json.loads((root / 'ASSUMPTION-DISCHARGE-LEDGER.json').read_text())
    formalization_coverage_ledger = json.loads((root / 'FORMALIZATION-COVERAGE-LEDGER.json').read_text())
    formal_proof_summary_text = (root / 'docs/30-program/formal-proof-summary.generated.md').read_text()
    pob_rows = proof_obligation_ledger.get('proof_obligation_rows', [])
    asd_rows = assumption_discharge_ledger.get('assumption_discharge_rows', [])
    fcv_rows = formalization_coverage_ledger.get('formalization_rows', [])
    pob_ids = [item.get('proof_obligation_id', '') for item in pob_rows]
    asd_ids = [item.get('assumption_discharge_id', '') for item in asd_rows]
    fcv_ids = [item.get('formalization_coverage_id', '') for item in fcv_rows]
    if proof_obligation_ledger.get('revision') != manifest['revision']:
        errors.append('PROOF-OBLIGATION-LEDGER revision drifted from manifest')
    if assumption_discharge_ledger.get('revision') != manifest['revision']:
        errors.append('ASSUMPTION-DISCHARGE-LEDGER revision drifted from manifest')
    if formalization_coverage_ledger.get('revision') != manifest['revision']:
        errors.append('FORMALIZATION-COVERAGE-LEDGER revision drifted from manifest')
    if len(pob_ids) != len(set(pob_ids)):
        errors.append('PROOF-OBLIGATION-LEDGER contains duplicate proof_obligation_id values')
    if len(asd_ids) != len(set(asd_ids)):
        errors.append('ASSUMPTION-DISCHARGE-LEDGER contains duplicate assumption_discharge_id values')
    if len(fcv_ids) != len(set(fcv_ids)):
        errors.append('FORMALIZATION-COVERAGE-LEDGER contains duplicate formalization_coverage_id values')
    known_pob_ids = set(pob_ids)
    known_asd_ids = set(asd_ids)
    known_fcv_ids = set(fcv_ids)
    allowed_pob_classes = set(witness_vocab.get('proof_obligation_class_labels', []))
    allowed_asd_classes = set(witness_vocab.get('assumption_discharge_class_labels', []))
    allowed_fcv_classes = set(witness_vocab.get('formalization_coverage_class_labels', []))
    pob_required = ['proof_obligation_id','route_ids','evidence_unit_ids','carrier_ids','protocol_ids','proof_obligation_class','statement_or_target','formal_system_or_notation','assumptions_required','proof_object_or_derivation_trace','proof_checker_or_reviewer','gap_or_informal_step_policy','maximum_authority_effect','rollback_rule_ids','source_refs']
    asd_required = ['assumption_discharge_id','route_ids','evidence_unit_ids','proof_obligation_ids','assumption_class','assumption_inventory','discharge_status','dependency_scope','hidden_assumption_search','maximum_authority_effect','rollback_rule_ids','source_refs']
    fcv_required = ['formalization_coverage_id','route_ids','evidence_unit_ids','proof_obligation_ids','assumption_discharge_ids','coverage_class','formalized_fragment','informal_remainder','kernel_or_checker_trust_base','library_or_axiom_boundary','portability_or_translation_limit','maximum_authority_effect','rollback_rule_ids','source_refs']
    for row in pob_rows:
        pid = row.get('proof_obligation_id','')
        missing = [field for field in pob_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'proof-obligation row {pid or "<missing>"} missing required fields: {missing}')
        if row.get('proof_obligation_class') not in allowed_pob_classes: errors.append(f'proof-obligation row {pid} has unknown proof_obligation_class: {row.get("proof_obligation_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'proof-obligation row {pid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'proof-obligation row {pid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'proof-obligation row {pid} references unknown evidence unit: {uid}')
        for cid in row.get('carrier_ids', []):
            if cid not in known_carrier_ids: errors.append(f'proof-obligation row {pid} references unknown carrier: {cid}')
        for ap in row.get('protocol_ids', []):
            if ap not in known_protocol_ids: errors.append(f'proof-obligation row {pid} references unknown protocol: {ap}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'proof-obligation row {pid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'proof-obligation row {pid} references unknown REF id: {ref}')
    for row in asd_rows:
        aid = row.get('assumption_discharge_id','')
        missing = [field for field in asd_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'assumption-discharge row {aid or "<missing>"} missing required fields: {missing}')
        if row.get('assumption_class') not in allowed_asd_classes: errors.append(f'assumption-discharge row {aid} has unknown assumption_class: {row.get("assumption_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'assumption-discharge row {aid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'assumption-discharge row {aid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'assumption-discharge row {aid} references unknown evidence unit: {uid}')
        for pid in row.get('proof_obligation_ids', []):
            if pid not in known_pob_ids: errors.append(f'assumption-discharge row {aid} references unknown proof-obligation row: {pid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'assumption-discharge row {aid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'assumption-discharge row {aid} references unknown REF id: {ref}')
    for row in fcv_rows:
        fid = row.get('formalization_coverage_id','')
        missing = [field for field in fcv_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'formalization-coverage row {fid or "<missing>"} missing required fields: {missing}')
        if row.get('coverage_class') not in allowed_fcv_classes: errors.append(f'formalization-coverage row {fid} has unknown coverage_class: {row.get("coverage_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'formalization-coverage row {fid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'formalization-coverage row {fid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'formalization-coverage row {fid} references unknown evidence unit: {uid}')
        for pid in row.get('proof_obligation_ids', []):
            if pid not in known_pob_ids: errors.append(f'formalization-coverage row {fid} references unknown proof-obligation row: {pid}')
        for aid in row.get('assumption_discharge_ids', []):
            if aid not in known_asd_ids: errors.append(f'formalization-coverage row {fid} references unknown assumption-discharge row: {aid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'formalization-coverage row {fid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'formalization-coverage row {fid} references unknown REF id: {ref}')
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('proof_obligation_ids') or not row.get('assumption_discharge_ids') or not row.get('formalization_coverage_ids'):
            errors.append(f'route row {rid} missing formal proof / assumption / formalization handles')
        for pid in row.get('proof_obligation_ids', []):
            if pid not in known_pob_ids: errors.append(f'route row {rid} references unknown proof-obligation row: {pid}')
        for aid in row.get('assumption_discharge_ids', []):
            if aid not in known_asd_ids: errors.append(f'route row {rid} references unknown assumption-discharge row: {aid}')
        for fid in row.get('formalization_coverage_ids', []):
            if fid not in known_fcv_ids: errors.append(f'route row {rid} references unknown formalization-coverage row: {fid}')
    for binding in binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['PROOF-OBLIGATION-LEDGER.json','ASSUMPTION-DISCHARGE-LEDGER.json','FORMALIZATION-COVERAGE-LEDGER.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing formal-proof controlling ledger: {rel}')
        for pid in binding.get('proof_obligation_ids', []):
            if pid not in known_pob_ids: errors.append(f'claim-route binding {bid} references unknown proof-obligation row: {pid}')
        for aid in binding.get('assumption_discharge_ids', []):
            if aid not in known_asd_ids: errors.append(f'claim-route binding {bid} references unknown assumption-discharge row: {aid}')
        for fid in binding.get('formalization_coverage_ids', []):
            if fid not in known_fcv_ids: errors.append(f'claim-route binding {bid} references unknown formalization-coverage row: {fid}')
    if f"- Proof-obligation rows: `{len(pob_rows)}`" not in formal_proof_summary_text:
        errors.append('formal-proof generated summary proof-obligation count drifted; run make index')
    if f"- Assumption-discharge rows: `{len(asd_rows)}`" not in formal_proof_summary_text:
        errors.append('formal-proof generated summary assumption-discharge count drifted; run make index')
    if f"- Formalization-coverage rows: `{len(fcv_rows)}`" not in formal_proof_summary_text:
        errors.append('formal-proof generated summary formalization-coverage count drifted; run make index')
    for row in route_rows:
        rid = row.get('route_id','')
        for pid in row.get('proof_obligation_ids', []):
            if ('proof-obligation', pid, 'route', rid, 'proof-obligation-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing proof-obligation→route edge for {pid} -> {rid}')
        for aid in row.get('assumption_discharge_ids', []):
            if ('assumption-discharge', aid, 'route', rid, 'assumption-discharge-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing assumption-discharge→route edge for {aid} -> {rid}')
        for fid in row.get('formalization_coverage_ids', []):
            if ('formalization-coverage', fid, 'route', rid, 'formalization-coverage-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing formalization-coverage→route edge for {fid} -> {rid}')
    if 'OQ-0072' not in registered_question_ids:
        errors.append('rev0275 formal proof-obligation / assumption-discharge / formalization-coverage burden requires registered OQ-0072')


    # Idealization / approximation-error / limit-interchange checks added in rev0276.
    idealization_ledger = json.loads((root / 'IDEALIZATION-LEDGER.json').read_text())
    approximation_error_ledger = json.loads((root / 'APPROXIMATION-ERROR-LEDGER.json').read_text())
    limit_interchange_ledger = json.loads((root / 'LIMIT-INTERCHANGE-LEDGER.json').read_text())
    idealization_summary_text = (root / 'docs/30-program/idealization-limit-summary.generated.md').read_text()
    idl_rows = idealization_ledger.get('idealization_rows', [])
    aer_rows = approximation_error_ledger.get('approximation_rows', [])
    lim_rows = limit_interchange_ledger.get('limit_rows', [])
    idl_ids = [item.get('idealization_id', '') for item in idl_rows]
    aer_ids = [item.get('approximation_error_id', '') for item in aer_rows]
    lim_ids = [item.get('limit_interchange_id', '') for item in lim_rows]
    if idealization_ledger.get('revision') != manifest['revision']:
        errors.append('IDEALIZATION-LEDGER revision drifted from manifest')
    if approximation_error_ledger.get('revision') != manifest['revision']:
        errors.append('APPROXIMATION-ERROR-LEDGER revision drifted from manifest')
    if limit_interchange_ledger.get('revision') != manifest['revision']:
        errors.append('LIMIT-INTERCHANGE-LEDGER revision drifted from manifest')
    if len(idl_ids) != len(set(idl_ids)): errors.append('IDEALIZATION-LEDGER contains duplicate idealization_id values')
    if len(aer_ids) != len(set(aer_ids)): errors.append('APPROXIMATION-ERROR-LEDGER contains duplicate approximation_error_id values')
    if len(lim_ids) != len(set(lim_ids)): errors.append('LIMIT-INTERCHANGE-LEDGER contains duplicate limit_interchange_id values')
    known_idl_ids = set(idl_ids); known_aer_ids = set(aer_ids); known_lim_ids = set(lim_ids)
    allowed_idl_classes = set(witness_vocab.get('idealization_class_labels', []))
    allowed_aer_classes = set(witness_vocab.get('approximation_error_class_labels', []))
    allowed_lim_classes = set(witness_vocab.get('limit_interchange_class_labels', []))
    idl_required = ['idealization_id','route_ids','evidence_unit_ids','idealization_class','idealized_target','distortion_or_omission','deidealization_requirement','validity_link','maximum_authority_effect','rollback_rule_ids','source_refs']
    aer_required = ['approximation_error_id','route_ids','evidence_unit_ids','idealization_ids','approximation_error_class','error_budget_object','bound_or_estimator','error_propagation_rule','residual_or_uncontrolled_error','maximum_authority_effect','rollback_rule_ids','source_refs']
    lim_required = ['limit_interchange_id','route_ids','evidence_unit_ids','idealization_ids','approximation_error_ids','limit_interchange_class','limit_sequence','commutation_or_singularity_test','finite_regime_recovery','forbidden_inference','maximum_authority_effect','rollback_rule_ids','source_refs']
    for row in idl_rows:
        iid = row.get('idealization_id','')
        missing = [field for field in idl_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'idealization row {iid or "<missing>"} missing required fields: {missing}')
        if row.get('idealization_class') not in allowed_idl_classes: errors.append(f'idealization row {iid} has unknown idealization_class: {row.get("idealization_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'idealization row {iid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'idealization row {iid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'idealization row {iid} references unknown evidence unit: {uid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'idealization row {iid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'idealization row {iid} references unknown REF id: {ref}')
    for row in aer_rows:
        aid = row.get('approximation_error_id','')
        missing = [field for field in aer_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'approximation-error row {aid or "<missing>"} missing required fields: {missing}')
        if row.get('approximation_error_class') not in allowed_aer_classes: errors.append(f'approximation-error row {aid} has unknown approximation_error_class: {row.get("approximation_error_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'approximation-error row {aid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'approximation-error row {aid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'approximation-error row {aid} references unknown evidence unit: {uid}')
        for iid in row.get('idealization_ids', []):
            if iid not in known_idl_ids: errors.append(f'approximation-error row {aid} references unknown idealization row: {iid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'approximation-error row {aid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'approximation-error row {aid} references unknown REF id: {ref}')
    for row in lim_rows:
        lid = row.get('limit_interchange_id','')
        missing = [field for field in lim_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'limit-interchange row {lid or "<missing>"} missing required fields: {missing}')
        if row.get('limit_interchange_class') not in allowed_lim_classes: errors.append(f'limit-interchange row {lid} has unknown limit_interchange_class: {row.get("limit_interchange_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'limit-interchange row {lid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'limit-interchange row {lid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'limit-interchange row {lid} references unknown evidence unit: {uid}')
        for iid in row.get('idealization_ids', []):
            if iid not in known_idl_ids: errors.append(f'limit-interchange row {lid} references unknown idealization row: {iid}')
        for aid in row.get('approximation_error_ids', []):
            if aid not in known_aer_ids: errors.append(f'limit-interchange row {lid} references unknown approximation-error row: {aid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'limit-interchange row {lid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'limit-interchange row {lid} references unknown REF id: {ref}')
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('idealization_ids') or not row.get('approximation_error_ids') or not row.get('limit_interchange_ids'):
            errors.append(f'route row {rid} missing idealization / approximation-error / limit-interchange handles')
        for iid in row.get('idealization_ids', []):
            if iid not in known_idl_ids: errors.append(f'route row {rid} references unknown idealization row: {iid}')
        for aid in row.get('approximation_error_ids', []):
            if aid not in known_aer_ids: errors.append(f'route row {rid} references unknown approximation-error row: {aid}')
        for lid in row.get('limit_interchange_ids', []):
            if lid not in known_lim_ids: errors.append(f'route row {rid} references unknown limit-interchange row: {lid}')
    for binding in binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['IDEALIZATION-LEDGER.json','APPROXIMATION-ERROR-LEDGER.json','LIMIT-INTERCHANGE-LEDGER.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing idealization/limit controlling ledger: {rel}')
        for iid in binding.get('idealization_ids', []):
            if iid not in known_idl_ids: errors.append(f'claim-route binding {bid} references unknown idealization row: {iid}')
        for aid in binding.get('approximation_error_ids', []):
            if aid not in known_aer_ids: errors.append(f'claim-route binding {bid} references unknown approximation-error row: {aid}')
        for lid in binding.get('limit_interchange_ids', []):
            if lid not in known_lim_ids: errors.append(f'claim-route binding {bid} references unknown limit-interchange row: {lid}')
    if f"- Idealization rows: `{len(idl_rows)}`" not in idealization_summary_text:
        errors.append('idealization generated summary idealization count drifted; run make index')
    if f"- Approximation-error rows: `{len(aer_rows)}`" not in idealization_summary_text:
        errors.append('idealization generated summary approximation-error count drifted; run make index')
    if f"- Limit-interchange rows: `{len(lim_rows)}`" not in idealization_summary_text:
        errors.append('idealization generated summary limit-interchange count drifted; run make index')
    for row in route_rows:
        rid = row.get('route_id','')
        for iid in row.get('idealization_ids', []):
            if ('idealization', iid, 'route', rid, 'idealization-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing idealization→route edge for {iid} -> {rid}')
        for aid in row.get('approximation_error_ids', []):
            if ('approximation-error', aid, 'route', rid, 'approximation-error-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing approximation-error→route edge for {aid} -> {rid}')
        for lid in row.get('limit_interchange_ids', []):
            if ('limit-interchange', lid, 'route', rid, 'limit-interchange-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing limit-interchange→route edge for {lid} -> {rid}')
    if 'OQ-0073' not in registered_question_ids:
        errors.append('rev0276 idealization / approximation-error / limit-interchange burden requires registered OQ-0073')



    # rev0277 boundary-condition / initial-data / sector-selection checks.
    boundary_condition_ledger = json.loads((root / 'BOUNDARY-CONDITION-LEDGER.json').read_text())
    initial_data_ledger = json.loads((root / 'INITIAL-DATA-LEDGER.json').read_text())
    sector_selection_ledger = json.loads((root / 'SECTOR-SELECTION-LEDGER.json').read_text())
    boundary_sector_summary_text = (root / 'docs/30-program/boundary-sector-summary.generated.md').read_text()
    bnd_rows = boundary_condition_ledger.get('boundary_rows', [])
    ini_rows = initial_data_ledger.get('initial_data_rows', [])
    sec_rows = sector_selection_ledger.get('sector_rows', [])
    bnd_ids = [item.get('boundary_condition_id', '') for item in bnd_rows]
    ini_ids = [item.get('initial_data_id', '') for item in ini_rows]
    sec_ids = [item.get('sector_selection_id', '') for item in sec_rows]
    if len(bnd_ids) != len(set(bnd_ids)): errors.append('BOUNDARY-CONDITION-LEDGER contains duplicate boundary_condition_id values')
    if len(ini_ids) != len(set(ini_ids)): errors.append('INITIAL-DATA-LEDGER contains duplicate initial_data_id values')
    if len(sec_ids) != len(set(sec_ids)): errors.append('SECTOR-SELECTION-LEDGER contains duplicate sector_selection_id values')
    known_bnd_ids = set(bnd_ids); known_ini_ids = set(ini_ids); known_sec_ids = set(sec_ids)
    allowed_bnd_classes = set(witness_vocab.get('boundary_condition_class_labels', []))
    allowed_ini_classes = set(witness_vocab.get('initial_data_class_labels', []))
    allowed_sec_classes = set(witness_vocab.get('sector_selection_class_labels', []))
    bnd_required = ['boundary_condition_id','route_ids','evidence_unit_ids','boundary_class','boundary_object','fixed_or_dynamic_status','boundary_sensitivity_test','forbidden_inference','maximum_authority_effect','rollback_rule_ids','source_refs']
    ini_required = ['initial_data_id','route_ids','evidence_unit_ids','boundary_condition_ids','initial_data_class','initial_data_object','constraint_or_prior_rule','sensitivity_or_robustness_test','residual_initial_condition_debt','maximum_authority_effect','rollback_rule_ids','source_refs']
    sec_required = ['sector_selection_id','route_ids','evidence_unit_ids','boundary_condition_ids','initial_data_ids','sector_selection_class','selected_sector_or_branch','selection_rule','rival_sectors_or_branches','forbidden_inference','maximum_authority_effect','rollback_rule_ids','source_refs']
    for row in bnd_rows:
        bid = row.get('boundary_condition_id','')
        missing = [field for field in bnd_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'boundary-condition row {bid or "<missing>"} missing required fields: {missing}')
        if row.get('boundary_class') not in allowed_bnd_classes: errors.append(f'boundary-condition row {bid} has unknown boundary_class: {row.get("boundary_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'boundary-condition row {bid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'boundary-condition row {bid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'boundary-condition row {bid} references unknown evidence unit: {uid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'boundary-condition row {bid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'boundary-condition row {bid} references unknown REF id: {ref}')
    for row in ini_rows:
        iid = row.get('initial_data_id','')
        missing = [field for field in ini_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'initial-data row {iid or "<missing>"} missing required fields: {missing}')
        if row.get('initial_data_class') not in allowed_ini_classes: errors.append(f'initial-data row {iid} has unknown initial_data_class: {row.get("initial_data_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'initial-data row {iid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'initial-data row {iid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'initial-data row {iid} references unknown evidence unit: {uid}')
        for bid in row.get('boundary_condition_ids', []):
            if bid not in known_bnd_ids: errors.append(f'initial-data row {iid} references unknown boundary-condition row: {bid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'initial-data row {iid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'initial-data row {iid} references unknown REF id: {ref}')
    for row in sec_rows:
        sid = row.get('sector_selection_id','')
        missing = [field for field in sec_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'sector-selection row {sid or "<missing>"} missing required fields: {missing}')
        if row.get('sector_selection_class') not in allowed_sec_classes: errors.append(f'sector-selection row {sid} has unknown sector_selection_class: {row.get("sector_selection_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'sector-selection row {sid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'sector-selection row {sid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'sector-selection row {sid} references unknown evidence unit: {uid}')
        for bid in row.get('boundary_condition_ids', []):
            if bid not in known_bnd_ids: errors.append(f'sector-selection row {sid} references unknown boundary-condition row: {bid}')
        for iid in row.get('initial_data_ids', []):
            if iid not in known_ini_ids: errors.append(f'sector-selection row {sid} references unknown initial-data row: {iid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'sector-selection row {sid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'sector-selection row {sid} references unknown REF id: {ref}')
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('boundary_condition_ids') or not row.get('initial_data_ids') or not row.get('sector_selection_ids'):
            errors.append(f'route row {rid} missing boundary-condition / initial-data / sector-selection handles')
        for bid in row.get('boundary_condition_ids', []):
            if bid not in known_bnd_ids: errors.append(f'route row {rid} references unknown boundary-condition row: {bid}')
        for iid in row.get('initial_data_ids', []):
            if iid not in known_ini_ids: errors.append(f'route row {rid} references unknown initial-data row: {iid}')
        for sid in row.get('sector_selection_ids', []):
            if sid not in known_sec_ids: errors.append(f'route row {rid} references unknown sector-selection row: {sid}')
    for binding in binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['BOUNDARY-CONDITION-LEDGER.json','INITIAL-DATA-LEDGER.json','SECTOR-SELECTION-LEDGER.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing boundary/sector controlling ledger: {rel}')
        for bnd in binding.get('boundary_condition_ids', []):
            if bnd not in known_bnd_ids: errors.append(f'claim-route binding {bid} references unknown boundary-condition row: {bnd}')
        for ini in binding.get('initial_data_ids', []):
            if ini not in known_ini_ids: errors.append(f'claim-route binding {bid} references unknown initial-data row: {ini}')
        for sec in binding.get('sector_selection_ids', []):
            if sec not in known_sec_ids: errors.append(f'claim-route binding {bid} references unknown sector-selection row: {sec}')
    if f"- Boundary-condition rows: `{len(bnd_rows)}`" not in boundary_sector_summary_text:
        errors.append('boundary-sector generated summary boundary count drifted; run make index')
    if f"- Initial-data rows: `{len(ini_rows)}`" not in boundary_sector_summary_text:
        errors.append('boundary-sector generated summary initial-data count drifted; run make index')
    if f"- Sector-selection rows: `{len(sec_rows)}`" not in boundary_sector_summary_text:
        errors.append('boundary-sector generated summary sector count drifted; run make index')
    for row in route_rows:
        rid = row.get('route_id','')
        for bnd in row.get('boundary_condition_ids', []):
            if ('boundary-condition', bnd, 'route', rid, 'boundary-condition-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing boundary-condition→route edge for {bnd} -> {rid}')
        for ini in row.get('initial_data_ids', []):
            if ('initial-data', ini, 'route', rid, 'initial-data-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing initial-data→route edge for {ini} -> {rid}')
        for sec in row.get('sector_selection_ids', []):
            if ('sector-selection', sec, 'route', rid, 'sector-selection-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing sector-selection→route edge for {sec} -> {rid}')
    if 'OQ-0074' not in registered_question_ids:
        errors.append('rev0277 boundary / initial-data / sector-selection burden requires registered OQ-0074')


    # rev0278 gauge-symmetry / constraint-closure / observable-quotient checks.
    gauge_symmetry_ledger = json.loads((root / 'GAUGE-SYMMETRY-LEDGER.json').read_text())
    constraint_closure_ledger = json.loads((root / 'CONSTRAINT-CLOSURE-LEDGER.json').read_text())
    observable_quotient_ledger = json.loads((root / 'OBSERVABLE-QUOTIENT-LEDGER.json').read_text())
    gauge_constraint_summary_text = (root / 'docs/30-program/gauge-constraint-summary.generated.md').read_text()
    gsy_rows = gauge_symmetry_ledger.get('gauge_rows', [])
    ccl_rows = constraint_closure_ledger.get('constraint_rows', [])
    obsq_rows = observable_quotient_ledger.get('observable_rows', [])
    gsy_ids = [item.get('gauge_symmetry_id', '') for item in gsy_rows]
    ccl_ids = [item.get('constraint_closure_id', '') for item in ccl_rows]
    obsq_ids = [item.get('observable_quotient_id', '') for item in obsq_rows]
    if len(gsy_ids) != len(set(gsy_ids)): errors.append('GAUGE-SYMMETRY-LEDGER contains duplicate gauge_symmetry_id values')
    if len(ccl_ids) != len(set(ccl_ids)): errors.append('CONSTRAINT-CLOSURE-LEDGER contains duplicate constraint_closure_id values')
    if len(obsq_ids) != len(set(obsq_ids)): errors.append('OBSERVABLE-QUOTIENT-LEDGER contains duplicate observable_quotient_id values')
    known_gsy_ids = set(gsy_ids); known_ccl_ids = set(ccl_ids); known_obsq_ids = set(obsq_ids)
    allowed_gsy_classes = set(witness_vocab.get('gauge_symmetry_class_labels', []))
    allowed_ccl_classes = set(witness_vocab.get('constraint_closure_class_labels', []))
    allowed_obsq_classes = set(witness_vocab.get('observable_quotient_class_labels', []))
    gsy_required = ['gauge_symmetry_id','route_ids','evidence_unit_ids','gauge_symmetry_class','gauge_or_redundancy_object','gauge_fixing_or_reduction_rule','residual_gauge_or_gribov_risk','invariant_quantity_required','forbidden_inference','maximum_authority_effect','rollback_rule_ids','source_refs']
    ccl_required = ['constraint_closure_id','route_ids','evidence_unit_ids','gauge_symmetry_ids','constraint_closure_class','constraint_set_or_algebra','closure_status','anomaly_or_second_class_risk','quantization_order_or_reduction_rule','maximum_authority_effect','rollback_rule_ids','source_refs']
    obsq_required = ['observable_quotient_id','route_ids','evidence_unit_ids','gauge_symmetry_ids','constraint_closure_ids','observable_quotient_class','observable_or_record_object','quotient_or_cohomology_rule','representative_dependence_test','residual_noninvariant_debt','forbidden_inference','maximum_authority_effect','rollback_rule_ids','source_refs']
    for row in gsy_rows:
        gid = row.get('gauge_symmetry_id','')
        missing = [field for field in gsy_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'gauge-symmetry row {gid or "<missing>"} missing required fields: {missing}')
        if row.get('gauge_symmetry_class') not in allowed_gsy_classes: errors.append(f'gauge-symmetry row {gid} has unknown gauge_symmetry_class: {row.get("gauge_symmetry_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'gauge-symmetry row {gid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'gauge-symmetry row {gid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'gauge-symmetry row {gid} references unknown evidence unit: {uid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'gauge-symmetry row {gid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'gauge-symmetry row {gid} references unknown REF id: {ref}')
    for row in ccl_rows:
        cid = row.get('constraint_closure_id','')
        missing = [field for field in ccl_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'constraint-closure row {cid or "<missing>"} missing required fields: {missing}')
        if row.get('constraint_closure_class') not in allowed_ccl_classes: errors.append(f'constraint-closure row {cid} has unknown constraint_closure_class: {row.get("constraint_closure_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'constraint-closure row {cid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'constraint-closure row {cid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'constraint-closure row {cid} references unknown evidence unit: {uid}')
        for gid in row.get('gauge_symmetry_ids', []):
            if gid not in known_gsy_ids: errors.append(f'constraint-closure row {cid} references unknown gauge-symmetry row: {gid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'constraint-closure row {cid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'constraint-closure row {cid} references unknown REF id: {ref}')
    for row in obsq_rows:
        oid = row.get('observable_quotient_id','')
        missing = [field for field in obsq_required if field not in row or row.get(field) in ('', [], None)]
        if missing: errors.append(f'observable-quotient row {oid or "<missing>"} missing required fields: {missing}')
        if row.get('observable_quotient_class') not in allowed_obsq_classes: errors.append(f'observable-quotient row {oid} has unknown observable_quotient_class: {row.get("observable_quotient_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'observable-quotient row {oid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'observable-quotient row {oid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'observable-quotient row {oid} references unknown evidence unit: {uid}')
        for gid in row.get('gauge_symmetry_ids', []):
            if gid not in known_gsy_ids: errors.append(f'observable-quotient row {oid} references unknown gauge-symmetry row: {gid}')
        for cid in row.get('constraint_closure_ids', []):
            if cid not in known_ccl_ids: errors.append(f'observable-quotient row {oid} references unknown constraint-closure row: {cid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'observable-quotient row {oid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'observable-quotient row {oid} references unknown REF id: {ref}')
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('gauge_symmetry_ids') or not row.get('constraint_closure_ids') or not row.get('observable_quotient_ids'):
            errors.append(f'route row {rid} missing gauge-symmetry / constraint-closure / observable-quotient handles')
        for gid in row.get('gauge_symmetry_ids', []):
            if gid not in known_gsy_ids: errors.append(f'route row {rid} references unknown gauge-symmetry row: {gid}')
        for cid in row.get('constraint_closure_ids', []):
            if cid not in known_ccl_ids: errors.append(f'route row {rid} references unknown constraint-closure row: {cid}')
        for oid in row.get('observable_quotient_ids', []):
            if oid not in known_obsq_ids: errors.append(f'route row {rid} references unknown observable-quotient row: {oid}')
    for binding in binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['GAUGE-SYMMETRY-LEDGER.json','CONSTRAINT-CLOSURE-LEDGER.json','OBSERVABLE-QUOTIENT-LEDGER.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing gauge/constraint/observable controlling ledger: {rel}')
        for gid in binding.get('gauge_symmetry_ids', []):
            if gid not in known_gsy_ids: errors.append(f'claim-route binding {bid} references unknown gauge-symmetry row: {gid}')
        for cid in binding.get('constraint_closure_ids', []):
            if cid not in known_ccl_ids: errors.append(f'claim-route binding {bid} references unknown constraint-closure row: {cid}')
        for oid in binding.get('observable_quotient_ids', []):
            if oid not in known_obsq_ids: errors.append(f'claim-route binding {bid} references unknown observable-quotient row: {oid}')
    if f"- Gauge-symmetry rows: `{len(gsy_rows)}`" not in gauge_constraint_summary_text:
        errors.append('gauge-constraint generated summary gauge count drifted; run make index')
    if f"- Constraint-closure rows: `{len(ccl_rows)}`" not in gauge_constraint_summary_text:
        errors.append('gauge-constraint generated summary constraint count drifted; run make index')
    if f"- Observable-quotient rows: `{len(obsq_rows)}`" not in gauge_constraint_summary_text:
        errors.append('gauge-constraint generated summary observable count drifted; run make index')
    for row in route_rows:
        rid = row.get('route_id','')
        for gid in row.get('gauge_symmetry_ids', []):
            if ('gauge-symmetry', gid, 'route', rid, 'gauge-symmetry-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing gauge-symmetry→route edge for {gid} -> {rid}')
        for cid in row.get('constraint_closure_ids', []):
            if ('constraint-closure', cid, 'route', rid, 'constraint-closure-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing constraint-closure→route edge for {cid} -> {rid}')
        for oid in row.get('observable_quotient_ids', []):
            if ('observable-quotient', oid, 'route', rid, 'observable-quotient-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing observable-quotient→route edge for {oid} -> {rid}')
    if 'OQ-0075' not in registered_question_ids:
        errors.append('rev0278 gauge / constraint / observable-quotient burden requires registered OQ-0075')


    # rev0280 composition / interface / global-consistency checks.
    comp_law_ledger = json.loads((root / 'COMPOSITION-LAW-LEDGER.json').read_text())
    iface_ledger = json.loads((root / 'INTERFACE-COMPATIBILITY-LEDGER.json').read_text())
    glob_ledger = json.loads((root / 'GLOBAL-CONSISTENCY-LEDGER.json').read_text())
    comp_summary_text = (root / 'docs/30-program/composition-consistency-summary.generated.md').read_text()
    cmp_rows = comp_law_ledger.get('composition_rows', [])
    ifc_rows = iface_ledger.get('interface_rows', [])
    glc_rows = glob_ledger.get('global_rows', [])
    if f"- Composition-law rows: `{len(cmp_rows)}`" not in comp_summary_text:
        errors.append('composition/global generated summary composition count drifted; run make index')
    if f"- Interface-compatibility rows: `{len(ifc_rows)}`" not in comp_summary_text:
        errors.append('composition/global generated summary interface count drifted; run make index')
    if f"- Global-consistency rows: `{len(glc_rows)}`" not in comp_summary_text:
        errors.append('composition/global generated summary global count drifted; run make index')
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('composition_law_ids') or not row.get('interface_compatibility_ids') or not row.get('global_consistency_ids'):
            errors.append(f'route row {rid} missing composition-law / interface-compatibility / global-consistency handles')
        for cid in row.get('composition_law_ids', []):
            if cid not in known_cmp_ids: errors.append(f'route row {rid} references unknown composition-law row: {cid}')
            if ('composition-law', cid, 'route', rid, 'composition-law-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing composition-law→route edge for {cid} -> {rid}')
        for iid in row.get('interface_compatibility_ids', []):
            if iid not in known_ifc_ids: errors.append(f'route row {rid} references unknown interface-compatibility row: {iid}')
            if ('interface-compatibility', iid, 'route', rid, 'interface-compatibility-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing interface-compatibility→route edge for {iid} -> {rid}')
        for gid in row.get('global_consistency_ids', []):
            if gid not in known_glc_ids: errors.append(f'route row {rid} references unknown global-consistency row: {gid}')
            if ('global-consistency', gid, 'route', rid, 'global-consistency-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing global-consistency→route edge for {gid} -> {rid}')
    for binding in binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['COMPOSITION-LAW-LEDGER.json','INTERFACE-COMPATIBILITY-LEDGER.json','GLOBAL-CONSISTENCY-LEDGER.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing composition/global controlling ledger: {rel}')
    if 'OQ-0077' not in registered_question_ids:
        errors.append('rev0280 composition-law / interface-compatibility / global-consistency burden requires registered OQ-0077')



    # rev0281 unitarity / causality / stability checks.
    unit_ledger = json.loads((root / 'UNITARITY-CHECK-LEDGER.json').read_text())
    caus_ledger = json.loads((root / 'CAUSALITY-CONE-LEDGER.json').read_text())
    stab_ledger = json.loads((root / 'STABILITY-POSITIVITY-LEDGER.json').read_text())
    viability_summary_text = (root / 'docs/30-program/unitarity-causality-stability-summary.generated.md').read_text()
    unit_rows = unit_ledger.get('unitarity_rows', [])
    caus_rows = caus_ledger.get('causality_rows', [])
    stab_rows = stab_ledger.get('stability_rows', [])
    if f"- Unitarity-check rows: `{len(unit_rows)}`" not in viability_summary_text:
        errors.append('unitarity/causality/stability generated summary unitarity count drifted; run make index')
    if f"- Causality-cone rows: `{len(caus_rows)}`" not in viability_summary_text:
        errors.append('unitarity/causality/stability generated summary causality count drifted; run make index')
    if f"- Stability/positivity rows: `{len(stab_rows)}`" not in viability_summary_text:
        errors.append('unitarity/causality/stability generated summary stability count drifted; run make index')
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('unitarity_check_ids') or not row.get('causality_cone_ids') or not row.get('stability_positivity_ids'):
            errors.append(f'route row {rid} missing unitarity / causality / stability handles')
        for uid in row.get('unitarity_check_ids', []):
            if uid not in known_uni_ids: errors.append(f'route row {rid} references unknown unitarity-check row: {uid}')
            if ('unitarity-check', uid, 'route', rid, 'unitarity-check-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing unitarity-check→route edge for {uid} -> {rid}')
        for cid in row.get('causality_cone_ids', []):
            if cid not in known_cau_ids: errors.append(f'route row {rid} references unknown causality-cone row: {cid}')
            if ('causality-cone', cid, 'route', rid, 'causality-cone-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing causality-cone→route edge for {cid} -> {rid}')
        for sid in row.get('stability_positivity_ids', []):
            if sid not in known_stb_ids: errors.append(f'route row {rid} references unknown stability-positivity row: {sid}')
            if ('stability-positivity', sid, 'route', rid, 'stability-positivity-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing stability-positivity→route edge for {sid} -> {rid}')
    for binding in binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['UNITARITY-CHECK-LEDGER.json','CAUSALITY-CONE-LEDGER.json','STABILITY-POSITIVITY-LEDGER.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing unitarity/causality/stability controlling ledger: {rel}')
        for uid in binding.get('unitarity_check_ids', []):
            if uid not in known_uni_ids: errors.append(f'claim-route binding {bid} references unknown unitarity-check row: {uid}')
        for cid in binding.get('causality_cone_ids', []):
            if cid not in known_cau_ids: errors.append(f'claim-route binding {bid} references unknown causality-cone row: {cid}')
        for sid in binding.get('stability_positivity_ids', []):
            if sid not in known_stb_ids: errors.append(f'claim-route binding {bid} references unknown stability-positivity row: {sid}')
    if 'OQ-0078' not in registered_question_ids:
        errors.append('rev0281 unitarity / causality / stability burden requires registered OQ-0078')

    # rev0282 quantization / classical-limit / semiclassical-correspondence checks.
    qmap_ledger = json.loads((root / 'QUANTIZATION-MAP-LEDGER.json').read_text())
    clim_ledger = json.loads((root / 'CLASSICAL-LIMIT-LEDGER.json').read_text())
    scor_ledger = json.loads((root / 'SEMICLASSICAL-CORRESPONDENCE-LEDGER.json').read_text())
    qsummary_path = root / 'docs/30-program/quantization-correspondence-summary.generated.md'
    qsummary_text = qsummary_path.read_text() if qsummary_path.exists() else ''
    qrows = qmap_ledger.get('quantization_rows', [])
    crows = clim_ledger.get('classical_limit_rows', [])
    srows = scor_ledger.get('semiclassical_rows', [])
    if f"- Quantization-map rows: `{len(qrows)}`" not in qsummary_text:
        errors.append('quantization/correspondence generated summary quantization count drifted; run make index')
    if f"- Classical-limit rows: `{len(crows)}`" not in qsummary_text:
        errors.append('quantization/correspondence generated summary classical-limit count drifted; run make index')
    if f"- Semiclassical-correspondence rows: `{len(srows)}`" not in qsummary_text:
        errors.append('quantization/correspondence generated summary semiclassical count drifted; run make index')
    for row in qrows:
        qid = row.get('quantization_map_id','')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'quantization-map row {qid} references unknown route: {rid}')
        for uid in row.get('evidence_unit_ids', []):
            if uid not in known_evidence_unit_ids: errors.append(f'quantization-map row {qid} references unknown evidence unit: {uid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'quantization-map row {qid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'quantization-map row {qid} references unknown REF id: {ref}')
    for row in crows:
        cid = row.get('classical_limit_id','')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'classical-limit row {cid} references unknown route: {rid}')
        for qid in row.get('quantization_map_ids', []):
            if qid not in known_qmap_ids: errors.append(f'classical-limit row {cid} references unknown quantization-map row: {qid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'classical-limit row {cid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'classical-limit row {cid} references unknown REF id: {ref}')
    for row in srows:
        sid = row.get('semiclassical_correspondence_id','')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'semiclassical-correspondence row {sid} references unknown route: {rid}')
        for qid in row.get('quantization_map_ids', []):
            if qid not in known_qmap_ids: errors.append(f'semiclassical-correspondence row {sid} references unknown quantization-map row: {qid}')
        for cid in row.get('classical_limit_ids', []):
            if cid not in known_clim_ids: errors.append(f'semiclassical-correspondence row {sid} references unknown classical-limit row: {cid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'semiclassical-correspondence row {sid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'semiclassical-correspondence row {sid} references unknown REF id: {ref}')
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('quantization_map_ids') or not row.get('classical_limit_ids') or not row.get('semiclassical_correspondence_ids'):
            errors.append(f'route row {rid} missing quantization / classical-limit / semiclassical-correspondence handles')
        for qid in row.get('quantization_map_ids', []):
            if qid not in known_qmap_ids: errors.append(f'route row {rid} references unknown quantization-map row: {qid}')
            if ('quantization-map', qid, 'route', rid, 'quantization-map-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing quantization-map→route edge for {qid} -> {rid}')
        for cid in row.get('classical_limit_ids', []):
            if cid not in known_clim_ids: errors.append(f'route row {rid} references unknown classical-limit row: {cid}')
            if ('classical-limit', cid, 'route', rid, 'classical-limit-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing classical-limit→route edge for {cid} -> {rid}')
        for sid in row.get('semiclassical_correspondence_ids', []):
            if sid not in known_scor_ids: errors.append(f'route row {rid} references unknown semiclassical-correspondence row: {sid}')
            if ('semiclassical-correspondence', sid, 'route', rid, 'semiclassical-correspondence-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing semiclassical-correspondence→route edge for {sid} -> {rid}')
    for binding in binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['QUANTIZATION-MAP-LEDGER.json','CLASSICAL-LIMIT-LEDGER.json','SEMICLASSICAL-CORRESPONDENCE-LEDGER.json','LEDGER-FAMILY-REGISTRY.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing quantization/correspondence controlling ledger: {rel}')
        for qid in binding.get('quantization_map_ids', []):
            if qid not in known_qmap_ids: errors.append(f'claim-route binding {bid} references unknown quantization-map row: {qid}')
        for cid in binding.get('classical_limit_ids', []):
            if cid not in known_clim_ids: errors.append(f'claim-route binding {bid} references unknown classical-limit row: {cid}')
        for sid in binding.get('semiclassical_correspondence_ids', []):
            if sid not in known_scor_ids: errors.append(f'claim-route binding {bid} references unknown semiclassical-correspondence row: {sid}')
    if 'OQ-0079' not in registered_question_ids:
        errors.append('rev0282 quantization / classical-limit / semiclassical-correspondence burden requires registered OQ-0079')

    # rev0282 ledger-family registry / route-layer coverage audit checks.
    registry = json.loads((root / 'LEDGER-FAMILY-REGISTRY.json').read_text())
    registry_summary_path = root / 'docs/30-program/route-layer-coverage-audit.generated.md'
    registry_summary_text = registry_summary_path.read_text() if registry_summary_path.exists() else ''
    reg_rows = registry.get('registry_rows', [])
    if f"- Registered layer families: `{len(reg_rows)}`" not in registry_summary_text:
        errors.append('route-layer coverage audit generated summary registry count drifted; run make index')
    if f"- Route rows audited: `{len(route_rows)}`" not in registry_summary_text:
        errors.append('route-layer coverage audit generated summary route count drifted; run make index')
    for fam in reg_rows:
        fid = fam.get('family_id','')
        for rel in fam.get('ledger_files', []):
            if not (root / rel).exists():
                errors.append(f'ledger-family registry row {fid} references missing ledger: {rel}')
        oqid = fam.get('open_question_id')
        if oqid and oqid not in registered_question_ids:
            errors.append(f'ledger-family registry row {fid} references unknown open question: {oqid}')
        fields = fam.get('route_fields', [])
        for row in route_rows:
            rid = row.get('route_id','')
            for field in fields:
                if not row.get(field):
                    errors.append(f'route-layer registry family {fid} field {field} empty on route {rid}')
                max_allowed = fam.get('maximum_route_field_cardinality')
                if fam.get('cardinality_policy') == 'route-local-plus-wrapper':
                    if max_allowed is None:
                        max_allowed = 3
                    if len(row.get(field, [])) > int(max_allowed):
                        errors.append(f'route-layer registry family {fid} field {field} exceeds declared cardinality on route {rid}: {len(row.get(field, []))} > {max_allowed}')


    # rev0283 information / entropy / no-go checks.
    for rel in ['INFORMATION-FLOW-LEDGER.json','ENTROPY-ACCOUNTING-LEDGER.json','NO-GO-COMPLIANCE-LEDGER.json','schemas/information-flow-ledger.schema.json','schemas/entropy-accounting-ledger.schema.json','schemas/no-go-compliance-ledger.schema.json']:
        if not (root / rel).exists():
            errors.append(f'missing rev0283 information/entropy/no-go surface: {rel}')
    info_summary_text = (root / 'docs/30-program/information-entropy-summary.generated.md').read_text() if (root / 'docs/30-program/information-entropy-summary.generated.md').exists() else ''
    info_rows = information_flow_ledger_for_edges.get('information_rows', [])
    ent_rows = entropy_accounting_ledger_for_edges.get('entropy_rows', [])
    ngc_rows = no_go_compliance_ledger_for_edges.get('no_go_rows', [])
    if f"- Information-flow rows: `{len(info_rows)}`" not in info_summary_text:
        errors.append('information/entropy/no-go generated summary information count drifted; run make index')
    if f"- Entropy-accounting rows: `{len(ent_rows)}`" not in info_summary_text:
        errors.append('information/entropy/no-go generated summary entropy count drifted; run make index')
    if f"- No-go-compliance rows: `{len(ngc_rows)}`" not in info_summary_text:
        errors.append('information/entropy/no-go generated summary no-go count drifted; run make index')
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('information_flow_ids') or not row.get('entropy_accounting_ids') or not row.get('no_go_compliance_ids'):
            errors.append(f'route row {rid} missing information / entropy / no-go handles')
        for iid in row.get('information_flow_ids', []):
            if iid not in known_ifl_ids: errors.append(f'route row {rid} references unknown information-flow row: {iid}')
            if ('information-flow', iid, 'route', rid, 'information-flow-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing information-flow→route edge for {iid} -> {rid}')
        for eid in row.get('entropy_accounting_ids', []):
            if eid not in known_ent_ids: errors.append(f'route row {rid} references unknown entropy-accounting row: {eid}')
            if ('entropy-accounting', eid, 'route', rid, 'entropy-accounting-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing entropy-accounting→route edge for {eid} -> {rid}')
        for nid in row.get('no_go_compliance_ids', []):
            if nid not in known_ngc_ids: errors.append(f'route row {rid} references unknown no-go-compliance row: {nid}')
            if ('no-go-compliance', nid, 'route', rid, 'no-go-compliance-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing no-go-compliance→route edge for {nid} -> {rid}')
    for row in info_rows:
        iid=row.get('information_flow_id','')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'information-flow row {iid} references unknown route: {rid}')
        for eu in row.get('evidence_unit_ids', []):
            if eu not in known_evidence_unit_ids: errors.append(f'information-flow row {iid} references unknown evidence unit: {eu}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'information-flow row {iid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'information-flow row {iid} references unknown REF id: {ref}')
    for row in ent_rows:
        eid=row.get('entropy_accounting_id','')
        for iid in row.get('information_flow_ids', []):
            if iid not in known_ifl_ids: errors.append(f'entropy-accounting row {eid} references unknown information-flow row: {iid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'entropy-accounting row {eid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'entropy-accounting row {eid} references unknown REF id: {ref}')
    for row in ngc_rows:
        nid=row.get('no_go_compliance_id','')
        for iid in row.get('information_flow_ids', []):
            if iid not in known_ifl_ids: errors.append(f'no-go-compliance row {nid} references unknown information-flow row: {iid}')
        for eid in row.get('entropy_accounting_ids', []):
            if eid not in known_ent_ids: errors.append(f'no-go-compliance row {nid} references unknown entropy-accounting row: {eid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'no-go-compliance row {nid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'no-go-compliance row {nid} references unknown REF id: {ref}')
    info_binding_rows = [b for b in binding_rows if b.get('claim_or_oq_id') == 'OQ-0080']
    if not info_binding_rows:
        errors.append('OQ-0080 requires a claim-route binding row')
    for binding in info_binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['INFORMATION-FLOW-LEDGER.json','ENTROPY-ACCOUNTING-LEDGER.json','NO-GO-COMPLIANCE-LEDGER.json','LEDGER-FAMILY-REGISTRY.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing information/entropy/no-go controlling ledger: {rel}')
        for iid in binding.get('information_flow_ids', []):
            if iid not in known_ifl_ids: errors.append(f'claim-route binding {bid} references unknown information-flow row: {iid}')
        for eid in binding.get('entropy_accounting_ids', []):
            if eid not in known_ent_ids: errors.append(f'claim-route binding {bid} references unknown entropy-accounting row: {eid}')
        for nid in binding.get('no_go_compliance_ids', []):
            if nid not in known_ngc_ids: errors.append(f'claim-route binding {bid} references unknown no-go-compliance row: {nid}')
    if 'OQ-0080' not in registered_question_ids:
        errors.append('rev0283 information / entropy / no-go burden requires registered OQ-0080')


    # rev0284 symmetry / anomaly / conservation checks.
    for rel in ['SYMMETRY-REALIZATION-LEDGER.json','ANOMALY-MATCHING-LEDGER.json','CONSERVATION-LAW-LEDGER.json','schemas/symmetry-realization-ledger.schema.json','schemas/anomaly-matching-ledger.schema.json','schemas/conservation-law-ledger.schema.json']:
        if not (root / rel).exists():
            errors.append(f'missing rev0284 symmetry/anomaly/conservation surface: {rel}')
    sym_summary_text = (root / 'docs/30-program/symmetry-anomaly-summary.generated.md').read_text() if (root / 'docs/30-program/symmetry-anomaly-summary.generated.md').exists() else ''
    sym_rows = symmetry_realization_ledger_for_edges.get('symmetry_rows', [])
    anm_rows = anomaly_matching_ledger_for_edges.get('anomaly_rows', [])
    con_rows = conservation_law_ledger_for_edges.get('conservation_rows', [])
    if f"- Symmetry-realization rows: `{len(sym_rows)}`" not in sym_summary_text:
        errors.append('symmetry/anomaly generated summary symmetry count drifted; run make index')
    if f"- Anomaly-matching rows: `{len(anm_rows)}`" not in sym_summary_text:
        errors.append('symmetry/anomaly generated summary anomaly count drifted; run make index')
    if f"- Conservation-law rows: `{len(con_rows)}`" not in sym_summary_text:
        errors.append('symmetry/anomaly generated summary conservation count drifted; run make index')
    if f"- Registered route-layer families: `{len(reg_rows)}`" not in route_summary_text:
        errors.append('route-state generated summary registry-family count drifted; run make index')
    if '| `symmetry-anomaly-conservation` | `OQ-0081`' not in route_summary_text:
        errors.append('route-state generated summary is not reflecting the rev0284 registry family; run make index')
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('symmetry_realization_ids') or not row.get('anomaly_matching_ids') or not row.get('conservation_law_ids'):
            errors.append(f'route row {rid} missing symmetry / anomaly / conservation handles')
        for sid in row.get('symmetry_realization_ids', []):
            if sid not in known_sym_ids: errors.append(f'route row {rid} references unknown symmetry-realization row: {sid}')
            if ('symmetry-realization', sid, 'route', rid, 'symmetry-realization-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing symmetry-realization→route edge for {sid} -> {rid}')
        for aid in row.get('anomaly_matching_ids', []):
            if aid not in known_anm_ids: errors.append(f'route row {rid} references unknown anomaly-matching row: {aid}')
            if ('anomaly-matching', aid, 'route', rid, 'anomaly-matching-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing anomaly-matching→route edge for {aid} -> {rid}')
        for cid in row.get('conservation_law_ids', []):
            if cid not in known_con_ids: errors.append(f'route row {rid} references unknown conservation-law row: {cid}')
            if ('conservation-law', cid, 'route', rid, 'conservation-law-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing conservation-law→route edge for {cid} -> {rid}')
    for row in sym_rows:
        sid=row.get('symmetry_realization_id','')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'symmetry-realization row {sid} references unknown route: {rid}')
        for eu in row.get('evidence_unit_ids', []):
            if eu not in known_evidence_unit_ids: errors.append(f'symmetry-realization row {sid} references unknown evidence unit: {eu}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'symmetry-realization row {sid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'symmetry-realization row {sid} references unknown REF id: {ref}')
    for row in anm_rows:
        aid=row.get('anomaly_matching_id','')
        for sid in row.get('symmetry_realization_ids', []):
            if sid not in known_sym_ids: errors.append(f'anomaly-matching row {aid} references unknown symmetry-realization row: {sid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'anomaly-matching row {aid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'anomaly-matching row {aid} references unknown REF id: {ref}')
    for row in con_rows:
        cid=row.get('conservation_law_id','')
        for sid in row.get('symmetry_realization_ids', []):
            if sid not in known_sym_ids: errors.append(f'conservation-law row {cid} references unknown symmetry-realization row: {sid}')
        for aid in row.get('anomaly_matching_ids', []):
            if aid not in known_anm_ids: errors.append(f'conservation-law row {cid} references unknown anomaly-matching row: {aid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'conservation-law row {cid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'conservation-law row {cid} references unknown REF id: {ref}')
    sym_binding_rows = [b for b in binding_rows if b.get('claim_or_oq_id') == 'OQ-0081']
    if not sym_binding_rows:
        errors.append('OQ-0081 requires a claim-route binding row')
    for binding in sym_binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['SYMMETRY-REALIZATION-LEDGER.json','ANOMALY-MATCHING-LEDGER.json','CONSERVATION-LAW-LEDGER.json','LEDGER-FAMILY-REGISTRY.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing symmetry/anomaly/conservation controlling ledger: {rel}')
        for sid in binding.get('symmetry_realization_ids', []):
            if sid not in known_sym_ids: errors.append(f'claim-route binding {bid} references unknown symmetry-realization row: {sid}')
        for aid in binding.get('anomaly_matching_ids', []):
            if aid not in known_anm_ids: errors.append(f'claim-route binding {bid} references unknown anomaly-matching row: {aid}')
        for cid in binding.get('conservation_law_ids', []):
            if cid not in known_con_ids: errors.append(f'claim-route binding {bid} references unknown conservation-law row: {cid}')
    if 'OQ-0081' not in registered_question_ids:
        errors.append('rev0284 symmetry / anomaly / conservation burden requires registered OQ-0081')

    # rev0285 topology / dimension / signature checks and binding-field normalization audit.
    for rel in ['SPACETIME-TOPOLOGY-LEDGER.json','DIMENSION-REALIZATION-LEDGER.json','SIGNATURE-STRUCTURE-LEDGER.json','schemas/spacetime-topology-ledger.schema.json','schemas/dimension-realization-ledger.schema.json','schemas/signature-structure-ledger.schema.json']:
        if not (root / rel).exists():
            errors.append(f'missing rev0285 topology/dimension/signature surface: {rel}')
    top_summary_text = (root / 'docs/30-program/topology-dimension-signature-summary.generated.md').read_text() if (root / 'docs/30-program/topology-dimension-signature-summary.generated.md').exists() else ''
    top_rows = spacetime_topology_ledger_for_edges.get('topology_rows', [])
    dim_rows = dimension_realization_ledger_for_edges.get('dimension_rows', [])
    sig_rows = signature_structure_ledger_for_edges.get('signature_rows', [])
    if f"- Spacetime-topology rows: `{len(top_rows)}`" not in top_summary_text:
        errors.append('topology/dimension/signature generated summary topology count drifted; run make index')
    if f"- Dimension-realization rows: `{len(dim_rows)}`" not in top_summary_text:
        errors.append('topology/dimension/signature generated summary dimension count drifted; run make index')
    if f"- Signature-structure rows: `{len(sig_rows)}`" not in top_summary_text:
        errors.append('topology/dimension/signature generated summary signature count drifted; run make index')
    if '| `topology-dimension-signature` | `OQ-0082`' not in route_summary_text:
        errors.append('route-state generated summary is not reflecting the rev0285 registry family; run make index')
    binding_audit_path = root / 'docs/30-program/claim-route-binding-field-audit.generated.md'
    binding_audit_text = binding_audit_path.read_text() if binding_audit_path.exists() else ''
    registry_route_fields = []
    for fam in reg_rows:
        for field in fam.get('route_fields', []):
            if field not in registry_route_fields:
                registry_route_fields.append(field)
    missing_binding_cells = [(b.get('binding_id','<missing>'), field) for b in binding_rows for field in registry_route_fields if field not in b]
    if f"- Missing binding-field cells: `{len(missing_binding_cells)}`" not in binding_audit_text:
        errors.append('claim-route binding field audit generated summary drifted; run make index')
    if missing_binding_cells:
        errors.append(f'claim-route binding rows are missing registered route-layer fields: {missing_binding_cells[:5]}')
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('spacetime_topology_ids') or not row.get('dimension_realization_ids') or not row.get('signature_structure_ids'):
            errors.append(f'route row {rid} missing topology / dimension / signature handles')
        for tid in row.get('spacetime_topology_ids', []):
            if tid not in known_top_ids: errors.append(f'route row {rid} references unknown spacetime-topology row: {tid}')
            if ('spacetime-topology', tid, 'route', rid, 'spacetime-topology-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing spacetime-topology→route edge for {tid} -> {rid}')
        for did in row.get('dimension_realization_ids', []):
            if did not in known_dim_ids: errors.append(f'route row {rid} references unknown dimension-realization row: {did}')
            if ('dimension-realization', did, 'route', rid, 'dimension-realization-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing dimension-realization→route edge for {did} -> {rid}')
        for sid in row.get('signature_structure_ids', []):
            if sid not in known_sig_ids: errors.append(f'route row {rid} references unknown signature-structure row: {sid}')
            if ('signature-structure', sid, 'route', rid, 'signature-structure-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing signature-structure→route edge for {sid} -> {rid}')
    allowed_top_classes = set(witness_vocab.get('topology_class_labels', []))
    allowed_dim_classes = set(witness_vocab.get('dimension_realization_class_labels', []))
    allowed_sig_classes = set(witness_vocab.get('signature_structure_class_labels', []))
    for row in top_rows:
        tid=row.get('spacetime_topology_id','')
        if row.get('topology_class') not in allowed_top_classes: errors.append(f'spacetime-topology row {tid} has unknown topology_class: {row.get("topology_class")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'spacetime-topology row {tid} references unknown route: {rid}')
        for eu in row.get('evidence_unit_ids', []):
            if eu not in known_evidence_unit_ids: errors.append(f'spacetime-topology row {tid} references unknown evidence unit: {eu}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'spacetime-topology row {tid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'spacetime-topology row {tid} references unknown REF id: {ref}')
    for row in dim_rows:
        did=row.get('dimension_realization_id','')
        if row.get('dimension_class') not in allowed_dim_classes: errors.append(f'dimension-realization row {did} has unknown dimension_class: {row.get("dimension_class")}')
        for tid in row.get('spacetime_topology_ids', []):
            if tid not in known_top_ids: errors.append(f'dimension-realization row {did} references unknown spacetime-topology row: {tid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'dimension-realization row {did} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'dimension-realization row {did} references unknown REF id: {ref}')
    for row in sig_rows:
        sid=row.get('signature_structure_id','')
        if row.get('signature_class') not in allowed_sig_classes: errors.append(f'signature-structure row {sid} has unknown signature_class: {row.get("signature_class")}')
        for tid in row.get('spacetime_topology_ids', []):
            if tid not in known_top_ids: errors.append(f'signature-structure row {sid} references unknown spacetime-topology row: {tid}')
        for did in row.get('dimension_realization_ids', []):
            if did not in known_dim_ids: errors.append(f'signature-structure row {sid} references unknown dimension-realization row: {did}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'signature-structure row {sid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'signature-structure row {sid} references unknown REF id: {ref}')
    top_binding_rows = [b for b in binding_rows if b.get('claim_or_oq_id') == 'OQ-0082']
    if not top_binding_rows:
        errors.append('OQ-0082 requires a claim-route binding row')
    for binding in top_binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['SPACETIME-TOPOLOGY-LEDGER.json','DIMENSION-REALIZATION-LEDGER.json','SIGNATURE-STRUCTURE-LEDGER.json','LEDGER-FAMILY-REGISTRY.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing topology/dimension/signature controlling ledger: {rel}')
        for tid in binding.get('spacetime_topology_ids', []):
            if tid not in known_top_ids: errors.append(f'claim-route binding {bid} references unknown spacetime-topology row: {tid}')
        for did in binding.get('dimension_realization_ids', []):
            if did not in known_dim_ids: errors.append(f'claim-route binding {bid} references unknown dimension-realization row: {did}')
        for sid in binding.get('signature_structure_ids', []):
            if sid not in known_sig_ids: errors.append(f'claim-route binding {bid} references unknown signature-structure row: {sid}')
    if 'OQ-0082' not in registered_question_ids:
        errors.append('rev0285 topology / dimension / signature burden requires registered OQ-0082')


    # rev0286 algebraic-locality / subsystem-factorization / edge-mode-center checks and registry surface audit.
    for rel in ['ALGEBRAIC-LOCALITY-LEDGER.json','SUBSYSTEM-FACTORIZATION-LEDGER.json','EDGE-MODE-CENTER-LEDGER.json','schemas/algebraic-locality-ledger.schema.json','schemas/subsystem-factorization-ledger.schema.json','schemas/edge-mode-center-ledger.schema.json']:
        if not (root / rel).exists():
            errors.append(f'missing rev0286 subsystem/algebra/edge-center surface: {rel}')
    alg_summary_text = (root / 'docs/30-program/subsystem-algebra-summary.generated.md').read_text() if (root / 'docs/30-program/subsystem-algebra-summary.generated.md').exists() else ''
    alg_rows = algebraic_locality_ledger_for_edges.get('algebraic_rows', [])
    fac_rows = subsystem_factorization_ledger_for_edges.get('factorization_rows', [])
    edg_rows = edge_mode_center_ledger_for_edges.get('edge_mode_rows', [])
    if f"- Algebraic-locality rows: `{len(alg_rows)}`" not in alg_summary_text:
        errors.append('subsystem/algebra generated summary algebraic-locality count drifted; run make index')
    if f"- Subsystem-factorization rows: `{len(fac_rows)}`" not in alg_summary_text:
        errors.append('subsystem/algebra generated summary factorization count drifted; run make index')
    if f"- Edge-mode/center rows: `{len(edg_rows)}`" not in alg_summary_text:
        errors.append('subsystem/algebra generated summary edge-center count drifted; run make index')
    if '| `subsystem-algebra-edge-center` | `OQ-0083`' not in route_summary_text:
        errors.append('route-state summary missing rev0286 subsystem-algebra-edge-center registry row; run make index')
    surface_audit_path = root / 'docs/30-program/ledger-family-surface-audit.generated.md'
    surface_audit_text = surface_audit_path.read_text() if surface_audit_path.exists() else ''
    if f"- Registered layer families: `{len(reg_rows)}`" not in surface_audit_text or '- Missing surface cells: `0`' not in surface_audit_text:
        errors.append('ledger-family surface/schema audit generated summary drifted or reports missing surfaces; run make index')
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('algebraic_locality_ids') or not row.get('subsystem_factorization_ids') or not row.get('edge_mode_center_ids'):
            errors.append(f'route row {rid} missing algebraic-locality / subsystem-factorization / edge-center handles')
        for aid in row.get('algebraic_locality_ids', []):
            if aid not in known_alg_ids: errors.append(f'route row {rid} references unknown algebraic-locality row: {aid}')
            if ('algebraic-locality', aid, 'route', rid, 'algebraic-locality-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing algebraic-locality→route edge for {aid} -> {rid}')
        for fid in row.get('subsystem_factorization_ids', []):
            if fid not in known_fac_ids: errors.append(f'route row {rid} references unknown subsystem-factorization row: {fid}')
            if ('subsystem-factorization', fid, 'route', rid, 'subsystem-factorization-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing subsystem-factorization→route edge for {fid} -> {rid}')
        for eid in row.get('edge_mode_center_ids', []):
            if eid not in known_edg_ids: errors.append(f'route row {rid} references unknown edge-mode-center row: {eid}')
            if ('edge-mode-center', eid, 'route', rid, 'edge-mode-center-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing edge-mode-center→route edge for {eid} -> {rid}')
    allowed_alg_classes = set(witness_vocab.get('algebraic_locality_class_labels', []))
    allowed_fac_classes = set(witness_vocab.get('subsystem_factorization_class_labels', []))
    allowed_edg_classes = set(witness_vocab.get('edge_mode_center_class_labels', []))
    for row in alg_rows:
        aid=row.get('algebraic_locality_id','')
        if row.get('algebraic_locality_class') not in allowed_alg_classes: errors.append(f'algebraic-locality row {aid} has unknown algebraic_locality_class: {row.get("algebraic_locality_class")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'algebraic-locality row {aid} references unknown route: {rid}')
        for eu in row.get('evidence_unit_ids', []):
            if eu not in known_evidence_unit_ids: errors.append(f'algebraic-locality row {aid} references unknown evidence unit: {eu}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'algebraic-locality row {aid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'algebraic-locality row {aid} references unknown REF id: {ref}')
    for row in fac_rows:
        fid=row.get('subsystem_factorization_id','')
        if row.get('subsystem_factorization_class') not in allowed_fac_classes: errors.append(f'subsystem-factorization row {fid} has unknown subsystem_factorization_class: {row.get("subsystem_factorization_class")}')
        for aid in row.get('algebraic_locality_ids', []):
            if aid not in known_alg_ids: errors.append(f'subsystem-factorization row {fid} references unknown algebraic-locality row: {aid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'subsystem-factorization row {fid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'subsystem-factorization row {fid} references unknown REF id: {ref}')
    for row in edg_rows:
        eid=row.get('edge_mode_center_id','')
        if row.get('edge_mode_center_class') not in allowed_edg_classes: errors.append(f'edge-mode-center row {eid} has unknown edge_mode_center_class: {row.get("edge_mode_center_class")}')
        for aid in row.get('algebraic_locality_ids', []):
            if aid not in known_alg_ids: errors.append(f'edge-mode-center row {eid} references unknown algebraic-locality row: {aid}')
        for fid in row.get('subsystem_factorization_ids', []):
            if fid not in known_fac_ids: errors.append(f'edge-mode-center row {eid} references unknown subsystem-factorization row: {fid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'edge-mode-center row {eid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'edge-mode-center row {eid} references unknown REF id: {ref}')
    alg_binding_rows = [b for b in binding_rows if b.get('claim_or_oq_id') == 'OQ-0083']
    if not alg_binding_rows:
        errors.append('OQ-0083 requires a claim-route binding row')
    for binding in alg_binding_rows:
        bid = binding.get('binding_id','')
        for rel in ['ALGEBRAIC-LOCALITY-LEDGER.json','SUBSYSTEM-FACTORIZATION-LEDGER.json','EDGE-MODE-CENTER-LEDGER.json','LEDGER-FAMILY-REGISTRY.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing subsystem/algebra controlling ledger: {rel}')
        for aid in binding.get('algebraic_locality_ids', []):
            if aid not in known_alg_ids: errors.append(f'claim-route binding {bid} references unknown algebraic-locality row: {aid}')
        for fid in binding.get('subsystem_factorization_ids', []):
            if fid not in known_fac_ids: errors.append(f'claim-route binding {bid} references unknown subsystem-factorization row: {fid}')
        for eid in binding.get('edge_mode_center_ids', []):
            if eid not in known_edg_ids: errors.append(f'claim-route binding {bid} references unknown edge-mode-center row: {eid}')
    if 'OQ-0083' not in registered_question_ids:
        errors.append('rev0286 subsystem / algebra / edge-center burden requires registered OQ-0083')


    # rev0286 measure-definition / ensemble-sampling / typicality-weighting checks and binding-control audit.
    for rel in ['MEASURE-DEFINITION-LEDGER.json','ENSEMBLE-SAMPLING-LEDGER.json','TYPICALITY-WEIGHTING-LEDGER.json','schemas/measure-definition-ledger.schema.json','schemas/ensemble-sampling-ledger.schema.json','schemas/typicality-weighting-ledger.schema.json']:
        if not (root / rel).exists():
            errors.append(f'missing rev0286 measure/ensemble/typicality surface: {rel}')
    mea_summary_text = (root / 'docs/30-program/measure-ensemble-typicality-summary.generated.md').read_text() if (root / 'docs/30-program/measure-ensemble-typicality-summary.generated.md').exists() else ''
    mea_rows = measure_definition_ledger_for_edges.get('measure_rows', [])
    ens_rows = ensemble_sampling_ledger_for_edges.get('ensemble_rows', [])
    typ_rows = typicality_weighting_ledger_for_edges.get('typicality_rows', [])
    if f"- Measure-definition rows: `{len(mea_rows)}`" not in mea_summary_text:
        errors.append('measure/ensemble/typicality generated summary measure count drifted; run make index')
    if f"- Ensemble-sampling rows: `{len(ens_rows)}`" not in mea_summary_text:
        errors.append('measure/ensemble/typicality generated summary ensemble count drifted; run make index')
    if f"- Typicality-weighting rows: `{len(typ_rows)}`" not in mea_summary_text:
        errors.append('measure/ensemble/typicality generated summary typicality count drifted; run make index')
    if '| `measure-ensemble-typicality` | `OQ-0084`' not in route_summary_text:
        errors.append('route-state summary missing rev0286 measure-ensemble-typicality registry row; run make index')
    binding_control_audit_path = root / 'docs/30-program/binding-control-ledger-coverage-audit.generated.md'
    binding_control_audit_text = binding_control_audit_path.read_text() if binding_control_audit_path.exists() else ''
    if f"- Registered layer families: `{len(reg_rows)}`" not in binding_control_audit_text or '- Missing controlling-ledger cells: `0`' not in binding_control_audit_text:
        errors.append('binding control-ledger coverage audit generated summary drifted or reports missing cells; run make index')
    for row in route_rows:
        rid=row.get('route_id','')
        if not row.get('measure_definition_ids') or not row.get('ensemble_sampling_ids') or not row.get('typicality_weighting_ids'):
            errors.append(f'route row {rid} missing measure-definition / ensemble-sampling / typicality-weighting handles')
        for mid in row.get('measure_definition_ids', []):
            if mid not in known_mea_ids: errors.append(f'route row {rid} references unknown measure-definition row: {mid}')
            if ('measure-definition', mid, 'route', rid, 'measure-definition-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing measure-definition→route edge for {mid} -> {rid}')
        for eid in row.get('ensemble_sampling_ids', []):
            if eid not in known_ens_ids: errors.append(f'route row {rid} references unknown ensemble-sampling row: {eid}')
            if ('ensemble-sampling', eid, 'route', rid, 'ensemble-sampling-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing ensemble-sampling→route edge for {eid} -> {rid}')
        for tid in row.get('typicality_weighting_ids', []):
            if tid not in known_typ_ids: errors.append(f'route row {rid} references unknown typicality-weighting row: {tid}')
            if ('typicality-weighting', tid, 'route', rid, 'typicality-weighting-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing typicality-weighting→route edge for {tid} -> {rid}')
    allowed_mea_classes = set(witness_vocab.get('measure_definition_class_labels', []))
    allowed_ens_classes = set(witness_vocab.get('ensemble_sampling_class_labels', []))
    allowed_typ_classes = set(witness_vocab.get('typicality_weighting_class_labels', []))
    for row in mea_rows:
        mid=row.get('measure_definition_id','')
        if row.get('measure_class') not in allowed_mea_classes: errors.append(f'measure-definition row {mid} has unknown measure_class: {row.get("measure_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'measure-definition row {mid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'measure-definition row {mid} references unknown route: {rid}')
        for eu in row.get('evidence_unit_ids', []):
            if eu not in known_evidence_unit_ids: errors.append(f'measure-definition row {mid} references unknown evidence unit: {eu}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'measure-definition row {mid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'measure-definition row {mid} references unknown REF id: {ref}')
    for row in ens_rows:
        eid=row.get('ensemble_sampling_id','')
        if row.get('ensemble_class') not in allowed_ens_classes: errors.append(f'ensemble-sampling row {eid} has unknown ensemble_class: {row.get("ensemble_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'ensemble-sampling row {eid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for mid in row.get('measure_definition_ids', []):
            if mid not in known_mea_ids: errors.append(f'ensemble-sampling row {eid} references unknown measure-definition row: {mid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'ensemble-sampling row {eid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'ensemble-sampling row {eid} references unknown REF id: {ref}')
    for row in typ_rows:
        tid=row.get('typicality_weighting_id','')
        if row.get('typicality_class') not in allowed_typ_classes: errors.append(f'typicality-weighting row {tid} has unknown typicality_class: {row.get("typicality_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'typicality-weighting row {tid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for mid in row.get('measure_definition_ids', []):
            if mid not in known_mea_ids: errors.append(f'typicality-weighting row {tid} references unknown measure-definition row: {mid}')
        for eid in row.get('ensemble_sampling_ids', []):
            if eid not in known_ens_ids: errors.append(f'typicality-weighting row {tid} references unknown ensemble-sampling row: {eid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'typicality-weighting row {tid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'typicality-weighting row {tid} references unknown REF id: {ref}')
    mea_binding_rows = [b for b in binding_rows if b.get('claim_or_oq_id') == 'OQ-0084']
    if not mea_binding_rows:
        errors.append('OQ-0084 requires a claim-route binding row')
    for binding in mea_binding_rows:
        bid=binding.get('binding_id','')
        for rel in ['MEASURE-DEFINITION-LEDGER.json','ENSEMBLE-SAMPLING-LEDGER.json','TYPICALITY-WEIGHTING-LEDGER.json','LEDGER-FAMILY-REGISTRY.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing measure/ensemble/typicality controlling ledger: {rel}')
        for mid in binding.get('measure_definition_ids', []):
            if mid not in known_mea_ids: errors.append(f'claim-route binding {bid} references unknown measure-definition row: {mid}')
        for eid in binding.get('ensemble_sampling_ids', []):
            if eid not in known_ens_ids: errors.append(f'claim-route binding {bid} references unknown ensemble-sampling row: {eid}')
        for tid in binding.get('typicality_weighting_ids', []):
            if tid not in known_typ_ids: errors.append(f'claim-route binding {bid} references unknown typicality-weighting row: {tid}')
    if 'OQ-0084' not in registered_question_ids:
        errors.append('rev0286 measure / ensemble / typicality burden requires registered OQ-0084')

    # rev0287 matter-sector and program-namespace checks.
    for rel in ['PARTICLE-SPECTRUM-LEDGER.json','INTERACTION-COUPLING-LEDGER.json','MASS-HIERARCHY-LEDGER.json','schemas/particle-spectrum-ledger.schema.json','schemas/interaction-coupling-ledger.schema.json','schemas/mass-hierarchy-ledger.schema.json']:
        if not (root / rel).exists():
            errors.append(f'missing rev0287 matter-sector surface: {rel}')
    psp_rows = particle_spectrum_ledger_for_edges.get('particle_spectrum_rows', [])
    icg_rows = interaction_coupling_ledger_for_edges.get('interaction_coupling_rows', [])
    mhg_rows = mass_hierarchy_ledger_for_edges.get('mass_hierarchy_rows', [])
    matter_summary_text = (root / 'docs/30-program/matter-sector-summary.generated.md').read_text() if (root / 'docs/30-program/matter-sector-summary.generated.md').exists() else ''
    if f"- Particle-spectrum rows: `{len(psp_rows)}`" not in matter_summary_text:
        errors.append('matter-sector generated summary particle-spectrum count drifted; run make index')
    if f"- Interaction-coupling rows: `{len(icg_rows)}`" not in matter_summary_text:
        errors.append('matter-sector generated summary coupling count drifted; run make index')
    if f"- Mass/hierarchy rows: `{len(mhg_rows)}`" not in matter_summary_text:
        errors.append('matter-sector generated summary mass/hierarchy count drifted; run make index')
    if '| `matter-spectrum-coupling-mass` | `OQ-0085`' not in route_summary_text:
        errors.append('route-state summary missing rev0287 matter-spectrum-coupling-mass registry row; run make index')
    allowed_psp_classes = set(witness_vocab.get('particle_spectrum_class_labels', []))
    allowed_icg_classes = set(witness_vocab.get('interaction_coupling_class_labels', []))
    allowed_mhg_classes = set(witness_vocab.get('mass_hierarchy_class_labels', []))
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('particle_spectrum_ids') or not row.get('interaction_coupling_ids') or not row.get('mass_hierarchy_ids'):
            errors.append(f'route row {rid} missing particle-spectrum / interaction-coupling / mass-hierarchy handles')
        for pid in row.get('particle_spectrum_ids', []):
            if pid not in known_psp_ids: errors.append(f'route row {rid} references unknown particle-spectrum row: {pid}')
            if ('particle-spectrum', pid, 'route', rid, 'particle-spectrum-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing particle-spectrum→route edge for {pid} -> {rid}')
        for cid in row.get('interaction_coupling_ids', []):
            if cid not in known_icg_ids: errors.append(f'route row {rid} references unknown interaction-coupling row: {cid}')
            if ('interaction-coupling', cid, 'route', rid, 'interaction-coupling-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing interaction-coupling→route edge for {cid} -> {rid}')
        for mid in row.get('mass_hierarchy_ids', []):
            if mid not in known_mhg_ids: errors.append(f'route row {rid} references unknown mass-hierarchy row: {mid}')
            if ('mass-hierarchy', mid, 'route', rid, 'mass-hierarchy-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing mass-hierarchy→route edge for {mid} -> {rid}')
    for row in psp_rows:
        pid=row.get('particle_spectrum_id','')
        if row.get('spectrum_class') not in allowed_psp_classes: errors.append(f'particle-spectrum row {pid} has unknown spectrum_class: {row.get("spectrum_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'particle-spectrum row {pid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'particle-spectrum row {pid} references unknown route: {rid}')
        for eu in row.get('evidence_unit_ids', []):
            if eu not in known_evidence_unit_ids: errors.append(f'particle-spectrum row {pid} references unknown evidence unit: {eu}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'particle-spectrum row {pid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'particle-spectrum row {pid} references unknown REF id: {ref}')
    for row in icg_rows:
        cid=row.get('interaction_coupling_id','')
        if row.get('coupling_class') not in allowed_icg_classes: errors.append(f'interaction-coupling row {cid} has unknown coupling_class: {row.get("coupling_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'interaction-coupling row {cid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for pid in row.get('particle_spectrum_ids', []):
            if pid not in known_psp_ids: errors.append(f'interaction-coupling row {cid} references unknown particle-spectrum row: {pid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'interaction-coupling row {cid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'interaction-coupling row {cid} references unknown REF id: {ref}')
    for row in mhg_rows:
        mid=row.get('mass_hierarchy_id','')
        if row.get('mass_hierarchy_class') not in allowed_mhg_classes: errors.append(f'mass/hierarchy row {mid} has unknown mass_hierarchy_class: {row.get("mass_hierarchy_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'mass/hierarchy row {mid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for pid in row.get('particle_spectrum_ids', []):
            if pid not in known_psp_ids: errors.append(f'mass/hierarchy row {mid} references unknown particle-spectrum row: {pid}')
        for cid in row.get('interaction_coupling_ids', []):
            if cid not in known_icg_ids: errors.append(f'mass/hierarchy row {mid} references unknown interaction-coupling row: {cid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'mass/hierarchy row {mid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'mass/hierarchy row {mid} references unknown REF id: {ref}')
    mat_binding_rows = [b for b in binding_rows if b.get('claim_or_oq_id') == 'OQ-0085']
    if not mat_binding_rows:
        errors.append('OQ-0085 requires a claim-route binding row')
    for binding in mat_binding_rows:
        bid=binding.get('binding_id','')
        for rel in ['PARTICLE-SPECTRUM-LEDGER.json','INTERACTION-COUPLING-LEDGER.json','MASS-HIERARCHY-LEDGER.json','LEDGER-FAMILY-REGISTRY.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing matter-sector controlling ledger: {rel}')
        for pid in binding.get('particle_spectrum_ids', []):
            if pid not in known_psp_ids: errors.append(f'claim-route binding {bid} references unknown particle-spectrum row: {pid}')
        for cid in binding.get('interaction_coupling_ids', []):
            if cid not in known_icg_ids: errors.append(f'claim-route binding {bid} references unknown interaction-coupling row: {cid}')
        for mid in binding.get('mass_hierarchy_ids', []):
            if mid not in known_mhg_ids: errors.append(f'claim-route binding {bid} references unknown mass/hierarchy row: {mid}')
    if 'OQ-0085' not in registered_question_ids:
        errors.append('rev0287 matter-sector burden requires registered OQ-0085')
    program_audit_path = root / 'docs/30-program/program-id-namespace-audit.generated.md'
    program_audit_text = program_audit_path.read_text() if program_audit_path.exists() else ''
    if '- Duplicate IDs: `0`' not in program_audit_text:
        errors.append('program-id namespace audit missing or reports duplicate WS/BR/RF identifiers; run make index')
    import re as _re
    for prefix, rel in [('WS','docs/30-program/workstreams.md'), ('BR','docs/30-program/bridge-experiments.md'), ('RF','docs/30-program/research-frontiers.md')]:
        txt=(root/rel).read_text()
        line_pattern = _re.compile(rf'^\s*(?:#+\s+|-\s+)?`?({prefix}-\d+)`?\b')
        ids=[]
        for line in txt.splitlines():
            m=line_pattern.search(line)
            if m:
                ids.append(m.group(1))
        if len(ids) != len(set(ids)):
            errors.append(f'{rel} contains duplicate {prefix} identifiers')


    # rev0289 black-hole horizon / thermodynamics / evaporation controls.
    for rel in ['HORIZON-STRUCTURE-LEDGER.json','BLACK-HOLE-THERMODYNAMICS-LEDGER.json','EVAPORATION-RADIATION-LEDGER.json']:
        if not (root / rel).exists():
            errors.append(f'rev0289 black-hole-sector ledger missing: {rel}')
    for rel in ['schemas/horizon-structure-ledger.schema.json','schemas/black-hole-thermodynamics-ledger.schema.json','schemas/evaporation-radiation-ledger.schema.json']:
        if not (root / rel).exists():
            errors.append(f'rev0289 black-hole-sector schema missing: {rel}')
    hzn_rows = horizon_structure_ledger_for_edges.get('horizon_rows', [])
    bht_rows = black_hole_thermodynamics_ledger_for_edges.get('thermodynamics_rows', [])
    evr_rows = evaporation_radiation_ledger_for_edges.get('evaporation_rows', [])
    bh_summary_path = root / 'docs/30-program/black-hole-sector-summary.generated.md'
    bh_summary_text = bh_summary_path.read_text() if bh_summary_path.exists() else ''
    if f"- Horizon-structure rows: `{len(hzn_rows)}`" not in bh_summary_text:
        errors.append('black-hole-sector summary horizon count drifted; run make index')
    if f"- Black-hole thermodynamics rows: `{len(bht_rows)}`" not in bh_summary_text:
        errors.append('black-hole-sector summary thermodynamics count drifted; run make index')
    if f"- Evaporation/radiation rows: `{len(evr_rows)}`" not in bh_summary_text:
        errors.append('black-hole-sector summary evaporation count drifted; run make index')
    allowed_hzn_classes = set(witness_vocab.get('horizon_structure_class_labels', []))
    allowed_bht_classes = set(witness_vocab.get('black_hole_thermodynamics_class_labels', []))
    allowed_evr_classes = set(witness_vocab.get('evaporation_radiation_class_labels', []))
    for row in route_rows:
        rid = row.get('route_id','')
        if not row.get('horizon_structure_ids') or not row.get('black_hole_thermodynamics_ids') or not row.get('evaporation_radiation_ids'):
            errors.append(f'route row {rid} missing horizon / black-hole-thermodynamics / evaporation handles')
        for hid in row.get('horizon_structure_ids', []):
            if hid not in known_hzn_ids: errors.append(f'route row {rid} references unknown horizon-structure row: {hid}')
            if ('horizon-structure', hid, 'route', rid, 'horizon-structure-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing horizon-structure→route edge for {hid} -> {rid}')
        for bid in row.get('black_hole_thermodynamics_ids', []):
            if bid not in known_bht_ids: errors.append(f'route row {rid} references unknown black-hole-thermodynamics row: {bid}')
            if ('black-hole-thermodynamics', bid, 'route', rid, 'black-hole-thermodynamics-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing black-hole-thermodynamics→route edge for {bid} -> {rid}')
        for eid in row.get('evaporation_radiation_ids', []):
            if eid not in known_evr_ids: errors.append(f'route row {rid} references unknown evaporation-radiation row: {eid}')
            if ('evaporation-radiation', eid, 'route', rid, 'evaporation-radiation-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing evaporation-radiation→route edge for {eid} -> {rid}')
    for row in hzn_rows:
        hid=row.get('horizon_structure_id','')
        if row.get('horizon_class') not in allowed_hzn_classes: errors.append(f'horizon-structure row {hid} has unknown horizon_class: {row.get("horizon_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'horizon-structure row {hid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'horizon-structure row {hid} references unknown route: {rid}')
        for eu in row.get('evidence_unit_ids', []):
            if eu not in known_evidence_unit_ids: errors.append(f'horizon-structure row {hid} references unknown evidence unit: {eu}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'horizon-structure row {hid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'horizon-structure row {hid} references unknown REF id: {ref}')
    for row in bht_rows:
        bid=row.get('black_hole_thermodynamics_id','')
        if row.get('thermodynamics_class') not in allowed_bht_classes: errors.append(f'black-hole-thermodynamics row {bid} has unknown thermodynamics_class: {row.get("thermodynamics_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'black-hole-thermodynamics row {bid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for hid in row.get('horizon_structure_ids', []):
            if hid not in known_hzn_ids: errors.append(f'black-hole-thermodynamics row {bid} references unknown horizon-structure row: {hid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'black-hole-thermodynamics row {bid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'black-hole-thermodynamics row {bid} references unknown REF id: {ref}')
    for row in evr_rows:
        eid=row.get('evaporation_radiation_id','')
        if row.get('evaporation_class') not in allowed_evr_classes: errors.append(f'evaporation-radiation row {eid} has unknown evaporation_class: {row.get("evaporation_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'evaporation-radiation row {eid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for hid in row.get('horizon_structure_ids', []):
            if hid not in known_hzn_ids: errors.append(f'evaporation-radiation row {eid} references unknown horizon-structure row: {hid}')
        for bid in row.get('black_hole_thermodynamics_ids', []):
            if bid not in known_bht_ids: errors.append(f'evaporation-radiation row {eid} references unknown black-hole-thermodynamics row: {bid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'evaporation-radiation row {eid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'evaporation-radiation row {eid} references unknown REF id: {ref}')
    bh_binding_rows = [b for b in binding_rows if b.get('claim_or_oq_id') == 'OQ-0087']
    if not bh_binding_rows:
        errors.append('OQ-0087 requires a claim-route binding row')
    for binding in bh_binding_rows:
        bid=binding.get('binding_id','')
        for rel in ['HORIZON-STRUCTURE-LEDGER.json','BLACK-HOLE-THERMODYNAMICS-LEDGER.json','EVAPORATION-RADIATION-LEDGER.json','LEDGER-FAMILY-REGISTRY.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing black-hole-sector controlling ledger: {rel}')
        for hid in binding.get('horizon_structure_ids', []):
            if hid not in known_hzn_ids: errors.append(f'claim-route binding {bid} references unknown horizon-structure row: {hid}')
        for bid2 in binding.get('black_hole_thermodynamics_ids', []):
            if bid2 not in known_bht_ids: errors.append(f'claim-route binding {bid} references unknown black-hole-thermodynamics row: {bid2}')
        for eid in binding.get('evaporation_radiation_ids', []):
            if eid not in known_evr_ids: errors.append(f'claim-route binding {bid} references unknown evaporation-radiation row: {eid}')
    if 'OQ-0087' not in registered_question_ids:
        errors.append('rev0289 black-hole-sector burden requires registered OQ-0087')
    source_audit_path = root / 'docs/30-program/source-reference-usage-audit.generated.md'
    source_audit_text = source_audit_path.read_text() if source_audit_path.exists() else ''
    if '- Unknown source_refs: `0`' not in source_audit_text:
        errors.append('source-reference usage audit missing or reports unknown source_refs; run make index')
    # rev0290 curvature-regime / singularity-resolution / censorship-hyperbolicity controls.
    for rel in ['CURVATURE-REGIME-LEDGER.json','SINGULARITY-RESOLUTION-LEDGER.json','CENSORSHIP-HYPERBOLICITY-LEDGER.json']:
        if not (root / rel).exists():
            errors.append(f'rev0290 singularity/censorship ledger missing: {rel}')
    for rel in ['schemas/curvature-regime-ledger.schema.json','schemas/singularity-resolution-ledger.schema.json','schemas/censorship-hyperbolicity-ledger.schema.json']:
        if not (root / rel).exists():
            errors.append(f'rev0290 singularity/censorship schema missing: {rel}')
    curvature_ledger = json.loads((root / 'CURVATURE-REGIME-LEDGER.json').read_text()) if (root / 'CURVATURE-REGIME-LEDGER.json').exists() else {'curvature_rows': []}
    singularity_ledger = json.loads((root / 'SINGULARITY-RESOLUTION-LEDGER.json').read_text()) if (root / 'SINGULARITY-RESOLUTION-LEDGER.json').exists() else {'singularity_rows': []}
    censorship_ledger = json.loads((root / 'CENSORSHIP-HYPERBOLICITY-LEDGER.json').read_text()) if (root / 'CENSORSHIP-HYPERBOLICITY-LEDGER.json').exists() else {'censorship_rows': []}
    crv_rows = curvature_ledger.get('curvature_rows', [])
    sng_rows = singularity_ledger.get('singularity_rows', [])
    chy_rows = censorship_ledger.get('censorship_rows', [])
    crv_ids = [row.get('curvature_regime_id','') for row in crv_rows]
    sng_ids = [row.get('singularity_resolution_id','') for row in sng_rows]
    chy_ids = [row.get('censorship_hyperbolicity_id','') for row in chy_rows]
    if len(crv_ids) != len(set(crv_ids)): errors.append('CURVATURE-REGIME-LEDGER contains duplicate curvature_regime_id values')
    if len(sng_ids) != len(set(sng_ids)): errors.append('SINGULARITY-RESOLUTION-LEDGER contains duplicate singularity_resolution_id values')
    if len(chy_ids) != len(set(chy_ids)): errors.append('CENSORSHIP-HYPERBOLICITY-LEDGER contains duplicate censorship_hyperbolicity_id values')
    known_crv_ids = set(crv_ids); known_sng_ids = set(sng_ids); known_chy_ids = set(chy_ids)
    sc_summary_text = (root / 'docs/30-program/singularity-censorship-summary.generated.md').read_text() if (root / 'docs/30-program/singularity-censorship-summary.generated.md').exists() else ''
    if f"- Curvature-regime rows: `{len(crv_rows)}`" not in sc_summary_text:
        errors.append('singularity/censorship summary curvature-regime count drifted; run make index')
    if f"- Singularity-resolution rows: `{len(sng_rows)}`" not in sc_summary_text:
        errors.append('singularity/censorship summary singularity-resolution count drifted; run make index')
    if f"- Censorship/hyperbolicity rows: `{len(chy_rows)}`" not in sc_summary_text:
        errors.append('singularity/censorship summary censorship/hyperbolicity count drifted; run make index')
    allowed_crv_classes = set(witness_vocab.get('curvature_regime_class_labels', []))
    allowed_sng_classes = set(witness_vocab.get('singularity_resolution_class_labels', []))
    allowed_chy_classes = set(witness_vocab.get('censorship_hyperbolicity_class_labels', []))
    for row in route_rows:
        rid=row.get('route_id','')
        if not row.get('curvature_regime_ids') or not row.get('singularity_resolution_ids') or not row.get('censorship_hyperbolicity_ids'):
            errors.append(f'route row {rid} missing curvature / singularity / censorship handles')
        for cid in row.get('curvature_regime_ids', []):
            if cid not in known_crv_ids: errors.append(f'route row {rid} references unknown curvature-regime row: {cid}')
            if ('curvature-regime', cid, 'route', rid, 'curvature-regime-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing curvature-regime→route edge for {cid} -> {rid}')
        for sid in row.get('singularity_resolution_ids', []):
            if sid not in known_sng_ids: errors.append(f'route row {rid} references unknown singularity-resolution row: {sid}')
            if ('singularity-resolution', sid, 'route', rid, 'singularity-resolution-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing singularity-resolution→route edge for {sid} -> {rid}')
        for hid in row.get('censorship_hyperbolicity_ids', []):
            if hid not in known_chy_ids: errors.append(f'route row {rid} references unknown censorship/hyperbolicity row: {hid}')
            if ('censorship-hyperbolicity', hid, 'route', rid, 'censorship-hyperbolicity-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing censorship-hyperbolicity→route edge for {hid} -> {rid}')
    for row in crv_rows:
        cid=row.get('curvature_regime_id','')
        if row.get('curvature_class') not in allowed_crv_classes: errors.append(f'curvature-regime row {cid} has unknown curvature_class: {row.get("curvature_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'curvature-regime row {cid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'curvature-regime row {cid} references unknown route: {rid}')
        for eu in row.get('evidence_unit_ids', []):
            if eu not in known_evidence_unit_ids: errors.append(f'curvature-regime row {cid} references unknown evidence unit: {eu}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'curvature-regime row {cid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'curvature-regime row {cid} references unknown REF id: {ref}')
    for row in sng_rows:
        sid=row.get('singularity_resolution_id','')
        if row.get('singularity_class') not in allowed_sng_classes: errors.append(f'singularity-resolution row {sid} has unknown singularity_class: {row.get("singularity_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'singularity-resolution row {sid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for cid in row.get('curvature_regime_ids', []):
            if cid not in known_crv_ids: errors.append(f'singularity-resolution row {sid} references unknown curvature-regime row: {cid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'singularity-resolution row {sid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'singularity-resolution row {sid} references unknown REF id: {ref}')
    for row in chy_rows:
        hid=row.get('censorship_hyperbolicity_id','')
        if row.get('censorship_class') not in allowed_chy_classes: errors.append(f'censorship/hyperbolicity row {hid} has unknown censorship_class: {row.get("censorship_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'censorship/hyperbolicity row {hid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for cid in row.get('curvature_regime_ids', []):
            if cid not in known_crv_ids: errors.append(f'censorship/hyperbolicity row {hid} references unknown curvature-regime row: {cid}')
        for sid in row.get('singularity_resolution_ids', []):
            if sid not in known_sng_ids: errors.append(f'censorship/hyperbolicity row {hid} references unknown singularity-resolution row: {sid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'censorship/hyperbolicity row {hid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'censorship/hyperbolicity row {hid} references unknown REF id: {ref}')
    sc_binding_rows = [b for b in binding_rows if b.get('claim_or_oq_id') == 'OQ-0088']
    if not sc_binding_rows:
        errors.append('OQ-0088 requires a claim-route binding row')
    for binding in sc_binding_rows:
        bid=binding.get('binding_id','')
        for rel in ['CURVATURE-REGIME-LEDGER.json','SINGULARITY-RESOLUTION-LEDGER.json','CENSORSHIP-HYPERBOLICITY-LEDGER.json','LEDGER-FAMILY-REGISTRY.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing singularity/censorship controlling ledger: {rel}')
        for cid in binding.get('curvature_regime_ids', []):
            if cid not in known_crv_ids: errors.append(f'claim-route binding {bid} references unknown curvature-regime row: {cid}')
        for sid in binding.get('singularity_resolution_ids', []):
            if sid not in known_sng_ids: errors.append(f'claim-route binding {bid} references unknown singularity-resolution row: {sid}')
        for hid in binding.get('censorship_hyperbolicity_ids', []):
            if hid not in known_chy_ids: errors.append(f'claim-route binding {bid} references unknown censorship/hyperbolicity row: {hid}')
    if 'OQ-0088' not in registered_question_ids:
        errors.append('rev0290 singularity/censorship/hyperbolicity burden requires registered OQ-0088')
    constitutional_audit_text = (root / 'docs/30-program/constitutional-id-namespace-audit.generated.md').read_text() if (root / 'docs/30-program/constitutional-id-namespace-audit.generated.md').exists() else ''
    if '- Duplicate namespace IDs: `0`' not in constitutional_audit_text:
        errors.append('constitutional ID namespace audit missing or reports duplicate IDs; run make index')
    if '- Missing namespace IDs: `0`' not in constitutional_audit_text:
        errors.append('constitutional ID namespace audit missing or reports missing IDs; run make index')



    # rev0292 classical-GR recovery ledgers and parity audit.
    for rel in ['EQUIVALENCE-PRINCIPLE-LEDGER.json','WEAK-FIELD-PPN-LEDGER.json','GRAVITATIONAL-RADIATION-LEDGER.json']:
        if not (root / rel).exists():
            errors.append(f'rev0292 classical-GR recovery ledger missing: {rel}')
    for rel in ['schemas/equivalence-principle-ledger.schema.json','schemas/weak-field-ppn-ledger.schema.json','schemas/gravitational-radiation-ledger.schema.json']:
        if not (root / rel).exists():
            errors.append(f'rev0292 classical-GR recovery schema missing: {rel}')
    if (root / 'docs/30-program/classical-gr-recovery-summary.generated.md').exists():
        classical_summary_text = (root / 'docs/30-program/classical-gr-recovery-summary.generated.md').read_text()
        if f"- Revision: `{manifest['revision']}`" not in classical_summary_text:
            errors.append('classical-GR recovery generated summary revision drifted from manifest; run make index')
    else:
        errors.append('missing classical-GR recovery generated summary')
    if (root / 'docs/30-program/ledger-row-count-parity-audit.generated.md').exists():
        parity_text = (root / 'docs/30-program/ledger-row-count-parity-audit.generated.md').read_text()
        if f"- Registry revision: `{manifest['revision']}`" not in parity_text or '- Parity failures: `0`' not in parity_text:
            errors.append('ledger row-count parity audit drifted or reports failures; run make index and repair route-local rows')
    else:
        errors.append('missing ledger row-count parity audit generated surface')
    for row in route_rows:
        rid=row.get('route_id','')
        for field in ['equivalence_principle_ids','weak_field_ppn_ids','gravitational_radiation_ids']:
            if not row.get(field):
                errors.append(f'route row {rid} missing rev0292 classical-GR handle field {field}')
    if not any(b.get('claim_or_oq_id')=='OQ-0090' for b in claim_binding_ledger.get('binding_rows', [])):
        errors.append('OQ-0090 lacks a claim-route binding row')

    if 'OQ-0058' not in registered_question_ids:
        errors.append('rev0261 duality / underdetermination pressure requires registered OQ-0058')
    if 'OQ-0059' not in registered_question_ids:
        errors.append('rev0262 observed-sector recovery burden requires registered OQ-0059')
    if 'OQ-0060' not in registered_question_ids:
        errors.append('rev0263 public-record carrier / acquisition burden requires registered OQ-0060')
    if 'OQ-0061' not in registered_question_ids:
        errors.append('rev0264 defeat/rollback/severity burden requires registered OQ-0061')
    if 'OQ-0062' not in registered_question_ids:
        errors.append('rev0265 evidence-credit / independence burden requires registered OQ-0062')
    if 'OQ-0063' not in registered_question_ids:
        errors.append('rev0266 contrast-class / likelihood-update / prior-sensitivity burden requires registered OQ-0063')
    if 'OQ-0064' not in registered_question_ids:
        errors.append('rev0267 measurement-model / systematic-uncertainty / calibration-traceability burden requires registered OQ-0064')
    if 'OQ-0065' not in registered_question_ids:
        errors.append('rev0268 validity-domain / transportability / extrapolation-fence burden requires registered OQ-0065')
    if 'OQ-0066' not in registered_question_ids:
        errors.append('rev0269 causal-mechanism / intervention / counterfactual burden requires registered OQ-0066')
    if 'OQ-0067' not in registered_question_ids:
        errors.append('rev0270 selection-function / multiplicity / reporting-bias burden requires registered OQ-0067')
    if 'OQ-0068' not in registered_question_ids:
        errors.append('rev0271 model-capacity / complexity-penalty / generalization burden requires registered OQ-0068')
    if 'OQ-0069' not in registered_question_ids:
        errors.append('rev0272 semantic-binding / ontology-commitment / claim-language-permission burden requires registered OQ-0069')
    if 'OQ-0070' not in registered_question_ids:
        errors.append('rev0273 social-authority / review-replication / consensus-elicitation burden requires registered OQ-0070')
    if 'OQ-0071' not in registered_question_ids:
        errors.append('rev0274 computational-reproducibility / numerical-stability / software-provenance burden requires registered OQ-0071')
    if 'OQ-0071' not in registered_question_ids:
        errors.append('rev0274 computational-reproducibility / numerical-stability / software-supply-chain burden requires registered OQ-0071')
    if 'OQ-0087' not in registered_question_ids:
        errors.append('rev0289 black-hole horizon / thermodynamics / evaporation burden requires registered OQ-0087')
    if 'OQ-0088' not in registered_question_ids:
        errors.append('rev0290 singularity-resolution / censorship-hyperbolicity burden requires registered OQ-0088')
    if 'OQ-0089' not in registered_question_ids:
        errors.append('rev0291 stress-energy / backreaction / energy-condition burden requires registered OQ-0089')
    if 'OQ-0090' not in registered_question_ids:
        errors.append('rev0292 classical-GR equivalence / PPN / radiation burden requires registered OQ-0090')
    if 'OQ-0094' not in registered_question_ids:
        errors.append('rev0296 correlation-function / operator-insertion / bootstrap-data burden requires registered OQ-0094')

    # rev0294 asymptotic-state / infrared-dressing / scattering-observable checks and route-schema audit.
    for rel in ['ASYMPTOTIC-STATE-LEDGER.json','INFRARED-DRESSING-LEDGER.json','SCATTERING-OBSERVABLE-LEDGER.json','schemas/asymptotic-state-ledger.schema.json','schemas/infrared-dressing-ledger.schema.json','schemas/scattering-observable-ledger.schema.json']:
        if not (root / rel).exists():
            errors.append(f'missing rev0294 asymptotic/IR/scattering surface: {rel}')
    asy_summary_text = (root / 'docs/30-program/asymptotic-ir-scattering-summary.generated.md').read_text() if (root / 'docs/30-program/asymptotic-ir-scattering-summary.generated.md').exists() else ''
    asy_rows = asymptotic_state_ledger_for_edges.get('asymptotic_state_rows', [])
    ird_rows = infrared_dressing_ledger_for_edges.get('infrared_dressing_rows', [])
    sco_rows = scattering_observable_ledger_for_edges.get('scattering_observable_rows', [])
    if f"- Asymptotic-state rows: `{len(asy_rows)}`" not in asy_summary_text:
        errors.append('asymptotic/IR/scattering generated summary asymptotic-state count drifted; run make index')
    if f"- Infrared-dressing rows: `{len(ird_rows)}`" not in asy_summary_text:
        errors.append('asymptotic/IR/scattering generated summary infrared-dressing count drifted; run make index')
    if f"- Scattering-observable rows: `{len(sco_rows)}`" not in asy_summary_text:
        errors.append('asymptotic/IR/scattering generated summary scattering-observable count drifted; run make index')
    if '| `asymptotic-ir-scattering` | `OQ-0092`' not in route_summary_text:
        errors.append('route-state summary missing rev0294 asymptotic-ir-scattering registry row; run make index')
    for row in route_rows:
        rid=row.get('route_id','')
        if not row.get('asymptotic_state_ids') or not row.get('infrared_dressing_ids') or not row.get('scattering_observable_ids'):
            errors.append(f'route row {rid} missing asymptotic-state / infrared-dressing / scattering-observable handles')
        for aid in row.get('asymptotic_state_ids', []):
            if aid not in known_asy_ids: errors.append(f'route row {rid} references unknown asymptotic-state row: {aid}')
            if ('asymptotic-state', aid, 'route', rid, 'asymptotic-state-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing asymptotic-state→route edge for {aid} -> {rid}')
        for iid in row.get('infrared_dressing_ids', []):
            if iid not in known_ird_ids: errors.append(f'route row {rid} references unknown infrared-dressing row: {iid}')
            if ('infrared-dressing', iid, 'route', rid, 'infrared-dressing-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing infrared-dressing→route edge for {iid} -> {rid}')
        for sid in row.get('scattering_observable_ids', []):
            if sid not in known_sco_ids: errors.append(f'route row {rid} references unknown scattering-observable row: {sid}')
            if ('scattering-observable', sid, 'route', rid, 'scattering-observable-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing scattering-observable→route edge for {sid} -> {rid}')
    allowed_asy_classes=set(witness_vocab.get('asymptotic_state_class_labels', []))
    allowed_ird_classes=set(witness_vocab.get('infrared_dressing_class_labels', []))
    allowed_sco_classes=set(witness_vocab.get('scattering_observable_class_labels', []))
    for row in asy_rows:
        aid=row.get('asymptotic_state_id','')
        if row.get('asymptotic_state_class') not in allowed_asy_classes: errors.append(f'asymptotic-state row {aid} has unknown asymptotic_state_class: {row.get("asymptotic_state_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'asymptotic-state row {aid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'asymptotic-state row {aid} references unknown route: {rid}')
        for eu in row.get('evidence_unit_ids', []):
            if eu not in known_evidence_unit_ids: errors.append(f'asymptotic-state row {aid} references unknown evidence unit: {eu}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'asymptotic-state row {aid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'asymptotic-state row {aid} references unknown REF id: {ref}')
    for row in ird_rows:
        iid=row.get('infrared_dressing_id','')
        if row.get('infrared_dressing_class') not in allowed_ird_classes: errors.append(f'infrared-dressing row {iid} has unknown infrared_dressing_class: {row.get("infrared_dressing_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'infrared-dressing row {iid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for aid in row.get('asymptotic_state_ids', []):
            if aid not in known_asy_ids: errors.append(f'infrared-dressing row {iid} references unknown asymptotic-state row: {aid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'infrared-dressing row {iid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'infrared-dressing row {iid} references unknown REF id: {ref}')
    for row in sco_rows:
        sid=row.get('scattering_observable_id','')
        if row.get('scattering_observable_class') not in allowed_sco_classes: errors.append(f'scattering-observable row {sid} has unknown scattering_observable_class: {row.get("scattering_observable_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'scattering-observable row {sid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for aid in row.get('asymptotic_state_ids', []):
            if aid not in known_asy_ids: errors.append(f'scattering-observable row {sid} references unknown asymptotic-state row: {aid}')
        for iid in row.get('infrared_dressing_ids', []):
            if iid not in known_ird_ids: errors.append(f'scattering-observable row {sid} references unknown infrared-dressing row: {iid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'scattering-observable row {sid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'scattering-observable row {sid} references unknown REF id: {ref}')
    asy_binding_rows=[b for b in binding_rows if b.get('claim_or_oq_id')=='OQ-0092']
    if not asy_binding_rows:
        errors.append('OQ-0092 requires a claim-route binding row')
    for binding in asy_binding_rows:
        bid=binding.get('binding_id','')
        for rel in ['ASYMPTOTIC-STATE-LEDGER.json','INFRARED-DRESSING-LEDGER.json','SCATTERING-OBSERVABLE-LEDGER.json','LEDGER-FAMILY-REGISTRY.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing asymptotic/IR/scattering controlling ledger: {rel}')
        for aid in binding.get('asymptotic_state_ids', []):
            if aid not in known_asy_ids: errors.append(f'claim-route binding {bid} references unknown asymptotic-state row: {aid}')
        for iid in binding.get('infrared_dressing_ids', []):
            if iid not in known_ird_ids: errors.append(f'claim-route binding {bid} references unknown infrared-dressing row: {iid}')
        for sid in binding.get('scattering_observable_ids', []):
            if sid not in known_sco_ids: errors.append(f'claim-route binding {bid} references unknown scattering-observable row: {sid}')
    route_schema_audit_path=root/'docs/30-program/candidate-route-schema-field-audit.generated.md'
    route_schema_audit_text=route_schema_audit_path.read_text() if route_schema_audit_path.exists() else ''
    if f"- Registered layer families: `{len(reg_rows)}`" not in route_schema_audit_text or '- Missing schema-required route fields: `0`' not in route_schema_audit_text:
        errors.append('candidate-route schema field audit generated summary drifted or reports missing fields; run make index')
    if 'OQ-0092' not in registered_question_ids:
        errors.append('rev0294 asymptotic-state / infrared-dressing / scattering-observable burden requires registered OQ-0092')


    # rev0296 correlation-function / operator-insertion / bootstrap-data checks and binding-schema audit.
    for rel in ['CORRELATION-FUNCTION-LEDGER.json','OPERATOR-INSERTION-LEDGER.json','BOOTSTRAP-DATA-LEDGER.json','schemas/correlation-function-ledger.schema.json','schemas/operator-insertion-ledger.schema.json','schemas/bootstrap-data-ledger.schema.json']:
        if not (root / rel).exists():
            errors.append(f'missing rev0296 correlator/operator/bootstrap surface: {rel}')
    cob_summary_text = (root / 'docs/30-program/correlator-operator-bootstrap-summary.generated.md').read_text() if (root / 'docs/30-program/correlator-operator-bootstrap-summary.generated.md').exists() else ''
    cfn_rows = correlation_function_ledger_for_edges.get('correlation_function_rows', [])
    opi_rows = operator_insertion_ledger_for_edges.get('operator_insertion_rows', [])
    bsd_rows = bootstrap_data_ledger_for_edges.get('bootstrap_data_rows', [])
    if f"- Correlation-function rows: `{len(cfn_rows)}`" not in cob_summary_text:
        errors.append('correlator/operator/bootstrap generated summary correlation-function count drifted; run make index')
    if f"- Operator-insertion rows: `{len(opi_rows)}`" not in cob_summary_text:
        errors.append('correlator/operator/bootstrap generated summary operator-insertion count drifted; run make index')
    if f"- Bootstrap/CFT-data rows: `{len(bsd_rows)}`" not in cob_summary_text:
        errors.append('correlator/operator/bootstrap generated summary bootstrap-data count drifted; run make index')
    if '| `correlation-operator-bootstrap` | `OQ-0094`' not in route_summary_text:
        errors.append('route-state summary missing rev0296 correlation-operator-bootstrap registry row; run make index')
    for row in route_rows:
        rid=row.get('route_id','')
        for cid in row.get('correlation_function_ids', []):
            if cid not in known_cfn_ids: errors.append(f'route row {rid} references unknown correlation-function row: {cid}')
            if ('correlation-function', cid, 'route', rid, 'correlation-function-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing correlation-function→route edge for {cid} -> {rid}')
        for oid in row.get('operator_insertion_ids', []):
            if oid not in known_opi_ids: errors.append(f'route row {rid} references unknown operator-insertion row: {oid}')
            if ('operator-insertion', oid, 'route', rid, 'operator-insertion-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing operator-insertion→route edge for {oid} -> {rid}')
        for bid in row.get('bootstrap_data_ids', []):
            if bid not in known_bsd_ids: errors.append(f'route row {rid} references unknown bootstrap-data row: {bid}')
            if ('bootstrap-data', bid, 'route', rid, 'bootstrap-data-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing bootstrap-data→route edge for {bid} -> {rid}')
    allowed_cfn_classes=set(witness_vocab.get('correlation_function_class_labels', []))
    allowed_opi_classes=set(witness_vocab.get('operator_insertion_class_labels', []))
    allowed_bsd_classes=set(witness_vocab.get('bootstrap_data_class_labels', []))
    for row in cfn_rows:
        cid=row.get('correlation_function_id','')
        if row.get('correlation_function_class') not in allowed_cfn_classes: errors.append(f'correlation-function row {cid} has unknown correlation_function_class: {row.get("correlation_function_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'correlation-function row {cid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'correlation-function row {cid} references unknown route: {rid}')
        for eu in row.get('evidence_unit_ids', []):
            if eu not in known_evidence_unit_ids: errors.append(f'correlation-function row {cid} references unknown evidence unit: {eu}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'correlation-function row {cid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'correlation-function row {cid} references unknown REF id: {ref}')
    for row in opi_rows:
        oid=row.get('operator_insertion_id','')
        if row.get('operator_insertion_class') not in allowed_opi_classes: errors.append(f'operator-insertion row {oid} has unknown operator_insertion_class: {row.get("operator_insertion_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'operator-insertion row {oid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for cid in row.get('correlation_function_ids', []):
            if cid not in known_cfn_ids: errors.append(f'operator-insertion row {oid} references unknown correlation-function row: {cid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'operator-insertion row {oid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'operator-insertion row {oid} references unknown REF id: {ref}')
    for row in bsd_rows:
        bid=row.get('bootstrap_data_id','')
        if row.get('bootstrap_data_class') not in allowed_bsd_classes: errors.append(f'bootstrap-data row {bid} has unknown bootstrap_data_class: {row.get("bootstrap_data_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'bootstrap-data row {bid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for cid in row.get('correlation_function_ids', []):
            if cid not in known_cfn_ids: errors.append(f'bootstrap-data row {bid} references unknown correlation-function row: {cid}')
        for oid in row.get('operator_insertion_ids', []):
            if oid not in known_opi_ids: errors.append(f'bootstrap-data row {bid} references unknown operator-insertion row: {oid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'bootstrap-data row {bid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'bootstrap-data row {bid} references unknown REF id: {ref}')
    cob_binding_rows=[b for b in binding_rows if b.get('claim_or_oq_id')=='OQ-0094']
    if not cob_binding_rows:
        errors.append('OQ-0094 requires a claim-route binding row')
    for binding in cob_binding_rows:
        bid=binding.get('binding_id','')
        for rel in ['CORRELATION-FUNCTION-LEDGER.json','OPERATOR-INSERTION-LEDGER.json','BOOTSTRAP-DATA-LEDGER.json','LEDGER-FAMILY-REGISTRY.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing correlator/operator/bootstrap controlling ledger: {rel}')
    binding_schema_audit_path=root/'docs/30-program/claim-route-binding-schema-field-audit.generated.md'
    binding_schema_audit_text=binding_schema_audit_path.read_text() if binding_schema_audit_path.exists() else ''
    if f"- Registered layer families: `{len(reg_rows)}`" not in binding_schema_audit_text or '- Missing binding-schema required fields: `0`' not in binding_schema_audit_text:
        errors.append('claim-route binding schema field audit generated summary drifted or reports missing fields; run make index')
    if 'OQ-0094' not in registered_question_ids:
        errors.append('rev0296 correlation-function / operator-insertion / bootstrap-data burden requires registered OQ-0094')



    # rev0297 phase-structure / order-parameter / universality-class checks and route/binding schema-property audit.
    for rel in ['PHASE-STRUCTURE-LEDGER.json','ORDER-PARAMETER-LEDGER.json','UNIVERSALITY-CLASS-LEDGER.json','schemas/phase-structure-ledger.schema.json','schemas/order-parameter-ledger.schema.json','schemas/universality-class-ledger.schema.json']:
        if not (root / rel).exists():
            errors.append(f'missing rev0297 phase/order/universality surface: {rel}')
    pou_summary_text = (root / 'docs/30-program/phase-order-universality-summary.generated.md').read_text() if (root / 'docs/30-program/phase-order-universality-summary.generated.md').exists() else ''
    phs_rows = phase_structure_ledger_for_edges.get('phase_structure_rows', [])
    opm_rows = order_parameter_ledger_for_edges.get('order_parameter_rows', [])
    ucl_rows = universality_class_ledger_for_edges.get('universality_class_rows', [])
    if f"- Phase-structure rows: `{len(phs_rows)}`" not in pou_summary_text:
        errors.append('phase/order/universality generated summary phase-structure count drifted; run make index')
    if f"- Order-parameter rows: `{len(opm_rows)}`" not in pou_summary_text:
        errors.append('phase/order/universality generated summary order-parameter count drifted; run make index')
    if f"- Universality-class rows: `{len(ucl_rows)}`" not in pou_summary_text:
        errors.append('phase/order/universality generated summary universality-class count drifted; run make index')
    if '| `phase-order-universality` | `OQ-0095`' not in route_summary_text:
        errors.append('route-state summary missing rev0297 phase-order-universality registry row; run make index')
    for row in route_rows:
        rid=row.get('route_id','')
        for pid in row.get('phase_structure_ids', []):
            if pid not in known_phs_ids: errors.append(f'route row {rid} references unknown phase-structure row: {pid}')
            if ('phase-structure', pid, 'route', rid, 'phase-structure-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing phase-structure→route edge for {pid} -> {rid}')
        for oid in row.get('order_parameter_ids', []):
            if oid not in known_opm_ids: errors.append(f'route row {rid} references unknown order-parameter row: {oid}')
            if ('order-parameter', oid, 'route', rid, 'order-parameter-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing order-parameter→route edge for {oid} -> {rid}')
        for uid in row.get('universality_class_ids', []):
            if uid not in known_ucl_ids: errors.append(f'route row {rid} references unknown universality-class row: {uid}')
            if ('universality-class', uid, 'route', rid, 'universality-class-condition') not in edge_key_set:
                errors.append(f'authority dependency graph missing universality-class→route edge for {uid} -> {rid}')
    allowed_phs_classes=set(witness_vocab.get('phase_structure_class_labels', []))
    allowed_opm_classes=set(witness_vocab.get('order_parameter_class_labels', []))
    allowed_ucl_classes=set(witness_vocab.get('universality_class_labels', []))
    for row in phs_rows:
        pid=row.get('phase_structure_id','')
        if row.get('phase_structure_class') not in allowed_phs_classes: errors.append(f'phase-structure row {pid} has unknown phase_structure_class: {row.get("phase_structure_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'phase-structure row {pid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for rid in row.get('route_ids', []):
            if rid not in known_route_ids: errors.append(f'phase-structure row {pid} references unknown route: {rid}')
        for eu in row.get('evidence_unit_ids', []):
            if eu not in known_evidence_unit_ids: errors.append(f'phase-structure row {pid} references unknown evidence unit: {eu}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'phase-structure row {pid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'phase-structure row {pid} references unknown REF id: {ref}')
    for row in opm_rows:
        oid=row.get('order_parameter_id','')
        if row.get('order_parameter_class') not in allowed_opm_classes: errors.append(f'order-parameter row {oid} has unknown order_parameter_class: {row.get("order_parameter_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'order-parameter row {oid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for pid in row.get('phase_structure_ids', []):
            if pid not in known_phs_ids: errors.append(f'order-parameter row {oid} references unknown phase-structure row: {pid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'order-parameter row {oid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'order-parameter row {oid} references unknown REF id: {ref}')
    for row in ucl_rows:
        uid=row.get('universality_class_id','')
        if row.get('universality_class') not in allowed_ucl_classes: errors.append(f'universality-class row {uid} has unknown universality_class: {row.get("universality_class")}')
        if row.get('maximum_authority_effect') not in allowed_states: errors.append(f'universality-class row {uid} has unknown maximum_authority_effect: {row.get("maximum_authority_effect")}')
        for pid in row.get('phase_structure_ids', []):
            if pid not in known_phs_ids: errors.append(f'universality-class row {uid} references unknown phase-structure row: {pid}')
        for oid in row.get('order_parameter_ids', []):
            if oid not in known_opm_ids: errors.append(f'universality-class row {uid} references unknown order-parameter row: {oid}')
        for rb in row.get('rollback_rule_ids', []):
            if rb not in known_rollback_ids: errors.append(f'universality-class row {uid} references unknown rollback rule: {rb}')
        for ref in row.get('source_refs', []):
            if f'`{ref}`' not in bib: errors.append(f'universality-class row {uid} references unknown REF id: {ref}')
    pou_binding_rows=[b for b in binding_rows if b.get('claim_or_oq_id')=='OQ-0095']
    if not pou_binding_rows:
        errors.append('OQ-0095 requires a claim-route binding row')
    for binding in pou_binding_rows:
        bid=binding.get('binding_id','')
        for rel in ['PHASE-STRUCTURE-LEDGER.json','ORDER-PARAMETER-LEDGER.json','UNIVERSALITY-CLASS-LEDGER.json','LEDGER-FAMILY-REGISTRY.json']:
            if rel not in binding.get('controlling_ledgers', []):
                errors.append(f'claim-route binding {bid} missing phase/order/universality controlling ledger: {rel}')
    schema_prop_audit_path=root/'docs/30-program/route-binding-schema-property-audit.generated.md'
    schema_prop_audit_text=schema_prop_audit_path.read_text() if schema_prop_audit_path.exists() else ''
    if '- Candidate-route required fields missing property declarations: `0`' not in schema_prop_audit_text or '- Claim-route binding required fields missing property declarations: `0`' not in schema_prop_audit_text:
        errors.append('route/binding schema property audit generated summary drifted or reports missing property declarations; run make index')
    if 'OQ-0095' not in registered_question_ids:
        errors.append('rev0297 phase-structure / order-parameter / universality-class burden requires registered OQ-0095')

    if 'OQ-0091' not in registered_question_ids:
        errors.append('rev0293 state-preparation / detector-response / decoherence burden requires registered OQ-0091')
except Exception as e:
    errors.append(f'json parse failure: {e}')

if errors:
    print('LINT FAILED')
    for e in errors:
        print('-', e)
    sys.exit(1)

print('LINT OK')

