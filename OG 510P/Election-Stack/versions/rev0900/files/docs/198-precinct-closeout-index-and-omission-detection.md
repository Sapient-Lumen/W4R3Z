# 198 — Precinct closeout index + omission detection (make missingness provable)

**Track:** A (Deployable core)

`197` defines *per‑precinct closeout micro‑packets* (poll tape photos, seals, closeout note).
This doc adds the missing coordination artifact: a **closeout index** that lets the public and auditors
quickly answer:

- *Which reporting units have published closeout micro‑packets?*
- *Which are missing, late, or only available on some mirrors?*

Without an index, an attacker can win via **selective omission**: most precinct packets exist, but the
controversial ones “never show up,” and nobody can prove the gap.

See also:
- `197-precinct-closeout-evidence-capture-and-publication.md` (micro‑packets)
- `195-rumor-control-and-status-boards-as-verifiable-public-surfaces.md` (public surfaces as verifiable indexes)
- `187-publication-compliance-and-coverage.md` + `181-publication-contract-and-deadline-breach-proofs.md` (measurable deadlines)
- `174-coverage-accounting-and-representativeness.md` (coverage posture)

---

## 198.1 Threat model (what the index prevents)

The closeout index primarily reduces impact from:

- **Selective omission:** some precincts’ packets are never published (or quietly removed).
- **Split‑view publication:** different audiences see different precinct subsets.
- **Mirror divergence:** one mirror has a packet; another does not.
- **Slow drift edits:** packets change without an obvious, auditable “new version” declaration.

The index does **not** prove correctness of the tally; it proves **presence/absence + linkage**.

---

## 198.2 Minimal object: `PrecinctCloseoutIndex` (content‑addressed)

Track A defines a small evidence object:

- Envelope kind: `hfv.results.closeout_index`
- Payload schema: `schemas/PrecinctCloseoutIndex.json`

The payload is intentionally boring: a mapping of `reporting_unit_id → closeout_packet_manifest_sha256`,
plus minimal election scope and update chaining.

Optional (court-facing): each entry MAY include `custody_anchor_sha256` to bind the reporting unit to a physical ballot custody packet digest (seal logs / chain-of-custody scans), so digital omission detection can be paired with physical custody evidence.

**Design rules (tight):**
- Keep each entry short (no narratives; narratives live in `PublicNotice` or the packet note).
- Treat every update as a **new index object** (no in‑place edits).
- Chain updates with `previous_index_sha256` so rollback/rewrites are detectable.

---

## 198.3 Publication pattern (operator‑deployable)

Minimum deployable pattern:

1. **Maintain a stable public location** for the latest index, e.g.:
   - `.../closeout/index-latest.json` (bytes equal to the latest index payload)
   - `.../closeout/index-history/sha256-<hex>.json` (immutable copies)

2. For each index update, publish a **PublicNotice** whose payload includes:
   - the index payload digest (`sha256:<hex>`),
   - the index history URL(s), and
   - (optional) `next_update_at` commitment if more precincts are expected soon.

3. Mirror the **PublicNotice digest** across declared official channels (parity), per `194`/`195`.

4. If you publish a `PublicNoticeFeed` (docs/200), ensure each index-update notice appears in the feed window so observers can discover updates from any channel.


The public surface (status board) should show **the notice digest**, not “trust me, this is the list.”

---

## 198.4 Completeness semantics (what “missing” means)

To make missingness provable, the index MUST be evaluated against an **expected reporting‑unit set**.
Track A keeps this flexible because jurisdictions differ.

Recommended sources for the expected set (choose one and pin it):
- a jurisdiction‑published reporting‑unit roster (preferred),
- a ballot style assignment roster (`60`/`61` pipeline artifacts), or
- a canonical “precinct list” published as an evidence packet.

Operational rule: the expected set SHOULD be published (or at least hashed and pinned) *before* polls close,
so “we never had that precinct” cannot be retroactively invented.

**Index payload fields support this** via optional `expected_set_sha256` (digest of the roster bytes).

---

## 198.5 Verification (what observers can check)

Given:
- an index payload (or immutable history copy), and
- the PublicNotice digest that announced it,

an observer can verify:

- the index payload digest matches the announced digest (no silent edits),
- the update chain is consistent (`previous_index_sha256`),
- each referenced closeout packet manifest digest exists on ≥2 mirrors (or record divergence),
- the index coverage relative to the expected reporting‑unit set (if the expected set bytes are available).

If a precinct is missing, the observer SHOULD emit a `PublicationSuppressionReport` (or a
`PublicationCoverageReport` window) anchored to a trigger event (`187`).

---

## 198.6 Anti‑gaming notes (keep it honest)

- Publish **no‑update markers**: if no new precinct packets arrived in a window, publish an index update
  that restates the prior digest and explains “no change” in the accompanying PublicNotice.
  Silence is otherwise indistinguishable from suppression.

- Avoid “one giant file” drift: keep history immutable and small; the latest pointer can move.

- Do not claim “complete” unless you can cite the expected set digest and the index covers it.

---

## 198.7 Source anchors (informative)

- `xref: cisa_rumorcontrol_page` (treat public pages as correction/index surfaces; see also `195`)
- `source: eac_enhancing_election_security_public_comms_2024_pdf` (public comms posture as an operational surface)
