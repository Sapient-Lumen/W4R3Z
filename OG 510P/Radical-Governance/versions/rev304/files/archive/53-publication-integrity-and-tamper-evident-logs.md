# Publication Integrity & Tamper‑Evident Logs (Anti–Silent Revision)

**Purpose:** prevent silent edits and disappearance of public artifacts so accountability survives conflict, drift, and capture.
**Person served:** a person (including future persons) relying on public records to contest power who needs official artifacts to be tamper‑evident and retrievable as‑of.

**From-below:** This prevents silent edits by making changes tamper‑evident, so the record you relied on can’t be rewritten without trace.
**EXP pointer:** counters `EXP-01` (Opacity) by preserving durable, contestable records (and survives degraded modes) (`98-persons-path-and-accessibility-invariants.md`).
**As-of & corrections:** This artifact is versioned and queryable “as-of”; corrections emit a citable update (`REL-*`) and must propagate to dependent records/systems (see `31`, `70`, `73`; integrity rules live here). (`101` NR-07, NR-15)
**Authority:** every published feed MUST name the publishing unit (and its delegation/mandate where relevant) so integrity promises are enforceable and contestable (`34-...`, `32-...`). (See `101-claude-rev142-normative-requirements.md` (NR-09).)
**Retaliation safety:** default to role/office identifiers (not personal identifiers) and route protected disclosures via `83-...` / secrecy governance `77-...` when exposure increases harm. (See `101-claude-rev142-normative-requirements.md` (NR-08).)

**Mercy / interim protection:** where this interface can impose coercion, deprivation, or irreversible loss, it MUST define an auditable waiver/exception path (`85-waivers-variances-and-exceptions-discipline.md`) and an interim protection / stay rule when deadlines are missed or a credible hardship claim is filed (`82-service-standards-and-minimum-service-guarantees.md`, `36-appeal-lanes-and-redress-registry.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05, NR-16).)
**Time bounds & escalation:** disclose ack/decision deadlines + no-response rule (auto-escalation / interim protection) and publish tail waits for high-harm classes (default: `82-service-standards-and-minimum-service-guarantees.md`; receipt semantics: `31-records-foi-and-government-memory.md`). (See `101-claude-rev142-normative-requirements.md` (NR-05).)
**Notices & receipts:** rights‑affecting outcomes MUST generate a comprehension-tested Decision Receipt with the `31` minimum fields (incl. consequence triggers, as‑of basis, deadlines, and the binding follow‑through lane). (See `101-claude-rev142-normative-requirements.md` (NR-02, NR-15).)


Governance becomes non-auditable when public artifacts can be **quietly changed or deleted**. This memo specifies a compact *publication integrity layer* that makes register entries, releases (`REL-*`), and “as‑of” facts **verifiable over time**.

**Use-case:** if a decision receipt (`DRR-*`) cites a rule (`RULE-*`) or a release (`REL-*`), a reviewer must be able to retrieve the **exact version** that existed “as-of” the decision, and detect later changes.
**Intergenerational note:** durable records are a form of representation. They speak for people who cannot contest (the dead, the disappeared, future persons). (See `101-claude-rev142-normative-requirements.md` (NR-12).) At the governance/violence boundary (`[TM-31]`), publication integrity may be the **last preservable constraint** and the foundation for eventual accountability (`31-...`, `04-...`).

Anchors: append-only log pattern ([BIB-RFC6962]); transparent log implementations ([BIB-TRILLIAN], [BIB-SIGSTORE-REKOR]); trusted timestamping ([BIB-RFC3161]); provenance/attestation patterns ([BIB-SLSA-1-0], [BIB-IN-TOTO]).

## Kernel anchors (do not repeat)
- **Protective legibility / adoption:** disclosure and controls can be weaponized or ignored; design for safety and incentives. (`99-protective-legibility-and-adoption-dynamics.md`)
- **From-below usability:** these artifacts MUST remain comprehensible and actionable via the person’s path (assisted/offline options; no insider knowledge). (`98-persons-path-and-accessibility-invariants.md`)
- Release registry (what gets published): `51-...`.
- Records custody / FOI and durable “as-of” access: `31-...`.
- Secrecy governance (what must not be published): `77-...`.
- Interop version semantics + join keys: `70-...`.

## Named tensions (design must surface these)
- Immutability for trust vs correction for justice (fix without erasing).
- Transparency vs retaliation/coercion risk (don’t publish targets).
- Cryptographic rigor vs accessibility and low-infrastructure verification.
- Disclosure for accountability vs attacker advantage (cyber/CI contexts).

---
## A) Threat model (what this layer defends against)
Publication integrity is a defense against:
- **Silent edits:** content changes without a visible changelog (including “statistical rebases”).
- **Backdating:** rewriting history to make prior decisions appear justified.
- **Selective deletion:** removing embarrassing rows, files, or pages.
- **Forked reality:** different audiences seeing different “official” versions.
- **Capture by hosting:** a single portal can disappear, be censored, or be rewritten.

This layer does **not** prevent lawful change (amending a rule, correcting data). It prevents **undetectable** change and makes contestation feasible.

---

## B) Integrity levels (choose the smallest that works)
| Level | What you ship | What you get |
|---|---|---|
| L0 — Basic legibility | stable IDs + “as‑of” access + changelog | no silent edits inside the platform (auditable by inspection) |
| L1 — Signed bundles | hash manifest + signature (+ mirrors) | tamper detection even if hosting is compromised |
| L2 — Timestamped signatures | L1 + trusted timestamp token | stronger “existed at time T” claims |
| L3 — Transparency log | append-only Merkle log + monitors | public “no deletion / consistent history” guarantees |

Default recommendation: **L1** for core registers and canonical `REL-*` releases; **L3** for constitutional registers and high‑stakes feeds (competence ledger, PRR, EMR, core enforcement logs).

---

## C) Minimum viable publication integrity (L0)
Any public feed (register or release) SHOULD provide:
- **Stable identifiers** in rows/records (the archive’s join-keys).
- **As‑of retrieval:** prior versions remain retrievable (use tombstones rather than deletion).
- **Changelog:** what changed, when, and why (one screen; link to detail where needed).
- **Canonical + mirror links:** at least one independently hosted mirror pointer (see §E).

This is the *floor* that prevents “nothing changed” ambiguity.

---

## D) Signed bundle pattern (L1–L2)
When publishing an update (a register export or `REL-*` release), ship a **bundle**:
1) **Payload**: the files (CSV/JSON/PDF/etc.)
2) **Manifest**: a file list + cryptographic hashes (e.g., SHA‑256) + sizes
3) **Signature**: a detached signature over the manifest by the publishing unit (or an attested key)
4) *(Optional L2)* **Timestamp token** for the signature/manifest ([BIB-RFC3161])

**Rule:** the manifest and signature are treated as part of the publication. If a file changes, a **new bundle** is published and linked in the changelog.

**Where it joins:**
- A `REL-*` record SHOULD point to the bundle manifest + signature.
- Core registers SHOULD publish each export as a `REL-*` (lightweight) so audits can cite `REL-*` instead of brittle URLs.
- Decision receipts (`DRR-*`) that rely on a `REL-*` SHOULD cite the **as‑of version** (timestamp or version tag).

---

## E) Mirrors (anti-host capture)
- Maintain ≥2 **independent mirrors** for constitutional feeds (a second government host + civil-society mirror is ideal).
- Publish mirror pointers in the register/release metadata (and in the manifest if feasible).
- Treat prolonged mirror divergence as an incident for oversight (`OFR-*`), since divergence implies forked reality.

---

## F) Transparency log upgrade (L3)
For the highest stakes feeds, publish bundle manifests into an **append-only transparency log** (Merkle tree):
- Each update publishes a signed **checkpoint** (tree head).
- Anyone can request **inclusion** and **consistency proofs** to verify no deletions or rewrites.
- Independent monitors “watch” the log and alert on inconsistency.

This is the same pattern used in Certificate Transparency ([BIB-RFC6962]). Practical starting points include Trillian ([BIB-TRILLIAN]) or existing transparency log infrastructure (e.g., Rekor) ([BIB-SIGSTORE-REKOR]).

**Minimal operational rule:** a unit that publishes a transparency log MUST publish at least one public monitor feed (or endorse third-party monitors) so verification happens in practice.

---

## G) Provenance & attestations (optional; high-value for “generated facts”)
For algorithmic outputs, complex pipelines, or heavily transformed datasets:
- publish provenance/attestations describing **how** the artifact was produced (tooling, inputs, steps, environment).
- keep the claims modest: provenance improves auditability; it does not guarantee correctness.

Supply chain patterns such as SLSA and in‑toto provide workable formats and threat models for attestations ([BIB-SLSA-1-0], [BIB-IN-TOTO]). This is optional, but recommended for `REL-TYPE: TECH` and for releases that drive enforcement or entitlement decisions.

---

## H) Exceptions (privacy / security / operational)
- If the payload is gated or confidential, still publish **existence metadata** + method note + revision log + how to request access (`FOI-*` or lane `AL-*`).
- If publishing hashes creates risk (e.g., confirming the existence of a sensitive file), publish a redacted manifest and log the exception with a reason code (`RC-FOI-*` where applicable).
- Where you still need “existed at time T” without confirming details publicly, consider **guarded commitments** (e.g., salted commitments held in the oversight channel and referenced by a public receipt) so later declassification can be matched to earlier receipts.

---
- **Protective legibility:** publication integrity can be used to *target* people (e.g., identifying who published what, when). Minimize personally identifying metadata in public manifests; use role/office identifiers and apply secrecy governance when exposure increases harm (`77`, `99`).
- **Usable verification:** provide a human-readable “verify this release” path (not only cryptographic primitives) so journalists/advocates can validate receipts without specialized tooling (`51`, `98`).
## I) Minimal metrics (signals)
- share of core feeds shipped at **L1+** (manifest + signature) [DAG-5]
- correction / revision latency (median + 90p) [DAG-5]
- mirror divergence incidents (count; time-to-resolve)
- transparency log monitor coverage (yes/no; number of independent monitors)

See also: `31-records-foi-and-government-memory.md` (records discipline), `51-release-registry.md` (release objects), `80-implementation-roadmap.md` (sequencing), `32-oversight-institutions-and-follow-through.md` (legibility-gap audits).

## J) Collapse boundary (when other safeguards fail)
When lawful governance collapses into violence or war, many interfaces in this archive stop functioning. What can often still be preserved is the **record**: (See `101-claude-rev142-normative-requirements.md` (NR-13).)
This matters because people who can no longer contest—including the dead—are represented only by the integrity of the record.
- Keep issuing/collecting *receipts and logs* (even on paper) and publish checksumed bundles when possible.
- Prioritize **as-of access** and **non-deletion** rules for coercive events, emergency measures, and high-stakes service denials.
- Mirror minimally outside the threatened host (see §E) so evidence survives capture or destruction.
- Treat record destruction or silent revision as a first-order incident (`DRR-TYPE: INCIDENT` + `OFR-*` follow-through).

(See the “collapse boundary” note in `23-emergency-governance-and-exceptions.md` for the broader limit.)