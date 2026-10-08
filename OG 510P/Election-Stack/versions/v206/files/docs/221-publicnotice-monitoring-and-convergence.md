# 221 — PublicNotice monitoring and convergence (feeds + “effective state”)

**Track:** A (Deployable core)

PublicNotices (`186`) + feeds (`200`) make official comms **content-addressed**, **receipt-backed**, and **rollback-detectable**.
But “verifiable” only matters if **multiple audiences converge** on the same observed state.

This doc defines a **small monitor contract** for:

- **Integrity:** verifying feeds/notices (digests, continuity, required attachments)
- **Parity:** detecting split-views across official channels
- **Convergence:** computing and comparing “current official state” using `220`

See also:
- Official channel directory (what to monitor): `203`
- `.well-known` bootstrap (domain-first discovery): `204`
- Parity snapshots (publishable split-view evidence): `201`
- Update/correction contract: `219`
- Effective-state semantics (deterministic interpretation): `220`


## 221.1 Monitoring goal (tight)
A PublicNotice monitor SHOULD be able to answer:

> “Given the official channel set, do they agree on the same **effective current state**?”

If not, the monitor MUST be able to produce a **portable proof of divergence** (typically `201`, plus a bounded PublicNotice describing the mismatch).


## 221.2 Inputs (what a monitor consumes)
A monitor’s inputs are intentionally boring and public:

- **Channel set:** from the official channel directory (`203`) and/or domain-first `/.well-known` bootstrap (`204`).
- **Latest feed locations:** stable “latest feed” URLs per channel (`200`).
- **A fetch policy:** cadence, timeouts, caching rules, and a “holdback window” for propagation delays (see 221.4).
- **A verifier profile:** what “valid” means for receipts, attachments, and envelope parsing (`188`, `193`).


## 221.3 Invariants to enforce (the minimum)
Monitors SHOULD enforce these invariants (and surface failures as incidents, not private surprises):

1) **Digest validity**
   - every fetched feed and notice verifies against its stated digest (`186`, `200`)

2) **Feed continuity**
   - the latest feed’s `prior_feed_digest` (or equivalent linkage) matches the previously observed head
   - any rollback/rewrite behavior is captured as a public surface anomaly (`200`, `201`, `205`)

3) **Attachment completeness**
   - any required attachments referenced by a notice are fetchable and digest-verifiable (`186`, `180`)

4) **Effective-state convergence**
   - when computing “current state” via `220`, the set of head notices + attached corrections is consistent across channels (within the holdback window)


## 221.4 The holdback window (anti false positives)
Channels do not update simultaneously.
A monitor SHOULD define a **holdback window** (e.g., minutes to tens of minutes) during which “new head observed on channel A but not yet on channel B” is tracked as **pending propagation**, not immediately escalated.

After the holdback window expires, non-convergence becomes a **parity failure** and must be treated as a public incident (`201`, `186`).


## 221.5 Minimal algorithm (reference)
This is not a protocol; it is a **deterministic monitor loop**.

1) **Discover**
   - load the official channel set (`203` / `204`)
   - resolve each channel’s “latest feed” location(s) (`200`)

2) **Fetch + verify feeds**
   - fetch the latest feed from each channel
   - verify digest + envelope parsing (`200`)
   - retain the observed head digest per channel (monitors must remember prior state)

3) **Assemble the notice set**
   - union the notice digests/IDs referenced by the observed feed window(s)
   - fetch missing notices/attachments from any channel or mirror (`200`)

4) **Compute effective state**
   - compute heads + attach corrections per `220`
   - represent effective state as a stable set of `(notice_id, digest)` pairs

5) **Compare across channels**
   - if effective-state sets match: record success
   - if mismatch and within holdback: record “pending propagation”
   - if mismatch and outside holdback: generate a parity snapshot (`201`) and publish a bounded PublicNotice describing the mismatch (`186`)

**Operator note:** if a monitor cannot fetch a channel, treat it as a *surface availability* incident; do not silently drop the channel from comparisons (`205`, `08`).


## 221.6 Output artifacts (what to publish when it matters)
When failures occur, publish evidence that makes the dispute portable:

- `hfv.public.surface_parity_snapshot` capturing what each channel served (`201`)
  - Use a stable anomaly code in `observations[].notes` when applicable (see `docs/SURFACE_ANOMALY_CODES.md`), e.g. `surface_effective_state_divergence` for `220`-computed mismatches.
- if the snapshot computation is likely to be contested, include a small capture note that pins the raw capture bytes (no screenshots): `DOC:docs/223-public-surface-capture-notes-and-reproducibility.md`
- a PublicNotice referencing the snapshot digest and describing the mismatch (`186`, `219`)
- (optional) a verifier report over the captured artifacts, if you maintain a public verifier surface (`193`)

For a bounded dispute handoff bundle recipe, see `222`.

Avoid publishing “monitor screenshots”; publish **digest-verifiable** artifacts instead (`180`, `195`).


## 221.7 Size discipline
- keep monitors’ “state memory” small: store only recent heads, plus enough history to detect rollbacks (windowed feeds exist for this reason)
- publish only what is needed to prove divergence (snapshot + bounded notice), not full logs
