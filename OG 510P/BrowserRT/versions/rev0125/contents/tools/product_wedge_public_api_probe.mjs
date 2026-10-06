#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/public-api.mjs';
import { runProductWedgeConsumer } from '../examples/product-wedge-consumer.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-PRODUCT-WEDGE-PUBLIC-API-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const report = await runProductWedgeConsumer();
  assert.equal(report.revision, REVISION);
  assert.equal(report.version, VERSION);
  assert.equal(report.status, 'passed', report.validation.errors.join('; '));
  assert.equal(report.receipt.proof.publicApiImportOnly, true);
  assert.equal(report.receipt.proof.storageLaneWriteRead, true);
  assert.equal(report.receipt.proof.traceReceiptClosed, true);
  return report;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runProbe();
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
}
