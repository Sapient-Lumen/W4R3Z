#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    'START_HERE.md',
    'README.md',
    'CHANGELOG.md',
    'AGENTS.md',
    'CONTEXT-PACK.md',
    'REENTRY-CONTRACT.json',
    'SURFACE-STATUS.json',
    'REVISION-RECEIPT.json',
    'VALIDATION-INDEX.json',
    'docs/00-meta/datacube-lessons.md',
    'docs/00-meta/cloudtainer-only-contract.md',
    'docs/00-meta/related-work-research-pass-001.md',
    'docs/05-research/related-work-map.md',
    'docs/05-research/steal-bank.md',
    'docs/05-research/testing-facility-research-pass-002.md',
    'docs/10-contract/ambition-contract.md',
    'docs/10-contract/runtime-contract.md',
    'docs/10-contract/message-envelope-v1.md',
    'docs/10-contract/memory-ownership.md',
    'docs/10-contract/capability-tiers.md',
    'docs/20-architecture/borrowed-patterns-map.md',
    'docs/20-architecture/runtime-primitives.md',
    'docs/20-architecture/tradeoff-register.md',
    'docs/20-architecture/mesh-and-lifecycle.md',
    'docs/20-architecture/supervision-and-reconciliation.md',
    'docs/20-architecture/object-refs-and-data-plane.md',
    'docs/40-validation/validation-plan.md',
    'docs/40-validation/cloudtainer-test-economics.md',
    'docs/40-validation/test-facility-architecture.md',
    'docs/40-validation/test-pyramid-and-slices.md',
    'docs/40-validation/timing-budget-contract.md',
    'docs/40-validation/turn-start-procedure.md',
    'docs/40-validation/process-start-policy.md',
    'docs/40-validation/affected-selection-and-timing.md',
    'docs/40-validation/browser-harness-plan.md',
    'docs/40-validation/flake-and-chaos-policy.md',
    'docs/40-validation/benchmark-and-stress-policy.md',
    'docs/40-validation/test-artifact-policy.md',
    'docs/40-validation/capability-gated-testing.md',
    'docs/40-validation/test-surface-inventory.md',
    'docs/50-roadmap/ambition-frontier.md',
    'docs/50-roadmap/phase-roadmap.md',
    'docs/50-roadmap/testing-facility-roadmap.md',
    'docs/60-proof/phase-zero-executable-proof.md',
    'docs/90-open-questions.md',
    'src/browserrt.mjs',
    'src/agent-runtime.mjs',
    'src/agent-worker.mjs',
    'src/browser-agent-worker.mjs',
    'src/node-agent-worker.mjs',
    'src/test-facility.mjs',
    'src/types.d.ts',
    'test/smoke.mjs',
    'test/manifest.json',
    'test/impact-map.json',
    'test/surface-inventory.json',
    'test/quarantine.json',
    'test/harness-selftest.mjs',
    'tools/run_rev0005_proof.mjs',
    'tools/run_tests.mjs',
    'tools/plan_tests.mjs',
    'tools/validate_test_surface.mjs',
    'tools/analyze_tests.mjs',
    'tools/turn_bootstrap.mjs',
    'tools/package_release.py',
    'tools/verify_release.py',
    'artifacts/proof/REV0005-PROOF-RUN.json',
    'artifacts/validation/REV0005-TEST-HARNESS-RUN.json',
    'artifacts/validation/REV0005-TURN-BOOTSTRAP-RUN.json',
    'artifacts/validation/REV0005-TURN-SMOKE-RUN.json',
    'artifacts/validation/REV0005-TEST-SURFACE-REPORT.json',
    'artifacts/validation/REV0005-TEST-TIMING-HISTORY.json',
    'artifacts/validation/REV0005-TEST-ANALYSIS.json',
    'artifacts/research/TEST-FACILITY-RESEARCH-REGISTRY.json',
    'artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json',
]

FORBIDDEN_STALE_PATHS = [
    'tools/run_rev0004_proof.mjs',
    'artifacts/proof/REV0004-PROOF-RUN.json',
    'artifacts/validation/REV0004-TEST-HARNESS-RUN.json',
    'artifacts/validation/REV0004-TURN-BOOTSTRAP-RUN.json',
    'artifacts/validation/REV0004-TURN-SMOKE-RUN.json',
    'test/browserrt-test-inventory.json',
    'tools/check_timing_policy.mjs',
    'tools/explain_test_matrix.mjs',
    'docs/40-validation/browserrt-test-inventory.md',
]

REQUIRED_CONTEXT_SECTIONS = [
    '## Current orientation',
    '## Learned from example datacubes',
    '## Runtime north star',
    '## Frozen design pressures',
    '## Testing facility posture',
    '## Must-read set',
    '## Commands',
    '## Current non-claims',
]

REQUIRED_RUNTIME_STRINGS = [f'BR-INV-{i:03d}' for i in range(1, 10)]
REQUIRED_TEST_STRINGS = [f'BRT-TEST-{i:03d}' for i in range(1, 13)]
URL_RE = re.compile(r'https?://')
CHANGELOG_HEADING_RE = re.compile(r'^## (rev\d{4}) — (\d{4}-\d{2}-\d{2})$', re.M)


def fail(message: str) -> None:
    print(f'[check_cube] FAIL: {message}')
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f'[check_cube] OK: {message}')


def read_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def load_json(rel: str):
    try:
        return json.loads(read_text(rel))
    except Exception as exc:
        fail(f'{rel} is not valid JSON: {exc}')


def current_revision() -> str:
    return load_json('REVISION-RECEIPT.json').get('revision')


def check_required_files() -> None:
    missing = [rel for rel in REQUIRED_FILES if not (ROOT / rel).exists()]
    if missing:
        fail('missing required files: ' + ', '.join(missing))
    stale = [rel for rel in FORBIDDEN_STALE_PATHS if (ROOT / rel).exists()]
    if stale:
        fail('stale duplicate or obsolete surfaces found: ' + ', '.join(stale))
    ok(f'{len(REQUIRED_FILES)} required files present and stale surfaces absent')


def check_context_pack() -> None:
    rev = current_revision()
    txt = read_text('CONTEXT-PACK.md')
    for section in REQUIRED_CONTEXT_SECTIONS:
        if section not in txt:
            fail(f'CONTEXT-PACK.md missing {section}')
    changelog = read_text('CHANGELOG.md')
    headings = CHANGELOG_HEADING_RE.findall(changelog)
    if not headings:
        fail('CHANGELOG.md missing top revision heading')
    if headings[0][0] != rev:
        fail(f'CHANGELOG.md top revision {headings[0][0]} does not match receipt revision {rev}')
    if len([h for h in headings if h[0] == rev]) != 1:
        fail(f'CHANGELOG.md must contain exactly one {rev} heading')
    first = txt.splitlines()[0]
    expected = f'# BrowserRT context pack — {headings[0][0]} ({headings[0][1]})'
    if first != expected:
        fail(f'context pack first line mismatch: expected {expected!r}, got {first!r}')
    ok('context pack contract holds')


def check_contract_docs() -> None:
    runtime = read_text('docs/10-contract/runtime-contract.md')
    for needle in REQUIRED_RUNTIME_STRINGS:
        if needle not in runtime:
            fail(f'runtime contract missing invariant {needle}')
    tiers = read_text('docs/10-contract/capability-tiers.md')
    for tier in ['basic', 'workered', 'isolated', 'persistent', 'accelerated', 'mesh']:
        if tier not in tiers:
            fail(f'capability tiers missing {tier}')
    economics = read_text('docs/40-validation/cloudtainer-test-economics.md')
    for needle in REQUIRED_TEST_STRINGS:
        if needle not in economics:
            fail(f'test economics doc missing {needle}')
    for rel in ['docs/40-validation/process-start-policy.md', 'docs/40-validation/affected-selection-and-timing.md', 'docs/40-validation/browser-harness-plan.md']:
        if 'Revision: rev0005' not in read_text(rel):
            fail(f'{rel} missing rev0005 revision marker')
    ok('runtime and testing contract surfaces contain required invariants')


def check_json_alignment() -> None:
    receipt = load_json('REVISION-RECEIPT.json')
    status = load_json('SURFACE-STATUS.json')
    reentry = load_json('REENTRY-CONTRACT.json')
    validation = load_json('VALIDATION-INDEX.json')
    rev = receipt.get('revision')
    for name, obj in [('SURFACE-STATUS.json', status), ('REENTRY-CONTRACT.json', reentry), ('VALIDATION-INDEX.json', validation)]:
        if obj.get('revision') != rev:
            fail(f'{name} revision {obj.get("revision")} does not match receipt revision {rev}')
    if receipt.get('previous_revision') != 'rev0004':
        fail('REVISION-RECEIPT.json previous_revision must be rev0004')
    if not receipt.get('non_claims'):
        fail('REVISION-RECEIPT.json must preserve non_claims')
    ok('JSON revision alignment holds')


def check_no_external_urls_or_deps() -> None:
    offenders = []
    for path in ROOT.rglob('*'):
        if path.is_dir() or '.git' in path.parts or path.suffix == '.zip':
            continue
        try:
            txt = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        if URL_RE.search(txt):
            offenders.append(str(path.relative_to(ROOT)))
    if offenders:
        fail('external URL(s) found; cloudtainer-only cube forbids them: ' + ', '.join(offenders[:10]))
    pkg = load_json('package.json')
    if pkg.get('dependencies') not in ({}, None):
        fail('package.json dependencies must be empty')
    if pkg.get('devDependencies') not in ({}, None):
        fail('package.json devDependencies must be empty')
    ok('no external URLs or npm dependencies detected')


def check_related_work_surfaces() -> None:
    registry = load_json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json')
    if registry.get('revision') != current_revision():
        fail('related-work registry revision mismatch')
    titles = [src.get('title', '') for fam in registry.get('families', []) for src in fam.get('sources', [])]
    for required in ['Comlink', 'WebContainer API', 'Origin private file system', 'WebGPU API', 'Ray Core', 'Dask distributed scheduler', 'WebAssembly Component Model']:
        if required not in titles:
            fail(f'related-work registry missing {required}')
    txt = read_text('docs/20-architecture/borrowed-patterns-map.md')
    for needle in ['task', 'agent', 'object ref', 'supervisor', 'provider']:
        if needle not in txt:
            fail(f'borrowed patterns map missing vocabulary: {needle}')
    ok('related-work surfaces present and mapped')


def check_test_facility_surfaces() -> None:
    registry = load_json('artifacts/research/TEST-FACILITY-RESEARCH-REGISTRY.json')
    if registry.get('revision') != current_revision():
        fail('test-facility registry revision mismatch')
    titles = [src.get('title', '') for fam in registry.get('families', []) for src in fam.get('sources', [])]
    for required in ['Bazel Test Encyclopedia', 'Node.js test runner documentation', 'Playwright sharding documentation', 'Nx affected documentation', 'Turborepo remote caching documentation', 'pytest-xdist documentation', 'Vitest performance documentation', 'Web Platform Tests documentation', 'Chrome DevTools Protocol documentation', 'OpenTelemetry traces documentation']:
        if required not in titles:
            fail(f'test-facility registry missing {required}')
    manifest = load_json('test/manifest.json')
    if manifest.get('revision') != current_revision() or manifest.get('schema') != 2:
        fail('test manifest revision/schema mismatch')
    ids = [task.get('id') for task in manifest.get('tasks', [])]
    for required in ['cube:check', 'harness:selftest', 'harness:surface-inventory', 'runtime:smoke', 'proof:phase-zero-agent-supervisor']:
        if required not in ids:
            fail(f'test manifest missing task {required}')
    for task in manifest.get('tasks', []):
        for required_field in ['areas', 'size', 'isolation', 'flakiness', 'risk']:
            if required_field not in task:
                fail(f'{task.get("id")} missing {required_field}')
    impact = load_json('test/impact-map.json')
    inventory = load_json('test/surface-inventory.json')
    quarantine = load_json('test/quarantine.json')
    if impact.get('revision') != current_revision() or inventory.get('revision') != current_revision() or quarantine.get('revision') != current_revision():
        fail('test map/quarantine revision mismatch')
    harness = read_text('tools/run_tests.mjs')
    for needle in ['--tier', '--shard', '--jobs', '--json', '--changed', '--only-affected', '--dry-run', '--history', 'parallelGroup', 'timingSummary']:
        if needle not in harness:
            fail(f'test harness missing {needle}')
    for rel, needles in {
        'tools/plan_tests.mjs': ['explainImpact', 'impactedTaskIds'],
        'tools/validate_test_surface.mjs': ['validateSurfaceInventory', 'validateQuarantine'],
        'tools/analyze_tests.mjs': ['slowest', 'estimateMisses']
    }.items():
        txt = read_text(rel)
        for needle in needles:
            if needle not in txt:
                fail(f'{rel} missing {needle}')
    bootstrap = read_text('tools/turn_bootstrap.mjs')
    for needle in ['startLongLivedProcessesAcrossTurns', 'withinTurnReusableProcesses', 'processesToStartImmediatelyByDefault', 'recommended_next_commands']:
        if needle not in bootstrap:
            fail(f'turn bootstrap missing {needle}')
    ok('test facility surfaces present')


def check_executable_proof_surfaces() -> None:
    source = read_text('src/browserrt.mjs')
    for needle in ['createBootReport', 'createEnvelope', 'createTransferObjectRef', 'createTransferObject', 'WorkerAgent', 'Supervisor', 'object:transfer-ref', 'supervisor:restart']:
        if needle not in source:
            fail(f'executable proof source missing {needle}')
    smoke = read_text('test/smoke.mjs')
    for needle in ["assert.equal(REVISION, 'rev0005')", "supervisor.call('crash-now'", 'transferObject.buffer.byteLength, 0']:
        if needle not in smoke:
            fail(f'smoke proof missing {needle}')
    proof_runner = read_text('tools/run_rev0005_proof.mjs')
    for needle in ['REV0005-PROOF-RUN.json', 'rev0005-phase-zero-executable-proof', "assert.equal(proof.version, '0.0.5')"]:
        if needle not in proof_runner:
            fail(f'proof runner missing {needle}')
    proof_doc = read_text('docs/60-proof/phase-zero-executable-proof.md')
    for needle in ['boot report', 'bounded channel', 'worker agent', 'transferable object ref', 'supervisor restart']:
        if needle not in proof_doc:
            fail(f'phase-zero proof doc missing {needle}')
    ok('executable proof source surfaces present')


def check_executable_proof_artifact() -> None:
    proof = load_json('artifacts/proof/REV0005-PROOF-RUN.json')
    if proof.get('revision') != current_revision():
        fail('rev0005 proof artifact revision mismatch')
    if proof.get('proof_id') != 'rev0005-phase-zero-executable-proof':
        fail('rev0005 proof artifact has unexpected proof_id')
    observed = proof.get('observations', {})
    for key in ['agentPing', 'callerBufferDetached', 'crashRejected', 'supervisorRecovered']:
        if observed.get(key) is not True:
            fail(f'rev0005 proof observation not true: {key}')
    if observed.get('supervisorRestartCount') != 1:
        fail('rev0005 proof must show exactly one supervisor restart')
    required = set(proof.get('required_event_kinds', []))
    actual = set(proof.get('event_kinds', []))
    missing = sorted(required - actual)
    if missing:
        fail('rev0005 proof missing trace event kinds: ' + ', '.join(missing))
    ok('rev0005 executable proof artifact present and meaningful')


def check_test_artifacts() -> None:
    report = load_json('artifacts/validation/REV0005-TEST-HARNESS-RUN.json')
    if report.get('revision') != current_revision() or report.get('status') != 'passed':
        fail('test harness run not passed/current')
    task_ids = [task.get('id') for task in report.get('tasks', [])]
    for required in ['harness:selftest', 'harness:surface-inventory', 'runtime:smoke', 'proof:phase-zero-agent-supervisor']:
        if required not in task_ids:
            fail(f'test harness artifact missing task {required}')
    if not report.get('timingSummary'):
        fail('test harness report missing timingSummary')
    bootstrap = load_json('artifacts/validation/REV0005-TURN-BOOTSTRAP-RUN.json')
    if bootstrap.get('revision') != current_revision() or bootstrap.get('status') != 'passed':
        fail('turn bootstrap artifact not passed/current')
    smoke = load_json('artifacts/validation/REV0005-TURN-SMOKE-RUN.json')
    if smoke.get('revision') != current_revision() or smoke.get('status') != 'passed':
        fail('turn smoke artifact not passed/current')
    surface = load_json('artifacts/validation/REV0005-TEST-SURFACE-REPORT.json')
    if surface.get('revision') != current_revision() or surface.get('status') != 'passed':
        fail('surface report not passed/current')
    history = load_json('artifacts/validation/REV0005-TEST-TIMING-HISTORY.json')
    if not history.get('runs'):
        fail('timing history missing runs')
    analysis = load_json('artifacts/validation/REV0005-TEST-ANALYSIS.json')
    if analysis.get('revision') != current_revision() or analysis.get('status') != 'passed':
        fail('test analysis not passed/current')
    ok('test timing/surface artifacts present and passed')


def check_datacube_audit() -> None:
    audit = load_json('artifacts/datacube-audit/EXAMPLE-DATACUBE-REVIEW.json')
    if len(audit.get('examples', [])) != 3:
        fail('example datacube audit must describe three examples')
    for example in audit['examples']:
        if example.get('file_count', 0) <= 0:
            fail('example audit row missing file_count')
    ok('example datacube audit present')


def main() -> int:
    check_required_files()
    check_context_pack()
    check_contract_docs()
    check_json_alignment()
    check_no_external_urls_or_deps()
    check_datacube_audit()
    check_related_work_surfaces()
    check_test_facility_surfaces()
    check_executable_proof_surfaces()
    check_executable_proof_artifact()
    check_test_artifacts()
    ok('cube checks passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
