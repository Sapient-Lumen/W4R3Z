import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_DIR = ROOT / 'examples' / 'real-data-requests'
SCHEMA_PATH = ROOT / 'schemas' / 'real-data-request.schema.json'
SRC_ALLOWED = {'SRC2', 'SRC3', 'SRC4'}
STATUS_ALLOWED = {'draft', 'ready', 'sent', 'received', 'blocked'}
FORBIDDEN_HINTS = [
    'raw learner prompts', 'chat transcripts', 'diagnosis', 'disability', 'accommodation',
    'language-access', 'hardship', 'immigration', 'discipline', 'counselling', 'api keys',
    'exploit strings', 'system prompts', 'tool payloads', 'small subgroup', 'screenshots'
]
REQUIRED_DECISION_TERMS = ['authority', 'evidence', 'construct', 'public', 'protected', 'security']

REQUIRED_MICRO_PACKET_TERMS = [
    'service', 'owner', 'source system', 'date range', 'cohort', 'ai action',
    'fallback', 'incident', 'workload', 'training', 'public claim ceiling',
    'stop condition', 'redaction assertion', 'owner attestation'
]
DOWNSTREAM_COMPLETION_TERMS = [
    'completed owner packet workbench', 'completed first-packet decision board',
    'completed decision board', 'completed live-window', 'completed live window',
    'completed post-decision change ticket', 'completed end-of-window readout',
    'completed post-readout action', 'closure-ready', 'closeout minutes',
    'signoff quorum'
]


def fail(errors, rel, msg):
    errors.append(f'{rel}: {msg}')


def parse_date(value, errors, rel, field):
    try:
        date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date')


def nonempty(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0 and all(nonempty(v) for v in value)
    return value is not None


ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_ids = {item['id'] for item in ft_items}


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    data = json.loads(path.read_text(encoding='utf-8'))
    required = [
        'request_id', 'title', 'related_followthrough', 'status', 'source_truth_class_required',
        'first_sprint_scope', 'outreach_preflight', 'owner_reply_intake', 'minimum_packet_fields', 'prohibited_transfer_fields', 'owner_attestations',
        'acceptable_aggregate_metrics', 'decision_delta_questions', 'redaction_before_transfer',
        'stop_conditions', 'last_reviewed'
    ]
    for field in required:
        if field not in data or not nonempty(data[field]):
            fail(errors, rel, f'missing or empty {field}')
    if errors:
        return errors

    if not data['request_id'].startswith('RDR-'):
        fail(errors, rel, 'request_id must start RDR-')
    if data['related_followthrough'] not in ft_ids:
        fail(errors, rel, 'related_followthrough not found')
    if data['status'] not in STATUS_ALLOWED:
        fail(errors, rel, 'status invalid')
    if data['source_truth_class_required'] not in SRC_ALLOWED:
        fail(errors, rel, 'source_truth_class_required must be SRC2, SRC3, or SRC4')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')

    scope = data.get('first_sprint_scope', {})
    if not isinstance(scope, dict):
        fail(errors, rel, 'first_sprint_scope must be an object')
    else:
        for field in ['selected_service_record_id', 'fallback_service_record_id', 'scope_rule', 'packet_ceiling', 'field_survival_categories', 'fallback_conditions']:
            if field not in scope or not nonempty(scope[field]):
                fail(errors, rel, f'first_sprint_scope.{field} missing or empty')
        if scope.get('selected_service_record_id') == scope.get('fallback_service_record_id'):
            fail(errors, rel, 'first_sprint_scope selected and fallback services must differ')
        ceiling = scope.get('packet_ceiling', {})
        for key in ['services', 'date_ranges', 'source_systems']:
            if ceiling.get(key) != 1:
                fail(errors, rel, f'first_sprint_scope.packet_ceiling.{key} must be 1')
        if ceiling.get('owners') not in {1, 2}:
            fail(errors, rel, 'first_sprint_scope.packet_ceiling.owners must be 1 or 2')
        if ceiling.get('raw_learner_data_allowed') is not False:
            fail(errors, rel, 'first_sprint_scope must forbid raw learner data')
        survival_text = ' '.join(scope.get('field_survival_categories', [])).lower()
        for term in ['authority', 'evidence', 'construct', 'public', 'protected', 'security', 'trim']:
            if term not in survival_text:
                fail(errors, rel, f'first_sprint_scope.field_survival_categories missing {term}')
        fallback_text = ' '.join(scope.get('fallback_conditions', [])).lower()
        for term in ['raw learner', 'full export']:
            if term not in fallback_text:
                fail(errors, rel, f'first_sprint_scope.fallback_conditions missing {term}')


    preflight = data.get('outreach_preflight', {})
    if not isinstance(preflight, dict):
        fail(errors, rel, 'outreach_preflight must be an object')
    else:
        for field in ['first_contact_surface', 'selected_contact_service_id', 'first_owner_roles', 'why_this_service_first', 'owner_time_ceiling_minutes', 'response_clock', 'success_definition', 'silence_or_refusal_rule', 'do_not_wait_for']:
            if field not in preflight or not nonempty(preflight[field]):
                fail(errors, rel, f'outreach_preflight.{field} missing or empty')
        contact_surface = preflight.get('first_contact_surface', '')
        if contact_surface and not (ROOT / contact_surface).exists():
            fail(errors, rel, f'outreach_preflight.first_contact_surface does not exist: {contact_surface}')
        if preflight.get('selected_contact_service_id') != scope.get('selected_service_record_id'):
            fail(errors, rel, 'outreach_preflight.selected_contact_service_id must match first_sprint_scope.selected_service_record_id')
        if preflight.get('owner_time_ceiling_minutes', 999) > 10:
            fail(errors, rel, 'outreach_preflight.owner_time_ceiling_minutes must be 10 or less for a first owner reply')
        if len(preflight.get('first_owner_roles', [])) > 2:
            fail(errors, rel, 'outreach_preflight.first_owner_roles should name no more than two first-contact roles')
        role_text = ' '.join(preflight.get('first_owner_roles', [])).lower()
        for term in ['lms', 'integration', 'technical', 'vendor']:
            if term in role_text:
                fail(errors, rel, 'outreach_preflight.first_owner_roles must not require technical/vendor owners before the core reply')
        why_text = ' '.join(preflight.get('why_this_service_first', [])).lower()
        for term in ['staff', 'draft', 'aggregate']:
            if term not in why_text:
                fail(errors, rel, f'outreach_preflight.why_this_service_first missing {term}')
        clock = preflight.get('response_clock', {})
        if not isinstance(clock, dict):
            fail(errors, rel, 'outreach_preflight.response_clock must be an object')
        else:
            if clock.get('initial_response_business_days', 99) > 3:
                fail(errors, rel, 'outreach_preflight.response_clock.initial_response_business_days must be 3 or less for the core reply')
            if clock.get('follow_up_count') not in {0, 1}:
                fail(errors, rel, 'outreach_preflight.response_clock.follow_up_count must be 0 or 1')
            if clock.get('no_response_after_business_days', 99) > 7:
                fail(errors, rel, 'outreach_preflight.response_clock.no_response_after_business_days must be 7 or less for the core reply')
            if 'no-owner-packet' not in str(clock.get('default_no_response_outcome', '')).lower():
                fail(errors, rel, 'outreach_preflight.response_clock.default_no_response_outcome must record NO-OWNER-PACKET')
        refusal = preflight.get('silence_or_refusal_rule', '').lower()
        if 'do not' not in refusal or 'new control' not in refusal:
            fail(errors, rel, 'outreach_preflight.silence_or_refusal_rule must forbid new-control escalation from silence/refusal')
        wait_text = ' '.join(preflight.get('do_not_wait_for', [])).lower()
        for term in ['raw learner', 'full export', 'vendor']:
            if term not in wait_text:
                fail(errors, rel, f'outreach_preflight.do_not_wait_for missing {term}')



    intake = data.get('owner_reply_intake', {})
    if not isinstance(intake, dict):
        fail(errors, rel, 'owner_reply_intake must be an object')
    else:
        for field in ['reply_sheet_surface', 'reply_template_path', 'triage_tool_path', 'receipt_tool_path', 'receipt_output_rule', 'intake_tool_path', 'intake_bundle_output_rule', 'staging_tool_path', 'staging_note_template_path', 'smoke_tool_path', 'synthetic_smoke_fixture_path', 'workbench_seed_tool_path', 'workbench_seed_doc_surface', 'workbench_seed_output_rule', 'core_reply_rows', 'accepted_initial_outcomes', 'no_packet_outcome', 'intake_rules', 'local_only_exclusions', 'outcome_routes']:
            if field not in intake or not nonempty(intake[field]):
                fail(errors, rel, f'owner_reply_intake.{field} missing or empty')
        reply_surface = intake.get('reply_sheet_surface', '')
        if reply_surface and not (ROOT / reply_surface).exists():
            fail(errors, rel, f'owner_reply_intake.reply_sheet_surface does not exist: {reply_surface}')
        triage_tool = intake.get('triage_tool_path', '')
        if triage_tool:
            ttool = ROOT / triage_tool
            if not ttool.exists():
                fail(errors, rel, f'owner_reply_intake.triage_tool_path does not exist: {triage_tool}')
            elif ttool.name != 'triage_owner_reply_csv.py':
                fail(errors, rel, 'owner_reply_intake.triage_tool_path must point to triage_owner_reply_csv.py')
        receipt_tool = intake.get('receipt_tool_path', '')
        if receipt_tool:
            rtool = ROOT / receipt_tool
            if not rtool.exists():
                fail(errors, rel, f'owner_reply_intake.receipt_tool_path does not exist: {receipt_tool}')
            elif rtool.name != 'receipt_owner_reply_csv.py':
                fail(errors, rel, 'owner_reply_intake.receipt_tool_path must point to receipt_owner_reply_csv.py')
        receipt_rule = intake.get('receipt_output_rule', {})
        if not isinstance(receipt_rule, dict):
            fail(errors, rel, 'owner_reply_intake.receipt_output_rule must be an object')
        else:
            if receipt_rule.get('content_copied') is not False:
                fail(errors, rel, 'owner_reply_intake.receipt_output_rule.content_copied must be false')
            rr_text = ' '.join(str(v) for v in receipt_rule.values()).lower()
            for term in ['scratch', 'docs', 'examples', 'raw owner answers', 'not src2+', 'not closure evidence']:
                if term not in rr_text:
                    fail(errors, rel, f'owner_reply_intake.receipt_output_rule missing {term}')
        intake_tool = intake.get('intake_tool_path', '')
        if intake_tool:
            itool = ROOT / intake_tool
            if not itool.exists():
                fail(errors, rel, f'owner_reply_intake.intake_tool_path does not exist: {intake_tool}')
            elif itool.name != 'intake_owner_reply_csv.py':
                fail(errors, rel, 'owner_reply_intake.intake_tool_path must point to intake_owner_reply_csv.py')
        intake_rule = intake.get('intake_bundle_output_rule', {})
        if not isinstance(intake_rule, dict):
            fail(errors, rel, 'owner_reply_intake.intake_bundle_output_rule must be an object')
        else:
            if intake_rule.get('content_copied') is not False:
                fail(errors, rel, 'owner_reply_intake.intake_bundle_output_rule.content_copied must be false')
            for bool_field in ['writes_receipt', 'writes_triage', 'writes_staging_only_when_proceed_staged']:
                if intake_rule.get(bool_field) is not True:
                    fail(errors, rel, f'owner_reply_intake.intake_bundle_output_rule.{bool_field} must be true')
            ir_text = ' '.join(str(v) for v in intake_rule.values()).lower()
            for term in ['scratch', 'docs', 'examples', 'templates', 'tools', 'receipt', 'triage', 'raw owner answers', 'not src2+', 'not closure evidence', 'public claims']:
                if term not in ir_text:
                    fail(errors, rel, f'owner_reply_intake.intake_bundle_output_rule missing {term}')
        seed_tool = intake.get('workbench_seed_tool_path', '')
        if seed_tool:
            seed_path = ROOT / seed_tool
            if not seed_path.exists():
                fail(errors, rel, f'owner_reply_intake.workbench_seed_tool_path does not exist: {seed_tool}')
            elif seed_path.name != 'seed_owner_packet_workbench.py':
                fail(errors, rel, 'owner_reply_intake.workbench_seed_tool_path must point to seed_owner_packet_workbench.py')
        seed_surface = intake.get('workbench_seed_doc_surface', '')
        if seed_surface:
            seed_doc = ROOT / seed_surface
            if not seed_doc.exists():
                fail(errors, rel, f'owner_reply_intake.workbench_seed_doc_surface does not exist: {seed_surface}')
            else:
                seed_doc_text = seed_doc.read_text(encoding='utf-8').lower()
                for term in ['workbench seed', 'not_accepted', 'does not copy owner answers', 'ft-0181 remains live']:
                    if term not in seed_doc_text:
                        fail(errors, rel, f'owner_reply_intake.workbench_seed_doc_surface missing {term}')
        seed_rule = intake.get('workbench_seed_output_rule', {})
        if not isinstance(seed_rule, dict):
            fail(errors, rel, 'owner_reply_intake.workbench_seed_output_rule must be an object')
        else:
            if seed_rule.get('requires_proceed_staged') is not True:
                fail(errors, rel, 'owner_reply_intake.workbench_seed_output_rule.requires_proceed_staged must be true')
            if seed_rule.get('content_copied') is not False:
                fail(errors, rel, 'owner_reply_intake.workbench_seed_output_rule.content_copied must be false')
            if seed_rule.get('acceptance_state') != 'NOT_ACCEPTED':
                fail(errors, rel, 'owner_reply_intake.workbench_seed_output_rule.acceptance_state must be NOT_ACCEPTED')
            sr_text = ' '.join(str(v) for v in seed_rule.values()).lower()
            for term in ['scratch', 'docs', 'examples', 'templates', 'tools', 'proceed-staged', 'not_accepted', 'not src2+', 'not custody evidence', 'not closure evidence', 'public claims']:
                if term not in sr_text:
                    fail(errors, rel, f'owner_reply_intake.workbench_seed_output_rule missing {term}')
        staging_tool = intake.get('staging_tool_path', '')
        if staging_tool:
            stool = ROOT / staging_tool
            if not stool.exists():
                fail(errors, rel, f'owner_reply_intake.staging_tool_path does not exist: {staging_tool}')
            elif stool.name != 'stage_owner_reply_csv.py':
                fail(errors, rel, 'owner_reply_intake.staging_tool_path must point to stage_owner_reply_csv.py')

        smoke_tool = intake.get('smoke_tool_path', '')
        if smoke_tool:
            smtool = ROOT / smoke_tool
            if not smtool.exists():
                fail(errors, rel, f'owner_reply_intake.smoke_tool_path does not exist: {smoke_tool}')
            elif smtool.name != 'smoke_owner_reply_pipeline.py':
                fail(errors, rel, 'owner_reply_intake.smoke_tool_path must point to smoke_owner_reply_pipeline.py')
        smoke_fixture = intake.get('synthetic_smoke_fixture_path', '')
        if smoke_fixture:
            sfpath = ROOT / smoke_fixture
            if not sfpath.exists():
                fail(errors, rel, f'owner_reply_intake.synthetic_smoke_fixture_path does not exist: {smoke_fixture}')
            elif sfpath.suffix != '.csv':
                fail(errors, rel, 'owner_reply_intake.synthetic_smoke_fixture_path must point to a CSV fixture')
            elif 'fixtures/' not in smoke_fixture or 'smoke' not in smoke_fixture:
                fail(errors, rel, 'owner_reply_intake.synthetic_smoke_fixture_path must be a clearly labeled fixtures/...smoke CSV')
            else:
                smoke_text = sfpath.read_text(encoding='utf-8').lower()
                for term in ['synthetic smoke fixture', 'not a returned owner packet', 'not src2+ evidence', 'do not claim learning']:
                    if term not in smoke_text:
                        fail(errors, rel, f'owner_reply_intake.synthetic_smoke_fixture_path missing safety label: {term}')

        staging_template = intake.get('staging_note_template_path', '')
        if staging_template:
            spath = ROOT / staging_template
            if not spath.exists():
                fail(errors, rel, f'owner_reply_intake.staging_note_template_path does not exist: {staging_template}')
            else:
                stxt = spath.read_text(encoding='utf-8').lower()
                for term in ['proceed-staged', 'not closure evidence', 'owner packet workbench', 'ft-0181 remains live']:
                    if term not in stxt:
                        fail(errors, rel, f'owner_reply_intake.staging_note_template_path missing {term}')
        template_path = intake.get('reply_template_path', '')
        if template_path:
            tpath = ROOT / template_path
            if not tpath.exists():
                fail(errors, rel, f'owner_reply_intake.reply_template_path does not exist: {template_path}')
            elif tpath.suffix != '.csv':
                fail(errors, rel, 'owner_reply_intake.reply_template_path must point to a CSV template')
            else:
                with tpath.open(newline='', encoding='utf-8') as fh:
                    csv_rows = list(csv.DictReader(fh))
                expected_columns = {'row_id', 'required_owner_reply', 'owner_response', 'local_only_check', 'intake_note'}
                if set(csv_rows[0].keys() if csv_rows else []) != expected_columns:
                    fail(errors, rel, 'owner reply CSV template columns must be row_id, required_owner_reply, owner_response, local_only_check, intake_note')
                if len(csv_rows) != 8:
                    fail(errors, rel, 'owner reply CSV template must contain exactly eight owner rows')
                row_ids = [row.get('row_id') for row in csv_rows]
                if row_ids != [str(i) for i in range(1, 9)]:
                    fail(errors, rel, 'owner reply CSV template row_id values must be 1 through 8')
                if any(row.get('owner_response', '').strip() for row in csv_rows):
                    fail(errors, rel, 'owner reply CSV template must leave owner_response blank')
                csv_text = ' '.join((row.get('required_owner_reply', '') + ' ' + row.get('local_only_check', '') + ' ' + row.get('intake_note', '')).lower() for row in csv_rows)
                for term in ['service', 'owner', 'source', 'date range', 'aggregate', 'draft', 'fallback', 'rollback', 'workload', 'training', 'public claim', 'redaction', 'attestation']:
                    if term not in csv_text:
                        fail(errors, rel, f'owner reply CSV template missing {term}')
                for term in ['raw', 'protected', 'small cells', 'vendor']:
                    if term not in csv_text:
                        fail(errors, rel, f'owner reply CSV template local-only checks missing {term}')
        rows = intake.get('core_reply_rows', [])
        if len(rows) != 8:
            fail(errors, rel, 'owner_reply_intake.core_reply_rows must contain exactly eight rows')
        row_text = ' '.join(rows).lower()
        for term in ['service', 'owner', 'source', 'date range', 'aggregate', 'draft', 'fallback', 'rollback', 'workload', 'training', 'public claim', 'redaction', 'attestation']:
            if term not in row_text:
                fail(errors, rel, f'owner_reply_intake.core_reply_rows missing {term}')
        outcomes = set(intake.get('accepted_initial_outcomes', []))
        for outcome in ['PROCEED-STAGED', 'RE-ASK-ONCE', 'BLOCK-OVERBROAD', 'BLOCK-PROTECTED', 'BLOCK-AUTHORITY', 'BLOCK-SECURITY', 'BLOCK-EVIDENCE', 'NO-OWNER-PACKET']:
            if outcome not in outcomes:
                fail(errors, rel, f'owner_reply_intake.accepted_initial_outcomes missing {outcome}')
        no_packet = intake.get('no_packet_outcome', '').lower()
        if 'no-owner-packet' not in no_packet or 'new control' not in no_packet:
            fail(errors, rel, 'owner_reply_intake.no_packet_outcome must record NO-OWNER-PACKET and forbid new-control escalation')
        intake_text = ' '.join(intake.get('intake_rules', [])).lower()
        for term in ['eight-row', 'csv template', 'triage', 'triage_owner_reply_csv.py', 'receipt_owner_reply_csv.py', 'local receipt', 'intake_owner_reply_csv.py', 'intake bundle', 'seed_owner_packet_workbench.py', 'workbench seed', 'not_accepted', 'stage_owner_reply_csv.py', 'smoke_owner_reply_pipeline.py', 'synthetic fixture', 'proceed-staged note', 'downstream', 'raw learner', 'protected', 'full-export', 'new registry', 'workbench']:
            if term not in intake_text:
                fail(errors, rel, f'owner_reply_intake.intake_rules missing {term}')
        exclusion_text = ' '.join(intake.get('local_only_exclusions', [])).lower()
        for term in ['raw learner', 'protected', 'small cells', 'credentials', 'vendor']:
            if term not in exclusion_text:
                fail(errors, rel, f'owner_reply_intake.local_only_exclusions missing {term}')
        routes = intake.get('outcome_routes', [])
        route_outcomes = [route.get('outcome') for route in routes if isinstance(route, dict)]
        expected_outcomes = ['PROCEED-STAGED', 'RE-ASK-ONCE', 'NO-OWNER-PACKET', 'BLOCK-OVERBROAD', 'BLOCK-PROTECTED', 'BLOCK-SECURITY', 'BLOCK-AUTHORITY', 'BLOCK-EVIDENCE']
        if sorted(route_outcomes) != sorted(expected_outcomes):
            fail(errors, rel, 'owner_reply_intake.outcome_routes must map each accepted triage outcome exactly once')
        route_by_outcome = {route.get('outcome'): route for route in routes if isinstance(route, dict)}
        required_route_targets = {
            'PROCEED-STAGED': 'templates/ft0181-proceed-staged-note-template.md',
            'RE-ASK-ONCE': 'templates/ft0181-owner-reask-once-message.md',
            'NO-OWNER-PACKET': 'templates/ft0181-triage-outcome-note-template.md',
            'BLOCK-OVERBROAD': 'templates/ft0181-triage-outcome-note-template.md',
            'BLOCK-PROTECTED': 'templates/ft0181-triage-outcome-note-template.md',
            'BLOCK-SECURITY': 'templates/ft0181-triage-outcome-note-template.md',
            'BLOCK-AUTHORITY': 'templates/ft0181-triage-outcome-note-template.md',
            'BLOCK-EVIDENCE': 'templates/ft0181-triage-outcome-note-template.md',
        }
        for outcome, target in required_route_targets.items():
            route = route_by_outcome.get(outcome, {})
            if route.get('next_artifact') != target:
                fail(errors, rel, f'owner_reply_intake.outcome_routes {outcome} must route to {target}')
            if target and not (ROOT / target).exists():
                fail(errors, rel, f'owner_reply_intake.outcome_routes target missing: {target}')
            route_text = (route.get('action', '') + ' ' + route.get('no_widening_rule', '')).lower()
            if 'do not' not in route_text:
                fail(errors, rel, f'owner_reply_intake.outcome_routes {outcome} must include a do-not-widen rule')
        reask_text = (route_by_outcome.get('RE-ASK-ONCE', {}).get('action', '') + ' ' + route_by_outcome.get('RE-ASK-ONCE', {}).get('no_widening_rule', '')).lower()
        for term in ['one clarification', 'full export', 'new registry']:
            if term not in reask_text:
                fail(errors, rel, f'owner_reply_intake.RE-ASK-ONCE route missing {term}')
        proceed_text = (route_by_outcome.get('PROCEED-STAGED', {}).get('action', '') + ' ' + route_by_outcome.get('PROCEED-STAGED', {}).get('no_widening_rule', '')).lower()
        for term in ['stage_owner_reply_csv.py', 'proceed-staged note', 'minimized', 'workbench', 'raw rows']:
            if term not in proceed_text:
                fail(errors, rel, f'owner_reply_intake.PROCEED-STAGED route missing {term}')

    for field, minimum in [
        ('minimum_packet_fields', 4),
        ('prohibited_transfer_fields', 4),
        ('owner_attestations', 3),
        ('acceptable_aggregate_metrics', 3),
        ('decision_delta_questions', 3),
        ('redaction_before_transfer', 2),
        ('stop_conditions', 3),
    ]:
        if len(data.get(field, [])) < minimum:
            fail(errors, rel, f'{field} needs at least {minimum} entries')


    if data.get('status') == 'ready' and len(data.get('minimum_packet_fields', [])) > 8:
        fail(errors, rel, 'ready minimum_packet_fields must fit the eight-row owner reply sheet')

    prohibited_text = ' '.join(data.get('prohibited_transfer_fields', [])).lower()
    missing_hints = [hint for hint in FORBIDDEN_HINTS if hint not in prohibited_text]
    if len(missing_hints) > 5:
        fail(errors, rel, 'prohibited_transfer_fields does not cover enough protected/raw categories')

    minimum_text = ' '.join(data.get('minimum_packet_fields', [])).lower()
    missing_micro_terms = [term for term in REQUIRED_MICRO_PACKET_TERMS if term not in minimum_text]
    if missing_micro_terms:
        fail(errors, rel, 'minimum_packet_fields missing owner-reply terms: ' + ', '.join(missing_micro_terms))

    downstream_terms = [term for term in DOWNSTREAM_COMPLETION_TERMS if term in minimum_text]
    if downstream_terms:
        fail(errors, rel, 'minimum_packet_fields must be sendable and must not require downstream completion artifacts: ' + ', '.join(downstream_terms))

    question_text = ' '.join(data.get('decision_delta_questions', [])).lower()
    missing_terms = [term for term in REQUIRED_DECISION_TERMS if term not in question_text]
    if missing_terms:
        fail(errors, rel, 'decision_delta_questions missing terms: ' + ', '.join(missing_terms))

    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU minimum real data request packet':
    raise SystemExit('real data request schema title mismatch')

paths = sorted(REQUEST_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no real data request packets found')

all_errors = []
ready = 0
for path in paths:
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('status') == 'ready':
        ready += 1
    all_errors.extend(validate(path))

if ready == 0:
    all_errors.append('no real data request packet is ready')

if all_errors:
    raise SystemExit('real data request validation errors:\n' + '\n'.join(all_errors))
print(f'check_real_data_requests: OK ({len(paths)} requests, {ready} ready)')
