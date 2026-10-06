# Time monitors + lie detection (treat time like a transparency problem)

If DeriveBSD uses:
- metadata expiry (TUF-inspired channel rules)
- certificate validity windows
- freshness requirements for receipts and attestations

…then **time becomes a security boundary**.

Most systems stop at “use NTP/NTS”. DeriveBSD’s greenfield advantage is that it already has:
- a standard `time-proof-bundle` evidence object
- a structured event journal
- policy-driven monitors for other lanes (transparency monitors, witness gossip)

So we can treat “lying time servers” as an operable problem, not a theoretical one.

## The idea

### 1) Fleet nodes emit time proof bundles
When `system.time` evaluates sources, it emits a `time-proof-bundle`:
- source ids + protocol
- reported times + uncertainty
- transcript digests (privacy-safe)
- agreement result (in quorum or not)

### 2) A monitor consumes proof bundles
A **time monitor** (local or fleet-level) watches for:
- repeated quorum failures
- systematic divergence by one source
- sudden multi-minute jumps correlated with network paths

…and emits alerts as **typed evidence**.

This is directly analogous to transparency monitoring:
- logs don’t prevent compromise; they make it *detectable*
- monitors turn “detectable” into “actionable”

## What to emit

### Events
Extend `time-event` with a few additional actions:
- `quorum-failed`
- `divergence-detected`
- `misbehavior-proof-captured`

These are *operational facts* that deserve first-class event identities.

### Receipts
When a workflow depends on time (update verification, release verification, secret issuance), it can require:
- a fresh `time-sync-snapshot`
- and optionally a recent `time-proof-bundle` meeting policy bounds

This keeps expiry-based rules honest.

## Response playbook (policy-driven)

When time is **degraded** or **divergent**, policy should be able to:
- stop accepting expiring metadata (channel updates)
- stop issuing short-lived credentials
- require a manual breakglass override (which is receipted)
- or allow a reviewed workflow to continue only under `allow-if-proof-fresh` with an exact `time-proof-bundle` join

This prevents “clock was wrong” from becoming a silent bypass.

## Privacy stance

Time proofs can become privacy-toxic if they capture too much.
Default stance:
- store transcript *digests* only
- let ordinary support handoff carry `time_sync_receipt_digests` instead of daemon-private monitor output when trustworthy-time actions matter
- allow exporting raw transcripts only inside incident bundles under export policy
- raw transcripts only inside stronger export paths under explicit export policy
- prefer aggregation (counts, rates) for fleet monitoring

## References

- Roughtime is designed to allow clients to retain cryptographic proof of inconsistencies:
  - IETF Roughtime draft: https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/
  - Google Roughtime repository: https://roughtime.googlesource.com/roughtime

- NTS is the standard way to authenticate NTP client/server mode:
  - RFC 8915: https://www.rfc-editor.org/info/rfc8915

See also:
- `docs/200-secure-time-bootstrapping.md`
- `docs/283-trustworthy-time-nts-roughtime-and-lkgt.md`
- `docs/61-channel-metadata-tuf-inspired.md`

Last updated: 2026-03-23r433
