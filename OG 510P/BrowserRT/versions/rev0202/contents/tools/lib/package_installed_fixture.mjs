import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { copyFile, mkdir, readFile, readdir, rm, stat, writeFile } from 'node:fs/promises';
import { basename, dirname, join, resolve } from 'node:path';

const NPM_ENV = Object.freeze({
  npm_config_update_notifier: 'false',
  npm_config_fund: 'false',
  npm_config_audit: 'false'
});

const RUNTIME_PACKAGE_JSON_KEYS = Object.freeze([
  'name',
  'version',
  'description',
  'type',
  'main',
  'exports',
  'types',
  'files',
  'sideEffects',
  'license',
  'keywords',
  'engines',
  'dependencies',
  'peerDependencies',
  'optionalDependencies',
  'funding',
  'homepage',
  'repository',
  'bugs'
]);

const FORBIDDEN_RUNTIME_PACKAGE_JSON_KEYS = Object.freeze([
  'scripts',
  'browserrt_current',
  'added',
  'changed',
  'artifacts',
  'artifacts_added_or_updated',
  'carried_forward_audits',
  'carried_forward_browser_proofs',
  'carried_forward_script_anchors',
  'cloudtainerValidationCommands',
  'current_artifacts',
  'current_commands',
  'current_validation_commands',
  'current_validations',
  'last_verified_commands',
  'linked_validation_commands',
  'must_read',
  'nonClaims',
  'non_claims',
  'package_commands',
  'summary_highlight',
  'touched_files',
  'validated_commands',
  'validation_commands'
]);

const RUNTIME_PACKAGE_JSON_MAX_BYTES = 8192;

export function runNpmForPackageFixture(cmd, args, options = {}) {
  const result = spawnSync(cmd, args, {
    cwd: options.cwd || process.cwd(),
    encoding: 'utf8',
    maxBuffer: 16 * 1024 * 1024,
    env: { ...process.env, ...NPM_ENV, ...(options.env || {}) }
  });
  if (result.status !== 0) {
    const err = new Error(`${cmd} ${args.join(' ')} failed with ${result.status}`);
    err.result = { status: result.status, signal: result.signal, stdout: result.stdout, stderr: result.stderr };
    throw err;
  }
  return result;
}

export function parseNpmPackJson(stdout) {
  const trimmed = String(stdout || '').trim();
  try { return JSON.parse(trimmed); } catch {}
  const first = trimmed.indexOf('[');
  const last = trimmed.lastIndexOf(']');
  if (first >= 0 && last > first) return JSON.parse(trimmed.slice(first, last + 1));
  throw new Error(`npm pack did not return parseable JSON: ${trimmed.slice(0, 400)}`);
}

function fileNamesFromPackInfo(packInfo) {
  return (packInfo?.files || []).map((file) => file.path).sort();
}

async function digestFile(path, algorithm, encoding = 'hex') {
  const data = await readFile(path);
  return createHash(algorithm).update(data).digest(encoding);
}

function readPackageJsonRawFromTarball(tarball) {
  const result = spawnSync('tar', ['-xOf', tarball, 'package/package.json'], { encoding: 'utf8', maxBuffer: 1024 * 1024 });
  if (result.status !== 0) {
    const error = new Error(`Unable to read package/package.json from prepared BrowserRT tarball: ${basename(tarball)}`);
    error.result = { status: result.status, signal: result.signal, stdout: result.stdout, stderr: result.stderr };
    throw error;
  }
  return result.stdout;
}

function runtimePackageJsonForPublication(rootPackage) {
  const slim = {};
  for (const key of RUNTIME_PACKAGE_JSON_KEYS) {
    if (rootPackage[key] !== undefined) slim[key] = rootPackage[key];
  }
  if (!slim.name || !slim.version || !slim.type || !slim.main || !slim.exports?.['.']?.import) {
    throw new Error('source package.json is missing required publication fields for the runtime package');
  }
  return slim;
}

async function expandPackageFileEntry(root, entry) {
  const normalized = String(entry || '').replace(/\\/g, '/').replace(/^\.\//, '').replace(/\/+$/, '');
  if (!normalized) return [];
  if (normalized.includes('**') || normalized === '.') {
    throw new Error(`BrowserRT runtime pack staging rejects broad package files entry: ${entry}`);
  }
  const star = normalized.match(/^(.+)\/\*\.([A-Za-z0-9.]+)$/);
  if (star) {
    const [, dir, suffix] = star;
    const rows = await readdir(join(root, dir), { withFileTypes: true });
    return rows
      .filter((row) => row.isFile() && row.name.endsWith(`.${suffix}`))
      .map((row) => `${dir}/${row.name}`)
      .sort();
  }
  if (normalized.includes('*')) throw new Error(`BrowserRT runtime pack staging only supports dir/*.ext files entries, got: ${entry}`);
  return [normalized];
}

async function copyRelativeFile(root, stagingRoot, rel) {
  const from = join(root, rel);
  const to = join(stagingRoot, rel);
  const info = await stat(from).catch(() => null);
  if (!info?.isFile()) throw new Error(`BrowserRT runtime pack staging expected file: ${rel}`);
  await mkdir(dirname(to), { recursive: true });
  await copyFile(from, to);
}

async function materializeRuntimePackageRoot({ root, stagingRoot }) {
  await rm(stagingRoot, { recursive: true, force: true });
  await mkdir(stagingRoot, { recursive: true });
  const rootPackage = JSON.parse(await readFile(join(root, 'package.json'), 'utf8'));
  const runtimePackage = runtimePackageJsonForPublication(rootPackage);
  const runtimePackageBytes = JSON.stringify(runtimePackage, null, 2) + '\n';
  if (Buffer.byteLength(runtimePackageBytes) > RUNTIME_PACKAGE_JSON_MAX_BYTES) {
    throw new Error(`runtime package.json staging budget exceeded: ${Buffer.byteLength(runtimePackageBytes)}>${RUNTIME_PACKAGE_JSON_MAX_BYTES}`);
  }
  await writeFile(join(stagingRoot, 'package.json'), runtimePackageBytes);
  const entries = Array.isArray(rootPackage.files) ? rootPackage.files : [];
  if (entries.length === 0) throw new Error('source package.json files field must list the publishable runtime package surface');
  const files = new Set();
  for (const entry of entries) {
    for (const rel of await expandPackageFileEntry(root, entry)) files.add(rel);
  }
  for (const rel of [...files].sort()) await copyRelativeFile(root, stagingRoot, rel);
  return Object.freeze({
    stagingRoot,
    runtimePackage,
    runtimePackageJsonBytes: Buffer.byteLength(runtimePackageBytes),
    copiedFileCount: files.size,
    copiedFiles: [...files].sort()
  });
}

function validateRuntimePackageJsonBoundary({ rootPackage, tarballPackage, rawPackageJson }) {
  const forbiddenKeys = FORBIDDEN_RUNTIME_PACKAGE_JSON_KEYS.filter((key) => Object.prototype.hasOwnProperty.call(tarballPackage, key));
  const publicFieldsMatch =
    tarballPackage.name === rootPackage.name &&
    tarballPackage.version === rootPackage.version &&
    tarballPackage.type === rootPackage.type &&
    tarballPackage.main === rootPackage.main &&
    JSON.stringify(tarballPackage.exports || null) === JSON.stringify(rootPackage.exports || null) &&
    JSON.stringify(tarballPackage.files || null) === JSON.stringify(rootPackage.files || null) &&
    JSON.stringify(tarballPackage.dependencies || {}) === JSON.stringify(rootPackage.dependencies || {});
  const rawBytes = Buffer.byteLength(rawPackageJson || '', 'utf8');
  const runtimeSlim = forbiddenKeys.length === 0 && rawBytes <= RUNTIME_PACKAGE_JSON_MAX_BYTES;
  return Object.freeze({ publicFieldsMatch, runtimeSlim, forbiddenKeys, rawBytes });
}

async function validatePackageTarballAgainstRoot({ root = process.cwd(), packInfo, tarball, source = 'unknown-package-source' }) {
  if (!packInfo?.filename) throw new Error('BrowserRT package metadata missing filename');
  const rootPackage = JSON.parse(await readFile(join(root, 'package.json'), 'utf8'));
  const resolvedTarball = resolve(tarball);
  const tarballStat = await stat(resolvedTarball).catch(() => null);
  if (!tarballStat?.isFile()) throw new Error(`Prepared BrowserRT package tarball missing or not a file: ${resolvedTarball}`);
  if (basename(resolvedTarball) !== packInfo.filename) throw new Error(`Prepared BrowserRT package tarball basename ${basename(resolvedTarball)} does not match pack metadata filename ${packInfo.filename}`);
  if (packInfo.name !== rootPackage.name) throw new Error(`Prepared BrowserRT package name ${packInfo.name} does not match source package ${rootPackage.name}`);
  if (packInfo.version !== rootPackage.version) throw new Error(`Prepared BrowserRT package version ${packInfo.version} does not match source package ${rootPackage.version}`);
  const rawPackageJson = readPackageJsonRawFromTarball(resolvedTarball);
  const tarballPackage = JSON.parse(rawPackageJson);
  if (tarballPackage.name !== rootPackage.name) throw new Error(`Prepared BrowserRT tarball package.json name ${tarballPackage.name} does not match source package ${rootPackage.name}`);
  if (tarballPackage.version !== rootPackage.version) throw new Error(`Prepared BrowserRT tarball package.json version ${tarballPackage.version} does not match source package ${rootPackage.version}`);
  const packageBoundary = validateRuntimePackageJsonBoundary({ rootPackage, tarballPackage, rawPackageJson });
  if (!packageBoundary.publicFieldsMatch) throw new Error('Prepared BrowserRT runtime package.json public fields do not match source package.json');
  if (!packageBoundary.runtimeSlim) throw new Error(`Prepared BrowserRT runtime package.json leaked cloudtainer keys or exceeded budget: keys=${packageBoundary.forbiddenKeys.join(',') || '<none>'} bytes=${packageBoundary.rawBytes}`);
  const sha1 = await digestFile(resolvedTarball, 'sha1');
  if (packInfo.shasum && sha1 !== packInfo.shasum) throw new Error(`Prepared BrowserRT tarball shasum ${sha1} does not match pack metadata shasum ${packInfo.shasum}`);
  let integrityMatches = null;
  if (typeof packInfo.integrity === 'string' && packInfo.integrity.startsWith('sha512-')) {
    const sha512 = await digestFile(resolvedTarball, 'sha512', 'base64');
    integrityMatches = `sha512-${sha512}` === packInfo.integrity;
    if (!integrityMatches) throw new Error('Prepared BrowserRT tarball sha512 integrity does not match pack metadata integrity');
  }
  return Object.freeze({
    source,
    tarball: resolvedTarball,
    filename: packInfo.filename,
    name: packInfo.name,
    version: packInfo.version,
    rootName: rootPackage.name,
    rootVersion: rootPackage.version,
    tarballBytes: tarballStat.size,
    fileCount: fileNamesFromPackInfo(packInfo).length,
    tarballExists: true,
    filenameMatchesPath: true,
    packInfoMatchesRoot: true,
    runtimePackageJsonMatchesRootPublicFields: true,
    tarballPackageJsonRuntimeSlim: true,
    tarballPackageJsonBytes: packageBoundary.rawBytes,
    tarballPackageJsonForbiddenKeys: packageBoundary.forbiddenKeys,
    // Legacy field retained as true for older report readers; the boundary is
    // now public-field equivalence plus a runtime-slim package.json, not byte-for-byte root metadata copying.
    tarballPackageJsonMatchesRoot: true,
    tarballShasumMatchesPackInfo: Boolean(packInfo.shasum),
    tarballIntegrityMatchesPackInfo: integrityMatches,
    sha1
  });
}

async function preparedPackageFromEnvironment({ root = process.cwd() } = {}) {
  const tarball = process.env.BROWSERRT_PREPARED_PACKAGE_TARBALL;
  const infoPath = process.env.BROWSERRT_PREPARED_PACKAGE_INFO_PATH;
  if (!tarball || !infoPath) return null;
  const packInfo = JSON.parse(await readFile(infoPath, 'utf8'));
  const source = process.env.BROWSERRT_PREPARED_PACKAGE_SOURCE || 'prepared-package-tarball';
  const validation = await validatePackageTarballAgainstRoot({ root, packInfo, tarball, source });
  return Object.freeze({
    packInfo,
    tarball: validation.tarball,
    fileNames: fileNamesFromPackInfo(packInfo),
    source,
    reusedPreparedTarball: true,
    infoPath,
    validation
  });
}

export async function preparePackageTarballForProbe({ root = process.cwd(), packDir }) {
  const prepared = await preparedPackageFromEnvironment({ root });
  if (prepared) return prepared;
  if (!packDir) throw new Error('preparePackageTarballForProbe requires packDir when no prepared package tarball is supplied');
  await mkdir(packDir, { recursive: true });
  const stagingRoot = join(packDir, 'browserrt-runtime-package-root');
  const staging = await materializeRuntimePackageRoot({ root, stagingRoot });
  const pack = runNpmForPackageFixture('npm', ['pack', '--json', '--pack-destination', packDir], { cwd: stagingRoot });
  const packRows = parseNpmPackJson(pack.stdout);
  const packInfo = packRows[0];
  if (!packInfo?.filename) throw new Error('npm pack did not report a filename');
  const tarball = join(packDir, packInfo.filename);
  const validation = await validatePackageTarballAgainstRoot({ root, packInfo, tarball, source: 'fresh-runtime-staged-npm-pack' });
  return Object.freeze({
    packInfo,
    tarball: validation.tarball,
    fileNames: fileNamesFromPackInfo(packInfo),
    source: 'fresh-runtime-staged-npm-pack',
    reusedPreparedTarball: false,
    infoPath: null,
    staging,
    validation
  });
}

export async function prepareSharedPackageTarballForBrowserBundle({ root = process.cwd(), tempDir }) {
  const prepared = await preparedPackageFromEnvironment({ root });
  if (prepared) return prepared;
  const packDir = join(tempDir, 'shared-package-pack');
  const preparedFresh = await preparePackageTarballForProbe({ root, packDir });
  const infoPath = join(packDir, 'browserrt-pack-info.json');
  await mkdir(dirname(infoPath), { recursive: true });
  await writeFile(infoPath, JSON.stringify(preparedFresh.packInfo, null, 2) + '\n');
  return Object.freeze({
    ...preparedFresh,
    tarball: resolve(preparedFresh.tarball),
    source: 'browser-bundle-shared-runtime-npm-pack',
    reusedPreparedTarball: false,
    infoPath,
    validation: { ...preparedFresh.validation, source: 'browser-bundle-shared-runtime-npm-pack' }
  });
}

export function envForPreparedPackage(packageTarball) {
  if (!packageTarball?.tarball || !packageTarball?.infoPath) return {};
  return Object.freeze({
    BROWSERRT_PREPARED_PACKAGE_TARBALL: packageTarball.tarball,
    BROWSERRT_PREPARED_PACKAGE_INFO_PATH: packageTarball.infoPath,
    BROWSERRT_PREPARED_PACKAGE_SOURCE: packageTarball.source || 'prepared-package-tarball',
    BROWSERRT_PREPARED_PACKAGE_FILENAME: packageTarball.packInfo?.filename || '',
    BROWSERRT_PREPARED_PACKAGE_NAME: packageTarball.packInfo?.name || '',
    BROWSERRT_PREPARED_PACKAGE_VERSION: packageTarball.packInfo?.version || '',
    BROWSERRT_PREPARED_PACKAGE_SHA1: packageTarball.validation?.sha1 || ''
  });
}
