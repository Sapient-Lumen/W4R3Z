# 926. Mission kernel, release-gate closure, and sprawl reset

**Track:** Shared

**Status:** synthetic release-integrity correction and product-scope audit

## 926.1 Executive finding

The archive's heart is not its document count, its cryptographic vocabulary, or its ability to describe every election edge case. Its heart is a **portable, independently replayable evidence-and-recovery layer for elections**: a way for officials, auditors, candidates, courts, journalists, civil-society monitors, and the public to test consequential claims without trusting one vendor, one dashboard, or one narrator.

That mission is strongest when it binds seven things into one inspectable chain:

1. the authorized election definition and parameters;
2. ballot accounting, reconciliation, and physical custody;
3. standardized cast-vote-record and results exports with digests;
4. audit, recount, adjudication, and escalation evidence;
5. authenticated official notices and corrections;
6. independent verifier outputs, including disagreement and failure evidence; and
7. incident, dispute, remedy, and closeout records.

This is the **mission kernel**. The rest of the archive should either implement it, test it, govern it, explain it to a defined audience, or live in an explicitly subordinate research annex.

## 926.2 What went severely wrong in the uploaded v887 carrier

The uploaded v887 carrier was not gate-clean. Its advertised one-command gate stopped because a new shared parser was absent from the tool-maturity registry. Independent execution of the remaining checks then exposed six more release-evidence defects:

- no current-v887 adopter-path smoke pass row;
- no current-v887 rows in four mandatory preparation ledgers;
- no README in the minimal PacketVerificationReport example;
- root entrypoints omitted shipped voter-facing documents 335 through 343;
- the adopter-capture validation report was stale; and
- the quarantined-source public-surface firewall report was stale.

These are not evidence that election outcomes were affected, nor evidence of malice. They are a **release-control failure**: the carrier claimed a current governed revision while mandatory current-revision evidence and navigation were incomplete.

The root architectural cause was more serious than any single stale row. `scripts/build_release_zip.py` could build a deterministic archive without proving that the full semantic gate and final manifest had passed in the same release operation. Deterministic bytes are useful, but deterministic packaging of an unchecked tree is still unchecked packaging.

## 926.3 Correction in v888

The v887 worktree was first repaired until all 162 child checks and the final manifest step passed. v888 then closes the packaging seam:

```bash
python3 scripts/release_gate.py --write-manifest \
  --build-zip /absolute/output/The-Election-Stack-revNNNN-YYYY.MM.DD.HH.MM-codename.zip
```

Under the existing single-instance release lock, this path now runs the full gate, writes the manifest only after all semantic checks pass, builds a new deterministic ZIP, and independently verifies that ZIP before returning success. It rejects partial-gate builds, relative output paths, manifest-skipping combinations, and existing output files. A verifier failure removes the newly built carrier.

The standalone ZIP builder remains useful for diagnostics and builder tests, but it is no longer presented as a release verdict.

## 926.4 What is missing from the mission, not merely from the files

### Named authority and acceptance

All 39 claim-evidence rows and all 27 hazard rows still name `TBD` as owner. All 27 hazards are open. The risk register contains 112 rows—29 critical and 70 high—with no closed row. A proof obligation without an accountable institution, acceptance criterion, decision deadline, and remedy path is a specification, not an operating assurance system.

### Real independent evidence

The archive has extensive synthetic fixtures and self-checks, but no live local drill, no completed external review, no measured witness network, no production trust-root governance, and no independently observed election closeout. The preparation ledgers accurately say `not_run` or `not_measured`; that honesty must be preserved while the project recruits real adopters.

### A concrete Track A value chain

Track A should become much more concrete around ballot definition, ballot accounting/custody, NIST common data formats, post-election audit evidence, adjudication, and closeout. These are the shortest path from the archive's theory to a useful jurisdiction-side evidence product. Paper records and audits are not fallback decorations; they are the material truth-and-recovery floor for binding elections.

### Production governance

Signer authorization, key lifecycle, log and witness diversity, revocation/status, emergency succession, publication authority, retention, records law, privacy/redaction, accessibility, language access, evidentiary admissibility, and incident command remain mostly modeled rather than institutionally operated.

### Honest maturity dimensions

A single label such as `pilot_ready` collapses too many meanings. Replace it over time with at least five independent axes:

- artifact/schema conformance;
- synthetic rehearsal coverage;
- deployment authority and local configuration;
- independent validation; and
- live operational evidence.

No component should inherit a deployment claim merely because its local fixture passes.

## 926.5 Where the archive is wasteful

### Documentation multiplication

The uploaded carrier contained 3,139 governed files and about 16.8 MB. It included 805 numbered documents. Documents 365 through 652 alone accounted for 288 files and roughly 5.0 MB—about 59 percent of numbered-document bytes. Much of that family repeats the same verifier questions, non-replacement disclaimers, and evidence-surface template around different platforms or audiences.

The content can be socially important while the representation is still wasteful. Freeze new family expansion unless a proposed document has a named owner, a distinct proof obligation, an executable artifact or test, and an explicit reason a parameterized registry/template cannot carry it. Consolidate repeated families gradually, retaining tombstones, stable identifiers, and digest-preserving migration notes so references do not disappear.

### Generated-evidence accumulation

The uploaded carrier shipped 625 report files; 579 had revision tokens in their names. Current release evidence should stay complete and readable, but historical generated bodies can be compacted into digest-preserving summaries when no gate or public contract requires the full duplicate body.

In v888, 25 superseded v886-v887 generated source-byte, fixture-sweep, and risk-priority reports were compacted in place after their original SHA-256 digests and sizes were recorded in `artifacts/reports/rev0888-stale-source-byte-report-compaction.json`. This recovered 324,640 gross bytes while preserving every path and leaving all current v888 report bodies complete.

### Source-byte tunnel vision

Pinning source bytes is valuable because upstream pages drift. But the source lock had 1,216 rows, only 118 pinned rows, 13 present receipts, and 105 missing receipts among the pinned set. The last several revisions devoted disproportionate engineering attention to moving that queue through increasingly elaborate batch, host-slice, DNS, retry, parser, and operator-workplan machinery.

After the most consequential sources are pinned, source-byte completion should be risk-tiered and time-boxed. It must not outrank named ownership, a real local pilot, ballot-accounting integration, audit closeout, independent review, or production authority. The project should optimize for **decision-relevant evidence**, not receipt-count completion as an end in itself.

### Gate process overhead

The release gate currently launches 162 Python child processes. Isolation and clear failure locality are useful, but much of the runtime is interpreter startup and repeated tree parsing. Keep the full release verdict, then evolve it into shared data-driven check runners and explicit `fast`, `core`, and `deep` stages. Only the complete deep path may publish a canonical release.

## 926.6 Product and research direction

The most credible near-term product is an **election evidence sidecar and verifier SDK**, not a replacement voting system. It should ingest jurisdiction/vendor exports, bind the authorized election definition, reconcile ballot accounting and custody, package standardized CVR/results data, record audit/recount/adjudication steps, publish signed notices, and emit independently replayable closeout packets.

Track C attestation, provenance, SCITT-style transparency, SLSA, and content credentials remain useful research inputs. They can establish who signed, built, endorsed, or published an object and whether views equivocate. They do not, by themselves, establish that voter intent was captured correctly or that a reported outcome is true. Track C therefore must not dictate Track A architecture or create a false substitute for paper, accounting, observation, and audits.

A practical sequence is:

1. one jurisdiction, one election type, one export profile, one closeout packet;
2. import/export adapters for NIST Ballot Definition, CVR, Voter Records Interchange, and Election Results common data formats;
3. ballot-accounting and risk-limiting/post-election audit evidence binding;
4. independent verifier and disagreement reports used by at least two outside organizations;
5. only then broader platform/media families, witness networks, and advanced attestation research.

## 926.7 Research alignment

The scope reset is aligned with the archive's pinned primary sources and explicitly labeled informative cross-references:

- NASEM's election-security work emphasizes voter-verifiable paper records and audits (`source: nasem_securing_the_vote_highlights_pdf`).
- The EAC's 2024 post-election tabulation audit guide treats audits as a structured election-administration process (`source: eac_post_election_tabulation_audit_guide_2024_pdf`).
- NIST publishes common data formats for Ballot Definition, Cast Vote Records, Voter Records Interchange, and Election Results, plus implementation guidance (`source: nist_sp1500_20_bd_pdf`, `source: nist_sp1500_103_cvr_pdf`, `source: nist_sp1500_100r2_err_pdf`, `source: nist_gcr_24_058_cdf_implementation_guidance_pdf`).
- NIST's Election Infrastructure Profile provides a cybersecurity-governance frame rather than an election-truth oracle (`xref: nist_nistpubs_vts_nist_vts_200_1`).
- EAT, SCITT, SLSA, and C2PA provide useful attestation, transparency, supply-chain, and provenance primitives, while provenance does not itself prove substantive truth (`source: rfc9711_txt`, `source: draft_scitt_architecture_22_txt`, `xref: slsa_spec_v1_2`, `xref: c2pa_content_credentials_spec_2_4_html`).

## 926.8 Stop rules

Do not add a new doctrine, registry, platform family, or generated report unless it closes a named mission-kernel proof obligation, removes a measured operational risk, supports an adopter, or is required by a release contract. Prefer deleting duplication, parameterizing repeated content, assigning owners, and running real exercises.

## 926.9 Boundary

v888 repairs release integrity and establishes a sharper mission/product direction. It remains synthetic-only. It is not current voter instruction, legal advice, certification, public-release authorization, source-byte completeness, production signer authority, independent validation, or live-pilot evidence.
