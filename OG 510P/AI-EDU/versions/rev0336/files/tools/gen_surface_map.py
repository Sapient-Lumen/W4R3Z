import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVISION = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8')).get('revision', 'unknown')

AXES = [
    'actor',
    'stakes',
    'sector',
    'function',
    'risk_family',
    'memory_state',
    'proof_state',
    'lifecycle',
    'authority',
    'owner',
    'evidence_level',
    'portability',
]

SURFACE_TYPES = [
    'reentry', 'charter', 'schema', 'map', 'runbook', 'bibliography', 'core', 'governance',
    'procurement', 'grammar', 'profile', 'branch', 'compression', 'operations', 'template',
    'assessment', 'ledger', 'index', 'tooling', 'quarantine'
]

CURATED = {
    'README.md',
    'START_HERE.md',
    'AGENTS.md',
    'docs/00-meta/datacube-schema.md',
    'docs/00-meta/surface-map-overview.md',
    'docs/00-meta/reentry-navigation-map.md',
    'docs/00-meta/cube-refactor-audit-rev0224.md',
    'docs/00-meta/cube-refactor-audit-rev0225.md',
    'docs/00-meta/toolchain-registry-and-lint-plane-refactor.md',
    'docs/00-meta/cube-refactor-audit-rev0226.md',
    'docs/00-meta/branch-family-index-and-refactor-map.md',
    'docs/00-meta/schema-registry-and-json-plane-refactor.md',
    'docs/00-meta/cube-refactor-audit-rev0227.md',
    'docs/00-meta/surface-contracts-and-metadata-drift-audit.md',
    'docs/00-meta/cube-refactor-audit-rev0228.md',
    'docs/00-meta/cube-deep-audit-rev0229.md',
    'docs/00-meta/cube-deep-audit-rev0230.md',
    'docs/00-meta/cube-deep-audit-rev0231.md',
    'docs/00-meta/assumption-ledger-triage-rev0230.md',
    'docs/10-core/reference-model.md',
    'docs/20-governance/evidence-and-procurement.md',
    'docs/20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md',
    'docs/20-governance/ai-action-authority-register-and-delegation-ceilings.md',
    'docs/20-governance/cognitive-effort-budget-and-construct-preservation-defaults.md',
    'docs/20-governance/ai-companion-dependency-and-youth-safeguarding-defaults.md',
    'docs/20-governance/ai-service-bom-and-procurement-intake.md',
    'docs/20-governance/ai-service-security-red-team-and-agentic-tool-boundaries.md',
    'docs/30-operations/ai-service-intake-and-decision-record-template.md',
    'docs/20-governance/evidence-grade-and-claim-strength-ladder.md',
    'docs/30-operations/ai-implementation-review-cycle-and-stop-rules.md',
    'docs/40-assessment/construct-map-and-ai-use-disclosure-matrix.md',
    'docs/20-governance/claim-family-evidence-matrix.md',
    'docs/20-governance/education-ai-deployment-risk-crosswalk.md',
    'docs/20-governance/evidence-expiry-and-renewal-clocks.md',
    'docs/20-governance/action-authority-ceiling-backfill-for-high-risk-functions.md',
    'docs/30-operations/ai-pilot-packet-and-filled-examples.md',
    'docs/30-operations/ft0181-first-pilot-sprint-execution-pack.md',
    'docs/30-operations/ft0181-owner-import-action-kit.md',
    'docs/30-operations/ft0181-owner-field-request-and-micro-packet.md',
    'docs/30-operations/ft0181-eight-row-owner-reply-sheet.md',
    'docs/30-operations/ft0181-owner-request-packet-prep.md',
    'docs/30-operations/ft0181-first-contact-reminder-workflow-packet.md',
    'docs/40-assessment/construct-family-crosswalk-for-proof-profiles.md',
    'docs/20-governance/open-question-registry.md',
    'docs/20-governance/profile-hardening-template-for-starter-defaults.md',
    'docs/20-governance/profile-hardening-application-rows.md',
    'docs/20-governance/micro-change-cluster-reset-and-change-budget-defaults.md',
    'docs/30-operations/service-record-backtest-results-and-field-trim.md',
    'docs/30-operations/machine-readable-service-record-schema-and-validator.md',
    'docs/30-operations/public-pilot-summary-examples.md',
    'docs/30-operations/documented-reliance-and-burden-thresholds.md',
    'docs/30-operations/no-fault-transition-cost-absorption-and-fee-waiver-rules.md',
    'docs/30-operations/transition-cost-allocation-and-substitute-equivalent-coverage.md',
    'docs/30-operations/real-pilot-record-import-and-normalization-workflow.md',
    'docs/30-operations/import-readiness-manifest-and-no-real-data-gate.md',
    'docs/30-operations/pilot-source-data-dictionary-template.md',
    'docs/30-operations/real-import-acceptance-tests-and-reviewer-calibration.md',
    'docs/30-operations/minimum-real-data-request-packet.md',
    'docs/30-operations/import-negative-fixtures-and-failure-mode-catalog.md',
    'docs/30-operations/release-candidate-state-and-open-item-freeze.md',
    'docs/30-operations/decision-delta-log-template-and-field-pruning-rules.md',
    'docs/30-operations/public-summary-render-smoke-tests.md',
    'docs/30-operations/operator-handoff-and-maintainer-runbook.md',
    'docs/30-operations/service-lifecycle-deprecation-and-archive-exit-rules.md',
    'docs/20-governance/evaluator-independence-and-evidence-contamination-controls.md',
    'docs/30-operations/real-import-closeout-board-and-decision-minutes.md',
    'docs/20-governance/external-evidence-watchlist-and-source-triage.md',
    'docs/30-operations/sector-adapters-for-service-record-schema.md',
    'docs/30-operations/public-summary-redaction-profiles.md',
    'docs/30-operations/release-audit-trace-and-reproducibility-manifest.md',
    'docs/30-operations/synthetic-example-labeling-and-source-status-controls.md',
    'docs/30-operations/policy-exception-and-waiver-control.md',
    'docs/30-operations/ready-but-not-closed-assurance-case.md',
    'docs/30-operations/control-coverage-matrix-and-validator-trace.md',
    'docs/30-operations/evidence-refresh-calendar-and-staleness-gates.md',
    'docs/30-operations/human-signoff-quorum-and-conflict-attestation.md',
    'docs/30-operations/release-invariants-and-claim-boundaries.md',
    'docs/30-operations/artifact-dependency-graph-and-control-plane.md',
    'docs/30-operations/version-delta-manifest-and-change-accounting.md',
    'docs/30-operations/recovery-drills-for-false-closure-and-leakage.md',
    'docs/30-operations/ft0181-closure-evidence-checklist.md',
    'docs/30-operations/control-saturation-and-no-new-control-rule.md',
    'docs/30-operations/release-candidate-maintenance-mode-and-stale-gate-policy.md',
    'docs/30-operations/real-evidence-chain-of-custody-and-redaction-workbench.md',
    'docs/30-operations/public-claim-lexicon-and-forbidden-phrases.md',
    'docs/00-meta/cube-deep-audit-rev0242.md',
    'docs/00-meta/cube-deep-audit-rev0243.md',
    'docs/00-meta/cube-deep-audit-rev0245.md',
    'docs/00-meta/cube-deep-audit-rev0253.md',
    f'docs/00-meta/cube-deep-audit-{REVISION}.md',
    f'docs/00-meta/mission-kernel-{REVISION}.md',
    f'docs/00-meta/field-execution-risk-burndown-{REVISION}.md',
    f'docs/00-meta/pedagogy-forward-execution-refactor-{REVISION}.md',
    f'docs/00-meta/field-handoff-bundle-audit-{REVISION}.md',
    'docs/30-operations/field-handoff-bundle.md',
    'docs/30-operations/ft0181-owner-contact-send-pack.md',
    'docs/30-operations/teacher-tutor-augmentation-micro-pilot.md',
    'docs/30-operations/teacher-tutor-micro-pilot-run-card.md',
    'docs/30-operations/teacher-tutor-micro-pilot-next-action-router.md',
    'docs/30-operations/teacher-tutor-micro-pilot-owner-review-stop.md',
    'docs/30-operations/teacher-tutor-micro-pilot-result-recorder.md',
    'docs/00-meta/live-window-terminal-state-brief-refactor-rev0299.md',
    'docs/00-meta/owner-route-block-audit-rev0281.md',
    'docs/00-meta/live-window-card-gate-audit-rev0281.md',
    'docs/00-meta/charter.md',
    'docs/00-meta/post-readout-recheck-gate-audit-rev0288.md',
    'docs/00-meta/branch-tail-freeze-and-pruning-audit-rev0267.md',
    'docs/30-operations/ft0181-workbench-review-record.md',
    'docs/30-operations/ft0181-public-outcome-kernel.md',
    'docs/30-operations/ft0181-end-of-window-readout-disposition-gate.md',
    'docs/30-operations/ft0181-post-readout-action-dispatch.md',
    'docs/30-operations/ft0181-post-readout-recheck-gate.md',
    'docs/30-operations/ft0181-post-readout-context-receipt-gate.md',
}


QUALITY_NEEDS_REVIEW = {
    'docs/00-meta/bibliography.md',
    'docs/20-governance/open-question-registry.md',
    'docs/20-governance/open-question-archive-detail.md',
    'CHANGELOG.md',
}


def title_for(path: Path) -> str:
    text = path.read_text(encoding='utf-8')
    for line in text.splitlines():
        if line.startswith('# '):
            return line[2:].strip()
    return path.stem.replace('-', ' ').replace('_', ' ').title()


def add_unique(items, *vals):
    for val in vals:
        if isinstance(val, (list, tuple, set)):
            for sub in val:
                add_unique(items, sub)
        elif val and val not in items:
            items.append(val)


def classify(rel: str, title: str, text: str) -> dict:
    s = f'{rel} {title} {text[:5000]}'.lower()
    actor = []
    stakes = []
    sector = []
    function = []
    risk = []
    memory = []
    proof = []
    tags = []

    add_unique(actor, 'institution')
    add_unique(sector, 'cross_sector')
    add_unique(stakes, 'course_credit')
    add_unique(function, 'governance')
    add_unique(risk, 'automation_opacity')
    add_unique(memory, 'none')
    add_unique(proof, 'none')

    if any(k in s for k in ['student', 'learner', 'youth', 'minor']): add_unique(actor, 'student')
    if any(k in s for k in ['teacher', 'tutor', 'educator', 'staff']): add_unique(actor, 'teacher')
    if any(k in s for k in ['vendor', 'provider', 'model', 'procurement', 'service']): add_unique(actor, 'vendor')
    if any(k in s for k in ['assessment', 'exam', 'proof', 'grade', 'marking', 'qualification']): add_unique(actor, 'assessment_body')
    if any(k in s for k in ['support', 'accommodation', 'accessibility', 'wellbeing', 'safeguard']): add_unique(actor, 'support_owner')
    if any(k in s for k in ['record', 'transcript', 'official']): add_unique(actor, 'record_owner')
    if any(k in s for k in ['public', 'library', 'workforce', 'community', 'recognition', 'standing']): add_unique(actor, 'public_learner')

    if any(k in s for k in ['practice', 'low-stakes']): add_unique(stakes, 'practice')
    if any(k in s for k in ['exam', 'gateway', 'qualification', 'capstone']): add_unique(stakes, 'gateway_exam')
    if any(k in s for k in ['professional', 'licensure', 'certification']): add_unique(stakes, 'professional_gate')
    if any(k in s for k in ['public benefit', 'benefit', 'workforce', 'aid', 'fee', 'waiver']): add_unique(stakes, 'public_benefit')
    if any(k in s for k in ['accessibility', 'accommodation', 'disability', 'language access']): add_unique(stakes, 'accessibility')
    if any(k in s for k in ['discipline', 'misconduct', 'malpractice']): add_unique(stakes, 'discipline')
    if any(k in s for k in ['wellbeing', 'safeguarding', 'companion', 'emotional']): add_unique(stakes, 'wellbeing')

    if any(k in s for k in ['minor', 'primary', 'elementary']): add_unique(sector, 'primary')
    if any(k in s for k in ['secondary', 'high school', 'k-12', 'k12']): add_unique(sector, 'secondary')
    if any(k in s for k in ['higher', 'university', 'college']): add_unique(sector, 'higher_ed')
    if any(k in s for k in ['vet', 'vocational']): add_unique(sector, 'vet')
    if any(k in s for k in ['adult', 'lifelong']): add_unique(sector, 'adult_learning')
    if any(k in s for k in ['workforce']): add_unique(sector, 'public_workforce')
    if any(k in s for k in ['library', 'civic', 'community']): add_unique(sector, 'library_civic')

    function.clear()
    if any(k in s for k in ['tutor', 'study help', 'student-facing']): add_unique(function, 'tutoring')
    if any(k in s for k in ['feedback', 'draft', 'writing']): add_unique(function, 'feedback')
    if any(k in s for k in ['drafting', 'copilot']): add_unique(function, 'drafting')
    if any(k in s for k in ['grading', 'marking', 'score']): add_unique(function, 'grading_support')
    if any(k in s for k in ['advising', 'navigation']): add_unique(function, 'advising')
    if any(k in s for k in ['routing', 'queue', 'handoff']): add_unique(function, 'routing')
    if any(k in s for k in ['accessibility', 'accommodation', 'protected access']): add_unique(function, 'accessibility')
    if any(k in s for k in ['assessment', 'proof', 'exam', 'artifact', 'checkpoint', 'bundle']): add_unique(function, 'assessment_proof')
    if any(k in s for k in ['procurement', 'bill of materials', 'bom', 'vendor']): add_unique(function, 'procurement')
    if any(k in s for k in ['observability', 'retention', 'log', 'trace']): add_unique(function, 'observability')
    if any(k in s for k in ['memory', 'personalization', 'profile']): add_unique(function, 'memory')
    if any(k in s for k in ['failure', 'fallback', 'degrade', 'outage']): add_unique(function, 'failure')
    if any(k in s for k in ['change', 'release', 'model update', 'maintenance']): add_unique(function, 'change')
    if any(k in s for k in ['recognition', 'equivalency', 'standing', 'public learning']): add_unique(function, 'public_recognition')
    if any(k in s for k in ['source data dictionary', 'acceptance packet', 'import readiness', 'pilot import']): add_unique(function, 'import_governance')
    if any(k in s for k in ['security', 'red-team', 'prompt injection', 'tool', 'agentic']): add_unique(function, 'security')
    if any(k in s for k in ['evidence grade', 'claim strength', 'ev0', 'claim family', 'evidence watchlist']): add_unique(function, 'evidence_governance')
    if any(k in s for k in ['construct map', 'construct-first', 'disclosure matrix']): add_unique(function, 'assessment_proof')
    if not function: add_unique(function, 'governance')

    risk.clear()
    for key, val in [
        ('learning', 'learning_loss'), ('answer', 'answer_dependence'), ('privacy', 'privacy'),
        ('surveillance', 'surveillance'), ('bias', 'bias'), ('access', 'access_chill'),
        ('emotional', 'emotional_dependency'), ('labor', 'labor_shift'), ('opaque', 'automation_opacity'),
        ('security', 'security'), ('prompt injection', 'security'), ('tool misuse', 'security'),
        ('record', 'record_error'), ('contest', 'contestability'), ('appeal', 'contestability'), ('claim', 'evidence_laundering'), ('construct', 'construct_drift')
    ]:
        if key in s: add_unique(risk, val)
    if not risk: add_unique(risk, 'automation_opacity')

    memory.clear()
    if any(k in s for k in ['stateless', 'no memory']): add_unique(memory, 'none')
    if any(k in s for k in ['session']): add_unique(memory, 'session')
    if any(k in s for k in ['preference']): add_unique(memory, 'learner_declared_preference')
    if any(k in s for k in ['course memory', 'continuity']): add_unique(memory, 'bounded_course_continuity')
    if any(k in s for k in ['m3', 'human-owned record', 'record rail']): add_unique(memory, 'human_owned_record_rail')
    if any(k in s for k in ['predictive', 'profile']): add_unique(memory, 'predictive_profile')
    if any(k in s for k in ['protected', 'accommodation', 'disability']): add_unique(memory, 'protected_local_record')
    if any(k in s for k in ['residue', 'minimized', 'minimization']): add_unique(memory, 'minimized_residue')
    if not memory: add_unique(memory, 'none')

    proof.clear()
    if any(k in s for k in ['disclosure']): add_unique(proof, 'student_disclosure')
    if any(k in s for k in ['checkpoint']): add_unique(proof, 'checkpoint')
    if any(k in s for k in ['trace', 'log excerpt']): add_unique(proof, 'process_trace_excerpt')
    if any(k in s for k in ['oral defense', 'oral-defence']): add_unique(proof, 'oral_defense')
    if any(k in s for k in ['live transfer']): add_unique(proof, 'live_transfer')
    if any(k in s for k in ['bundle']): add_unique(proof, 'bundle')
    if any(k in s for k in ['official record', 'transcript', 'score report']): add_unique(proof, 'official_record')
    if any(k in s for k in ['protected evidence', 'protected route', 'accommodation']): add_unique(proof, 'protected_evidence')
    if any(k in s for k in ['local only', 'local-only', 'residue']): add_unique(proof, 'local_only_residue')
    if not proof: add_unique(proof, 'none')

    if rel in {'README.md', 'START_HERE.md', 'AGENTS.md'}:
        typ='reentry'; lifecycle='starter_default'; owner='archive_maintainer'; portability='canonical'; authority='advice_only'; evidence=['local_judgment']
    elif rel == 'CHANGELOG.md':
        typ='ledger'; lifecycle='settled'; owner='archive_maintainer'; portability='canonical'; authority='advice_only'; evidence=['local_judgment']
    elif rel == 'ARCHIVE_INDEX.md':
        typ='index'; lifecycle='starter_default'; owner='archive_maintainer'; portability='canonical'; authority='advice_only'; evidence=['local_judgment']
    elif 'bibliography' in rel:
        typ='bibliography'; lifecycle='starter_default'; owner='archive_maintainer'; portability='canonical'; authority='advice_only'; evidence=['external_standard','local_judgment']
    elif 'datacube-schema' in rel:
        typ='schema'; lifecycle='starter_default'; owner='archive_maintainer'; portability='canonical'; authority='advice_only'; evidence=['external_standard','local_judgment']
    elif 'surface-map-overview' in rel or 'reentry-navigation-map' in rel or 'branch-family-index-and-refactor-map' in rel or 'schema-registry-and-json-plane-refactor' in rel or 'toolchain-registry-and-lint-plane-refactor' in rel or 'surface-contracts-and-metadata-drift-audit' in rel:
        typ='tooling' if 'registry' in rel or 'surface-contracts' in rel else 'map'; lifecycle='starter_default'; owner='archive_maintainer'; portability='canonical'; authority='advice_only'; evidence=['EV7-OPERATIONAL-AUDIT','local_judgment']
    elif 'cube-refactor-audit' in rel or 'cube-deep-audit' in rel or 'assumption-ledger-triage' in rel:
        typ='map'; lifecycle='maintenance'; owner='archive_maintainer'; portability='canonical'; authority='advice_only'; evidence=['EV7-OPERATIONAL-AUDIT','local_judgment']
    elif 'runbook' in rel:
        typ='runbook'; lifecycle='starter_default'; owner='archive_maintainer'; portability='canonical'; authority='advice_only'; evidence=['local_judgment']
    elif 'charter' in rel:
        typ='charter'; lifecycle='settled'; owner='archive_maintainer'; portability='canonical'; authority='advice_only'; evidence=['local_judgment']
    elif 'serial-repair-cycle-compression' in rel:
        typ='compression'; lifecycle='compression'; owner='assessment_owner'; portability='branch_portable'; authority='human_only'; evidence=['external_standard','local_judgment']
    elif 'evidence-grade-and-claim-strength' in rel:
        typ='governance'; lifecycle='starter_default'; owner='service_owner'; portability='canonical'; authority='advice_only'; evidence=['EV0-ASSERTION','EV2-LOCAL-PILOT','EV6-STANDARD-OR-LAW','EV7-OPERATIONAL-AUDIT']
    elif 'ai-implementation-review-cycle' in rel:
        typ='operations'; lifecycle='starter_default'; owner='service_owner'; portability='starter'; authority='draft_for_review'; evidence=['EV2-LOCAL-PILOT','EV7-OPERATIONAL-AUDIT']
    elif 'minimum-real-data-request' in rel or 'import-negative-fixtures' in rel or 'release-candidate-state' in rel or 'release-audit-trace' in rel or 'synthetic-example-labeling' in rel or 'policy-exception' in rel or 'ready-but-not-closed-assurance' in rel or 'control-saturation' in rel or 'maintenance-mode' in rel or 'evidence-chain-of-custody' in rel or 'public-claim-lexicon' in rel:
        typ='operations'; lifecycle='starter_default'; owner='archive_maintainer'; portability='starter'; authority='advice_only'; evidence=['EV7-OPERATIONAL-AUDIT','local_judgment']
    elif 'construct-map-and-ai-use-disclosure' in rel:
        typ='assessment'; lifecycle='starter_default'; owner='assessment_owner'; portability='starter'; authority='human_only'; evidence=['EV6-STANDARD-OR-LAW','local_judgment']
    elif 'ai-service-bom' in rel or 'procurement' in rel:
        typ='procurement'; lifecycle='starter_default'; owner='service_owner'; portability='starter'; authority='human_only'; evidence=['external_standard','current_law_or_policy','local_judgment']
    elif 'security' in rel or 'red-team' in rel or 'agentic' in rel:
        typ='governance'; lifecycle='starter_default'; owner='service_owner'; portability='starter'; authority='human_only'; evidence=['external_standard','operational_audit']
    elif 'template' in rel:
        typ='template'; lifecycle='starter_default'; owner='service_owner'; portability='starter'; authority='advice_only'; evidence=['local_judgment']
    elif '/10-core/' in rel:
        typ='core'; lifecycle='settled'; owner='archive_maintainer'; portability='canonical'; authority='advice_only'; evidence=['external_standard','local_judgment']
    elif '/40-assessment/' in rel:
        typ='assessment'; lifecycle='starter_default'; owner='assessment_owner'; portability='starter'; authority='human_only'; evidence=['external_standard','local_judgment']
    elif '/30-operations/' in rel:
        typ='operations'; lifecycle='starter_default'; owner='service_owner'; portability='starter'; authority='draft_for_review'; evidence=['local_judgment']
    elif '/90-quarantine/' in rel:
        typ='quarantine'; lifecycle='quarantine'; owner='archive_maintainer'; portability='quarantine'; authority='advice_only'; evidence=['theory']
    elif '/20-governance/' in rel:
        typ='branch' if any(k in rel for k in ['first-', 'portable-', 'late-relapse']) else 'governance'
        lifecycle='branch_archive' if typ=='branch' else 'starter_default'
        owner='assessment_owner' if any(k in s for k in ['exam','assessment','proof','score']) else 'service_owner'
        portability='branch_portable' if typ=='branch' else 'starter'
        authority='human_only' if any(k in s for k in ['record','assessment','discipline','official','protected','queue']) else 'advice_only'
        evidence=['external_standard','local_judgment']
    else:
        typ='governance'; lifecycle='starter_default'; owner='archive_maintainer'; portability='starter'; authority='advice_only'; evidence=['local_judgment']

    if rel in CURATED: quality='human-curated'
    elif rel in QUALITY_NEEDS_REVIEW or typ == 'branch': quality='rule-assisted'
    else: quality='rule-assisted'

    if 'hot-exam' in rel or 'exam' in s: add_unique(tags, 'hot-exam')
    if typ == 'branch': add_unique(tags, 'branch-archive')
    if 'serial' in s or 'rewatch' in s or 'dewatch' in s: add_unique(tags, 'serial-repair')
    if 'service' in s or 'procurement' in s or 'bom' in s: add_unique(tags, 'service-intake')
    if 'source data dictionary' in s or 'acceptance packet' in s or 'real import' in s: add_unique(tags, 'real-import')
    if 'evidence watchlist' in s: add_unique(tags, 'evidence-watchlist')
    if 'evidence grade' in s or 'claim strength' in s or 'ev0' in s: add_unique(tags, 'evidence-grade')
    if 'construct map' in s or 'construct-first' in s: add_unique(tags, 'construct-map')
    if 'implementation review' in s or 'stop rule' in s: add_unique(tags, 'implementation-cycle')
    if 'security' in s or 'prompt injection' in s: add_unique(tags, 'security')
    if 'companion' in s or 'safeguard' in s: add_unique(tags, 'companion-safeguarding')
    if 'surface' in s or 'datacube' in s: add_unique(tags, 'datacube')
    if rel.startswith('docs/00-meta/'):
        meta_tags = ['datacube']
        if 'schema-registry' in rel or 'toolchain-registry' in rel or 'surface-contracts' in rel:
            add_unique(meta_tags, 'registry')
        if 'cube-refactor-audit' in rel or 'cube-deep-audit' in rel:
            add_unique(meta_tags, 'refactor-audit')
        if 'branch-family-index' in rel:
            add_unique(meta_tags, 'branch-family')
        if 'surface-map' in rel or 'reentry-navigation' in rel or 'trajectory-map' in rel:
            add_unique(meta_tags, 'navigation')
        if 'bibliography' in rel:
            add_unique(meta_tags, 'bibliography')
        if 'assumption-ledger-triage' in rel:
            add_unique(meta_tags, 'assumption-ledger')
        tags = meta_tags
    elif rel in {'README.md', 'START_HERE.md', 'AGENTS.md', 'ARCHIVE_INDEX.md'}:
        tags = [tag for tag in tags if tag != 'hot-exam']
        add_unique(tags, 'datacube')
    if not tags: add_unique(tags, typ)

    primary_tags = []
    if rel.startswith('docs/00-meta/'):
        primary_tags = list(tags)
    elif typ == 'branch':
        add_unique(primary_tags, 'branch-archive')
        if 'hot-exam' in rel or 'hot exam' in s:
            add_unique(primary_tags, 'hot-exam')
    elif rel in {'README.md', 'START_HERE.md', 'AGENTS.md', 'ARCHIVE_INDEX.md'}:
        add_unique(primary_tags, 'datacube')
    else:
        if 'ft0181' in rel or 'ft-0181' in s:
            add_unique(primary_tags, 'ft0181')
        if any(k in rel for k in ['real-pilot-record-import', 'real-import', 'minimum-real-data-request', 'pilot-source-data-dictionary', 'import-readiness', 'decision-delta', 'closure-evidence']):
            add_unique(primary_tags, 'real-import')
        if 'minimum-real-data-request' in rel:
            add_unique(primary_tags, 'security')
        if 'ft0181-first-pilot-sprint' in rel:
            add_unique(primary_tags, 'implementation-cycle')
        if 'evidence-grade-and-claim-strength' in rel or 'claim-family-evidence' in rel:
            add_unique(primary_tags, 'evidence-grade')
        if 'construct-map' in rel or 'construct-family' in rel or '/40-assessment/' in rel:
            add_unique(primary_tags, 'construct-map')
        if 'service' in rel or 'procurement' in rel or 'bom' in rel:
            add_unique(primary_tags, 'service-intake')
        if 'security' in rel or 'red-team' in rel:
            add_unique(primary_tags, 'security')
        if not primary_tags:
            add_unique(primary_tags, typ)

    mentioned_tags = [tag for tag in tags if tag not in primary_tags]
    tags = primary_tags + mentioned_tags

    return {
        'path': rel,
        'title': title,
        'type': typ,
        'actor': actor,
        'stakes': stakes,
        'sector': sector,
        'function': function,
        'risk_family': risk,
        'memory_state': memory,
        'proof_state': proof,
        'lifecycle': lifecycle,
        'authority': authority,
        'owner': owner,
        'evidence_level': evidence,
        'portability': portability,
        'followthrough': sorted(set(re.findall(r'FT-\d{4}', text))),
        'open_questions': sorted(set(re.findall(r'OQ-\d{4}', text))),
        'assumptions': sorted(set(re.findall(r'AS-\d{4}', text))),
        'tags': tags,
        'primary_tags': primary_tags,
        'mentioned_tags': mentioned_tags,
        'classification_quality': quality,
    }

surfaces=[]
for path in sorted(ROOT.rglob('*.md')):
    if any(part in {'__pycache__', 'scratch'} for part in path.parts):
        continue
    rel=path.relative_to(ROOT).as_posix()
    text=path.read_text(encoding='utf-8')
    surfaces.append(classify(rel, title_for(path), text))

payload={
    'project':'AI-EDU',
    'schema_surface':'docs/00-meta/datacube-schema.md',
    'overview_surface':'docs/00-meta/surface-map-overview.md',
    'revision_introduced':'rev0209',
    'last_full_backfill_revision':REVISION,
    'status':'comprehensive-index',
    'axes':AXES,
    'surface_types':SURFACE_TYPES,
    'classification_quality_values':['human-curated','rule-assisted','needs-review'],
    'surfaces':surfaces,
    'stats':{
        'markdown_surfaces':len(surfaces),
        'human_curated':sum(1 for s in surfaces if s['classification_quality']=='human-curated'),
        'rule_assisted':sum(1 for s in surfaces if s['classification_quality']=='rule-assisted'),
        'needs_review':sum(1 for s in surfaces if s['classification_quality']=='needs-review'),
    },
    'maintenance_note':'Every canonical Markdown file should appear exactly once. Rule-assisted rows are retrieval aids and should be hand-curated before decision-grade use.'
}
(ROOT/'SURFACES.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(f'gen_surface_map: wrote {len(surfaces)} markdown surfaces')
