# Tradeoff register

This document records problems likely to arise if BrowserRT becomes ambitious.
It should be extended whenever a new attractive idea is added.

## T1: RPC friendliness versus hidden cost

Friendly worker APIs invite accidental structured cloning of huge objects.
Mitigation: RPC facade is cold-path only; hot paths require object refs or
explicit transfer policy.

## T2: Shared memory power versus deployment friction

SharedArrayBuffer unlocks fast shared-memory paths but depends on isolation and
resource headers. Mitigation: SAB is a capability tier; transferables remain the
baseline.

## T3: Work stealing versus data locality

Work stealing helps imbalance but can move work away from data owners. Mitigation:
object refs carry locality hints; actors can be pinned; queues expose steal
policy.

## T4: Cooperative scheduling versus stuck kernels

JavaScript tasks cannot be preempted like OS threads. Mitigation: cooperative
yield checkpoints for trusted kernels; killable worker boxes for untrusted or
non-cooperative kernels.

## T5: OPFS performance versus quota/eviction

OPFS is promising but storage is not infinite or permanent. Mitigation: quota
monitor, block checksums, manifest recovery, compaction, and non-claims about
user/browser deletion.

## T6: GPU acceleration versus variability

WebGPU can be fast, absent, disabled, device-lost, or slower than CPU for small
work. Mitigation: GPU is a lane with calibration, CPU fallback, and telemetry.

## T7: Cross-tab mesh versus lifecycle chaos

Tabs open, close, hide, throttle, crash, and reload. Mitigation: agent lifecycle,
heartbeats, locks, epochs, and explicit stale-agent recovery.

## T8: Service-worker cache power versus stale deployments

Service workers make offline/update flows powerful but can serve stale runtime
assets. Mitigation: versioned install, upgrade receipts, stale-client detection,
and clear rollback policy.

## T9: Devtools ambition versus archive bloat

Runtime introspection can become a huge side product. Mitigation: first traces
are compact JSON events; devtools is built from trace contracts incrementally.

## T10: Cloudtainer validation versus real-world claims

The cloudtainer can validate packaging, Node tests, local browser smoke paths,
and synthetic traces. It cannot prove mobile, GPU, thermal, or cross-browser
production performance. Mitigation: every performance claim must name its test
environment.

## T11: Plugin ambition versus security overclaim

A plugin/process model can discipline permissions inside an app, but it is not a
new browser security boundary. Mitigation: call it capability discipline, not
security isolation, unless proven otherwise.

## T12: One-runtime ambition versus scope explosion

A runtime that covers every lane can sprawl. Mitigation: freeze primitives,
implement narrow vertical slices, and demote ideas into future lanes without
adding unvalidated recurring surfaces.
