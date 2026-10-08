# 932. Mission heart, authentication boundary, and cloudtainer correction plan

**Track:** Shared / Track A mission-kernel assurance

**Status:** deep-read audit, trust-boundary correction, and forward plan for v894

## 932.1 Executive verdict

The heart of this project is not “a full electronic election stack” in the ordinary product sense. It is a **portable evidence-and-recovery sidecar** that should let an authorized third party answer, offline and without trusting one vendor dashboard:

1. Who authorized the election definition?
2. What ballots, records, and custody events existed?
3. How were reported results derived from exportable records?
4. What audit, recount, adjudication, or discrepancy occurred?
5. What official notice or correction was published, by whom, and when?
6. What did independent verifiers observe, including disagreement and failure?
7. What incident, remedy, retention, and closeout action followed?

The mission can be summarized in four verbs: **bind, preserve, replay, recover**.

The archive has unusually strong internal discipline, broad threat modeling, deterministic packaging, and honest synthetic/no-go language. Its main weakness is now the opposite of neglect: it has built a large self-verifying assurance world around a still-unproven adoption path. The project can prove that thousands of files agree with each other more readily than it can prove that one real jurisdiction supplied authentic, sufficient, independently replayable election evidence.

## 932.2 Baseline facts from the uploaded v893 carrier

The uploaded carrier contains:

- 3,396 files and 16,769,207 uncompressed bytes;
- 831 files under `docs/` and 2,097 under `artifacts/`;
- 167 release-gate child checks;
- seven mission-kernel rows and 28 minimum evidence classes in the full non-production drill;
- zero live evidence objects;
- 1,216 external-source rows, of which 118 are byte-pinned and 1,098 are unpinned;
- 13 source-byte receipts and 105 missing receipts among the pinned set;
- 51 exact-duplicate content groups spanning 289 files and about 349,790 avoidable bytes; and
- 28 revisions from v866 through v893 across June 10-18, 2026, including 15 revisions on June 13 and six on June 18.

These counts do not prove failure by themselves. They show where the project spends attention.

## 932.3 Severe trust-boundary defect corrected in v894

### What was wrong

The v893 mission-kernel intake treated a syntactically valid digest and a free-text `approving_role` as `live_valid`. When every required class on a row had that shape, the row could advance to `COMPLETE_PENDING_LOCAL_REVIEW`, and the package could reach `STAGED_PENDING_AUTHORITY_REVIEW_NOT_LIVE_READY`.

That was a materially misleading state transition. SHA-256 answers “do these bytes match this digest?” It does not answer:

- who created or approved the record;
- whether that signer was authorized for this jurisdiction and election;
- whether the authority scope was delegated, current, or revoked;
- whether the record is the referenced source or a substituted object;
- whether two records with the same typed role came from independent organizations; or
- whether the record belongs to the intended election, reporting unit, and closeout event.

The archive already has a stricter canonical path: signed `EvidenceEnvelope` objects, deterministic canonicalization, signer authorization, trust keysets, policy profiles, publication receipts, and strict packet verification. The mission-kernel intake had accidentally created a weaker side door around its own trust architecture.

### What v894 changes

ADR 0005 makes the rule explicit: digest-only live submissions are candidates, never authenticated evidence. The intake now:

- keeps authenticated live-object and class counts at zero;
- emits `NO_GO_LIVE_EVIDENCE_AUTHENTICATION_REQUIRED` for a shape-valid live candidate;
- requires a signed canonical `EvidenceEnvelope` and external trust-profile verification before future live promotion;
- rejects duplicate work-item and evidence-class keys instead of silently collapsing them;
- enforces submission/object source-mode agreement;
- rejects local, filesystem, and ambiguous record locators;
- requires positive byte counts, explicit UTC capture times, and retention references;
- cross-checks redaction status against the public/private boundary; and
- fingerprints files through one stable file descriptor with before/after metadata checks, reducing hash/stat race risk.

This revision deliberately does **not** pretend that envelope integration is complete. It removes the false positive state and makes the missing integration visible.

## 932.4 Release-control defect found in the uploaded carrier

A full baseline gate of v893 produced 166 passing child checks and one failure: `scripts/check_release_go_no_go_pack.py`. The canonical `release-go-no-go-decision.json` was stale relative to its generator because three dependency hashes had changed:

- `artifacts/reports/adopter-authority-capture-matrix.json`;
- `artifacts/reports/adopter-authority-capture-summary.json`; and
- `artifacts/reports/adopter-capture-record-validation-report.json`.

The defect did not show an election outcome problem. It showed that the shipped release verdict did not describe the shipped dependency bytes. A release process whose central promise is evidence coherence must treat this as a release-blocking contradiction.

The correction is to regenerate dependent packs in order and publish v894 only through the one-command full gate, manifest write, deterministic ZIP build, and independent ZIP verification path. A generated “GO synthetic only” file must never be treated as current merely because its prose still looks plausible.

## 932.5 What is missing

### One real adoption slice

The next decisive milestone is not another broad doctrine document. It is one bounded adopter slice:

- one jurisdiction;
- one election type;
- one authorized election-definition export;
- one ballot-accounting/custody dataset;
- one CVR and results export profile;
- one audit or recount method;
- one official notice/correction route;
- two independent verifier organizations; and
- one complete incident/dispute/retention closeout packet.

A synthetic replay proves software plumbing. It cannot prove access to records, authority, operator usability, chain of custody, legal retention, redaction judgment, or institutional response under deadline.

### Authentication integrated into the mission kernel

The submitter and intake need a production-grade envelope lane, not merely a documented dependency. The lane should verify exact payload bytes, canonical digests, signer authorization, trust-root pinning, jurisdiction/election scope, delegation and revocation state, and policy-profile identity. “Approving role” should become a derived display field from authenticated authority data, not a source of authority.

### Sufficiency semantics, not four checkboxes per row

Every row currently asks for four named classes. That symmetry is operationally convenient but can become checkbox assurance. Each class needs jurisdiction-specific sufficiency criteria, such as reporting-unit coverage, expected-vs-observed totals, custody gap thresholds, export completeness, audit sample and discrepancy semantics, dissent closure, publication timing, and retention disposition.

### Interoperability demonstrated against actual exports

NIST common data formats give the project the right integration seam: Ballot Definition, Cast Vote Records, Voter Records Interchange, Election Results Reporting, and Event Logging. The archive should maintain adapters and conformance fixtures, but the key milestone is replay against real vendor/jurisdiction exports with documented loss, extension, and ambiguity handling. Relevant locked sources include `nist_sp1500_20_bd_pdf`, `nist_sp1500_103_cvr_pdf`, `nist_sp1500_100r2_err_pdf`, and `nist_gcr_24_058_cdf_implementation_guidance_pdf`.

### Physical evidence and audit linkage

The archive is strongest when digital records are tied back to trustworthy evidence of voter intent, preservation, and post-election checking. The EAC audit and chain-of-custody references already pinned in the archive (`eac_post_election_tabulation_audit_guide_2024_pdf` and `eac_bestpractices_chain_of_custody_best_practices`) should shape concrete capture fields: container/seal identity, transfer actor and time, discrepancy, reconciliation, audit population, sample selection, interpretation rules, escalation, and disposition.

### Governance needed for adoption

The root lacks an explicit software/content license, contribution policy, security disclosure policy, supported Python/OS matrix, dependency lock or declared zero-dependency contract, and CI configuration. These are not cosmetic. Without an authorized license, outsiders do not have clear permission to reuse or modify the work. Without a reporting route and support matrix, operators cannot distinguish a supported assurance claim from a local experiment. License selection and institutional contact details require project authority and must not be invented by a maintainer.

### Independent review with closure

The risk and hazard surfaces are rich but predominantly open, while external-review and witness-health surfaces remain placeholder/not-measured. The project needs fewer evergreen “open” rows and more closed loops: named decision authority, due date, acceptance test, dissent record, remediation, retest, and closure evidence.

## 932.6 Where the cloudtainer is wasteful

### Internal-consistency work has displaced mission evidence

The 167-check gate is valuable, and v893 demonstrates that it catches real contradictions. But most checks validate archive shape, generated-artifact freshness, wording, references, and fixtures. The gate is not evidence that a jurisdiction’s source record is authentic or that a reported outcome matches trustworthy voter-intent evidence. The project should keep the deep release gate while creating a much smaller **mission-core gate** that answers only whether the seven evidence lanes are authenticated, sufficient, replayable, and independently reviewed.

### Template families are stored as prose instances

The archive includes 286 filenames containing `official-voter-information`, totaling about 4.94 MB. Large platform/media/firewall families repeat headings, disclaimers, and bounded verifier questions. The social distinctions may matter, but the representation should move toward:

- a structured audience/platform registry;
- one reviewed template and rendering generator;
- a small number of human-curated exceptions; and
- generated derivatives excluded from long-lived source history where reproducible.

Freeze new family growth unless a file carries a distinct legal requirement, proof obligation, owner, and test that cannot be represented as data.

### Historical state is neither full history nor a clean event log

At least 488 JSON objects carry original digest/size metadata associated with compaction; together, the compacted bodies are about 287 KB while declared originals were about 2.34 MB. This saves space, but an in-place hash-only stub without a retrieval locator is not a self-contained historical record. It preserves evidence that bytes once existed, not the bytes needed to replay them.

Stop treating the release tree as both current product and archival database. Preserve current release artifacts in the release, and move history to a separate content-addressed archive or signed delta/event log with resolvable object locations. Revision numbers should mark meaningful state transitions, not every regenerated snapshot.

**v894 bridge correction.** This revision does not create another hash-only compaction layer. It replaces 73 superseded v892-v893 generated reports, trust-policy fixtures, and source-byte checksum/workpack files with path-preserving stubs while retaining their exact pre-compaction bytes as 77 members in `artifacts/history/rev0894-superseded-v892-v893-artifacts.tar.gz`. Each stub binds its original byte count, SHA-256, bundle path, and exact member path; `tools/retrieve_compacted_history.py` recovers one member without arbitrary archive extraction and verifies it before writing. The bridge recovers 349,981 bytes before counting its report and retrieval tool. It does not repair older hash-only stubs whose original bytes were already absent, and it is not a substitute for the recommended separate content-addressed history store.

### Source-byte machinery is disproportionate

Exact source-byte pinning protects against upstream drift. However, the project has spent many revisions building batch, host-slice, DNS, retry, resume, receipt, and workpack machinery around 105 missing receipts. That lane should be risk-tiered. The highest-value election authority, CDF, audit, custody, and legal sources deserve pins first; low-impact context should not outrank a real adopter, signer governance, audit replay, or independent review.

### Release generation is too serial and self-referential

Many reports hash other generated reports, producing fragile order dependencies. The stale v893 go/no-go artifact is the predictable result. Replace the implicit generation sequence with a declared dependency DAG. Generate all leaves first, then summaries, then handoff/go-no-go, then manifest and ZIP. Cache immutable parse results and run independent checks in one process pool where safe, while preserving a single canonical deep verdict.

## 932.7 Scope correction

The current “Track A” mixes two different products:

- **A0 — Evidence sidecar:** read-only ingestion, normalization, accounting, packaging, replay, independent verification, and closeout around existing election systems.
- **A1 — Integrated transparency system:** signed event publication, checkpoints, inclusion proofs, witnesses, policy receipts, and client-visible transparency semantics integrated into production systems.

A0 is the credible near-term adoption path. It can be deployed without replacing ballot casting or tabulation and can create immediate value around exports, audits, notices, and disputes. A1 remains valuable, but its claims—such as client inclusion proofs and quorum-cosigned checkpoints—must not be inherited by an A0 deployment that cannot produce them.

Track B remote return research and Track C advanced attestation/provenance should remain explicitly subordinate research lanes until their assumptions and evidence are separately satisfied.

## 932.8 Correction order

### Now: release and trust integrity

1. Remove the digest-only live-promotion state and freeze the rule in ADR 0005.
2. Regenerate every dependent current-revision artifact in dependency order.
3. Run the full canonical gate, write the manifest, build the ZIP, and independently verify it.
4. Publish the baseline v893 stale-go/no-go defect as a known release-control finding.

### Next 30 days: make adoption possible

1. Select one A0 adopter profile and freeze its evidence contract.
2. Define the mission-kernel `EvidenceEnvelope` kind/payload and strict trust profile.
3. Add an end-to-end authenticated candidate fixture with signer delegation and revocation negative controls.
4. Add `LICENSE`, `SECURITY.md`, support matrix, and contribution governance after authorized project decisions.
5. Build a mission-core gate of roughly 10-20 checks; retain the full deep gate for releases.

### Next 90 days: prove interoperability and recovery

1. Replay actual Ballot Definition/CVR/ERR exports from at least one source system.
2. Bind ballot accounting, custody, audit sample/discrepancy, adjudication, and public notice records.
3. Have two outside organizations run the verifier independently and publish disagreements.
4. Exercise a missing-record, wrong-signer, revoked-signer, split-view, custody-gap, and corrected-results scenario.

### Next year: reduce and institutionalize

1. Separate current source, generated derivatives, and historical content-addressed objects.
2. Replace prose families with registries and reproducible renderers.
3. Create closure SLAs for critical risks and retire stale/open rows.
4. Add hosted signed build provenance while preserving deterministic rebuild verification.
5. Expand only after the first adopter slice produces a complete, independently replayable closeout packet.

## 932.9 Stop rules

Do not add a new numbered doctrine document, registry, report family, platform page, or release revision unless it does at least one of the following:

- closes a named mission-kernel evidence or authority gap;
- removes a measured release or operator risk;
- supports a real adopter or independent reviewer;
- consolidates/deletes more surface than it adds; or
- is required by an external interface or release contract.

Do not count a digest, signature, receipt, build provenance, or passing synthetic test as proof of substantive election truth. Each proves a narrower property and must remain labeled accordingly.

## 932.10 Online standards watch

As of June 18, 2026, EAC materials continue to emphasize audits as a tool for accuracy, transparency, security, and confidence, and the agency held a February 18, 2026 hearing while developing national audit standards work products. Treat that effort as a standards-watch input, not a finalized mandatory standard. NIST’s current CDF implementation guidance reinforces the value of interoperable Ballot Definition, CVR, VRI, ERR, and event-log data. The 2024 EAVS release reported that over 98 percent of jurisdictions used equipment with a paper ballot or auditable paper record, reinforcing the practical value of an evidence sidecar anchored to physical records rather than a paperless replacement architecture.

Before these online observations become evidence-facing requirements, add or refresh the corresponding source-lock rows and record authority/currentness review.

## 932.11 Boundary

v894 corrects an internal authentication boundary and release-evidence inconsistency. It remains synthetic/non-production only. It is not live election evidence, current voter instruction, certification, legal advice, public-release authorization, production signer authority, proof of an election outcome, or approval to test live election systems.
