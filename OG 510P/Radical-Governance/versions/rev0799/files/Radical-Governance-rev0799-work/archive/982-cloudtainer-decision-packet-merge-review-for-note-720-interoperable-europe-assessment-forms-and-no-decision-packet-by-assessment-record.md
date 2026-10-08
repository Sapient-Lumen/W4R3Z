# 982 — Cloudtainer decision-packet merge review for note 720, Interoperable Europe assessment forms, and no decision packet by assessment record

## One-line thesis

The archive should convert merge pressure on note `720` into a preservation packet rather than a deletion path: an interoperability assessment form, claim ledger, or procedural digital-waist case can test one kind of required assessment, but it does not preserve the generic decision-packet grammar for determination classes, reason-giving, effect dates, implementation holds, review clocks, withdrawal, supersession, and no government by outcome letter.

## Why this matters

The service-home lane now has successor-route, test, redirect-ledger, reader-visible, final-preservation, and cross-sector application coverage. Continuing to add service-home examples would risk diminishing returns. The retirement queue now points at a different danger: note `720` is a small zero-dependency route with lexical and tag overlap against note `858`, so it is easy for a future maintainer to think it has been absorbed by the Interoperable Europe assessment packet.

That would be wrong. Note `858` is a strong applied packet for a procedural digital waist: when a public-sector interoperability requirement triggers an assessment duty, the file should separate legal, organisational, semantic, and technical interoperability from form completion theater. Note `857` supplies the claim-ledger discipline needed to avoid citing a whole note as if every sentence were equally settled. Those are useful targets for absorption pressure, but neither one is a field-level decision-packet route.

Note `720` asks a different question: what is the authoritative act that grants, refuses, varies, suspends, revokes, returns, closes, supersedes, or conditions a live matter? That question must stay reusable across benefits, permits, migration, inspections, care, environmental approvals, redress, platform migrations, and cross-border digital services. A procedural assessment record may be mandatory and public-facing; it still is not automatically the decision object that changes a person's right, duty, status, money, or service access.

## Pattern pack

### 1. Determination-class grammar is not preserved by an assessment form

Note `720` protects the distinction between approval, refusal, conditional grant, variation, suspension, revocation, administrative return, referral, withdrawal acknowledgement, closure without merits, supersession, and extinction. Note `858` can test whether a binding interoperability requirement was assessed before adoption. It does not name the field's determination classes or say which act is being challenged.

If note `720` were retired into note `858`, the archive would accidentally narrow the decision object to the assessment obligation. That would miss fields where the key act is a benefit denial, platform status migration, permit condition, case closure, inspection order, emergency eligibility determination, or payment hold.

### 2. Reason-giving and legal-basis kernels are not the same as assessment criteria

Interoperability-assessment guidance can ask whether cross-border digital public-service effects were considered. That is important, but it is not the same as a minimum reason-giving kernel for a consequential decision. A decision packet must dock facts, findings, law, policy basis, conditions, duration, amount, status effect, and next action to the actual act.

A completed assessment form can still leave the affected person with only an opaque outcome letter.

### 3. Effectivity and review clocks need their own route

Note `720` preserves the separation between decision date, notice date, operative date, implementation date, review-clock start, payment/service/enforcement start, and stay or hold rules. Note `858` has assessment timing discipline, but it does not preserve appeal-clock and implementation-clock grammar for every consequential determination.

That is the key deletion blocker. Administrative injury often happens when a person cannot tell whether the right ended on decision, notice, effective date, service change, payment change, or appeal-window expiry.

### 4. Implementation duties and stays must stay visible

Decision packets need to state what a decision triggers downstream: status update, payment change, service handoff, enforcement, referral, compliance duty, temporary hold, stay, second look, or reversal route. A procedural interoperability packet can improve cross-border service design while still leaving downstream implementation duties outside the decision object.

The archive should therefore preserve note `720` until a successor route has explicit fields for implementation obligations and holds.

### 5. Withdrawal, correction, supersession, and lineage are decision-packet residue

Note `720` also carries lineage grammar for decisions that are corrected, withdrawn, superseded, remanded, varied, or reopened. This matters because people often challenge the wrong object when a field hides the relationship between old decision, new notice, revised reason, corrected record, and operative remedy.

Neither a claim ledger nor an interoperability assessment is a substitute for this lineage unless the successor route explicitly preserves it.

## Merge packet created in this revision

This revision adds `MP-004-720-to-857-858` to `metadata/route_merge_packets.json`.

The packet records:

- source note: `720`;
- candidate status: `merge_reviewed_keep_decision_packet_route_active`;
- possible target surfaces: note `857` and note `858`;
- protected elements: determination classes, authority/case anchors, reason-giving, effectivity/review clocks, implementation duties, stay/hold rules, correction/supersession/withdrawal lineage;
- holding: note `720` is **not deletion-ready**;
- next action: build a real decision-packet successor or schema extension before any absorption patch is attempted.

## Audit/refactor in this revision

The retirement audit now accepts and displays an explicit `review_packet_file` / `review_packet_note` for merge-reviewed candidates. The lint guard validates those pointers when present. This prevents future merge reviews from becoming invisible metadata rows that readers cannot inspect.

## Anti-theater tests

1. Can a reader identify the exact decision object, not merely an outcome, form, notice, or assessment?
2. Can the archive distinguish decision class, authority, case lineage, legal basis, reason kernel, effect date, implementation step, review clock, and stay rule?
3. Can a completed assessment record be separated from the rights-bearing or service-bearing decision that follows it?
4. Can a corrected, withdrawn, superseded, remanded, or varied decision preserve lineage to the original act?
5. Can the retirement audit show a reader-visible review packet before a similarity score becomes deletion pressure?

## Current holding

Keep note `720` active. `MP-004` is a preservation instruction, not a deletion instruction.

The new review narrows the retirement queue by removing a false candidate from raw similarity pressure. It does not reduce doctrine by deletion; it reduces risk by making the non-absorption explicit.

## Sources

This review relies on existing archive source keys from note `858`: Regulation (EU) 2024/903, Interoperable Europe assessment guidance, the mandatory-assessment update, and the two-year implementation update. Those sources establish assessment and interoperability context; they do not prove that an assessment record is a decision packet, that affected people received reasons, or that appeal and implementation clocks were correctly attached.
