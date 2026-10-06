#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { boot, REVISION, VERSION } from '../src/browserrt.mjs';

function normalizeTrace(events) {
  return events.map((event) => {
    const out = { kind: event.kind };
    for (const key of ['name', 'label', 'op', 'disposition', 'restartCount', 'transferCount', 'lane', 'priority', 'code']) {
      if (Object.hasOwn(event, key)) out[key] = event[key];
    }
    return out;
  });
}

export async function runProof() {
  const rt = await boot({ telemetry: 'always', proof: 'rev0005' });
  const report = rt.report;

  const channel = rt.channel({ label: 'proof-channel', capacity: 1, overflow: 'drop-oldest' });
  await channel.send('first');
  const channelOverflow = await channel.send('second');
  const channelValue = await channel.receive();

  const agent = await rt.spawnAgent({ name: 'proof-agent' });
  const ping = await agent.call('ping', { value: 'proof' });

  const buffer = new ArrayBuffer(16);
  new Uint32Array(buffer).set([3, 4, 5, 6]);
  const transfer = rt.transferObject(buffer, { id: 'transfer:proof', label: 'proof-sum' });
  const transferResult = await agent.call('sum-u32', {
    ref: transfer.ref,
    buffer: transfer.buffer
  }, {
    transfer: transfer.transferList,
    priority: 'user-blocking',
    lane: 'cpu'
  });
  const callerBufferDetached = buffer.byteLength === 0;
  await agent.terminate('proof-agent-done');

  const supervisor = rt.supervisor({ name: 'proof-supervisor', restartLimit: 2 });
  await supervisor.start();
  const before = await supervisor.call('ping', { value: 'before-crash' });
  let crashRejected = false;
  try {
    await supervisor.call('crash-now', { reason: 'rev0005 proof intentional crash' });
  } catch (error) {
    crashRejected = /exited|code 12|pending|closed/i.test(error.message);
  }
  const after = await supervisor.call('ping', { value: 'after-crash' });
  const supervisorSnapshot = supervisor.snapshot();
  await supervisor.close();

  const trace = rt.close();
  const eventKinds = trace.map((event) => event.kind);

  const proof = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    proof_id: 'rev0005-phase-zero-executable-proof',
    claims_checked: [
      'boot report emitted',
      'trace log records runtime and lane events',
      'bounded channel overflow is explicit',
      'worker agent handles ping call',
      'transferable object ref detaches ArrayBuffer at caller after transfer',
      'worker sums transferred ArrayBuffer contents',
      'supervisor restarts one failed worker agent'
    ],
    boot_report: {
      project: report.project,
      revision: report.revision,
      version: report.version,
      environment: report.environment,
      availableTierNames: report.availableTierNames,
      executableProofs: report.executableProofs
    },
    observations: {
      channelOverflow: channelOverflow.disposition,
      channelValue,
      agentPing: ping.pong === true && ping.payload?.value === 'proof',
      callerBufferDetached,
      transferSum: transferResult.sum,
      transferCount: transferResult.count,
      transferBytes: transferResult.bytes,
      transferRefId: transferResult.ref?.id ?? null,
      crashRejected,
      supervisorRestartCount: supervisorSnapshot.restartCount,
      supervisorRecovered: before.payload?.value === 'before-crash' && after.payload?.value === 'after-crash'
    },
    required_event_kinds: [
      'runtime:boot',
      'runtime:boot-report',
      'channel:create',
      'channel:send',
      'channel:receive',
      'object:transfer-ref',
      'agent:ready',
      'agent:call',
      'agent:result',
      'agent:exit',
      'supervisor:restart',
      'runtime:close'
    ],
    event_kinds: eventKinds,
    normalized_trace: normalizeTrace(trace)
  };

  assert.equal(proof.revision, 'rev0005');
  assert.equal(proof.version, '0.0.5');
  assert.equal(proof.boot_report.project, 'BrowserRT');
  assert.equal(proof.observations.channelOverflow, 'dropped-oldest');
  assert.equal(proof.observations.channelValue, 'second');
  assert.equal(proof.observations.agentPing, true);
  assert.equal(proof.observations.callerBufferDetached, true);
  assert.equal(proof.observations.transferSum, 18);
  assert.equal(proof.observations.transferCount, 4);
  assert.equal(proof.observations.transferBytes, 16);
  assert.equal(proof.observations.transferRefId, 'transfer:proof');
  assert.equal(proof.observations.crashRejected, true);
  assert.equal(proof.observations.supervisorRestartCount, 1);
  assert.equal(proof.observations.supervisorRecovered, true);
  for (const kind of proof.required_event_kinds) {
    assert.ok(proof.event_kinds.includes(kind), `missing trace kind ${kind}`);
  }
  return proof;
}

const args = new Set(process.argv.slice(2));
if (import.meta.url === `file://${process.argv[1]}`) {
  const proof = await runProof();
  if (args.has('--write')) {
    const out = 'artifacts/proof/REV0005-PROOF-RUN.json';
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(proof, null, 2) + '\n');
    console.log(out);
  } else {
    console.log('BrowserRT rev0005 executable proof passed');
  }
}
