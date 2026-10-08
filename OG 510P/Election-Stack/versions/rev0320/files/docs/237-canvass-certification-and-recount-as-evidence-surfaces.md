# 237 — Canvass, certification, and recount as evidence surfaces (milestone notices)

**Track:** A (Deployable core)

This archive does not attempt to encode every jurisdiction’s legal process.
But it *does* treat institutional milestones as a **legitimacy attack surface**:
attackers can win by creating credible confusion about *what was official, when, and on what evidence*.

This doc defines a **minimal, size-disciplined** pattern for publishing canvass/certification/recount milestones
as **digest-first, content-addressed evidence** using existing Track A surfaces.

See also: `234` (results status + correction discipline), `236` (results anchoring profile), `186–205` (PublicNotice and official surfaces),
`19` (certification + standards alignment), and ``adr/0003-institutional-volatility-as-threat.md``.

**Non-claim:** this doc does not define legal sufficiency. It defines a pattern that makes disputes easier to adjudicate.


## 237.1 Why milestones need an evidence pattern

Milestone announcements (“canvass started”, “certification issued”, “recount ordered”) are routinely:
- published across multiple channels (web, press releases, social),
- revised under time pressure,
- and targeted by misinformation (fake documents, fake screenshots, fake “official” statements).

Track A’s goal is not to prevent all controversy; it is to make the *facts about the artifacts* cheap to verify.


## 237.2 The minimal pattern (Track A)

When an official milestone occurs, publish **one small PublicNotice** that is:
- signed (under the jurisdiction’s PublicNoticeSigningKeyset),
- receipted + gossiped (anti selective disclosure), and
- digest-forward (references point to content-addressed bundles/objects).

Use:
- `PublicNotice.notice_type = election_milestone`
- `PublicNotice.milestone_id = <stable id>` from `artifacts/registries/election-milestones.csv`

Template:
- `artifacts/templates/public-notice-election-milestone-payload.json`


## 237.3 What a milestone notice should reference (digest-first)

A milestone notice SHOULD include digest references for the *relevant* evidence objects:

- **Results release evidence:** the ResultsReleasePackage (RRP) bundle/manifest digest and (if applicable) CRO digest.
- **Ordering evidence:** the checkpointed RESULTS anchor (see `236`) or inclusion proof pointer.
- **Institutional artifacts (optional):** if the jurisdiction publishes a certificate/order/minutes, reference it by digest.
  - Do not embed large PDFs in this archive; publish the file in an evidence packet and point to its digest.
  - Use a redaction log (`225`) if the artifact contains sensitive personal data.

Rule: the notice should be understandable without the artifact, but *binding* should be by digest.


## 237.4 Linking rules (no silent drift)

Milestones are a comms surface, so the `220` effective-state rules apply.

- If a milestone statement changes meaning (dates, scope, or what is “official”), publish a **new** PublicNotice.
- Use `notice_type=correction` + `correction_of_notice_id` when correcting.
- If a milestone is superseded (e.g., recount ordered then rescinded), publish a new `election_milestone` notice
  that uses `supersedes_notice_id` to link forward.

Never silently edit previously published milestone statements on an official channel without issuing a correction notice.


## 237.5 Relationship to `counts_status` and `unofficial`

Milestones do not replace `234`’s results-status fields.
They exist to prevent a common failure mode:

> “These totals became official at time T” is asserted only in mutable text, not in verifiable artifacts.

Recommended:
- CRO/ENRUpdate continues to carry `unofficial` + `counts_status`.
- PublicNotice milestone notices carry “institutional steps occurred” and bind those steps to the content-addressed results release.


## 237.6 Monitoring implications (portable checks)

Monitors/verifiers SHOULD treat milestone notices as cheap, portable checks:
- If a UI/API claims “certified”, there should exist a recent `election_milestone` notice with `milestone_id=certification_issued`
  referencing the certified release digests.
- If a certification is amended, there should be a `certification_amended` milestone notice that references the prior certification digests.
- If different audiences see different milestone statements, publish a parity snapshot (`201`) and reference its digest in a follow-up notice.


## 237.7 Keep it small

This pattern is intentionally bounded:
- one registry row per milestone ID,
- one PublicNotice per milestone event,
- digest references instead of screenshots.

If you need more, justify it against the size budget (`227`) and prefer adding a registry entry or checklist before adding prose.
