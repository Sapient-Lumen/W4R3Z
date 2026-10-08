# 486 — Authoritative time sources, timestamp confidence, and invalid-time quarantine

## One-line thesis

Any public-AI governance system that depends on clocks for deadlines, queue age, freshness, sequencing, signatures, retention, or incident ordering should declare its authoritative time basis, timestamp confidence, tolerated drift, and quarantine behavior when time trust degrades, so chronology cannot silently become a hidden source of injustice.

## Why this matters

The archive already runs on clocks. It has incident clocks, review clocks, queue clocks, approval freshness windows, lineage timestamps, release timestamps, and evidence retention schedules. What it still lacked was one explicit rule for whether **time itself is trustworthy enough** for those controls to mean what they claim.

That omission is dangerous because many governance failures are actually time failures in disguise. A queue looks compliant because the clock reset during a migration. An appeal packet seems late because one subsystem recorded local time without offset while another used UTC. A repaired record preserves content but loses trustworthy ordering. A stale approval looks current because a resynchronized node backdated the renewal event. A deadline appears expired because a device or service drifted beyond tolerance. The archive may preserve lots of facts while still failing to answer a simpler prior question: *are the timestamps themselves trustworthy enough for this conclusion?*

Without explicit time governance, chronology becomes ambient folklore. Deadlines, freshness, and sequence are then treated as objective facts when they may only be best guesses.

## Pattern pack

### 1. Declare an authoritative time basis

For each consequential system or evidence family, preserve:

- the authoritative time source or source class,
- whether timestamps are recorded in UTC, fixed offset, or both,
- the expected granularity,
- and which subsystems are allowed to mint authoritative timestamps.

A timestamp without time-basis context is weaker than it looks.

### 2. Distinguish display time from canonical recorded time

People may need local display time. The governed record should still preserve canonical recorded time in a stable machine-readable form with offset or UTC semantics intact. Local display convenience should not overwrite the canonical chronology basis.

### 3. Publish timestamp-confidence classes

The archive should be able to say whether chronology is currently:

- **trusted** — within tolerated drift and ordering assumptions remain admissible,
- **guarded** — time remains usable but some chronology-sensitive actions need caution,
- **quarantined** — drift or uncertainty exceeds tolerance for automated chronology-dependent conclusions,
- **unknown** or **clock-blind** — the archive cannot currently justify chronology-based claims.

These labels keep time trust visible instead of implicit.

### 4. Define drift budgets and invalid-time triggers

Institutions should define how much drift or uncertainty is tolerable for each consequential use, such as:

- queue dwell calculation,
- deadline enforcement,
- approval freshness,
- incident ordering,
- log correlation,
- signature validity windows,
- or record-retention cutoffs.

Once time confidence falls outside the relevant budget, the archive should say what automation is blocked, downgraded, or rerouted.

### 5. Quarantine chronology-sensitive conclusions when time trust fails

When time is no longer trustworthy enough, the institution should quarantine or visibly qualify chronology-sensitive conclusions such as:

- “late” or “on time,”
- “fresh” or “stale,”
- “older” or “newer,”
- “expired,”
- “first in queue,”
- or “after the incident start.”

The right answer is not to keep issuing crisp chronology labels on untrusted time.

### 6. Preserve affected-decision scope during time incidents

A time-confidence drop should preserve which prior or current decisions may be affected, for example:

- appeal timeliness judgments,
- queue age displays,
- incident sequence reconstruction,
- approval-expiry enforcement,
- or retention/disposition calculations.

Time incidents should not be treated as purely technical maintenance.

### 7. Record resynchronization and revalidation receipts

After repair or resynchronization, preserve a compact receipt showing:

- what failed,
- what source re-established time trust,
- which drift budget now applies,
- and whether chronology-sensitive conclusions were recomputed, grandfathered, or left under qualification.

A repaired clock should not silently rewrite the evidentiary story.

### 8. Separate monotonic sequencing from wall-clock dating where needed

Some controls need human date/time semantics. Others need reliable ordering. When those differ, the archive should preserve which one governs the conclusion instead of pretending a wall-clock string solved both.

## Guardrails

- Do not assume timestamps are trustworthy merely because they exist.
- Do not let local display time overwrite canonical recorded time.
- Do not keep issuing expiry, lateness, or freshness judgments when time confidence is quarantined.
- Do not hide resynchronization events that may affect chronology-sensitive review.
- Do not treat time incidents as beneath the governance boundary.

## Failure modes

- **clock certainty theater**: the system speaks crisply about age or order without proving time trust.
- **offset amnesia**: local time is recorded with no reliable offset, breaking cross-system review.
- **silent resync rewrite**: chronology changes after repair with no visible receipt.
- **deadline by drift**: rights are lost or queue status shifts because one clock wandered.
- **timestamp overbelief**: reviewers trust a stringified time more than the system’s actual confidence in it.

## Practical tests

A trustworthy-time discipline passes when it can answer yes to all of the following:

1. Does each chronology-sensitive control identify its authoritative time basis and canonical timestamp form?
2. Are drift budgets and timestamp-confidence classes defined for the uses that matter?
3. When time trust degrades, are chronology-sensitive conclusions downgraded, blocked, or qualified explicitly?
4. Can the institution identify which decisions may be affected by a time incident?
5. After repair, is there a visible revalidation receipt rather than a silent rewrite of chronology?

## Compression rule for the archive

If a consequential system can say **late, fresh, expired, first, current, or stale** but cannot also say **which time source justified that claim, how much drift was tolerated, and what happens when time trust fails**, then it is still letting **clock confidence impersonate due process**.
