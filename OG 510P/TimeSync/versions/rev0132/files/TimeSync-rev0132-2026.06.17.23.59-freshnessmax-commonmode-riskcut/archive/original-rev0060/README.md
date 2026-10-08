# TimeSync — rev0060

## What changed in this revision

This revision tests how strong an explicit `assessed_profile` reference must be.

### Added
- `PROFILE-REFERENCE-GRANULARITY-TEST.md`

### Tightened
- `START_HERE.md`
- `PROBLEM-FRAME.md`
- `TIMESTATE.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `DISCOVERY-REQUEST-SKETCH.md`
- `PROFILE-IDENTITY-EXPOSURE-TEST.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

## Why this matters

The archive now says:

```text
assessed_profile references are boundary-tiered.
```

A versioned public profile identifier may be enough in a boundary that can
resolve it. Cross-operator or deployment-local names need an authority. Detached
audit, long-retention, safety, or compliance boundaries may need a digest of the
normative profile rules. A signed profile-binding record is reserved for cases
where the receiver must independently verify who bound the profile id/version/digest.

That means:
- name-only profile references are generally too weak for exported actionable conformance
- not every assessment needs a digest or signature
- digest-backed profile references bind profile rules, not source packets or PDFs
- signed bindings do not become conformance certificates or negotiation objects
- `assessed_profile` stays local/export metadata, outside the minimal source packet

## Fast path

Open these first:
- `PROFILE-REFERENCE-GRANULARITY-TEST.md`
- `PROFILE-IDENTITY-EXPOSURE-TEST.md`
- `PROFILE-CONFORMANCE-MARKER-TEST.md`
- `TIMESTATE.md`
- `frontier-ticket.json`

## Archive theme

**profile references need boundary-strength binding, not a universal manifest**
