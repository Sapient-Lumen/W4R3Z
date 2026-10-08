import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
REGISTRY_PATH = ROOT / 'examples' / f'schema-fixture-domain-registry-{REV}.json'
SCHEMA_PATH = ROOT / 'schemas' / 'schema-fixture-domain-registry.schema.json'

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

registry = load(REGISTRY_PATH)

if Draft202012Validator is not None:
    schema = load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(registry), key=lambda e: list(e.path))
    if errors:
        raise SystemExit(f'{REGISTRY_PATH.relative_to(ROOT)} fails schema-fixture-domain-registry.schema.json: {errors[0].message}')

if registry.get('coverage_claim') not in {'registered-families-only','current-release-band','legacy-band-backfill','full-archive-corpus','mixed-current-plus-counts'}:
    raise SystemExit('registry coverage_claim missing or invalid')

seen = set()
fixture_dir = ROOT / 'fixtures' / 'negative-tests'
fixture_ids = {}
for path in fixture_dir.glob('*.json'):
    data = load(path)
    fid = data.get('fixture_id')
    if fid:
        fixture_ids[fid] = path

for fam in registry.get('families', []):
    fid = fam.get('family_id')
    if fid in seen:
        raise SystemExit(f'duplicate registry family_id: {fid}')
    seen.add(fid)
    for key in ['owner_surface', 'schema_path', 'example_path']:
        rel = fam.get(key)
        if not rel or not (ROOT / rel).exists():
            raise SystemExit(f'{fid} has missing {key}: {rel}')
    if not fam.get('domain') or '-' not in fam.get('domain'):
        raise SystemExit(f'{fid} has vague domain tag: {fam.get("domain")}')
    if not fam.get('lifecycle_axes'):
        raise SystemExit(f'{fid} lacks lifecycle axes')
    for fixture_id in fam.get('fixture_ids', []):
        if fixture_id not in fixture_ids:
            raise SystemExit(f'{fid} references unknown fixture_id: {fixture_id}')

counts = registry.get('audit_counts', {})
if counts.get('registered_families') != len(registry.get('families', [])):
    raise SystemExit('registry registered_families count does not match actual family count')
if counts.get('schemas', 0) != len(list((ROOT / 'schemas').glob('*.json'))):
    raise SystemExit('registry schema audit count is stale')
if counts.get('examples', 0) != len(list((ROOT / 'examples').glob('*.json'))):
    raise SystemExit('registry example audit count is stale')
if counts.get('negative_fixtures', 0) != len(list((ROOT / 'fixtures' / 'negative-tests').glob('*.json'))):
    raise SystemExit('registry fixture audit count is stale')
if registry.get('coverage_claim') == 'full-archive-corpus' and counts.get('registered_families') < counts.get('schemas', 0) // 2:
    raise SystemExit('registry claims full corpus coverage but family count is implausibly low')

required = {
    'LAB-EMPLOYMENT-STATUS', 'LAB-WAGE-TIME', 'LAB-WORKPLACE-SURVEILLANCE',
    'LAB-PROFESSIONAL-SERVICES', 'LAB-PLATFORM-WORK', 'LAB-BENEFITS-PORTABILITY',
    'META-SCHEMA-FIXTURE-REGISTRY',
    'CIVIL-STATUS-EVENT', 'DOMICILE-RESIDENCY', 'RELATIONSHIP-ASSOCIATION',
    'PUBLIC-SERVICE-INTAKE', 'CENSUS-PARTICIPATION-SAFEGUARD',
    'CIVIC-PARTICIPATION-RECORD', 'META-DOCTRINE-DEPENDENCY-MAP',
    'EXPRESSION-PLATFORM-MODERATION', 'EXPRESSION-REPUTATION-CORRECTION',
    'EXPRESSION-PERSONA-LIKENESS', 'EXPRESSION-COMMUNICATION-CONFIDENTIALITY',
    'EXPRESSION-CONTENT-PROVENANCE', 'EXPRESSION-SOCIAL-GRAPH-PORTABILITY',
    'META-RIGHTS-DOMAIN-COVERAGE-MAP',
    'META-FOLLOWTHROUGH-QUEUE', 'EMERGENCY-FIRST-TOUCH-ROUTING', 'EMERGENCY-CONTINUITY-ORDER', 'INCIDENT-STATE-PROFILE', 'EMERGENCY-CONTINUITY-DRILL', 'FEDERATED-NAMESPACE-CONTINUITY', 'SUCCESSOR-SUPERSESSION-TOPOLOGY', 'RESERVE-DEFAULT-REHABILITATION-LEDGER', 'WITNESS-POOL-ANTI-CAPTURE', 'LIVE-DRILL-EXECUTION-PACKET', 'DOWNSTREAM-RECALL-FORK-AFTERCARE', 'WELFARE-RESEARCH-SAFEGUARD', 'META-RESEARCH-TAIL-COMPACTION', 'WELFARE-SAFEGUARD-OPERATIONAL-HOOK', 'EXTERNAL-RECEIPT-SIMULATION-BUNDLE', 'EXTERNAL-RECEIPT-INTAKE-RECORD', 'WRSR-LIVE-EXERCISE-OUTCOME', 'EXTERNAL-RECEIPT-QUORUM-LEDGER', 'WRSR-RESULT-RETURN-RECEIPT', 'EXTERNAL-RECEIPT-REQUEST-PACKET', 'EXTERNAL-RECEIPT-RESPONSE-RECORD', 'RESPONSE-TO-INTAKE-CONVERSION-DRILL', 'ACTUAL-RECEIPT-IMPORT-GATE', 'FAILED-GATE-PUBLIC-SUMMARY', 'LIVE-COUNTERPARTY-IMPORT-ATTEMPT', 'QUORUM-RECOMPUTATION-REPORT', 'NONHOST-RESPONSE-ARTIFACT-ENVELOPE', 'LIVE-IMPORT-REPLAY-REPORT', 'LIVE-CLASS-LOCAL-IMPORT-REPLAY', 'COUNTERPARTY-ARTIFACT-CUSTODY-RECORD', 'RECEIPT-IMPORT-CHALLENGE-ROLLBACK', 'LIVE-RECEIPT-FLOOR-COMPUTED-SNAPSHOT', 'LIVE-RECEIPT-FLOOR-CONTROL-CASE', 'LIVE-ARTIFACT-IMPORT-FIELDKIT', 'ARTIFACT-IMPORT-INVARIANT-REPORT', 'LIVE-EVIDENCE-DROP-LEDGER', 'PRIVATE-EVIDENCE-VAULT-SPLIT', 'LIVE-ARTIFACT-CANDIDATE-CHALLENGE', 'COUNTERPARTY-ARTIFACT-CUSTODY-GATE', 'EXTERNAL-RECEIPT-RESPONSE-VERIFICATION-GATE', 'EXTERNAL-RECEIPT-INTAKE-CONVERSION-GATE', 'EXTERNAL-RECEIPT-IMPORT-READINESS-GATE', 'LIVE-RECEIPT-FLOOR-ACTIVATION-RECORD', 'LIVE-RECEIPT-QUORUM-PARTICIPATION-RECORD', 'LIVE-RECEIPT-FLOOR-RECOMPUTE-RECEIPT', 'LIVE-RECEIPT-PUBLICATION-ROLLBACK-ADJUDICATION', 'LIVE-RECEIPT-LATE-CHANGE-INGRESS', 'LIVE-RECEIPT-LATE-CHANGE-NOTICE-DISPATCH', 'LIVE-RECEIPT-LATE-CHANGE-REMEDY-RESOLUTION', 'LIVE-RECEIPT-LATE-CHANGE-REMEDY-EXECUTION'
}
missing = sorted(required - seen)
if missing:
    raise SystemExit(f'registry missing current required families: {missing}')

print('audit_schema_fixture_coverage: OK')
