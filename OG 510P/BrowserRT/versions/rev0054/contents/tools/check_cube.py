#!/usr/bin/env python3
from __future__ import annotations
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def fail(msg: str):
    print(f'[check_cube] FAIL: {msg}')
    raise SystemExit(1)

def ok(msg: str): print(f'[check_cube] OK: {msg}')

def text(rel: str) -> str: return (ROOT / rel).read_text(encoding='utf-8')

def j(rel: str):
    try: return json.loads(text(rel))
    except Exception as exc: fail(f'{rel} invalid JSON: {exc}')

def require_file(rel: str):
    if not (ROOT / rel).exists(): fail(f'missing required file: {rel}')

def require_all(rel: str, needles: list[str]):
    body = text(rel)
    missing = [n for n in needles if n not in body]
    if missing: fail(f'{rel} missing {missing}')

def runtime_revision() -> tuple[str, str, str]:
    rt = text('src/browserrt.mjs')
    rev = re.search(r"export const REVISION = '([^']+)';", rt)
    ver = re.search(r"export const VERSION = '([^']+)';", rt)
    if not rev or not ver: fail('src/browserrt.mjs missing REVISION/VERSION constants')
    return rev.group(1), 'REV' + rev.group(1)[3:], ver.group(1)

REV, PFX, VERSION = runtime_revision()
PREV = f'rev{int(REV[3:])-1:04d}'

REQUIRED_FILES = [
  'README.md','START_HERE.md','CONTEXT-PACK.md','AGENTS.md','CHANGELOG.md','REVISION-RECEIPT.json','CUBE-META.json','REENTRY-CONTRACT.json','SURFACE-STATUS.json','VALIDATION-INDEX.json','package.json','src/browserrt.mjs','src/types.d.ts',
  'src/kernel-kit-demo.mjs','src/kernel-kit-demo-observatory.mjs','src/kernel-kit-demo-usefulness.mjs','demo/kernel-kit-demo.html','demo/kernel-kit-demo-runner.mjs','tools/browser_kernel_kit_demo_probe.mjs',
  'tools/kernel_kit_support_bundle_probe.mjs','tools/kernel_kit_support_bundle_contract_audit.mjs','tools/kernel_kit_support_bundle_import_probe.mjs','tools/kernel_kit_support_bundle_import_contract_audit.mjs','tools/kernel_kit_support_bundle_diff_probe.mjs','tools/kernel_kit_support_bundle_diff_contract_audit.mjs','tools/kernel_kit_guided_tour_probe.mjs','tools/kernel_kit_guided_tour_contract_audit.mjs','tools/kernel_kit_handoff_markdown_probe.mjs','tools/kernel_kit_handoff_markdown_contract_audit.mjs','tools/kernel_kit_handoff_markdown_probe.mjs','tools/kernel_kit_handoff_markdown_contract_audit.mjs',
  'docs/20-architecture/kernel-kit-support-bundle-import-frontier.md','docs/40-validation/kernel-kit-support-bundle-import-slice.md',f'docs/40-validation/kernel-kit-support-bundle-import-contract-audit-{REV}.md',f'docs/50-roadmap/kernel-kit-support-bundle-import-roadmap-{REV}.md',
  'docs/20-architecture/kernel-kit-guided-tour-frontier.md','docs/40-validation/kernel-kit-guided-tour-slice.md',f'docs/40-validation/kernel-kit-guided-tour-contract-audit-{REV}.md',f'docs/50-roadmap/kernel-kit-guided-tour-roadmap-{REV}.md',
  'docs/20-architecture/kernel-kit-support-bundle-diff-frontier.md','docs/40-validation/kernel-kit-support-bundle-diff-slice.md',f'docs/40-validation/kernel-kit-support-bundle-diff-contract-audit-{REV}.md',f'docs/50-roadmap/kernel-kit-support-bundle-diff-roadmap-{REV}.md',
  'src/kernel-kit-handoff-markdown.mjs','docs/20-architecture/kernel-kit-handoff-markdown-frontier.md','docs/40-validation/kernel-kit-handoff-markdown-slice.md',f'docs/40-validation/kernel-kit-handoff-markdown-contract-audit-{REV}.md',f'docs/50-roadmap/kernel-kit-handoff-markdown-roadmap-{REV}.md',
  'src/kernel-kit-handoff-reader.mjs','tools/kernel_kit_handoff_markdown_import_probe.mjs','tools/kernel_kit_handoff_markdown_import_contract_audit.mjs','docs/20-architecture/kernel-kit-handoff-markdown-import-frontier.md','docs/40-validation/kernel-kit-handoff-markdown-import-slice.md',f'docs/40-validation/kernel-kit-handoff-markdown-import-contract-audit-{REV}.md',f'docs/50-roadmap/kernel-kit-handoff-markdown-import-roadmap-{REV}.md',
  'src/kernel-kit-readiness-gate.mjs','tools/kernel_kit_readiness_gate_probe.mjs','tools/kernel_kit_readiness_gate_contract_audit.mjs','tools/kernel_kit_readiness_contrast_probe.mjs','tools/kernel_kit_readiness_contrast_contract_audit.mjs','docs/20-architecture/kernel-kit-readiness-gate-frontier.md','docs/40-validation/kernel-kit-readiness-gate-slice.md',f'docs/40-validation/kernel-kit-readiness-gate-contract-audit-{REV}.md',f'docs/50-roadmap/kernel-kit-readiness-gate-roadmap-{REV}.md',
  'src/kernel-kit-readiness-contrast.mjs','tools/kernel_kit_readiness_contrast_probe.mjs','tools/kernel_kit_readiness_contrast_contract_audit.mjs','docs/20-architecture/kernel-kit-readiness-contrast-frontier.md','docs/40-validation/kernel-kit-readiness-contrast-slice.md',f'docs/40-validation/kernel-kit-readiness-contrast-contract-audit-{REV}.md',f'docs/50-roadmap/kernel-kit-readiness-contrast-roadmap-{REV}.md',
  'test/manifest.json','test/impact-map.json','test/surface-inventory.json','test/quarantine.json','artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json','artifacts/research/TEST-FACILITY-RESEARCH-REGISTRY.json'
]

REQUIRED_TASKS = {
  'cube:audit-surfaces','cube:deep-audit','facility:foundation-audit','harness:selftest','runtime:smoke',
  'browser:kernel-kit-demo-proof','demo:kernel-kit-proof','demo:kernel-kit-observatory-proof','facility:kernel-kit-observatory-audit','demo:kernel-kit-trace-export-proof','facility:kernel-kit-trace-export-audit','demo:kernel-kit-usefulness-proof','facility:kernel-kit-usefulness-audit','demo:kernel-kit-failure-mode-proof','demo:kernel-kit-export-bundle-proof','demo:kernel-kit-trace-comparison-proof','facility:kernel-kit-trace-comparison-audit','demo:kernel-kit-diagnostic-runbook-proof','facility:kernel-kit-diagnostic-runbook-audit','demo:kernel-kit-support-bundle-proof','facility:kernel-kit-support-bundle-audit','demo:kernel-kit-support-bundle-import-proof','facility:kernel-kit-support-bundle-import-audit','demo:kernel-kit-support-bundle-diff-proof','facility:kernel-kit-support-bundle-diff-audit','demo:kernel-kit-guided-tour-proof','facility:kernel-kit-guided-tour-audit','demo:kernel-kit-handoff-markdown-proof','facility:kernel-kit-handoff-markdown-audit','demo:kernel-kit-handoff-markdown-import-proof','facility:kernel-kit-handoff-markdown-import-audit','demo:kernel-kit-readiness-gate-proof','facility:kernel-kit-readiness-gate-audit','demo:kernel-kit-readiness-contrast-proof','facility:kernel-kit-readiness-contrast-audit',
  'scheduler:storage-lane-overload-governance-model-proof','scheduler:storage-lane-admission-model-proof','scheduler:provider-resilience-model-proof','ipc:persisted-spill-compaction-proof','ipc:persisted-spill-recovery-proof'
}

NON_CLAIMS = [
  'No production runtime claim.','No production support-bundle claim.','No production support-bundle import claim.','No production support-bundle diff claim.','No production guided-tour claim.','No production support-bundle diff claim.','No automated failure triage claim.','No support-bundle authenticity or signature claim.','No automated demo correctness claim.','No automated regression detection claim.',
  'No production handoff-markdown import claim.','No production readiness-gate claim.','No production readiness-contrast claim.','No automated regression detection claim.','No automated demo-go/no-go claim.','No automated next-session correctness claim.','No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.','No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim.','No throughput, latency, SLO, or real performance claim.','No exactly-once delivery claim.'
]

def main() -> int:
    for rel in REQUIRED_FILES: require_file(rel)
    ok(f'{len(REQUIRED_FILES)} required files present')
    pkg = j('package.json')
    if pkg.get('version') != VERSION: fail(f'package version mismatch {pkg.get("version")} != {VERSION}')
    receipt = j('REVISION-RECEIPT.json')
    if receipt.get('revision') != REV: fail(f'REVISION-RECEIPT revision mismatch: {receipt.get("revision")} != {REV}')
    if receipt.get('previous_revision') != PREV: fail(f'previous revision mismatch: {receipt.get("previous_revision")} != {PREV}')
    for rel in ['CUBE-META.json','REENTRY-CONTRACT.json','SURFACE-STATUS.json','VALIDATION-INDEX.json','test/manifest.json','test/impact-map.json','test/surface-inventory.json','test/quarantine.json','artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json','artifacts/research/TEST-FACILITY-RESEARCH-REGISTRY.json']:
        obj = j(rel)
        if obj.get('revision') != REV: fail(f'{rel} revision mismatch: {obj.get("revision")} != {REV}')
    ok('revision alignment holds')
    require_all('src/kernel-kit-handoff-markdown.mjs', ['createKernelKitHandoffMarkdown','validateKernelKitHandoffMarkdown','browserrt-kernel-kit-handoff-markdown-v1','No production handoff-markdown claim.'])
    require_all('src/kernel-kit-handoff-reader.mjs', ['createKernelKitHandoffMarkdownImportReport','validateKernelKitHandoffMarkdownImportReport','browserrt-kernel-kit-handoff-markdown-import-v1','No production handoff-markdown import claim.'])
    require_all('src/kernel-kit-readiness-gate.mjs', ['createKernelKitReadinessGate','validateKernelKitReadinessGate','browserrt-kernel-kit-readiness-gate-v1','No production readiness-gate claim.','No automated demo-go/no-go claim.'])
    require_all('src/kernel-kit-readiness-contrast.mjs', ['createKernelKitReadinessContrast','validateKernelKitReadinessContrast','createDegradedKernelKitReadinessGate','browserrt-kernel-kit-readiness-contrast-v1','No production readiness-contrast claim.','No automated regression detection claim.'])
    require_all('src/kernel-kit-demo.mjs', ['createKernelKitSupportBundle','validateKernelKitSupportBundle','createKernelKitSupportBundleImportReport','validateKernelKitSupportBundleImportReport','createKernelKitSupportBundleDiff','validateKernelKitSupportBundleDiff','createKernelKitGuidedTourReceipt','validateKernelKitGuidedTourReceipt','browserrt-kernel-kit-support-bundle-v1','browserrt-kernel-kit-support-bundle-import-report-v1','browserrt-kernel-kit-support-bundle-diff-v1','browserrt-kernel-kit-guided-tour-v1','No production support-bundle import claim.','No production support-bundle diff claim.','No production guided-tour claim.','No production support-bundle diff claim.'])
    require_all('src/browserrt.mjs', ['kernelKitHandoffMarkdown','validateKernelKitHandoffMarkdown','KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT','kernelKitHandoffMarkdownImport','validateKernelKitHandoffMarkdownImportReport','KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT','kernelKitReadinessGate','validateKernelKitReadinessGate','KERNEL_KIT_READINESS_GATE_FORMAT','kernelKitReadinessContrast','validateKernelKitReadinessContrast','KERNEL_KIT_READINESS_CONTRAST_FORMAT'])
    require_all('src/browserrt.mjs', ['kernelKitSupportBundle','kernelKitSupportBundleImportReport','kernelKitGuidedTourReceipt','KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT','KERNEL_KIT_GUIDED_TOUR_FORMAT'])
    require_all('src/types.d.ts', ['KernelKitHandoffMarkdown','createKernelKitHandoffMarkdown','validateKernelKitHandoffMarkdown','KernelKitHandoffMarkdownImportReport','createKernelKitHandoffMarkdownImportReport','validateKernelKitHandoffMarkdownImportReport','KernelKitReadinessGate','createKernelKitReadinessGate','validateKernelKitReadinessGate','KernelKitReadinessContrast','createKernelKitReadinessContrast','validateKernelKitReadinessContrast'])
    require_all('src/types.d.ts', ['KernelKitSupportBundleImportReport','KernelKitSupportBundleDiff','KernelKitGuidedTourReceipt','createKernelKitSupportBundleImportReport','createKernelKitSupportBundleDiff','createKernelKitGuidedTourReceipt'])
    require_all('demo/kernel-kit-demo-runner.mjs', ['buildKernelKitHandoffMarkdown','renderKernelKitHandoffMarkdown','window.__BROWSERRT_KERNEL_KIT_HANDOFF_MARKDOWN','importKernelKitHandoffMarkdown','renderKernelKitHandoffMarkdownImportReport','window.__BROWSERRT_KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT','buildKernelKitReadinessGate','renderKernelKitReadinessGate','window.__BROWSERRT_KERNEL_KIT_READINESS_GATE','buildKernelKitReadinessContrast','renderKernelKitReadinessContrast','window.__BROWSERRT_KERNEL_KIT_READINESS_CONTRAST'])
    require_all('demo/kernel-kit-demo-runner.mjs', ['importKernelKitSupportBundle','diffKernelKitSupportBundle','runKernelKitGuidedTour','BrowserRTKernelKitDemo','window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_IMPORT','window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_DIFF','window.__BROWSERRT_KERNEL_KIT_GUIDED_TOUR'])
    require_all('demo/kernel-kit-demo.html', ['Build handoff Markdown','Validate handoff Markdown','kernel-kit-handoff-markdown-output','kernel-kit-handoff-markdown-import-input','kernel-kit-handoff-markdown-import-output','No production handoff-markdown claim.','No production handoff-markdown import claim.','No production readiness-gate claim.','No production readiness-contrast claim.','No automated regression detection claim.','No automated demo-go/no-go claim.'])
    require_all('demo/kernel-kit-demo.html', ['Validate pasted bundle','Diff pasted bundle','Run guided tour','kernel-kit-support-bundle-input','kernel-kit-support-diff-output','kernel-kit-guided-tour-output','No production runtime claim'])
    require_all('tools/browser_kernel_kit_demo_probe.mjs', ['BrowserRTKernelKitDemo.buildHandoffMarkdown','BrowserRTKernelKitDemo.importHandoffMarkdown','validateKernelKitHandoffMarkdown','validateKernelKitHandoffMarkdownImportReport','handoffMarkdownImport','BrowserRTKernelKitDemo.buildReadinessGate','validateKernelKitReadinessGate','readinessGate','BrowserRTKernelKitDemo.buildReadinessContrast','validateKernelKitReadinessContrast','readinessContrast'])
    require_all('tools/browser_kernel_kit_demo_probe.mjs', ['BrowserRTKernelKitDemo.importSupportBundle','BrowserRTKernelKitDemo.diffSupportBundle','BrowserRTKernelKitDemo.runGuidedTour','validateKernelKitSupportBundleImportReport','validateKernelKitSupportBundleDiff','validateKernelKitGuidedTourReceipt'])
    for rel in ['tools/kernel_kit_support_bundle_import_probe.mjs','tools/kernel_kit_support_bundle_import_contract_audit.mjs','tools/kernel_kit_support_bundle_diff_probe.mjs','tools/kernel_kit_support_bundle_diff_contract_audit.mjs','tools/kernel_kit_guided_tour_probe.mjs','tools/kernel_kit_guided_tour_contract_audit.mjs','tools/kernel_kit_handoff_markdown_probe.mjs','tools/kernel_kit_handoff_markdown_contract_audit.mjs','tools/kernel_kit_handoff_markdown_import_probe.mjs','tools/kernel_kit_handoff_markdown_import_contract_audit.mjs','tools/kernel_kit_readiness_gate_probe.mjs','tools/kernel_kit_readiness_gate_contract_audit.mjs','tools/kernel_kit_readiness_contrast_probe.mjs','tools/kernel_kit_readiness_contrast_contract_audit.mjs']:
        require_all(rel, ['No production', 'browserrt-kernel-kit'])
    ok('kernel-kit import/guided-tour source, page, tools, and types are wired')
    manifest = j('test/manifest.json')
    tasks = {t.get('id'): t for t in manifest.get('tasks', [])}
    missing = sorted(REQUIRED_TASKS - set(tasks))
    if missing: fail('manifest missing tasks: ' + ', '.join(missing))
    browser_release = [t['id'] for t in manifest.get('tasks', []) if 'release' in t.get('tiers', []) and t.get('lane') == 'browser']
    if browser_release: fail('release tier must remain browser-light: ' + ', '.join(browser_release))
    for t in manifest.get('tasks', []):
        for out in t.get('outputs', []):
            if re.search(r'artifacts/(audit|proof|validation)/REV\d{4}-', out) and PFX not in out:
                fail(f'{t.get("id")} stale output {out}')
        cmd = ' '.join(t.get('command', []))
        for hit in re.findall(r'REV\d{4}-', cmd):
            if hit != f'{PFX}-': fail(f'{t.get("id")} stale command prefix {hit}')
    ok('manifest tasks and browser-light release posture hold')
    impact_ids = {tid for r in j('test/impact-map.json').get('rules', []) for tid in r.get('taskIds', [])}
    inventory_ids = {tid for s in j('test/surface-inventory.json').get('surfaces', []) for tid in s.get('currentTaskIds', []) + s.get('manifestTasks', [])}
    for tid in ['demo:kernel-kit-support-bundle-import-proof','facility:kernel-kit-support-bundle-import-audit','demo:kernel-kit-support-bundle-diff-proof','facility:kernel-kit-support-bundle-diff-audit','demo:kernel-kit-guided-tour-proof','facility:kernel-kit-guided-tour-audit','demo:kernel-kit-handoff-markdown-proof','facility:kernel-kit-handoff-markdown-audit','demo:kernel-kit-handoff-markdown-import-proof','facility:kernel-kit-handoff-markdown-import-audit','demo:kernel-kit-readiness-gate-proof','facility:kernel-kit-readiness-gate-audit','demo:kernel-kit-readiness-contrast-proof','facility:kernel-kit-readiness-contrast-audit','browser:kernel-kit-demo-proof']:
        if tid not in impact_ids: fail(f'impact map missing {tid}')
        if tid not in inventory_ids: fail(f'surface inventory missing {tid}')
    ok('impact map and surface inventory cover current Kernel Kit surfaces')
    for rel in ['README.md','START_HERE.md','CONTEXT-PACK.md','AGENTS.md','REVISION-RECEIPT.json','docs/00-meta/future-session-office-manual.md','docs/00-meta/non-claims-and-goals-charter.md','docs/20-architecture/kernel-kit-support-bundle-import-frontier.md','docs/20-architecture/kernel-kit-guided-tour-frontier.md',f'docs/40-validation/kernel-kit-support-bundle-import-contract-audit-{REV}.md',f'docs/40-validation/kernel-kit-guided-tour-contract-audit-{REV}.md',f'docs/40-validation/kernel-kit-handoff-markdown-contract-audit-{REV}.md',f'docs/40-validation/kernel-kit-handoff-markdown-import-contract-audit-{REV}.md','docs/20-architecture/kernel-kit-readiness-gate-frontier.md',f'docs/40-validation/kernel-kit-readiness-gate-contract-audit-{REV}.md','docs/20-architecture/kernel-kit-readiness-contrast-frontier.md',f'docs/40-validation/kernel-kit-readiness-contrast-contract-audit-{REV}.md']:
        body = text(rel)
        missing = [n for n in NON_CLAIMS if n not in body]
        if missing: fail(f'{rel} missing non-claims: {missing}')
    ok('future-session docs and non-claims are legible')
    makefile = text('Makefile')
    stale = [p for p in re.findall(r'REV(\d{4})', makefile) if int(p) < int(REV[3:])]
    if stale: fail('Makefile contains stale explicit REV prefixes: ' + ', '.join(sorted(set(stale))))
    if '$(PFX)' not in makefile: fail('Makefile must use dynamic $(PFX) current artifact prefix')
    ok('Makefile currentness holds')
    print(f'[check_cube] PASS {REV} {VERSION}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
