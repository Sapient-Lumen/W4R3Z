# 217 — Claim cards & traceability minspec (tight, bundle-ready)

**Track:** A (Deployable core)


This document defines a **small, repeatable “claim card”** format that can travel with an evidence bundle
(`211`) and reduce interpretive drift during disputes.

The goal is *not* to invent new bureaucracy.
It is to make sure every bundle answers, in bounded space:

- **What claim is being asserted (or refuted)?**
- **What is explicitly *not* being claimed?**
- **Which proof obligations are in play?**
- **Which concrete evidence objects are in the packet (and which are missing, provably)?**

Related:
- Scope + claim contract: `166` / `167`
- Claim/evidence matrix (authoritative rows): `artifacts/claims/claim-evidence-matrix.csv`
- Proof obligations registry: `164`
- Court bundle recipes: `211`
- Incident dispatch map: `216`
- Artifact reference tokens: `163`


## 217.1 The invariants (what makes a claim card useful)

A claim card MUST be:

1. **Bounded:** one claim (or one allegation family). If you need more, ship more cards/bundles.
2. **Traceable:** it names **PO-IDs** and references artifacts using `163` tokens.
3. **Non-ambiguous about scope:** it includes “non-claims” (what this packet cannot prove).
4. **Mirror-friendly:** it contains no high-risk bulk (no screenshots as embeds; no third-party PDFs).
5. **Epistemically labeled:** load-bearing statements are tagged (OBSERVED/MEASURED/REPORTED/INFERRED) with an explicit confidence marker (`218`).
6. **Update-disciplined:** it states when the claim card may be revised (and what would force a new bundle).


## 217.2 Minimal fields (do not add more unless you must)

Use `artifacts/templates/claim-card.md` as the canonical template.

**Required fields:**

- **ClaimID:** prefer `CLM-###` rows from `artifacts/claims/claim-evidence-matrix.csv`.
- **Claim statement:** one paragraph maximum.
- **Epistemic status + confidence:** tag the claim statement and any major inferences (`218`).
- **Scope boundary pointers:** cite the relevant boundary docs (`166`/`167`) and any scoped subclaims.
- **Proof obligations:** list `PO-###` IDs (registry in `164`).
- **Hazards addressed:** list `HZ-###` IDs if applicable (hazard register).
- **Evidence present:** a short list of `TYPE:path` tokens (`163`), plus the bundle’s `manifest.json`.
- **Evidence missing (if any):** *what is absent* and *what receipt proves absence* (missingness is evidence).

**Optional fields (use sparingly):**

- **Decision rule:** what would constitute “claim holds” vs “claim fails” for a verifier.
- **Public statement mapping:** which PublicNotice / digest card / parity snapshot(s) correspond to this claim.
- **Redaction notes:** if any evidence-relevant artifact was redacted/transformed, include `redaction-log.md` (see `DOC:docs/225-redaction-logs-and-transformation-accountability.md`) and cite `CHECK:artifacts/checklists/public-artifact-redaction-checklist.md`.


## 217.3 How to build a claim card quickly (from existing registries)

1. Start from the **ClaimID row** in `artifacts/claims/claim-evidence-matrix.csv`.
2. Copy the **ProofObligations** field as the canonical PO list (then prune, don’t expand).
3. Convert the row’s **EvidenceArtifacts** to a minimal “present in this packet” list.
4. Add **missingness** explicitly:
   - If something expected is absent, include the *receipt of absence* (coverage/missingness artifact).
5. Add a **one-line decision rule** if (and only if) it prevents public misinterpretation.


## 217.4 Bundle integration (recommended, not mandatory)

When assembling a bundle (`211`), include the claim card as:

- `claim.md` (renderable, human-first)
- and/or `claim.json` (optional future: machine-checked projection)

The bundle `manifest.json` should already content-address the packet. The claim card’s job is to keep
humans from accidentally smearing the claim boundary wider than the evidence supports.


## 217.5 Failure modes (what this prevents)

- **“Argument by folder”**: shipping a packet where no one can tell what’s being proven.
- **Scope creep**: the packet becomes a proxy for “the whole election is illegitimate.”
- **Post-hoc narrative edits**: new interpretations appear without changing the PO list or evidence set.
- **Selective omission**: missing artifacts are treated as “unknown” instead of *provably missing*.
