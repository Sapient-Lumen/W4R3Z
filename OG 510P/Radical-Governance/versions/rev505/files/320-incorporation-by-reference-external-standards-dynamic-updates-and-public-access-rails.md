# 320 — Incorporation by Reference, External Standards, Dynamic Updating, and Public-Access Rails

**Purpose:** let law use external material where it genuinely helps while preventing paywalled law, silent norm changes, and private rulemaking by reference.

**Why this memo exists:** the archive already covers standards as governance (`27`), public legal legibility and versioned rule inventories (`25` / `39`), generic rulemaking and change control (`118`), legislative drafting (`215`), delegated legislation (`317`), quasi-law and shadow-law risk (`318`), and statute-book maintenance (`319`). What it still lacked was one compact seam memo for the point where legislation or delegated legislation **imports an external document, code, standard, rate, framework, manual, or foreign/public text by reference instead of reproducing it on the face of the instrument**.

**Evidence anchors:** Canada’s current *Statutory Instruments Act* is a strong legal-design anchor because it expressly allows both date-pinned and ambulatory incorporation by reference, but limits the regulation-maker’s own documents to tightly bounded cases; it also requires incorporated material to be accessible and bars guilt or administrative sanction where the incorporated material was not accessible [BIB-CA-STATUTORY-INSTRUMENTS-IBR-2026]. New Zealand’s current *Legislation Act 2019* is a strong publication-and-fit anchor because section 64 limits incorporation by reference to cases where inclusion is impracticable or the material is too large for reasonable use, section 66 prevents later amendments from taking legal effect unless later legislation specifically incorporates them, and Schedule 2 requires public notice, opportunity to comment, clear identification, and public availability of the incorporated material [BIB-NZ-LEGISLATION-ACT-2019-2026] [BIB-NZ-LEGISLATION-ACT-SCHEDULE2-IBR-2026]. Australia’s current parliamentary scrutiny guidance is a strong scrutiny anchor because the Senate Scrutiny of Delegated Legislation Committee expects incorporated documents to be identified with specificity, their availability and access conditions explained, and the manner of incorporation stated; the Scrutiny of Bills Committee likewise expects explanatory materials to justify time-to-time incorporation and state whether the material will be freely available [BIB-AU-SDL-PRINCIPLE-F-2026] [BIB-AU-SB-PRINCIPLE-V-2026].

---

## Core claim

Incorporation by reference is legitimate when it keeps legislation usable **without outsourcing the real normative choices**.

It becomes constitutionally dangerous when it:
1. **moves the real rule into a paywalled or hard-to-find external document,**
2. **lets private or foreign bodies change applicable law without fresh scrutiny,**
3. **hides whether the reference is static or ambulatory,**
4. **uses the maker’s own manuals or technical tables as a side channel for changing law,**
5. **imports standards, rates, or codes without a stable version trail,**
6. **or leaves ordinary users unable to know what document actually governed them on the relevant date.**

The design target is simple:
- **keep the real policy, coverage, sanctions, and rights on the face of law,**
- **use incorporation only for bounded detail, large technical material, or externally maintained factual references,**
- **default to static / date-pinned references,**
- **treat ambulatory references as an exception that must be justified, legible, and monitorable,**
- **and never enforce incorporated material that people cannot reasonably find and use.**

---

## When to use this memo

Use `320` when the question is:
- when a law may incorporate external material by reference rather than reproducing it,
- when incorporation should be static versus time-to-time,
- how external standards, codes, indexes, rates, or foreign/public texts should be identified and versioned,
- when incorporated material must be freely accessible,
- how to prevent private standards or the maker’s own documents from quietly becoming law,
- how explanatory materials should justify incorporation by reference,
- or how the rule register should record incorporated material so “what text applied when” stays answerable.

This memo is the **incorporation-by-reference seam**. If the issue is standards governance in general, route to `27-standards-and-technical-governance.md`. If the issue is whether a norm belongs in primary law or delegated legislation at all, route to `317-delegated-legislation-empowering-provisions-henry-viii-powers-and-parliamentary-scrutiny-rails.md`. If the issue is the inventory, versioning, and point-in-time retrieval substrate for whatever was incorporated, route to `39-rulebook-and-instruments-registry.md`. If the issue is whether guidance, manuals, or codes are acting like law in practice, route to `318-statutory-guidance-codes-of-practice-directions-manuals-and-shadow-law-rails.md`. If the issue is person-facing discoverability of the governing rule, route to `25-legal-legibility-and-rule-inventory.md`.

---

## The smallest good architecture

### 1. Incorporation justification note (`IJN-*`)
For each incorporation by reference, publish one compact note stating:
- the parent Act / regulation and clause,
- the material incorporated,
- why incorporation is preferable to putting the material on the face of the instrument,
- whether the reference is static or ambulatory,
- who controls future changes to the incorporated material,
- and why the chosen scrutiny path is appropriate.

### 2. Reference mode declaration (`RMD-*`)
Every incorporated reference should be typed as one of:
- **Static / date-pinned** — the incorporated text is fixed as at a stated date or edition.
- **Ambulatory / time-to-time** — later changes automatically flow through.
- **Indexed / variable factual input** — an index, rate, number, or similar externally updated factual input.
- **Public-law cross-reference** — a reference to another public legislative text.

The instrument should say which mode applies on the face of the text or in an inseparable explanatory note.

### 3. Incorporated-material access record (`IAR-*`)
Maintain one public record for each incorporated item stating:
- exact title,
- edition / version / date,
- author or originating body,
- how it can be obtained,
- whether it is free to access and reuse,
- and what the fallback access path is if copyright prevents free publication.

### 4. Incorporated-change alert ledger (`ICAL-*`)
For ambulatory references or indexed / variable inputs, maintain an alertable ledger showing:
- each external change event,
- when it occurred,
- whether it changed obligations in practice,
- whether a parliamentary / ministerial / public notice step followed,
- and what transition or grace period applied.

### 5. Incorporated-material snapshot archive (`IMS-*`)
Keep a citable snapshot of the exact incorporated text or value set that applied during each effective window, so reviewers can reconstruct the governing rule environment as of a given date.

### 6. External-rule risk classification (`ERR-*`)
Classify incorporated material by source risk:
- **public legislation / official public rules**,
- **public technical standards body material**,
- **private standards body material**,
- **foreign or intergovernmental material**,
- **maker’s own documents**,
- **indexes / rates / numbers**.

Higher-risk classes require stronger justification, tighter access guarantees, and a stronger bias toward static incorporation.

---

## Design rules

### A. Keep the real normative choices in law
Do **not** use incorporation by reference to hide:
- who is covered,
- what conduct is prohibited or required,
- what sanctions apply,
- what exemptions exist,
- what review standard governs,
- or what major rights-affecting policy choice has actually been made.

External material may carry detail, methods, test protocols, or changing technical content. It should not carry the constitutional heart of the rule.

### B. Static reference is the default; ambulatory reference is an exception
The archive prefers **date-pinned incorporation** unless there is a specific reason why automatic updating is genuinely superior.

Ambulatory incorporation needs a stronger case because it can change the law without a fresh legislative act. Use it mainly for:
- rates, numbers, and indexes that are expected to vary,
- tightly bounded technical standards where frequent update is necessary,
- or public-law cross-references where the legal system openly accepts dynamic updating and supplies adequate notice / scrutiny.

Where ambulatory reference is used, the explanatory materials should say why static incorporation is not enough.

### C. Treat the maker’s own documents as especially suspect
The archive rejects self-incorporation as a hidden lawmaking lane.

If the regulation-maker or administering authority created the referenced document, the default assumption should be that the content belongs:
- on the face of the regulation,
- in another openly binding legislative instrument,
- or in a guidance instrument typed and handled under `318`.

Maker-authored material may sometimes be incorporated for incidental detail or faithful reproduction, but not as a convenience shortcut for changing law later without scrutiny.

### D. No paywalled law
A person must be able to find and use the incorporated material with reasonable ease.

If copyright or licensing blocks free republication, the system still owes a real access solution:
- public online access where lawful,
- clear public notice of where and how it may be inspected,
- stable links or physical access points,
- and a plain-language compliance summary explaining what the incorporated material does.

If the state cannot provide usable access, it should not enforce the incorporated material as if access were obvious.

### E. Enforceability depends on accessibility and identification
The instrument should clearly identify the incorporated material by:
- title,
- version / edition / date where relevant,
- source body,
- and incorporation mode.

Ambiguity about “which standard” or “which version” is a rule-of-law defect, not a drafting nicety.

### F. External changes need visible change discipline
Where law incorporates external material dynamically, later changes should not arrive as silent legal drift.

At minimum, the polity should publish:
- the change event,
- the date it took practical effect,
- any grace period,
- and whether the change created a material new burden.

For higher-stakes ambulatory references, prefer a confirmatory parliamentary or ministerial notice step rather than pure silent flow-through.

### G. Imported private standards need a stronger public-interest test
Private or semi-private standards can be valuable, but they are not automatically fit to become law.

Before incorporation, the public authority should ask:
- is the standard genuinely better maintained externally,
- is the process sufficiently open and balanced,
- is the text accessible,
- does the standard affect rights or market access,
- and does the incorporation create vendor, professional, or incumbent gatekeeping power?

Where the answer is poor, rewrite the operative public-law requirements instead of importing the standard wholesale.

### H. The rule register must carry the incorporation trail
The PRR should not merely say “see external standard”.

It should record:
- the parent `RULE` ID,
- the incorporated material,
- the incorporation mode,
- the exact version or snapshot,
- the access path,
- and the dates during which that incorporated material had legal effect.

Without this, “what law applied when” becomes guesswork.

### I. Guidance cannot backdoor-amend incorporated law
Once a law incorporates external material, do **not** let agencies use FAQs, manuals, circulars, or software-configured rules to reinterpret or update that incorporated material in practice without a lawful change path.

If operational interpretation becomes necessary, it should be typed and published under `318`, not smuggled in as tacit override.

---

## Anti-patterns to reject

Reject designs where:
- a statute says “the relevant standard, as amended from time to time” with no explanation,
- incorporated material is identified only by a vague label or website,
- the incorporated text is paywalled and the public gets no workable access path,
- the regulation-maker’s own unpublished manual is incorporated by reference,
- dynamic external changes alter burdens with no public alert or transition period,
- the PRR cannot tell which edition applied on a specific date,
- or private standards bodies quietly become unreviewable lawmakers.

---

## Minimal archive joins

- `27-standards-and-technical-governance.md` for the wider governance question of how technical standards bodies, implementability, and anti-capture design should work.
- `25-legal-legibility-and-rule-inventory.md` for the person-facing rule-of-law baseline: people must be able to find the rules that govern them.
- `39-rulebook-and-instruments-registry.md` for the versioned substrate that should record incorporated materials, access paths, and point-in-time snapshots.
- `317-delegated-legislation-empowering-provisions-henry-viii-powers-and-parliamentary-scrutiny-rails.md` for the upstream question whether a bill or regulation should be using delegated legislation or incorporation by reference in the first place.
- `318-statutory-guidance-codes-of-practice-directions-manuals-and-shadow-law-rails.md` for the downstream risk that guidance, manuals, or pseudo-rules start changing the effect of incorporated material in practice.
- `319-statute-book-maintenance-consolidation-codification-repeal-and-revision-bill-rails.md` for the later maintenance question of how official current texts and provenance should remain usable after years of change.

---

## One-line design test

**If people cannot tell which outside document governed them on the relevant date, incorporation by reference has already failed the rule-of-law test.**
