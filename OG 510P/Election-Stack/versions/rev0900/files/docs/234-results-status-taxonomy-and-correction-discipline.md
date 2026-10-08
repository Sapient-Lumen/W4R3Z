# 234 — Results status taxonomy & correction discipline (unofficial → certified)

**Track:** A (Deployable core)

Public results are not just numbers; they are *claims under time pressure*.
This doc provides a **small, reusable vocabulary** for labeling results lifecycle states and for
making **corrections auditable** without turning every jurisdiction’s legal process into a spec.

**Non-claim:** this doc does **not** assert legal meaning or timelines. It defines *machine- and human-facing labels*
that make disputes easier to resolve and manipulation harder to hide.

See also: `63` (ENR security), `68` (results pipeline), `69` (drift detection), `200`/`220–222` (PublicNotice feeds + divergence handling),
and `09`/`36`/`59` (audit + recovery + dispute resolution).


## 234.1 Two orthogonal questions every public results surface must answer

1) **How complete are these numbers?** (counting status)
2) **What is their official status?** (unofficial vs certified)

Do not collapse these into one label.
Many legitimacy failures happen when “more complete” is misread as “more official”.


## 234.2 Recommended fields (CRO / ENRUpdate)

Track A’s results objects already support:
- `unofficial` (boolean; default true in CRO schema)
- `counts_status` (string; operator-declared lifecycle label)
- `report_detail_level` (string; disclosure + granularity hint)

**Rule:** public UIs/APIs MUST render `unofficial=true` as *unavoidable* (banner + API field + downloads).


## 234.3 A small counts_status vocabulary (recommended, not exhaustive)

These values are intentionally **generic**. Jurisdictions MAY add more specific suffixes, but SHOULD keep the base token stable.

- `partial` — results are incomplete (expected outstanding ballots / reporting units).
- `preliminary_complete` — all *expected* election-night sources ingested, but post-election processing remains.
- `canvass_in_progress` — official reconciliation/canvass process ongoing (totals may change).
- `recount_in_progress` — recount or expanded audit/review ongoing (totals may change).
- `certified` — certified totals released.
- `amended_certified` — certified totals were amended (must link to prior certified release and reason).

**Do not use “final”** unless the jurisdiction’s process truly makes it final; prefer `certified` / `amended_certified`.


## 234.4 Corrections: fail loud, link forward, never silently edit

“Silent edits” are a primary legitimacy hazard for ENR and post-election updates.

When anything changes (numbers, mappings, disclosure policy, or interpretive status text):

1) **Issue a new signed object** (`ENRUpdate` and/or new CRO in a new release package).
2) **Link it forward** to what it supersedes (hash/ID), and record a bounded reason.
3) **Anchor it** (PBB inclusion proof + witness checkpoints where available).
4) **Publish a PublicNotice correction/status_update** that carries digests, not screenshots.

Minimal correction reason categories (keep compact):
- `late_ballots_added`
- `duplicate_removed`
- `reporting_unit_fix`
- `contest_definition_fix`
- `disclosure_policy_change`
- `other` (with bounded explanation)

If you cannot state the reason yet, say so explicitly and set `counts_status` accordingly.


## 234.5 Certified releases and amendments (evidence discipline)

When publishing `counts_status=certified` or `amended_certified`, the publisher SHOULD:

- publish a **digest-first notice** (PublicNotice) that references:
  - the certified ResultsReleasePackage (or bundle manifest digest),
  - the certified CRO digest,
  - any audit/canvass evidence bundle digest (if available),
  - the prior certified digest if this is an amendment.

This is not a new evidence kind; it is the existing comms-as-evidence pattern applied to certification.

Optional tightening: publish a separate `PublicNotice.notice_type=election_milestone` with `milestone_id=certification_issued` (or `certification_amended`) bound to the certified release digests (see `237`).


## 234.6 Monitoring implications (portable checks)

Monitors/verifiers SHOULD treat these as *portable, cheap sanity checks*:

- `unofficial` must not disappear while totals are changing.
- `counts_status` transitions must be explainable (e.g., `partial → canvass_in_progress → certified`).
- decreases in totals without a correction link are a `69` monotonicity drift event.
- `amended_certified` must reference the prior certified digest and include a reason.


## 234.7 Minimal operator outputs (keep small)

For each release interval, an operator should be able to publish:

- a `ResultsReleasePackage` (downloadable; signed; content-addressed)
- a digest card for the release (see `206`)
- a PublicNotice that names the release digest and the intended `counts_status`/`unofficial` interpretation

Templates (operator ergonomics; keep payloads schema-valid):
- `artifacts/templates/results-release-package-payload.json`
- `artifacts/templates/public-notice-results-release-payload.json`
- `artifacts/templates/public-notice-results-correction-payload.json`

Everything else is optional and should be justified against bloat.
