# Sysctl snapshot as evidence (make drift explainable)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** operability, isolation, reproducibility
**Patterns:** Observation→Suggestion→Review→Enforce, Bundles

DeriveBSD already models sysctl mutation as a derived operation:
`sysctl.plan` → `sysctl.receipt`, with drift surfacing as `sysctl.event`.

What’s missing is a compact, deterministic object that answers:

- **What did we actually observe at drift-detection time?**
- **What keyset was checked?** (bounded, not `sysctl -a`)
- **Can a support bundle point at the observation without shipping raw command output?**

This doc introduces `sysctl.snapshot`: a bounded observation artifact that makes sysctl drift **explainable** and **bundle-friendly**.

## The artifact: `sysctl.snapshot`

`sysctl.snapshot` is a deterministic-by-default listing of observed values for a **bounded** keyset.
The intended default keyset is:

- the keys in the last applied `sysctl.plan`, plus
- an optional small allowlisted set of “operator extras” (policy-controlled).

It is *not* a full inventory (`sysctl -a`). If you need bulk inventory, add a separate lane artifact (Tier C) with explicit consent + export policy.

### The artifacts

Schema: `spec/sysctl.snapshot.schema.json`  
Example: `spec/examples/sysctl.snapshot.json`

## Where it plugs in

### 1) Drift detection (turn alerts into receipts)

A drift checker SHOULD:

- collect a `sysctl.snapshot` when drift is detected (or when policy says “always”),
- emit a `sysctl.event` that points at the snapshot digest (`snapshot_digest`), and
- keep the snapshot bounded and metadata-only (no bulk dumps, no secrets).

This makes “drift detected” alerts replayable: responders can inspect exactly what was observed.

### 2) Incident snapshots and support bundles

Support bundles and incident snapshots should include:

- the last applied `sysctl.plan` digest,
- the most recent `sysctl.receipt`,
- recent `sysctl.event`s, and
- the most recent `sysctl.snapshot` (or any snapshot referenced by the included events).

This keeps kernel knob posture in the evidence UX instead of becoming “run sysctl by hand” folklore.

### 3) Determinism + privacy posture

`sysctl.snapshot` is designed to be safe-by-default:

- bounded keyset
- values encoded as strings (sysctl(8) compatible)
- optional per-key `expected` and `status` fields, to keep UI fast
- optional `errors` list (no raw stderr/stdout blobs)

Export is still governed by `export.policy` and bundle transforms.

## References

- FreeBSD sysctl(8): https://man.freebsd.org/cgi/man.cgi?query=sysctl&sektion=8

Last updated: 2026-02-28r174
