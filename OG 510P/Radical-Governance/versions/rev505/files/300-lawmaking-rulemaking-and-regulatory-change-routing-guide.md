# 300 — Lawmaking / Rulemaking / Regulatory-Change Routing Guide

**Purpose:** turn the archive’s lawmaking / rulemaking / regulatory-change family into a readable stack so rule inventories, legislative drafting, impact assessment, and operational release discipline stop competing for the same conceptual role.

**Why this memo exists:** `25`, `39`, `118`, `215`, `317`, `320`, `316`, `319`, `318`, `216`, and `208` all surface for queries like “how should laws change”, “better rulemaking”, “what belongs in a bill packet”, “what belongs in delegated legislation”, “when does guidance become shadow law”, “how should regulations be reviewed”, “how do we avoid shipping policy blind”, or “how do we know what changed and when”. They describe one family from different layers. The archive should name those handoffs explicitly rather than invite flattening.

**Evidence anchors:** the OECD’s regulatory-policy baseline still frames rulemaking as a continuous policy cycle with ex ante impact assessment, ex post evaluation, periodic stock review, and communication strategy [BIB-OECD-RPG-0390] [BIB-OECD-RPO-2025]; current OECD EU better-regulation work emphasizes high-level strategy, implementation capacity, stakeholder engagement, evidence use, and regular review across the whole cycle [BIB-OECD-BETTERREG-EU-2025]; the European Commission’s current better-regulation hub keeps “evaluate first”, impact assessment, stakeholder consultation, scrutiny, subsidiarity/proportionality, and implementation dialogues in one operating frame [BIB-EC-BETTERREG-HUB-2026] [BIB-EC-EVALUATING-LAWS-2026].

---

## Canonical reading order

### 1. Start with `25-legal-legibility-and-rule-inventory.md`
Use `25` when the question is:
- how people can find the real rule that governs them,
- how “what was in force when” becomes answerable,
- how guidance, scripts, and software-configured pseudo-rules stop hiding in the dark,
- or how legal legibility becomes a person-facing rule-of-law condition instead of a publishing ritual.

`25` is the **public legal-legibility / rule-discoverability front door**.

### 2. Move to `39-rulebook-and-instruments-registry.md`
Use `39` when you need:
- the actual rule-register schema,
- stable IDs, versioning, authority chains, and effective windows,
- machine-readable “as-of” rule queries,
- or the operational substrate that lets decisions and releases cite the exact rule basis.

`39` is the **public-rules-register / versioned rulebook substrate memo**.

### 3. Use `118-rulemaking-and-change-control.md`
Use `118` when the real issue is:
- how any material rule change becomes a change packet with review gates,
- how authority, notice, rollback class, and remedy readiness are attached to a rule change,
- how ordinary rulemaking differs from emergency lanes,
- or how policy changes stop being unlogged power moves.

`118` is the **generic rule-change-control front door**.

### 4. Use `215-legislative-process-and-drafting-rails.md`
Use `215` when the question becomes:
- how bills, amendments, hearings, and enactment notes should work,
- how lawmaking stays diff-first, readable, and anti-bundled,
- how participation is joined to reasons and text,
- or how legislative changes publish implementation and remedy readiness before passage.

`215` is the **legislative-process / drafting / amendment-trace front door**.

### 5. Use `317-delegated-legislation-empowering-provisions-henry-viii-powers-and-parliamentary-scrutiny-rails.md`
Use `317` when the question becomes:
- what belongs in primary law versus delegated legislation,
- how empowering provisions should specify scope, purpose, maker, and legal basis,
- when draft instruments should be published with a bill,
- how Henry VIII powers, skeleton bills, and disallowance / affirmative procedures should be bounded,
- or how a statute can delegate implementation detail without delegating the real policy itself.

`317` is the **primary-to-secondary-legislation / parliamentary-scrutiny seam memo**.

### 6. Use `320-incorporation-by-reference-external-standards-dynamic-updates-and-public-access-rails.md`
Use `320` when the question becomes:
- when law may import an external standard, code, rate, index, or public text by reference,
- whether the reference should be static or time-to-time,
- how incorporated material should be identified, accessed, snapshotted, and surfaced in the rule register,
- how to prevent paywalled law or silent external updating,
- or how incorporation by reference differs from both ordinary delegated legislation and downstream guidance.

`320` is the **external-material / incorporation-by-reference seam memo**.

### 7. Use `316-bill-finalization-assent-promulgation-publication-commencement-and-constitutional-referral-rails.md`
Use `316` when the question becomes:
- how a bill becomes law after the final vote,
- how assent, reconsideration, constitutional referral, promulgation, and official publication should work,
- how commencement and transition rules should be made legible,
- or how final-stage corrections avoid becoming a shadow second lawmaking process.

`316` is the **how-bills-become-law / promulgation / commencement seam memo**.

### 8. Use `319-statute-book-maintenance-consolidation-codification-repeal-and-revision-bill-rails.md`
Use `319` when the question becomes:
- how to keep enacted law coherent after years of amendment drift,
- when to use consolidation, repeal, revision bills, restatement, or codification,
- how official current texts should relate to as-enacted texts and amendment history,
- how editorial or revision powers should be bounded,
- or how to improve legal accessibility without smuggling policy reform through a tidy-up lane.

`319` is the **statute-book-maintenance / consolidation / repeal / revision seam memo**.

### 9. Use `318-statutory-guidance-codes-of-practice-directions-manuals-and-shadow-law-rails.md`
Use `318` when the question becomes:
- whether guidance, codes, directions, manuals, FAQs, or scripts are actually binding,
- when “must have regard to” or quasi-mandatory guidance has become shadow law,
- how person-affecting guidance should be published, versioned, and challenged,
- or how internal manuals and software-configured pseudo-rules stop silently governing people.

`318` is the **law-to-operations / quasi-law / shadow-law seam memo**.

### 10. Use `216-regulatory-impact-assessment-and-ex-post-review-rails.md`
Use `216` when you need:
- a public hypothesis-and-evidence packet around a proposed rule,
- alternatives analysis, distributional analysis, administrative-burden assessment, and review triggers,
- mandatory ex post validation instead of “regulate and forget”,
- or a binding path from evidence to renew / modify / sunset.

`216` is the **impact-assessment / review / loop-closure memo**.

### 11. Use `208-change-management-and-release-engineering-for-government.md`
Use `208` when the issue is:
- how enacted or adopted changes are actually shipped into live services, operations, data flows, or algorithms,
- how change packets, release notes, monitoring, rollback classes, and post-implementation review should run,
- how implementation discipline connects authority, notice, and remedy,
- or how governments stop treating operational release as an invisible afterthought.

`208` is the **implementation / release-engineering / safe-ship operations memo**.

---

## The stack in one line

**How can people find the rules that actually govern them?** → `25`  
**How are those rules represented as stable, versioned, queryable objects?** → `39`  
**How do material rule changes become controlled, receipted change events?** → `118`  
**How should legislative text, amendments, and deliberation-to-text handoffs work?** → `215`  
**How should primary legislation delegate future lawmaking without becoming a blank cheque?** → `317`  
**When may law import an outside document, standard, rate, or code without becoming paywalled or silently self-updating?** → `320`  
**How does a passed bill become binding law through assent, promulgation, publication, and commencement?** → `316`  
**How do we keep the statute book coherent, current, and provenance-safe over time?** → `319`  
**How do guidance, codes, directions, manuals, and scripts gain or avoid legal effect?** → `318`  
**How do we assess likely impact and force later review?** → `216`  
**How do adopted changes get shipped safely into operating reality?** → `208`

---

## Confusion boundaries

### `25` vs `39`
- `25` is the **person-facing legal-legibility front door**.
- `39` is the **rule-register and versioning substrate** that makes legibility auditable and joinable.

### `39` vs `118`
- `39` tells you **what the rule objects are and how to query them “as-of”**.
- `118` tells you **how a proposed or adopted rule change moves through controlled change governance**.

### `39` vs `318`
- `39` is the **rule-register substrate** that inventories guidance-like artifacts and hidden rule surfaces.
- `318` is the **design memo** for how guidance, codes, directions, manuals, and shadow-law risks should be typed, published, and bounded.

### `39` vs `319`
- `39` is the **rule-register substrate** that stores official current texts, prior versions, and maintenance metadata.
- `319` is the **design memo** for when and how a jurisdiction should consolidate, repeal, restate, codify, or certify revision work in the first place.

### `118` vs `215`
- `118` is the **generic change-control frame** for rules across instruments.
- `215` is the **legislative specialization** for bills, amendments, committee process, and enactment packets.

### `215` vs `317`
- `215` governs **how a bill is drafted, amended, heard, and made vote-ready**.
- `317` governs **what the bill may safely delegate to future secondary legislation, and under what scrutiny and constraint**.

### `317` vs `316`
- `317` asks **how primary legislation delegates future lawmaking power and how delegated instruments are bounded.**
- `316` asks **how the bill that parliament has already passed becomes authentic, published, and legally live.**

### `317` vs `320`
- `317` governs **whether and how a bill or regulation should delegate future lawmaking power at all.**
- `320` governs **what happens once the instrument imports outside material by reference: static versus ambulatory mode, access, snapshots, and external-change discipline.**

### `320` vs `27`
- `320` governs **the legal seam where legislation imports external material by reference.**
- `27` governs **the broader institutional design of standards bodies, openness, anti-capture design, and conformance ecosystems.**

### `320` vs `39`
- `320` is the **design memo** for whether and how external material should be incorporated and surfaced.
- `39` is the **register / substrate memo** for recording the incorporated material, access path, version, and point-in-time snapshot.

### `320` vs `318`
- `320` governs **imported external material that law makes part of the binding rule.**
- `318` governs **guidance, manuals, codes, and pseudo-rules that sit alongside or downstream of law and may start acting like law in practice.**

### `317` vs `318`
- `317` governs **whether a norm should exist as delegated legislation at all, and under what scrutiny and constraint.**
- `318` governs **how guidance, codes, directions, manuals, and software-configured pseudo-rules are typed, published, versioned, and prevented from doing legislative work in disguise.**

### `316` vs `319`
- `316` governs **how a passed bill becomes authentic, officially published, and in force.**
- `319` governs **how that body of law is later kept coherent, current, and navigable through consolidation, repeal, restatement, and revision work.**

### `319` vs `318`
- `319` governs **maintenance of the statute book itself: official current texts, repeal of dead law, provenance-safe restructuring, and no-policy-change maintenance lanes.**
- `318` governs **quasi-law and operational instruments that sit downstream of enacted law and may start acting like law in practice.**

### `316` vs `318`
- `316` governs **how a bill or instrument becomes legally authentic, officially published, and in force.**
- `318` governs **what comes after that when softer or operational instruments start shaping compliance, discretion, or outcomes in practice.**

### `118` vs `216`
- `118` governs **authorization, notices, release class, and rollback discipline around rule changes**.
- `216` governs **evidence quality, alternatives analysis, review commitments, and ex post loop closure**.

### `316` vs `216`
- `316` asks **how a passed bill becomes authentic, published, and legally live.**
- `216` asks **what evidence justified the rule and how later review / renewal should work.**

### `319` vs `216`
- `319` asks **how to keep accumulated law coherent and current without changing policy in disguise.**
- `216` asks **whether the rule works, what its impacts are, and whether it should be renewed, changed, or sunset.**

### `318` vs `208`
- `318` governs **normative guidance, codes, directions, manuals, and public-facing or outcome-determinative pseudo-rules**.
- `208` governs **operational deployment into services, systems, staffing, procurement, and monitoring.**

### `216` vs `208`
- `216` asks **should this rule exist or continue, and under what evidence and review conditions?**
- `208` asks **how does the approved change get deployed safely into live administrative and technical systems?**

### `215` / `317` / `320` / `316` / `319` / `318` / `216` / `208` vs `206`
- `215`, `317`, `320`, `316`, `319`, `318`, `216`, and `208` govern **ordinary lawmaking, statutory delegation, incorporation by reference, legal finalization, statute-book maintenance, quasi-law guidance, review, and implementation change discipline**.
- `206-constitutional-change-and-amendment-rails.md` remains the **foundational-constitutional change neighbor** when the threshold is not ordinary rule change but constitutional amendment or entrenchment.

### `25` / `39` / `118` / `215` / `317` / `320` / `316` / `319` / `318` / `216` / `208` vs `207`
- This family governs **rulemaking, lawmaking, statutory delegation, incorporation by reference, legal finalization, statute-book maintenance, quasi-law guidance, evaluation, and implementation change**.
- `207-sunset-review-and-rollback-rails.md` remains the **sunset / rollback / deprecation neighbor** when the central problem is retiring, withdrawing, or reversing an already-existing rule set.

---

## Retrieval guidance (what to cite when)

- Cite `25` for **findability of rules, legal legibility, enforceable guidance visibility, public summaries, and challengeability of the rule basis**.
- Cite `39` for **rule IDs, version histories, authority chains, “as-of” queries, PRR fields, and machine-readable rulebook interfaces**.
- Cite `118` for **change packets, approval gates, normal vs emergency lanes, rollback classes, release notes, and change-control discipline for rules**.
- Cite `215` for **bill packets, amendment receipts, anti-bundling, public-diff requirements, deliberation-response logs, and enactment release notes**.
- Cite `317` for **empowering clauses, delegated powers memoranda, draft instruments, Henry VIII powers, skeleton-bill diagnosis, scrutiny-procedure choice, and modification / exemption time limits**.
- Cite `320` for **incorporation by reference, external standards / codes / rates, static versus ambulatory references, accessibility guarantees, and incorporated-material snapshots**.
- Cite `316` for **enrolled text, assent / reconsideration rules, constitutional referral before promulgation, official publication, commencement maps, and visible rectification**.
- Cite `318` for **legal-effect legends, statutory guidance, codes of practice, directions, manuals, unpublished scripts, software-configured pseudo-rules, and shadow-law diagnosis**.
- Cite `216` for **impact assessments, alternatives analysis, distributional review, review commitments, ex post evaluation, and renew / modify / sunset decisions**.
- Cite `208` for **implementation plans, release engineering, operational readiness, monitoring, rollback, and post-implementation review after a rule is adopted**.

---

## Safe merge rule for this cluster

Do **not** flatten this family into one general memo on “better regulation”, “legislation”, or “policy change”.
The safer pattern is:
1. keep `25` as the legal-legibility front door,
2. keep `39` as the PRR / rulebook substrate,
3. keep `118` as the generic rule-change-control front door,
4. keep `215` as the legislative-process specialization,
5. keep `317` as the primary-to-secondary-legislation / parliamentary-scrutiny seam,
6. keep `320` as the incorporation-by-reference / external-material seam,
7. keep `316` as the lawmaking-finalization / promulgation / commencement seam,
8. keep `319` as the statute-book-maintenance / consolidation / repeal / revision seam,
9. keep `216` as the impact-assessment / ex-post-review specialization,
10. keep `318` as the quasi-law / guidance / shadow-law seam,
11. keep `208` as the implementation / release-engineering specialization,
12. keep `206` and `207` as named constitutional-change and rollback neighbors,
13. and use this memo as the bridge that names the roles.

That preserves distinct retrieval hooks while sharply reducing reader confusion.
