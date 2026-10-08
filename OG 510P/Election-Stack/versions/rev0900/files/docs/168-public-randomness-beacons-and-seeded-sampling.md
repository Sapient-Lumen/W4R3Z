# 168. Public randomness beacons and seeded sampling (anti-grinding)

**Track:** Shared

This archive relies on **public inspections** (watchers challenging monitors, seeded challenges, coverage metrics).
A recurring attack is **challenge grinding**: a watcher selectively issues only “easy” or “friendly” challenges and
claims “we checked”.

This doc defines a **publicly verifiable randomness kernel** so challenge schedules and sampling are:
- unpredictable *before* a fixed time/round, and
- publicly reproducible *after* publication.

It is intended to be used by:
- inspection challenge schedules (`149-challenge-randomness-and-inspection-auditability.md`),
- random sampling for audits (where applicable),
- “choose a subset” procedures that must be provably unbiased.

## 168.1 Design goals

1. **Deterministic from public inputs.** Anyone can recompute the same schedule.
2. **Time-locked.** The seed must be chosen from a *future* round/time so participants cannot precompute and game it.
3. **Multi-source mixing.** Prefer combining independent beacons to reduce single-beacon trust.
4. **Stable transcript binding.** Seeds must bind to a clear context string (election id, jurisdiction, artifact type, epoch).
5. **Failure visibility.** If a beacon is unavailable, that fact becomes an auditable event (not silent fallback).

Authoritative sources:
- NIST Interoperable Randomness Beacons project overview (`xref: nist_irb_overview_html`)
- drand overview (`xref: drand_docs_overview_html`)

## 168.2 Randomness kernel: commitment → reveal

### Step A — publish a commitment (before the randomness exists)

Publish a signed `RandomnessCommitment`:

- `election_id`
- `purpose` (e.g., `inspection_challenges_v1`)
- `beacon_set` (ordered list of beacon ids)
- `target_time_or_round` (must be in the future relative to publication)
- `mix_function` (e.g., `SHA-256`)
- `context_string` (domain separation)
- `commit_signature`

This commitment prevents “we picked a different round after seeing the value”.

### Step B — after the target time/round, compute `seed`

Fetch the beacon outputs for the committed round/time and compute:

```
seed = SHA256(
  "VotingArchiveSeed/v1" ||
  context_string ||
  beacon_1_output ||
  beacon_2_output || ...
)
```

### Step C — derive all randomized choices deterministically

Derive decisions with a deterministic PRF/DRBG (e.g., HKDF-expand from `seed`), then map to choices:

- shuffle list → take first N
- uniform integer mod M (with rejection sampling)
- deterministic “sample without replacement”

## 168.3 Recommended beacon sets

### Baseline (single-beacon)
- NIST beacon / interoperable beacon ecosystem
  - `xref: nist_irb_overview_html`

### Preferred (mixed)
- NIST beacon(s) + drand (League of Entropy)
  - `xref: drand_docs_overview_html`

Rationale: mixing reduces the ability of any *one* beacon operator (or outage) to bias the result.

## 168.4 Failure handling policy (normative)

- If a committed beacon output is missing, the seed MUST be computed using a **documented** policy that is itself committed
  (e.g., “use remaining beacons, record `BeaconUnavailable` event”), and the event MUST be logged as evidence.
- The commitment MUST NOT allow “pick any beacon that worked” (that reintroduces grinding).

## 168.5 Evidence objects (recommended)

This archive does not yet standardize schemas for these objects, but implementers SHOULD treat them as signed evidence:

- `RandomnessCommitment`
- `RandomnessReveal` (includes fetched beacon material + computed seed)
- `BeaconUnavailable` (signed incident record)

See also: `92-offline-verifier-bundle-spec.md` for how these objects can be packed into dispute-ready bundles.
