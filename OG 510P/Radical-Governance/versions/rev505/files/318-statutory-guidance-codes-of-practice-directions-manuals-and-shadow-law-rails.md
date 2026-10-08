# 318 — Statutory Guidance, Codes of Practice, Directions, Manuals, and Shadow-Law Rails

**Purpose:** make the quasi-law layer explicit and bounded so guidance can help people comply with the law without quietly becoming the law.

**Why this memo exists:** the archive already covers legal legibility and hidden rule surfaces (`25` / `39`), generic rulemaking and change control (`118`), legislative drafting (`215`), delegated legislation (`317`), lawmaking finalization (`316`), and operational release (`208`). What it still lacked was one compact seam memo for the instruments that often sit **between enacted law and frontline administration**: **statutory guidance, codes of practice, directions, notices, manuals, circulars, FAQs, scripts, and software-configured pseudo-rules that can shape real-world obligations without always being treated as law**.

**Evidence anchors:** the UK Cabinet Office’s current *Guide to Making Legislation* is a strong drafting-side anchor because it says powers to issue directions or codes of practice may themselves be delegated legislative powers, and because it warns that codes are not to be used to define specific legal obligations [BIB-UK-GUIDE-MAKING-LEGISLATION-2025]. The House of Lords Delegated Powers and Regulatory Reform Committee’s current guidance is a strong constitutional boundary because it treats “must have regard to” guidance, directions, and codes of practice as disguised legislative instruments, says their use must be clearly justified, and states that mandatory guidance cannot be justified [BIB-UK-DPRRC-GUIDANCE-2024]. The Constitution Committee’s 2025 legislative-standards synthesis usefully names the problem directly: guidance and codes can be legislative in effect without adequate parliamentary oversight [BIB-UK-CONST-LEG-STANDARDS-2025]. The UK Government’s 2026 response on the rule of law is also useful because it restates, in current official terms, that guidance should not be used to circumvent the proper way of regulating a matter [BIB-UK-RULE-OF-LAW-2026]. New Zealand’s Legislation Act remains a useful publication-side anchor because it explicitly treats legislation-made instruments as typed legal objects with publication obligations, and because it joins secondary legislation with “other instruments” made under Acts instead of pretending the seam does not exist [BIB-NZ-LEGISLATION-ACT-2019-2026]. The Venice Commission’s updated Rule of Law Checklist remains the compact general baseline because legal certainty requires publication, accessibility, intelligibility, and foreseeability for laws and regulation in general [BIB-VENICE-ROL-2025].

---

## Core claim

Guidance is legitimate when it **explains**, **organizes discretion**, **offers examples**, or **helps implementation**.

It becomes constitutionally dangerous when it:
1. **creates obligations that are not actually in law,**
2. **makes departure practically impossible without saying so,**
3. **changes rights or burdens through “guidance updates” instead of lawful amendment,**
4. **stays unpublished while frontline staff or software use it against people,**
5. **or hides binding policy inside manuals, scripts, configuration tables, or “must have regard to” documents.**

The design target is simple:
- **name the legal effect,**
- **keep real duties in law,**
- **publish anything that affects people in practice,**
- **version and archive guidance like any other rule artifact,**
- **and escalate anything substantively legislative into a properly authorized and reviewable instrument.**

---

## When to use this memo

Use `318` when the question is:
- whether statutory guidance, codes of practice, directions, notices, circulars, or manuals are actually binding,
- what legal effect a code or guidance document should have,
- when guidance has become disguised legislation or shadow law,
- when frontline manuals or software-configured rules must be public,
- how “must have regard to” or “take into account” guidance should be bounded,
- how guidance, directions, and operational scripts should be versioned, published, and challengeable,
- or how to stop soft-law artifacts from becoming a hidden second legislature.

This memo is the **law-to-operations / quasi-law seam**. If the issue is the general public discoverability of rules or hidden rule surfaces, route to `25-legal-legibility-and-rule-inventory.md` or `39-rulebook-and-instruments-registry.md`. If the issue is how any rule change is governed as a change event, route to `118-rulemaking-and-change-control.md`. If the issue is what belongs in primary legislation versus delegated legislation, route to `317-delegated-legislation-empowering-provisions-henry-viii-powers-and-parliamentary-scrutiny-rails.md`. If the issue is the narrower seam where law imports an outside document, standard, rate, or code by reference and must decide whether later external changes flow through, route to `320-incorporation-by-reference-external-standards-dynamic-updates-and-public-access-rails.md`. If the issue is how a bill becomes law after passage, route to `316-bill-finalization-assent-promulgation-publication-commencement-and-constitutional-referral-rails.md`. If the issue is the safe operational deployment of already-authorized changes, route to `208-change-management-and-release-engineering-for-government.md`.

---

## The smallest good architecture

### 1. Guidance instrument classification note (`GIC-*`)
For every guidance-like instrument, publish one compact note stating:
- the maker,
- the legal basis,
- the intended audience,
- whether it is advisory, “must consider”, evidentiary, safe-harbor, approval-gating, or binding,
- whether a person may depart from it and on what standard,
- and what review / challenge lane exists.

### 2. Guidance publication and version ledger (`GPV-*`)
Maintain one public ledger linking:
- the parent Act / regulation / policy authority,
- the in-force guidance version,
- prior versions,
- issue date,
- in-force date,
- review date,
- and any superseding or withdrawn documents.

### 3. Legal-effect legend (`LEL-*`)
Every guidance document should carry, on page one, a plain-language legend stating one of the following:
- **Advisory only** — helps understanding but creates no independent legal duty.
- **Must consider** — decision-makers must consider it, but may depart with stated reasons.
- **Evidentiary / code effect** — may be used as evidence of good practice or compliance, but the legal duty still comes from law.
- **Safe harbor** — compliance with the guidance is deemed or presumed to satisfy a stated legal standard.
- **Binding direction / standard / notice** — the document has direct legal effect and must be treated as such.

### 4. Departure and reliance note (`DRL-*`)
Where officials or regulators may depart from guidance, require a short public note or decision-receipt field stating:
- whether departure occurred,
- why,
- whether the person affected was told,
- and whether the departure changes the remedy lane or review standard.

### 5. Shadow-law audit packet (`SLA-*`)
Periodically review:
- unpublished or poorly versioned manuals,
- internal scripts or configuration tables,
- FAQ or template language used repeatedly as if it were law,
- and enforcement / eligibility practices that depend on documents the public cannot easily find.

Any artifact that is legislative in effect should either be:
- moved into proper legislation or secondary legislation,
- reissued with a clear legal-effect legend and publication path,
- or withdrawn.

---

## Design rules

### A. Every guidance-like artifact must declare its legal effect explicitly
The archive disfavors vague middle categories.

A person reading a guidance document should be able to tell immediately whether it:
- merely advises,
- structures discretion,
- supplies evidence of good practice,
- creates a safe harbor,
- or binds directly.

If the state cannot describe the legal effect clearly, the instrument is too ambiguous to be safe.

### B. Do not put real duties in guidance
The default boundary is simple: **law creates obligations; guidance helps people understand or apply them**.

Do **not** use guidance, manuals, or FAQs to create:
- new eligibility conditions,
- new prohibitions,
- new sanctions,
- new reporting burdens,
- or new substantive compliance tests
unless the legal system openly treats the instrument as legislation or delegated legislation and gives it the corresponding publication and review treatment.

### C. “Must have regard to” is not a free pass
Where the law says decision-makers must have regard to guidance, the system should still specify:
- what can justify departure,
- whether reasons must be given,
- whether affected persons can challenge a failure to follow or consider the guidance,
- and whether the guidance is public and versioned.

A “must have regard to” formula that behaves like a binding rule should be treated as a warning sign that the real norm belongs in law.

### D. Mandatory guidance is bad design
If a document is mandatory in practice, the archive prefers that the legal system admit this openly.

Calling something “guidance” while treating departure as impossible:
- confuses the public,
- weakens parliamentary or democratic scrutiny,
- and makes judicial or administrative review harder.

If compliance is mandatory, redesign the instrument as law, secondary legislation, or another openly binding instrument.

### E. Person-affecting internal manuals and software-configured rules must not stay secret
The archive rejects dark administration.

If internal manuals, scripts, templates, queue logic, scoring rules, model prompts, or configuration tables materially shape:
- eligibility,
- enforcement,
- sanctions,
- inspection intensity,
- or remedy access,
then the public needs at least:
- the governing rule statement,
- the operative criteria,
- the current version,
- and a way to challenge the rule basis.

Internality is not a valid reason to hide outcome-determinative norms.

### F. Guidance should be easier to update than law, but never easier to hide
Fast-update guidance can be useful where:
- operational detail changes often,
- examples need refreshing,
- or frontline interpretation needs clarification.

But the price of faster updating is stronger publication discipline:
- visible version numbers,
- issue and in-force dates,
- archived superseded versions,
- change summaries,
- and one stable public URL or rulebook identifier.

### G. Courts, tribunals, reviewers, and ombuds institutions should know how to treat the document
A good system states whether a guidance or code:
- is relevant evidence,
- is something a decision-maker must consider,
- creates a rebuttable presumption,
- or is itself the binding instrument.

Without that clarity, review bodies waste time arguing about the status of the document instead of the merits of the dispute.

### H. Repeated guidance should trigger law-repair, not endless workaround layering
If the same subject attracts:
- many guidance revisions,
- chronic reliance on unpublished scripts,
- or repeated disputes about what the guidance really means,
then the archive prefers promoting the stable core into clearer law or properly typed delegated legislation.

Good guidance should reduce confusion; if it generates recurring confusion, the underlying legal design is probably under-specified.

### I. Guidance that affects the public should come with a plain-language summary
The public should not have to infer real-world effect from a dense technical document.

For every person-affecting guidance instrument, publish:
- what it is,
- who it applies to,
- whether it is binding,
- what changed,
- and how to challenge misuse of it.

---

## Anti-patterns to reject

Reject designs where:
- a ministry says a document is “only guidance” but frontline staff treat it as compulsory,
- penalties or refusals turn on criteria found only in a code, manual, FAQ, or template letter,
- a regulator updates substantive expectations through web guidance while avoiding the legal route for changing the rule,
- internal scoring or triage logic shapes outcomes but is omitted from the public rule inventory,
- old guidance remains online with no clear supersession path,
- or different agencies use competing unpublished manuals under the same law.

---

## Minimal archive joins

- `25-legal-legibility-and-rule-inventory.md` for public findability of real governing rules and challengeable rule bases.
- `39-rulebook-and-instruments-registry.md` for the versioned substrate and `GLAW` treatment of guidance that functions like law.
- `118-rulemaking-and-change-control.md` for rule-change receipts, review gates, and rollback discipline.
- `317-delegated-legislation-empowering-provisions-henry-viii-powers-and-parliamentary-scrutiny-rails.md` for the upstream question of what should be delegated at all.
- `316-bill-finalization-assent-promulgation-publication-commencement-and-constitutional-referral-rails.md` for the path by which a bill or instrument becomes legally live.
- `208-change-management-and-release-engineering-for-government.md` for deployment into live administrative and technical systems once the normative artifact is lawfully typed and published.

---

## One-line design test

**If a person can be denied, fined, inspected, downgraded, or excluded because of a rule in “guidance”, that rule probably needs stronger legal status, stronger visibility, or both.**
