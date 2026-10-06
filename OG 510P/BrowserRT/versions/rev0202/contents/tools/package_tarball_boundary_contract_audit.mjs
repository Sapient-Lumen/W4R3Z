#!/usr/bin/env node
// Manifest slice: facility:package-tarball-boundary-contract-audit. Fail-closed npm packlist and size-budget audit for BrowserRT's installed adoption wedge.
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { REVISION, VERSION } from '../src/public-api.mjs';
import { preparePackageTarballForProbe } from './lib/package_installed_fixture.mjs';

const REVISION_PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${REVISION_PREFIX}-PACKAGE-TARBALL-BOUNDARY-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const readJson = async (path) => JSON.parse(await readFile(path, 'utf8'));

const LIMITS = Object.freeze({
  fileCountMax: 75,
  packedBytesMax: 350_000,
  unpackedBytesMax: 1_800_000,
  srcBytesMax: 1_450_000,
  examplesBytesMax: 220_000,
  packageJsonBytesMax: 8_192,
  docsBytesMax: 25_000
});

const REQUIRED_FILES = Object.freeze([
  'package.json',
  'README.md',
  'START_HERE.md',
  'src/public-api.mjs',
  'src/public-api.d.ts',
  'src/runtime-core-public.mjs',
  'src/runtime-core-public.d.ts',
      'src/runtime-core-lane-adapter.mjs',
  'src/browser-storage-posture.mjs',
  'src/browser-storage-posture-public.d.ts',
  'src/browserrt.mjs',
  'src/types.d.ts',
  'src/product-wedge.mjs',
  'src/kernel-kit-demo.mjs',
  'examples/product-wedge-consumer.mjs',
  'examples/runtime-core-consumer.mjs',
  'examples/golden-workload-consumer.mjs',
  'examples/support-bundle-replay-consumer.mjs',
  'docs/10-architecture/product-wedge-public-api.md'
]);

const FORBIDDEN_PREFIXES = Object.freeze([
  'artifacts/',
  'demo/',
  'node_modules/',
  'test/',
  'tools/',
  'docs/00-meta/',
  'docs/20-architecture/',
  'docs/40-validation/'
]);

const PACKAGE_RUNTIME_ENTRYPOINTS = Object.freeze([
  'src/public-api.mjs',
  'src/runtime-core-public.mjs',
  'src/browser-storage-posture.mjs',
  'src/browser-agent-worker.mjs',
  'src/node-agent-worker.mjs'
]);

const PACKAGE_DECLARATION_FILES = Object.freeze([
  'src/browser-storage-posture-public.d.ts',
  'src/public-api.d.ts',
  'src/runtime-core-public.d.ts',
  'src/types.d.ts'
]);

function allowedPublishedPath(path) {
  return path === 'package.json' ||
    path === 'README.md' ||
    path === 'START_HERE.md' ||
    path === 'docs/10-architecture/product-wedge-public-api.md' ||
    /^src\/[^/]+\.(?:mjs|d\.ts)$/.test(path) ||
    /^examples\/[^/]+\.mjs$/.test(path);
}

function rootOf(path) {
  return path.includes('/') ? path.split('/')[0] : path;
}

function normalizePackageFileEntry(value) {
  return String(value || '').replace(/\\/g, '/').replace(/^\.\//, '').replace(/\/+$/, '');
}

function relativeImportTarget(fromPath, specifier) {
  if (!specifier.startsWith('./') || !specifier.endsWith('.mjs')) return null;
  return join(dirname(fromPath), specifier).replace(/\\/g, '/');
}

function sourceImportsFor(path, source) {
  const imports = new Set();
  const patterns = [
    /(?:import|export)\s+(?:[^'\"]*?\s+from\s+)?['\"](\.\/[^'\"]+)['\"]/g,
    /import\(['\"](\.\/[^'\"]+)['\"]\)/g
  ];
  for (const pattern of patterns) {
    for (const match of source.matchAll(pattern)) {
      const rel = relativeImportTarget(path, match[1]);
      if (rel) imports.add(rel);
    }
  }
  return [...imports].sort();
}

async function packageSourceClosure(root) {
  const seen = new Set();
  const stack = [...PACKAGE_RUNTIME_ENTRYPOINTS];
  while (stack.length > 0) {
    const rel = stack.pop();
    if (seen.has(rel)) continue;
    seen.add(rel);
    const source = await readFile(join(root, rel), 'utf8');
    for (const next of sourceImportsFor(rel, source)) stack.push(next);
  }
  return [...seen].sort();
}

function expectedPackageFilesFromClosure(closure) {
  return Object.freeze([
    ...closure,
    ...PACKAGE_DECLARATION_FILES,
    'examples/*.mjs',
    'README.md',
    'START_HERE.md',
    'docs/10-architecture/product-wedge-public-api.md'
  ]);
}

function packageFilesMatchExpected(pkgFiles, expected) {
  return JSON.stringify((pkgFiles || []).map(normalizePackageFileEntry)) === JSON.stringify(expected);
}

function isBroadPackageFileEntry(entry) {
  const normalized = normalizePackageFileEntry(entry);
  if (normalized === 'examples/*.mjs') return false;
  return normalized === '.' || normalized.includes('**') || normalized === 'src/*.mjs' || normalized === 'src/*.d.ts' || /^docs\/$/.test(normalized) || /^docs\/\*$/.test(normalized) || /^tools\//.test(normalized) || /^artifacts\//.test(normalized) || /^test\//.test(normalized) || /^demo\//.test(normalized) || normalized.includes('*');
}

function byteSummary(files) {
  const summary = Object.create(null);
  for (const file of files) summary[rootOf(file.path)] = (summary[rootOf(file.path)] || 0) + Number(file.size || 0);
  return Object.freeze(Object.fromEntries(Object.entries(summary).sort(([a], [b]) => a.localeCompare(b))));
}

function check(name, ok, details = {}) {
  return Object.freeze({ name, status: ok ? 'passed' : 'failed', ...details });
}

export async function runAudit() {
  const root = process.cwd();
  const workspace = await mkdtemp(join(tmpdir(), 'browserrt-package-tarball-boundary-'));
  const packDir = join(workspace, 'pack');
  try {
    await mkdir(packDir, { recursive: true });
    const prepared = await preparePackageTarballForProbe({ root, packDir });
    const { packInfo, fileNames } = prepared;
    const pkg = await readJson('package.json');
    const manifest = await readJson('test/manifest.json');
    const packageProbeNames = (await readdir('tools'))
      .filter((name) => /^package_installed_.*_probe\.mjs$/.test(name))
      .sort();
    const packageProbeTexts = Object.fromEntries(await Promise.all(packageProbeNames.map(async (name) => [name, await readFile(`tools/${name}`, 'utf8')])));
    const packageProbeFixtureViolations = packageProbeNames.filter((name) => {
      const text = packageProbeTexts[name] || '';
      return !text.includes('preparePackageTarballForProbe') ||
        !text.includes('runNpmForPackageFixture') ||
        text.includes("import { spawnSync } from 'node:child_process'") ||
        /\nfunction run\(/.test(text) ||
        /\nfunction parseNpmPackJson\(/.test(text);
    });
    const auditText = await readFile('tools/package_tarball_boundary_contract_audit.mjs', 'utf8');
    const publicAuditText = await readFile('tools/public_api_contract_audit.mjs', 'utf8');
    const publicApiText = await readFile('src/public-api.mjs', 'utf8');
    const taskById = (id) => (manifest.tasks || []).find((task) => task.id === id) || {};
    const boundaryTask = taskById('facility:package-tarball-boundary-contract-audit');
    const files = (packInfo.files || []).map((file) => Object.freeze({ path: file.path, size: Number(file.size || 0), mode: file.mode || null })).sort((a, b) => a.path.localeCompare(b.path));
    const roots = byteSummary(files);
    const missingRequired = REQUIRED_FILES.filter((name) => !fileNames.includes(name));
    const forbiddenFiles = fileNames.filter((name) => FORBIDDEN_PREFIXES.some((prefix) => name.startsWith(prefix)));
    const disallowedFiles = fileNames.filter((name) => !allowedPublishedPath(name));
    const rootReceiptLeaks = fileNames.filter((name) => /^REV\d{4}-LINKED-REVISION-RECEIPT\.json$|^REVISION-RECEIPT\.json$|^CUBE-META\.json$|^VALIDATION-INDEX\.json$|^SURFACE-STATUS\.json$|\.zip$|\.tgz$/.test(name));
    const sourceClosure = await packageSourceClosure(root);
    const expectedPackageFiles = expectedPackageFilesFromClosure(sourceClosure);
    const normalizedPackageFiles = (pkg.files || []).map(normalizePackageFileEntry);
    const broadFilesConfig = (pkg.files || []).filter(isBroadPackageFileEntry);
    const unusedPackedSourceFiles = fileNames.filter((name) => /^src\/[^/]+\.mjs$/.test(name) && !sourceClosure.includes(name));
    const missingClosureSourceFiles = sourceClosure.filter((name) => !fileNames.includes(name));

    const checks = [
      check('package-exports-root-public-api-and-runtime-core-subpath', pkg.exports?.['.']?.import === './src/public-api.mjs' && pkg.exports?.['.']?.types === './src/public-api.d.ts' && pkg.exports?.['./runtime-core']?.import === './src/runtime-core-public.mjs' && pkg.exports?.['./runtime-core']?.types === './src/runtime-core-public.d.ts' && pkg.exports?.['./browser-storage-posture']?.import === './src/browser-storage-posture.mjs' && pkg.exports?.['./browser-storage-posture']?.types === './src/browser-storage-posture-public.d.ts' && pkg.exports?.['./internal'] === undefined, { exports: pkg.exports }),
      check('package-root-browserrt-full-facade-is-lazy', !/from '\.\/browserrt\.mjs'/.test(publicApiText) && publicApiText.includes("await import('./browserrt.mjs')") && publicApiText.includes("from './runtime-core-public.mjs'"), { publicApiStaticBrowserRtImport: /from '\.\/browserrt\.mjs'/.test(publicApiText) }),
      check('package-files-config-is-narrow', Array.isArray(pkg.files) && broadFilesConfig.length === 0 && packageFilesMatchExpected(pkg.files, expectedPackageFiles), { filesConfig: normalizedPackageFiles, expectedPackageFiles, broadFilesConfig }),
      check('package-src-allowlist-matches-public-runtime-closure', unusedPackedSourceFiles.length === 0 && missingClosureSourceFiles.length === 0 && !normalizedPackageFiles.includes('src/*.mjs') && !normalizedPackageFiles.includes('src/*.d.ts'), { entrypoints: PACKAGE_RUNTIME_ENTRYPOINTS, dynamicWorkerEntrypoints: ['src/browser-agent-worker.mjs','src/node-agent-worker.mjs'], closureFileCount: sourceClosure.length, closureBytes: sourceClosure.reduce((sum, name) => sum + Number(files.find((file) => file.path === name)?.size || 0), 0), unusedPackedSourceFiles, missingClosureSourceFiles }),
      check('required-runtime-and-adoption-files-present', missingRequired.length === 0, { missingRequired }),
      check('forbidden-development-roots-absent', forbiddenFiles.length === 0, { forbiddenFiles: forbiddenFiles.slice(0, 20) }),
      check('published-paths-stay-in-allowed-roots', disallowedFiles.length === 0, { disallowedFiles: disallowedFiles.slice(0, 20) }),
      check('root-receipts-and-archives-not-packed', rootReceiptLeaks.length === 0, { rootReceiptLeaks }),
      check('tarball-file-count-budget', fileNames.length <= LIMITS.fileCountMax, { actual: fileNames.length, limit: LIMITS.fileCountMax }),
      check('tarball-packed-byte-budget', Number(packInfo.size || 0) <= LIMITS.packedBytesMax, { actual: Number(packInfo.size || 0), limit: LIMITS.packedBytesMax }),
      check('tarball-unpacked-byte-budget', Number(packInfo.unpackedSize || 0) <= LIMITS.unpackedBytesMax, { actual: Number(packInfo.unpackedSize || 0), limit: LIMITS.unpackedBytesMax }),
      check('src-byte-budget', Number(roots.src || 0) <= LIMITS.srcBytesMax, { actual: Number(roots.src || 0), limit: LIMITS.srcBytesMax }),
      check('examples-byte-budget', Number(roots.examples || 0) <= LIMITS.examplesBytesMax, { actual: Number(roots.examples || 0), limit: LIMITS.examplesBytesMax }),
      check('package-json-byte-budget', Number(roots['package.json'] || 0) <= LIMITS.packageJsonBytesMax, { actual: Number(roots['package.json'] || 0), limit: LIMITS.packageJsonBytesMax }),
      check('runtime-package-json-is-slim-staged-boundary', prepared.validation?.runtimePackageJsonMatchesRootPublicFields === true && prepared.validation?.tarballPackageJsonRuntimeSlim === true && (prepared.validation?.tarballPackageJsonForbiddenKeys || []).length === 0, { validation: prepared.validation }),
      check('docs-byte-budget', Number(roots.docs || 0) <= LIMITS.docsBytesMax, { actual: Number(roots.docs || 0), limit: LIMITS.docsBytesMax }),
      check('package-installed-probes-share-tarball-fixture',
        packageProbeNames.length >= 10 && packageProbeFixtureViolations.length === 0,
        { checkedProbeCount: packageProbeNames.length, packageProbeFixtureViolations }
      ),
      check('boundary-audit-registered-in-package-and-manifest',
        String(pkg.scripts?.['audit:package-tarball-boundary'] || '').includes('tools/package_tarball_boundary_contract_audit.mjs') &&
        Array.isArray(boundaryTask.command) && boundaryTask.command.includes('tools/package_tarball_boundary_contract_audit.mjs') &&
        Array.isArray(boundaryTask.inputs) && ['package.json','tools/package_tarball_boundary_contract_audit.mjs','tools/lib/package_installed_fixture.mjs','tools/package_installed_consumer_smoke_probe.mjs','tools/package_installed_browser_opfs_consumer_probe.mjs','tools/package_installed_browser_cross_tab_opfs_consumer_probe.mjs','tools/package_installed_browser_tab_close_opfs_consumer_probe.mjs'].every((item) => boundaryTask.inputs.includes(item)) &&
        Array.isArray(boundaryTask.outputs) && boundaryTask.outputs.includes(`artifacts/audit/${REVISION_PREFIX}-PACKAGE-TARBALL-BOUNDARY-CONTRACT-AUDIT.json`)
      ),
      check('public-api-audit-knows-package-boundary-audit',
        publicAuditText.includes('audit:package-tarball-boundary') && publicAuditText.includes('facility:package-tarball-boundary-contract-audit')
      ),
      check('browser-storage-posture-subpath-is-typed-and-packed', pkg.exports?.['./browser-storage-posture']?.import === './src/browser-storage-posture.mjs' && pkg.exports?.['./browser-storage-posture']?.types === './src/browser-storage-posture-public.d.ts' && fileNames.includes('src/browser-storage-posture.mjs') && fileNames.includes('src/browser-storage-posture-public.d.ts'), { export: pkg.exports?.['./browser-storage-posture'] || null }),
      check('audit-self-documents-current-budgets', auditText.includes('fileCountMax: 75') && auditText.includes('unpackedBytesMax: 1_800_000') && auditText.includes('packedBytesMax: 350_000') && auditText.includes('packageJsonBytesMax: 8_192') && auditText.includes('examplesBytesMax: 220_000') && auditText.includes('package-src-allowlist-matches-public-runtime-closure')),
      check('shared-package-fixture-materializes-runtime-package-root', auditText.includes('runtime-package-json-is-slim-staged-boundary') && (await readFile('tools/lib/package_installed_fixture.mjs', 'utf8')).includes('materializeRuntimePackageRoot') && (await readFile('tools/lib/package_installed_fixture.mjs', 'utf8')).includes('RUNTIME_PACKAGE_JSON_KEYS'))
    ];

    const failed = checks.filter((row) => row.status !== 'passed');
    assert.deepEqual(failed.map((row) => row.name), [], `package tarball boundary contract failed: ${failed.map((row) => row.name).join(', ')}`);
    return Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      status: 'passed',
      audit_id: `${REVISION}-package-tarball-boundary-contract-audit`,
      purpose: 'Fail-closed npm package boundary and size-budget audit: the installed adoption wedge must not silently pack tools, tests, artifacts, root receipts, broad docs, or unbounded source growth; src is allowlisted to public/runtime import closure, not broad-globbed.',
      package: Object.freeze({
        name: packInfo.name,
        version: packInfo.version,
        filename: packInfo.filename,
        source: prepared.source,
        reusedPreparedTarball: prepared.reusedPreparedTarball,
        packedBytes: Number(packInfo.size || 0),
        unpackedBytes: Number(packInfo.unpackedSize || 0),
        fileCount: fileNames.length,
        rootBytes: roots,
        largestFiles: files.slice().sort((a, b) => b.size - a.size).slice(0, 12)
      }),
      limits: LIMITS,
      requiredFiles: REQUIRED_FILES,
      forbiddenPrefixes: FORBIDDEN_PREFIXES,
      checks,
      nonClaims: Object.freeze([
        'This audit checks local npm pack output only; it does not publish to a registry, prove semver compatibility, run browser OPFS, reserve quota, survive eviction, or prove cross-browser behavior.',
        'The byte budgets are cloudtainer/adoption-wedge guardrails, not a product performance benchmark or bundle-size guarantee for downstream bundlers.'
      ])
    });
  } finally {
    await rm(workspace, { recursive: true, force: true });
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  try {
    const report = await runAudit();
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } catch (error) {
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', audit_id: `${REVISION}-package-tarball-boundary-contract-audit`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_tarball_boundary_contract_audit] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
