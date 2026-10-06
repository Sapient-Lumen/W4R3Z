#!/usr/bin/env node
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const execFileAsync = promisify(execFile);
const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-BROWSER-PROCESS-CLEANUP-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function isBrowserProcessRow(row) {
  const comm = String(row.comm || '');
  const args = String(row.args || '');
  if (/^(chromium|chrome|chrome_crashpad_handler|google-chrome)$/i.test(comm)) return true;
  if (/^(\/bin\/sh\s+)?(\/usr\/bin\/chromium|\/usr\/lib\/chromium\/chromium|\/opt\/google\/chrome\/chrome)(\s|$)/i.test(args)) return true;
  return false;
}

function parsePs(text) {
  const rows = [];
  for (const raw of text.split('\n')) {
    const line = raw.trim();
    if (!line) continue;
    const match = line.match(/^(\d+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s*(.*)$/);
    if (!match) continue;
    rows.push({ pid: Number(match[1]), ppid: Number(match[2]), pgid: Number(match[3]), stat: match[4], comm: match[5], args: match[6] || '' });
  }
  return rows;
}

export async function runAudit() {
  let psText = '';
  try {
    const { stdout } = await execFileAsync('ps', ['-eo', 'pid,ppid,pgid,stat,comm,args'], { maxBuffer: 1024 * 1024 });
    psText = stdout;
  } catch (error) {
    return {
      project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
      status: 'failed', generatedAt: new Date().toISOString(),
      purpose: 'Audit that managed BrowserRT Chromium/CDP probes did not leave BrowserRT-tagged browser processes alive in the cloudtainer.',
      error: { name: error?.name || 'Error', message: error?.message || String(error) },
      nonClaims: ['Process cleanup audit is a cloudtainer hygiene check only; it does not prove browser runtime semantics.']
    };
  }
  const rows = parsePs(psText);
  const browserRows = rows.filter((row) => isBrowserProcessRow(row));
  const managedRows = browserRows.filter((row) => /browserrt-|opfs-|kernel-kit|--remote-debugging-port/i.test(row.args) && /browserrt/i.test(row.args));
  const staleManagedRows = managedRows.filter((row) => !/browser_process_cleanup_audit/i.test(row.args));
  const checks = [
    { name: 'no-live-browserrt-managed-browser-processes', status: staleManagedRows.length === 0 ? 'passed' : 'failed', staleCount: staleManagedRows.length },
    { name: 'ps-readable', status: rows.length > 0 ? 'passed' : 'failed', rowCount: rows.length }
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(),
    purpose: 'Cloudtainer browser-process cleanup audit: catch BrowserRT-managed Chromium/CDP probe processes that remain alive after browser proofs or package-time validation.',
    counts: { processRows: rows.length, browserProcessRows: browserRows.length, browserRtManagedRows: managedRows.length, staleManagedRows: staleManagedRows.length },
    checks,
    staleManagedRows: staleManagedRows.map((row) => ({ pid: row.pid, ppid: row.ppid, pgid: row.pgid, stat: row.stat, comm: row.comm, args: row.args.slice(0, 500) })),
    browserProcessSample: browserRows.slice(0, 12).map((row) => ({ pid: row.pid, ppid: row.ppid, pgid: row.pgid, stat: row.stat, comm: row.comm, args: row.args.slice(0, 220) })),
    nonClaims: [
      'Cloudtainer process cleanup audit is a hygiene guard, not an OPFS durability or browser conformance proof.',
      'Only BrowserRT-tagged managed Chromium/CDP command lines with browser process names are treated as failure candidates; unrelated system browser processes and shell/status commands that merely mention browser terms are not controlled by this cube.',
      'Zombie processes without BrowserRT profile/debugging markers are reported only as browserProcessSample context.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else {
  console.log(JSON.stringify(report, null, 2));
}
if (report.status !== 'passed') process.exitCode = 1;
