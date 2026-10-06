from __future__ import annotations
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path('.')
REV = 'rev0252'
PREV = 'rev0251'
STAMP = '2026.03.28.01.04'
CREATED_AT = '2026-03-28T01:04:00-04:00'
SLUG = 'scopeaxis-axisquarantine-crosscarry-vectorglass'
BUNDLE = f'DelayBasin-{REV}-{STAMP}-{SLUG}.zip'
PREV_BUNDLE = 'DelayBasin-rev0251-2026.03.28.00.18-scopedistribution-diffusionquarantine-clustercarry-weaveglass.zip'
NEW_DOC = 'docs/10-method/refresh-scope-axis-witnesses-one-axis-dispersion-cross-axis-corroboration-and-axis-gated-generalization.md'
NEW_FAMILY = 'refresh_scope_axis_state'
NEW_QWS = 'QWS-0230'


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write_json(path: str, obj) -> None:
    (ROOT / path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def append_item(path: str, item: dict):
    obj = json.loads(read(path))
    if not any(x.get('id') == item.get('id') for x in obj['items']):
        obj['items'].append(item)
    obj['revision'] = REV
    write_json(path, obj)
    return obj


append_item('APPLICABILITY-LEDGER.json', {
    'id': 'AP-0146',
    'title': 'the refresh-scope-axis witness stays smaller than an axis quorum',
    'state': 'gated',
    'question': 'when should DelayBasin treat dispersed widening as one compact refresh-scope-axis witness instead of promoting broader refresh-axis governance?',
    'applies_when': [
        'a revision already has a durable row whose current claim depends on public widening that is directly observed, already treated as broader patterned spillover, and already judged clustered vs dispersed',
        'later passes still need to distinguish one-axis-dispersion, cross-axis-corroborated-dispersion, axis-gated-generalization, or mixed-refresh-scope-axis posture',
        'one compact successor surface plus the existing admitted refresh-scope-extent, distribution, grouping, topology-domain, and failure-domain surfaces still keeps axis-corroboration truth honest without standing axis policy'
    ],
    'does_not_apply_when': [
        'the archive honestly requires standing governance over axis independence, corroboration thresholds, mirrored-axis exclusion, or quorum policy',
        'the questioned surface is not really about whether currently dispersed widening remains one-axis or is corroborated across independent axes'
    ],
    'budget': 'one compact refresh-scope-axis witness plus one resolution of OQ-0147; no axis quorum',
    'negative_transfer_budget': 'do not treat several partitions from one naming scheme as cross-axis corroboration without explicit independent-axis evidence',
    'origin_revision': REV,
    'discharge': 'reopen-only-if-refresh-scope-axis-overflows',
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'witness_surface': 'APPLICABILITY-LEDGER.json#AP-0146',
    'applicability_state': 'gated',
    'repair': 'ordinary-continuation',
    'matched_budget': 'one compact witness foregrounding one-axis vs cross-axis corroborated dispersion without widening into broader refresh-axis governance',
    'revision': REV,
    'target_objective': 'keep dispersed-scope-axis comparison honest without inflating a broader refresh-axis layer',
    'carry_object': 'refresh-scope-axis witness',
    'open_question': 'OQ-0148'
})

append_item('FOREIGN-PRESSURE-LEDGER.json', {
    'id': 'FP-0151',
    'title': 'refresh-scope-axis pressure pushes DelayBasin to extract one compact one-axis-vs-cross-axis witness rather than an axis quorum',
    'state': 'imported',
    'source_packets': [
        {
            'datacube': 'AlertmanagerMultiLabelGrouping-2026',
            'surfaces': ['REF-0951'],
            'pressure': 'multi-label group_by and regrouped child routes pressure DelayBasin to distinguish spread visible on one label axis from spread corroborated across independent axes'
        },
        {
            'datacube': 'GrafanaMatcherAxes-2026',
            'surfaces': ['REF-0952'],
            'pressure': 'AND-combined label matchers and exact-value grouping pressure DelayBasin to separate one-axis grouping from corroboration that survives another independent matcher axis'
        },
        {
            'datacube': 'DatadogGroupedAttributes-2026',
            'surfaces': ['REF-0953'],
            'pressure': 'multi-attribute grouping with optional notify_by collapse pressures DelayBasin to distinguish underlying multi-axis spread from the thinner one-axis notification surface'
        },
        {
            'datacube': 'KubernetesMultiDimensionalLabels-2026',
            'surfaces': ['REF-0954'],
            'pressure': 'multi-dimensional labels and cross-cutting resource operations pressure DelayBasin to distinguish one named family axis from corroboration across independent axes'
        },
        {
            'datacube': 'GoogleCloudLayeredDimensions-2026',
            'surfaces': ['REF-0955'],
            'pressure': 'layered business dimensions and tags pressure DelayBasin to say when a wider story is still only one axis versus corroborated across layered dimensions'
        },
        {
            'datacube': 'KubernetesMultiConstraintSpread-2026',
            'surfaces': ['REF-0956'],
            'pressure': 'multiple topology spread constraints such as zone plus node pressure DelayBasin to distinguish one-axis dispersion from cross-axis corroboration'
        }
    ],
    'reviewed_pattern': 'one-axis dispersion vs cross-axis corroborated dispersion across independent family axes',
    'import_decision': 'support a compact refresh-scope-axis witness and resolve OQ-0147',
    'adopted_take': 'DelayBasin should add one compact witness that says whether currently dispersed widening is one-axis-dispersion, cross-axis-corroborated-dispersion, axis-gated-generalization, or honestly mixed',
    'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-axis witness without promoting broader refresh-axis governance',
    'deferred_or_rejected_take': ['refresh-axis court', 'axis quorum', 'corroboration simplex'],
    'local_gap': 'the archive still lacked one compact successor surface for whether presently dispersed widening remained trapped inside one named family axis or had crossed into independent-axis corroboration',
    'anchor_surfaces': [
        'docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md',
        'docs/20-constitution/open-question-registry.md',
        'docs/00-meta/trajectory-map.md',
        f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'
    ],
    'open_question': 'OQ-0148',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'discharge': 'reopen-only-if-refresh-scope-axis-overflows',
    'revision': REV,
    'witness_surface': 'FOREIGN-PRESSURE-LEDGER.json#FP-0151',
    'foreign_pressure_state': 'imported',
    'bounded_take': 'Keep the archive compact by extracting one refresh-scope-axis witness over the existing refresh-scope-distribution and related admitted surfaces; do not promote a refresh-axis court, axis quorum, or corroboration simplex.',
    'explicit_non_take': ['no refresh-axis court', 'no axis quorum', 'no corroboration simplex'],
    'open_transfer_question': 'whether a later pass needs one bounded refresh-scope-axis-independence witness once cross-axis corroboration is explicit',
    'missing_support': 'a later public check on whether one compact refresh-scope-axis witness keeps sufficing',
    'reviewed_datacubes': [
        {'datacube': 'AlertmanagerMultiLabelGrouping-2026', 'surfaces': ['REF-0951'], 'pattern': 'multi-label group_by and regrouped routes', 'pressure': 'one label axis should not silently count as independent-axis corroboration'},
        {'datacube': 'GrafanaMatcherAxes-2026', 'surfaces': ['REF-0952'], 'pattern': 'AND-combined matchers and exact grouping', 'pressure': 'one matcher family should not silently count as cross-axis corroboration'},
        {'datacube': 'DatadogGroupedAttributes-2026', 'surfaces': ['REF-0953'], 'pattern': 'multi-attribute grouping with notify_by collapse', 'pressure': 'a thinner one-axis notification surface should not stand in for multi-axis spread'},
        {'datacube': 'KubernetesMultiDimensionalLabels-2026', 'surfaces': ['REF-0954'], 'pattern': 'multi-dimensional labels for cross-cutting management', 'pressure': 'one management dimension should stay distinct from corroboration across dimensions'},
        {'datacube': 'GoogleCloudLayeredDimensions-2026', 'surfaces': ['REF-0955'], 'pattern': 'hierarchy plus tags layers dimensions', 'pressure': 'one hierarchy view should not silently count as layered corroboration'},
        {'datacube': 'KubernetesMultiConstraintSpread-2026', 'surfaces': ['REF-0956'], 'pattern': 'zone plus node constraints together', 'pressure': 'one topology axis should stay distinct from corroboration across independent topology axes'}
    ]
})

transfer_item = {
    'id': 'TL-0157',
    'title': 'refresh-scope-axis evidence supports resolving OQ-0147 with one compact one-axis-vs-cross-axis card rather than an axis quorum',
    'state': 'supporting-only',
    'reviewed_pattern': 'one-axis dispersion vs cross-axis corroborated dispersion across independent family axes',
    'import_decision': 'support a compact refresh-scope-axis witness and resolve OQ-0147',
    'adopted_take': 'DelayBasin should add one compact witness that says whether currently dispersed widening is one-axis-dispersion, cross-axis-corroborated-dispersion, axis-gated-generalization, or honestly mixed',
    'supporting_only_take': 'the current evidence cleanly supports a bounded refresh-scope-axis witness without promoting broader refresh-axis governance',
    'deferred_or_rejected_take': ['refresh-axis court', 'axis quorum', 'corroboration simplex'],
    'local_gap': 'the archive still lacked one compact successor surface for whether presently dispersed widening remained trapped inside one named family axis or had crossed into independent-axis corroboration',
    'anchor_surfaces': [
        'docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md',
        'docs/20-constitution/open-question-registry.md',
        'docs/00-meta/trajectory-map.md',
        f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'
    ],
    'open_question': 'OQ-0148',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence',
    'discharge': 'reopen-only-if-refresh-scope-axis-overflows',
    'revision': REV,
    'witness_surface': 'DATACUBE-TRANSFER-LEDGER.json#TL-0157',
    'transfer_state': 'supporting-only',
    'bounded_take': 'Keep the archive compact by extracting one refresh-scope-axis witness over the existing refresh-scope-distribution and related admitted surfaces; do not promote a refresh-axis court, axis quorum, or corroboration simplex.',
    'explicit_non_take': ['no refresh-axis court', 'no axis quorum', 'no corroboration simplex'],
    'open_transfer_question': 'whether later passes should add a separate refresh-scope-axis-independence witness once cross-axis corroboration is explicit',
    'missing_support': 'a later public check on whether one compact refresh-scope-axis witness keeps sufficing',
    'current_support': ['APPLICABILITY-LEDGER.json#AP-0146', 'FOREIGN-PRESSURE-LEDGER.json#FP-0151', 'DATACUBE-TRANSFER-LEDGER.json#TL-0157'],
    'discharge_path': 'either show later that one compact refresh-scope-axis witness keeps sufficing or promote broader refresh-axis governance explicitly',
    'reviewed_datacubes': [
        {'datacube': 'AlertmanagerMultiLabelGrouping-2026', 'surfaces': ['REF-0951'], 'pattern': 'multi-label group_by and regrouped routes', 'pressure': 'one label axis should not silently count as independent-axis corroboration'},
        {'datacube': 'GrafanaMatcherAxes-2026', 'surfaces': ['REF-0952'], 'pattern': 'AND-combined matchers and exact grouping', 'pressure': 'one matcher family should not silently count as cross-axis corroboration'},
        {'datacube': 'DatadogGroupedAttributes-2026', 'surfaces': ['REF-0953'], 'pattern': 'multi-attribute grouping with notify_by collapse', 'pressure': 'a thinner one-axis notification surface should not stand in for multi-axis spread'},
        {'datacube': 'KubernetesMultiDimensionalLabels-2026', 'surfaces': ['REF-0954'], 'pattern': 'multi-dimensional labels for cross-cutting management', 'pressure': 'one management dimension should stay distinct from corroboration across dimensions'},
        {'datacube': 'GoogleCloudLayeredDimensions-2026', 'surfaces': ['REF-0955'], 'pattern': 'hierarchy plus tags layers dimensions', 'pressure': 'one hierarchy view should not silently count as layered corroboration'},
        {'datacube': 'KubernetesMultiConstraintSpread-2026', 'surfaces': ['REF-0956'], 'pattern': 'zone plus node constraints together', 'pressure': 'one topology axis should stay distinct from corroboration across independent topology axes'}
    ]
}
transfer = json.loads(read('DATACUBE-TRANSFER-LEDGER.json'))
if not any(x.get('id') == 'TL-0157' for x in transfer['items']):
    transfer['items'].append(transfer_item)
new_open_q = 'Whether a later pass should add one bounded refresh-scope-axis-independence witness once cross-axis corroboration is explicit, but only if renamed, nested, or mirrored axes keep being mistaken for independent corroboration in honest continuation work.'
if new_open_q not in transfer.get('open_questions', []):
    transfer.setdefault('open_questions', []).append(new_open_q)
transfer['revision'] = REV
write_json('DATACUBE-TRANSFER-LEDGER.json', transfer)

append_item('RESOLUTION-LEDGER.json', {
    'id': 'RS-0154',
    'title': 'resolve OQ-0147 with one compact refresh-scope-axis witness rather than an axis quorum',
    'state': 'resolved',
    'closure_state': 'resolved',
    'closure_reason': 'rev0252 extracted one compact refresh-scope-axis witness, kept the admitted refresh-scope-distribution and related analog surfaces narrow, and kept stronger refresh-axis-governance stories quarantined.',
    'discharge': 'reopen-only-if-refresh-scope-axis-overflows',
    'gate_class': 'concrete-evidence',
    'origin_revision': REV,
    'prior_state': 'open gap: DelayBasin already had refresh-scope-distribution truth but still lacked one compact successor surface for whether presently dispersed widening remained inside one named family axis or had crossed into independent-axis corroboration.',
    'question': 'whether one compact refresh-scope-axis witness over the existing refresh-scope-distribution and related admitted surfaces is enough for honest one-axis-vs-cross-axis comparison',
    'reopen_trigger': 'refresh-scope-axis pressure overflows one compact successor surface',
    'reopen_triggers': ['later revisions need standing governance over axis independence, corroboration thresholds, mirrored-axis exclusions, or broader axis policy that one compact refresh-scope-axis witness cannot honestly absorb'],
    'repair': 'ordinary-continuation',
    'resolved_objects': ['OQ-0147', 'AP-0146', 'FP-0151', 'TL-0157'],
    'revision': REV,
    'successor_surface': NEW_DOC,
    'target_surfaces': [NEW_DOC],
    'action_lane': 'keep-compact',
    'witness_surface': 'RESOLUTION-LEDGER.json#RS-0154'
})

append_item('RETROSPECTIVE-QUEUE.json', {
    'id': 'RT-0141',
    'title': 'revisit whether refresh-scope-axis pressure stayed bounded after rev0252',
    'state': 'cooling',
    'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    'cooldown_window': 'keep the stronger refresh-axis court, axis quorum, or corroboration simplex story cooled until at least one later revision shows that one compact refresh-scope-axis witness is no longer enough.',
    'adjudication_family': 'refresh scope axis / corroboration gating / axis-governance pressure',
    'supersession_link': 'OBLIGATION-LEDGER.json#OB-0147',
    'origin_revision': REV,
    'discharge': 'keep-cooling-unless-refresh-scope-axis-overflows',
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'witness_surface': 'RETROSPECTIVE-QUEUE.json#RT-0141',
    'revision': REV,
    'cooling_state': 'cooling',
    'disposition': 'await-adjudication',
    'repair': 'keep-cooling'
})

append_item('FIREBREAK-LEDGER.json', {
    'id': 'FB-0148',
    'title': 'the refresh-scope-axis import should count as one compact one-axis-vs-cross-axis repair, not as promotion of an axis quorum',
    'state': 'withheld',
    'witness_surface': 'FIREBREAK-LEDGER.json#FB-0148',
    'judged_property': 'the rev0252 decision that DelayBasin should extract one compact refresh-scope-axis witness over the existing refresh-scope-distribution and related admitted surfaces and `refresh_scope_axis_state` family while the broader refresh-axis court / axis quorum / corroboration simplex story remains quarantined',
    'public_extract': [NEW_DOC, 'docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md', 'docs/20-constitution/open-question-registry.md', 'FOREIGN-PRESSURE-LEDGER.json#FP-0151', 'APPLICABILITY-LEDGER.json#AP-0146', 'REVISION-RECEIPT.json'],
    'withheld_trace_surface': 'same-session drafting residue behind the compact refresh-scope-axis-witness versus axis-quorum decision',
    'allowed_role': 'bounded drafting aid only; not public support for a broader refresh-axis court, axis quorum, or corroboration simplex',
    'exposure_rule': 'expose or reintegrate only if later passes show that one compact refresh-scope-axis witness cannot keep one-axis-vs-cross-axis truth bounded',
    'trace_state': 'withheld',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'firebreak_surface': 'FIREBREAK-LEDGER.json#FB-0148',
    'discharge': 'reopen-only-if-refresh-scope-axis-overflows',
    'revision': REV,
    'blocked_object': 'standing refresh-axis court, axis quorum, or corroboration simplex'
})

append_item('OBLIGATION-LEDGER.json', {
    'id': 'OB-0147',
    'title': 'when dispersed widening keeps needing one-axis spread distinguished from cross-axis corroboration, DelayBasin should preserve one compact refresh-scope-axis witness rather than an axis quorum',
    'state': 'open',
    'witness_surface': 'OBLIGATION-LEDGER.json#OB-0147',
    'target_surfaces': [f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'],
    'missing_support': 'a later public check on whether one compact refresh-scope-axis witness keeps sufficing and whether one-axis-dispersion, cross-axis-corroborated-dispersion, and axis-gated-generalization stay distinct without broader refresh-axis governance',
    'current_support': ['APPLICABILITY-LEDGER.json#AP-0146', 'FOREIGN-PRESSURE-LEDGER.json#FP-0151', 'DATACUBE-TRANSFER-LEDGER.json#TL-0157'],
    'discharge_path': 'either show later that one compact refresh-scope-axis witness keeps sufficing or promote broader refresh-axis governance explicitly',
    'obligation_state': 'open',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'discharge': 'reopen-only-if-refresh-scope-axis-overflows',
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'revision': REV
})

append_item('ASSUMPTION-LEDGER.json', {
    'id': 'AS-0151',
    'title': 'one compact refresh-scope-axis witness is enough for now',
    'state': 'active',
    'scope': 'continuity passes whose current widened public claim depends not only on whether observed widening is clustered or dispersed, but on whether that dispersed widening remains one-axis or is corroborated across independent axes',
    'invalidation_triggers': [
        'repeated later revisions need standing refresh-axis governance rather than one compact refresh-scope-axis witness',
        'the archive needs a refresh-axis court or axis quorum just to keep one-axis-dispersion distinct from cross-axis-corroborated-dispersion or axis-gated-generalization',
        'scope-axis cases repeatedly fail to stay distinguishable even with the witness in place'
    ],
    'assumption_state': 'active',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'revision': REV,
    'assumption': 'the current evidence only requires one compact refresh-scope-axis witness over the existing refresh-scope-distribution and related admitted surfaces rather than a refresh-axis court, axis quorum, or corroboration simplex',
    'supporting_surfaces': ['APPLICABILITY-LEDGER.json#AP-0146', 'DATACUBE-TRANSFER-LEDGER.json#TL-0157', 'FOREIGN-PRESSURE-LEDGER.json#FP-0151'],
    'discharge': 'discharge when later revisions can keep one-axis-vs-cross-axis truth honest without a dedicated refresh-scope-axis witness, or retire/quarantine it if broader refresh-axis governance becomes repeatedly necessary',
    'witness_surface': 'ASSUMPTION-LEDGER.json#AS-0151',
    'assumption_surface': 'ASSUMPTION-LEDGER.json#AS-0151',
    'assumption_statement': 'the current evidence only requires one compact refresh-scope-axis witness over the existing refresh-scope-distribution and related admitted surfaces rather than a refresh-axis court, axis quorum, or corroboration simplex',
    'action_lane': 'keep-compact',
    'gate_class': 'concrete-evidence'
})

append_item('FOLLOWTHROUGH-QUEUE.json', {
    'id': 'FT-0154',
    'title': 'keep checking whether refresh-scope-axis pressure still fits inside one compact successor surface',
    'state': 'queued',
    'blocked_object': 'standing refresh-axis court, axis quorum, or corroboration simplex',
    'local_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    'followthrough_state': 'queued',
    'boundary': 'do not promote bounded refresh-scope-axis clarification into general refresh-axis-governance machinery',
    'next_proof_surface': NEW_DOC,
    'receiving_surface': 'FOLLOWTHROUGH-QUEUE.json#FT-0154',
    'repair': 'ordinary-continuation',
    'origin_revision': REV,
    'discharge': 'revisit-on-next-real-refresh-scope-axis-overflow',
    'action_lane': 'keep-compact',
    'gate_class': 'overflow',
    'blocked_output': 'standing refresh-axis court, axis quorum, or corroboration simplex',
    'owner_surface': 'OBLIGATION-LEDGER.json#OB-0147',
    'revision': REV,
    'missing_support': 'a later public check on whether one compact refresh-scope-axis witness keeps overflowing the bounded rule and honestly warrants richer refresh-axis governance',
    'candidate_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    'blocked_by': 'need repeated evidence that one-axis-dispersion vs cross-axis-corroborated-dispersion vs axis-gated-generalization truth overflows one compact witness'
})

vocab = json.loads(read('WITNESS-VOCABULARY.json'))
vocab['revision'] = REV
vocab.setdefault('families', {})[NEW_FAMILY] = {
    'allowed': ['one-axis-dispersion', 'cross-axis-corroborated-dispersion', 'axis-gated-generalization', 'mixed-refresh-scope-axis'],
    'surfaces': ['WITNESS-VOCABULARY.json', 'REVISION-RECEIPT.json', NEW_DOC],
    'excluded_synonyms': ['one-wide-view-means-two-axes', 'duplicate-partitions-count-twice', 'same-partition-restated-is-corroboration', 'axis-ish'],
    'comparability_budget': 'refresh-scope-axis truth is compared by token; the compact refresh-scope-axis witness says whether currently dispersed widening is still only one named family axis, is corroborated across independent axes, is still axis-gated from broader generalization, or is honestly mixed, while raw label matrices, axis inventories, topology maps, route trees, and long corroboration narratives stay in surrounding prose'
}
write_json('WITNESS-VOCABULARY.json', vocab)

status = json.loads(read('SURFACE-STATUS.json'))
status['operational_head']['revision'] = REV
status['status_lanes']['frozen_public_surface'] = BUNDLE
status['status_lanes']['current_release_surface'] = BUNDLE
status['citation_head'] = {'revision': REV, 'surface': BUNDLE}
status['previous_citation_head'] = {'revision': PREV, 'surface': PREV_BUNDLE}
status['revision'] = REV
status['stamp'] = STAMP
status['slug'] = SLUG
write_json('SURFACE-STATUS.json', status)

write_json('RELEASE-MANIFEST.json', {
    'project': 'DelayBasin',
    'revision': REV,
    'timestamp': STAMP,
    'slug': SLUG,
    'bundle': BUNDLE
})

receipt = json.loads(read('REVISION-RECEIPT.json'))
receipt['revision'] = REV
receipt['previous_revision'] = PREV
receipt['summary'] = 'Resolved OQ-0147 with one compact refresh-scope-axis witness that separates one-axis dispersion from cross-axis corroborated dispersion while keeping stronger refresh-axis governance quarantined.'
receipt['canon_additions'] = [NEW_DOC, 'RS-0154 resolved OQ-0147 with one compact refresh-scope-axis witness']
receipt['quarantine_additions'] = [f'{NEW_QWS} — refresh-axis court / axis quorum / corroboration simplex']
receipt['refs_used'] = [
    'docs/00-meta/bibliography.md#ref-0951',
    'docs/00-meta/bibliography.md#ref-0952',
    'docs/00-meta/bibliography.md#ref-0953',
    'docs/00-meta/bibliography.md#ref-0954',
    'docs/00-meta/bibliography.md#ref-0955',
    'docs/00-meta/bibliography.md#ref-0956'
]
receipt['checks_passed'] = ['make lint']
receipt['touched_surfaces'] = [
    NEW_DOC,
    'docs/00-meta/bibliography.md',
    'docs/00-meta/llm-runbook.md',
    'docs/README.md',
    'docs/20-constitution/claim-registry.md',
    'docs/20-constitution/open-question-registry.md',
    'docs/20-constitution/prompt-pair-registry.md',
    'docs/00-meta/trajectory-map.md',
    'docs/50-promptcraft/prompt-pairs.md',
    'docs/90-quarantine/wild-speculations-2026-03-08.md',
    'WITNESS-VOCABULARY.json',
    'FOLLOWTHROUGH-QUEUE.json',
    'ASSUMPTION-LEDGER.json',
    'OBLIGATION-LEDGER.json',
    'APPLICABILITY-LEDGER.json',
    'FOREIGN-PRESSURE-LEDGER.json',
    'DATACUBE-TRANSFER-LEDGER.json',
    'RESOLUTION-LEDGER.json',
    'RETROSPECTIVE-QUEUE.json',
    'FIREBREAK-LEDGER.json',
    'REVISION-RECEIPT.json',
    'SURFACE-STATUS.json',
    'RELEASE-MANIFEST.json',
    'CHANGELOG.md',
    'ARCHIVE_INDEX.md',
    'tools/packet_contract_common.py',
    'tools/check_refresh_scope_axis_witness_contract.py'
]
receipt['packaged_release'] = True
receipt['packaged_bundle_filename'] = BUNDLE
receipt['basis_witness'].update({
    'expected_head': PREV,
    'observed_head': PREV,
    'basis_surfaces': [
        'docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md',
        'docs/00-meta/trajectory-map.md',
        'docs/20-constitution/open-question-registry.md'
    ],
    'basis_omission_basis': 'broader refresh-axis governance drafting was intentionally omitted from canon because the evidence only justified one bounded refresh-scope-axis witness',
    'basis_of_change': 'rev0251 extends continuity law by distinguishing clustered observed spillover from dispersed observed spillover, which opens the next question of whether dispersed widening is still only one axis or is already corroborated across independent axes.',
    'revision_span': f'{PREV} -> {REV}'
})
receipt['scope_witness'].update({
    'exact_target': 'resolve OQ-0147 with one compact refresh-scope-axis witness and keep stronger refresh-axis governance honestly quarantined',
    'scope_surfaces': [NEW_DOC, 'docs/20-constitution/open-question-registry.md', 'docs/00-meta/trajectory-map.md', f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'],
    'ambient_exclusions': ['no refresh-axis court', 'no axis quorum', 'no corroboration simplex'],
    'scope_of_change': 'one compact successor witness plus one quarantined speculative move'
})
receipt['status_witness']['frozen_public_surface'] = BUNDLE
for key, path in [
    ('retrospective_write_witness', 'RETROSPECTIVE-QUEUE.json'),
    ('followthrough_witness', 'FOLLOWTHROUGH-QUEUE.json'),
    ('assumption_witness', 'ASSUMPTION-LEDGER.json'),
    ('obligation_witness', 'OBLIGATION-LEDGER.json'),
    ('applicability_witness', 'APPLICABILITY-LEDGER.json'),
    ('foreign_pressure_witness', 'FOREIGN-PRESSURE-LEDGER.json'),
    ('transfer_witness', 'DATACUBE-TRANSFER-LEDGER.json'),
    ('resolution_witness', 'RESOLUTION-LEDGER.json'),
    ('reasoning_firebreak_witness', 'FIREBREAK-LEDGER.json'),
    ('firebreak_witness', 'FIREBREAK-LEDGER.json'),
]:
    receipt[key] = json.loads(read(path))['items'][-1]
receipt['vocabulary_witness'] = {
    'witness_surface': 'WITNESS-VOCABULARY.json',
    'controlled_families': ['action_lane', 'gate_class', NEW_FAMILY],
    'target_surfaces': ['WITNESS-VOCABULARY.json', 'REVISION-RECEIPT.json', NEW_DOC],
    'ambient_synonyms_excluded': ['one-wide-view-means-two-axes', 'duplicate-partitions-count-twice', 'same-partition-restated-is-corroboration', 'axis-ish'],
    'comparability_budget': 'refresh-scope-axis truth is compared by token; the compact refresh-scope-axis witness says whether currently dispersed widening is still only one named family axis, is corroborated across independent axes, is still axis-gated from broader generalization, or is honestly mixed, while raw label matrices, axis inventories, topology maps, route trees, and long corroboration narratives stay in surrounding prose',
    'vocabulary_state': 'locked',
    'repair': 'ordinary-continuation',
    NEW_FAMILY: 'one-axis-dispersion|cross-axis-corroborated-dispersion|axis-gated-generalization|mixed-refresh-scope-axis'
}
receipt['counterfactual_shadow'] = {
    'status': 'rejected-nearby-move',
    'nearby_rejected_move': 'broader refresh-axis court / axis quorum / corroboration simplex',
    'pivot_surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}',
    'rejection_reason': 'current external pressure supports one compact one-axis-vs-cross-axis witness, not standing governance over axis independence or corroboration policy',
    'still_live': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}'
}
receipt['summary_highlight'] = 'crosscarry'
receipt['codename'] = 'vectorglass'
receipt['created_at'] = CREATED_AT
receipt['comparison_witness'] = {
    'previous_revision': PREV,
    'current_revision': REV,
    'current_pressure_id': 'FP-0151',
    'current_import_id': 'TL-0157',
    'basis_surface': 'docs/10-method/refresh-scope-distribution-witnesses-clustered-observed-spillover-dispersed-observed-spillover-and-distribution-gated-generalization.md',
    'delta_surface': NEW_DOC,
    'comparison_summary': 'rev0252 adds one compact refresh-scope-axis witness so dispersed widening across one named family axis no longer stands in for corroborated spread across independent axes.'
}
receipt['changes'] = [
    {'kind': 'canon', 'surface': NEW_DOC, 'summary': 'added one compact refresh-scope-axis witness with one-axis, cross-axis, axis-gated, and mixed states'},
    {'kind': 'quarantine', 'surface': f'docs/90-quarantine/wild-speculations-2026-03-08.md#{NEW_QWS}', 'summary': 'kept stronger refresh-axis governance quarantined rather than promoting it into canon'},
    {'kind': 'hygiene', 'surface': 'tools/packet_contract_common.py', 'summary': 'centralized named refresh-scope packet validators into a shared helper path and added an axis witness contract checker'}
]
receipt['receipt_freshness_witness'] = {
    'packaged_bundle_filename': BUNDLE,
    'manifest_timestamp_token': STAMP,
    'receipt_timestamp_token': STAMP,
    'bundle_stem_suffix_relation': 'slug ends with crosscarry + vectorglass and remains aligned to the current summary/codename pair while preserving the axisquarantine middle token',
    'current_import_id': 'TL-0157',
    'current_pressure_id': 'FP-0151',
    'change_anchor_surface': 'CHANGELOG.md',
    'freshness_state': 'current-aligned',
    'repair': 'ordinary-continuation'
}
receipt['question_posture_witness'] = {
    'resolution_surface': 'RESOLUTION-LEDGER.json',
    'registry_surface': 'docs/20-constitution/open-question-registry.md',
    'trajectory_surface': 'docs/00-meta/trajectory-map.md',
    'synced_resolved_questions': ['OQ-0147'],
    'frontier_selection_rule': 'resolved OQ-0147 is synchronized across resolution ledger, registry, and trajectory while frontier selection advances to OQ-0148',
    'posture_state': 'resolved-sync-current',
    'repair': 'ordinary-continuation'
}
receipt['current_import_id'] = 'TL-0157'
receipt['current_pressure_id'] = 'FP-0151'
receipt['import_witness'] = deepcopy(receipt['transfer_witness'])
receipt['new_classes_or_families'] = [NEW_FAMILY]
receipt['quarantined_non_take'] = ['refresh-axis court', 'axis quorum', 'corroboration simplex']
receipt['artifacts_touched'] = list(receipt['touched_surfaces'])
receipt['refresh_scope_axis_witness'] = {
    'witness_surface': NEW_DOC,
    'family': NEW_FAMILY,
    'state_tokens': ['one-axis-dispersion', 'cross-axis-corroborated-dispersion', 'axis-gated-generalization', 'mixed-refresh-scope-axis'],
    'overflow_rule': 'reopen-only-if-refresh-scope-axis-overflows'
}
receipt['refresh_scope_axis_witness_contract'] = {
    'family': NEW_FAMILY,
    'states': ['one-axis-dispersion', 'cross-axis-corroborated-dispersion', 'axis-gated-generalization', 'mixed-refresh-scope-axis']
}
receipt['refresh_scope_axis_witness_meta'] = {'checker': 'tools/check_refresh_scope_axis_witness_contract.py'}
write_json('REVISION-RECEIPT.json', receipt)

print('finalize_rev0252: OK')
