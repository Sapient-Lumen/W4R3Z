import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))['revision']

FAMILY_DESCRIPTIONS = {
    'hot_exam_recipient_followup_shells': 'Long serial branch history for hot-exam recipient follow-up, repair, rewatch, dewatch, route stability, standing, migration, and residue cases.',
    'packet_maintenance_envelopes': 'Portable and late-relapse branches for packet-maintenance envelopes, promotion, cooldown, breach, and ordinary restoration.',
    'after_hours_service_truth_profiles': 'Portable and late-relapse branches for after-hours service-truth profiles, missed-window handling, repair, republishing, and return sensitivity.',
    'hot_exam_closure_reopen_reclosure': 'Hot-exam proof mismatch, authoritative-update, reopen, reclosure, and official-disposition branches.',
    'override_child_branches': 'Override-row and child-branch splits for direct production, writing, protected access, and local hardening.',
    'hot_exam_family_children': 'Hot-exam family, modality, phase-band, and shared-publication child surfaces.',
    'hot_exam_status_notice': 'Hot-exam timing, notice, status vocabulary, transfer proof, and fulfillment status surfaces.',
    'hot_exam_delivery_request': 'Hot-exam bounded request, fulfillment, recipient confirmation, and delivery-evidence surfaces.',
    'recovery_authority_branches': 'Portable recovery-authority handback, review-window, substitute-path, and publication branches.',
    'hot_exam_modality_children': 'Hot-exam modality-child route failure, staffing, protected exposure, and incident-routing surfaces.',
    'hot_exam_late_outcomes': 'Official hot-exam late-outcome contestability, inspection, and learner-remedy surfaces.',
    'other_branch_history': 'Remaining branch-history surfaces that are still valid but should route through the family index before spawning siblings.',
}

PREFERRED_ENTRY = {
    'hot_exam_recipient_followup_shells': 'docs/20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md',
    'packet_maintenance_envelopes': 'docs/20-governance/portable-defaults-for-predeclared-packet-maintenance-envelopes.md',
    'after_hours_service_truth_profiles': 'docs/20-governance/portable-quantitative-bands-for-promoted-after-hours-service-truth-profiles.md',
    'hot_exam_closure_reopen_reclosure': 'docs/20-governance/first-proof-mismatch-and-reopen-defaults-for-hot-exam-closure-fields.md',
    'override_child_branches': 'docs/20-governance/profile-hardening-application-rows.md',
    'hot_exam_family_children': 'docs/20-governance/first-modality-child-splits-and-fallback-defaults-for-hot-exam-family-shells.md',
    'hot_exam_status_notice': 'docs/20-governance/first-status-vocabulary-and-escalation-crosswalk-defaults-for-hot-exam-notice-shells.md',
    'hot_exam_delivery_request': 'docs/20-governance/first-request-status-and-submission-state-defaults-for-hot-exam-bounded-request-shells.md',
    'recovery_authority_branches': 'docs/20-governance/portable-owner-facing-handback-packet-fields-for-recovery-authority-families.md',
    'hot_exam_modality_children': 'docs/20-governance/first-route-failure-staffing-and-publication-minima-for-hot-exam-modality-children.md',
    'hot_exam_late_outcomes': 'docs/20-governance/first-contestability-and-learner-facing-remedy-defaults-for-official-hot-exam-late-outcomes.md',
    'other_branch_history': 'docs/00-meta/branch-family-index-and-refactor-map.md',
}


def is_branch_path(path: Path) -> bool:
    return path.parent == ROOT / 'docs' / '20-governance' and re.match(r'^(first|portable|late-relapse)-', path.name) is not None


def family_for(rel: str) -> str:
    n = Path(rel).stem
    if 'hot-exam-recipient-followup-shells' in n:
        return 'hot_exam_recipient_followup_shells'
    if 'hot-exam-modality-children' in n:
        return 'hot_exam_modality_children'
    if 'hot-exam-family-shells' in n or 'named-hot-exam-family-children' in n or 'hot-exam-phase-bands' in n or 'exam-family-child-splits' in n:
        return 'hot_exam_family_children'
    if 'hot-exam-status-shells' in n or 'hot-exam-request-status-shells' in n or 'hot-exam-notice-shells' in n or 'hot-exam-timing-shells' in n:
        return 'hot_exam_status_notice'
    if 'hot-exam-late-outcome' in n or 'hot-exam-late-outcomes' in n:
        return 'hot_exam_late_outcomes'
    if 'hot-exam-closure-fields' in n or 'hot-exam-mismatch-shells' in n or 'hot-exam-reclosure-shells' in n or 'reopened-hot-exam-final-ordinary-shells' in n or 'hot-exam-authoritative-update-shells' in n:
        return 'hot_exam_closure_reopen_reclosure'
    if 'hot-exam-delivery-evidence-shells' in n or 'hot-exam-fulfillment-shells' in n or 'hot-exam-followup-shells' in n or 'hot-exam-bounded-request-shells' in n:
        return 'hot_exam_delivery_request'
    if 'after-hours-service-truth-profiles' in n:
        return 'after_hours_service_truth_profiles'
    if 'packet-maintenance-envelopes' in n:
        return 'packet_maintenance_envelopes'
    if 'recovery' in n:
        return 'recovery_authority_branches'
    if 'override-rows' in n or 'child-branches' in n or 'writing-override' in n or 'direct-production' in n or 'hot-direct-production' in n:
        return 'override_child_branches'
    return 'other_branch_history'


branch_paths = sorted(
    p.relative_to(ROOT).as_posix()
    for p in (ROOT / 'docs' / '20-governance').glob('*.md')
    if is_branch_path(p)
)
families_by_id = defaultdict(list)
for rel in branch_paths:
    families_by_id[family_for(rel)].append(rel)

families = []
for family_id in sorted(families_by_id, key=lambda k: (-len(families_by_id[k]), k)):
    paths = families_by_id[family_id]
    families.append({
        'family_id': family_id,
        'description': FAMILY_DESCRIPTIONS.get(family_id, family_id.replace('_', ' ')),
        'count': len(paths),
        'preferred_entry': PREFERRED_ENTRY.get(family_id, paths[0]),
        'canonical_compression': 'docs/20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md' if family_id.startswith('hot_exam') else 'docs/00-meta/branch-family-index-and-refactor-map.md',
        'refactor_posture': 'archive_in_place_with_family_index',
        'new_branch_rule': 'Search this family and the compression surface before creating another sibling. Add a new branch only for a genuinely new material pattern, not for the next ordinal relapse.',
        'paths': paths,
    })

payload = {
    'project': 'AI-EDU',
    'revision': REVISION,
    'status': 'branch-family-index',
    'generated_by': 'tools/gen_branch_family_index.py',
    'branch_detection_rule': 'Markdown files in docs/20-governance whose basename starts with first-, portable-, or late-relapse-.',
    'stats': {
        'branch_surfaces': len(branch_paths),
        'families': len(families),
        'largest_family': families[0]['family_id'] if families else None,
        'largest_family_count': families[0]['count'] if families else 0,
    },
    'families': families,
    'maintenance_note': 'This index is a retrieval/refactor layer. It does not move historical files and does not close FT-0181.'
}
(ROOT / 'BRANCH_FAMILY_INDEX.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'gen_branch_family_index: wrote {len(branch_paths)} branch surfaces in {len(families)} families')
