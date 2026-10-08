# 317 — Delegated Legislation, Empowering Provisions, Henry VIII Powers, and Parliamentary-Scrutiny Rails

**Purpose:** make the primary-to-secondary legislation seam explicit and bounded so statutes do not become blank cheques for executive lawmaking.

**Why this memo exists:** the archive already covers generic rulemaking and change control (`118`), legislative drafting and amendment traceability (`215`), bill finalization / promulgation / commencement (`316`), impact assessment (`216`), and implementation / release engineering (`208`). What it still lacked was one compact seam memo for the stage where a statute **delegates lawmaking power onward**: **what must stay on the face of the Act, how empowering provisions should specify scope, which scrutiny procedure fits which power, when draft instruments should be published, when Henry VIII powers are ever tolerable, and how delegated legislation remains reviewable instead of becoming a shadow legislature**.

**Evidence anchors:** Germany’s Basic Law remains one of the clearest constitutional baselines because Article 80 requires the **content, purpose, and scope** of delegated authority to be specified in the law itself and requires each statutory instrument to state its legal basis [BIB-GERMANY-BASIC-LAW-2026]. The UK’s 2025 *Guide to Making Legislation* remains a strong operating anchor because it requires departments to justify delegated powers, choose and justify the parliamentary procedure, and prepare a delegated powers memorandum for bills containing such powers [BIB-UK-GUIDE-MAKING-LEGISLATION-2025]. The House of Lords Delegated Powers and Regulatory Reform Committee’s current guidance remains a sharp constitutional design anchor because it says the principal aspects of policy should be on the face of a bill, not left to delegated legislation, and treats skeleton legislation and Henry VIII powers as exceptional and justification-heavy [BIB-UK-DPRRC-GUIDANCE-2024]. The Constitution Committee’s 2025 legislative-standards synthesis reinforces the same point: broad or vague delegated powers, skeleton bills, creating public bodies by delegated powers, and significant criminal-offence design by delegation are constitutionally suspect, while draft instruments materially improve scrutiny [BIB-UK-CONST-LEG-STANDARDS-2025]. Australia’s Senate Scrutiny of Delegated Legislation guidance is useful because it turns these concerns into a publishable scrutiny checklist: significant elements of major schemes, serious penalties, taxes, and modifications of primary legislation should ordinarily stay in primary law or be tightly justified and time-limited if delegated [BIB-AU-SDL-GUIDELINES-2024] [BIB-AU-SDL-PRINCIPLE-J-2024] [BIB-AU-SDL-PRINCIPLE-L-2024]. New Zealand’s Legislation Act remains a useful publication-side anchor because it makes publication, presentation, and disallowance legible at the level of particular empowering provisions rather than treating secondary legislation as a hidden side channel [BIB-NZ-LEGISLATION-ACT-2019-2026].

---

## Core claim

A bill is not democratically complete just because it passes.

If it delegates future lawmaking, the polity still has to answer five questions clearly:
1. **Threshold:** what must stay in primary law, and what may be delegated?
2. **Empowerment:** who may make the secondary law, about what, and within what scope?
3. **Scrutiny:** what parliamentary procedure, consultation, publication, and explanation are required?
4. **Constraint:** may the instrument amend primary legislation, exempt people from it, or defer core policy choices?
5. **Lifecycle:** how is the instrument published, reviewed, sunsetted, corrected, and linked back to the parent Act?

Where those questions are left vague, framework statutes become **permission slips for executive legislation**.

The archive’s preference is straightforward:
- **principal policy in the Act,**
- **detailed implementation only by delegation,**
- **typed empowering clauses,**
- **procedure matched to risk,**
- **draft instruments for broad powers,**
- **and visible review / sunset rules for instruments that modify primary law or do unusually heavy policy work.**

---

## When to use this memo

Use `317` when the question is:
- what belongs in primary legislation versus delegated legislation,
- how empowering provisions should specify the maker, scope, purpose, and legal basis,
- what scrutiny procedure should apply to regulations, rules, orders, codes, or statutory instruments,
- when draft regulations should be published during bill scrutiny,
- when Henry VIII powers are ever acceptable,
- how to stop framework or skeleton bills from shifting core policy to ministers,
- how modification / exemption powers in delegated legislation should be bounded,
- or how delegated legislation should be published, presented, disallowed, reviewed, and sunsetted.

This memo is the **primary-to-secondary legislation seam**. If the issue is the generic governance of any rule change, route to `118-rulemaking-and-change-control.md`. If the issue is how a bill is drafted, amended, and made vote-ready, route to `215-legislative-process-and-drafting-rails.md`. If the issue is how a passed bill becomes binding law through assent, promulgation, publication, and commencement, route to `316-bill-finalization-assent-promulgation-publication-commencement-and-constitutional-referral-rails.md`. If the issue is impact assessment or ex post review of a rule, route to `216-regulatory-impact-assessment-and-ex-post-review-rails.md`. If the issue is operational deployment of an adopted rule, route to `208-change-management-and-release-engineering-for-government.md`.

---

## The smallest good architecture

### 1. Delegation map note (`DGN-*`)
For each bill that delegates legislative power, publish one compact map stating:
- each delegated power in the bill,
- the intended maker,
- the subject matter,
- whether it is ordinary, Henry VIII, commencement-only, emergency, or consequential,
- whether subdelegation is allowed,
- the parliamentary scrutiny procedure,
- the consultation requirement,
- and the publication / laying / disallowance / review path.

### 2. Delegated powers memorandum (`DPM-*`)
Publish one bill-level memorandum stating for each power:
- why delegation is necessary,
- why the chosen procedure is appropriate,
- what stays on the face of the bill,
- what draft instrument text exists already,
- and what safeguards limit discretion.

### 3. Draft instrument packet (`DIP-*`)
For any power that is broad, constitutionally sensitive, or central to how the Act will work, publish:
- draft regulations or a close illustrative draft,
- the policy choices that will still remain open,
- the expected timeline for making the instrument,
- and the effect on rights, burdens, costs, and remedies.

### 4. Instrument explanatory note (`IEN-*`)
Every delegated legislative instrument should carry one public note stating:
- the enabling section,
- the precise legal effect,
- the parliamentary procedure used,
- consultation undertaken or omitted,
- commencement and expiry rules,
- review trigger or sunset,
- and any interaction with primary legislation.

### 5. Delegated legislation tracker (`DLT-*`)
Maintain a public tracker linking:
- the parent Act,
- each delegated power,
- each instrument made under it,
- the laying / presentation / disallowance clock,
- current status (draft / made / in force / revoked / sunsetted),
- and any review or replacement work.

---

## Design rules

### A. Put principal policy on the face of the Act
The default boundary is simple: **acts decide the main policy; instruments fill in detail**.

Do **not** use delegated legislation to postpone choices that parliament should actually debate, such as:
- the basic shape of a major regulatory scheme,
- the central definitions that determine who is covered,
- major coercive powers,
- the creation of important public bodies,
- serious offences or penalties,
- or tax and levy architecture.

Delegation is justified by technicality, operational detail, update frequency, or bounded flexibility — not by legislative convenience or policy indecision.

### B. Every empowering clause should specify the content, purpose, and scope of the power
A valid delegation should answer, in the Act itself:
- **who** may make the instrument,
- **about what**,
- **for what statutory purpose**,
- **within what limits**,
- and **whether further subdelegation is allowed**.

Bad empowering clauses rely on words like “appropriate”, “expedient”, or “as the Minister considers necessary” without meaningful constraint.

### C. Each instrument must visibly carry its legal basis
No delegated legislation should float free of its parent authority.

The public should be able to tell, from the face of the instrument and its explanatory note:
- which section authorized it,
- whether the power amends primary law,
- whether parliament may disallow it,
- and whether it is time-limited.

### D. Choose the scrutiny procedure by risk, not by habit
Negative, affirmative, superaffirmative, confirmatory, or disallowance-based procedures should track the legal effect of the instrument.

The archive’s rough preference ladder is:
- **ordinary technical updates** → lighter procedure may suffice,
- **rights, burdens, eligibility, market structure, or institutional design** → stronger procedure,
- **Henry VIII or primary-law modification powers** → strong procedure plus explicit justification,
- **emergency instruments** → temporary exceptional lane, then normal scrutiny or lapse.

Procedure selection should be explained power by power, not hidden inside boilerplate.

### E. Henry VIII powers should be narrow, exceptional, and presumed to need stronger scrutiny
Powers that let ministers amend, repeal, suspend, or otherwise alter primary legislation are a constitutional exception, not a convenience device.

Where such a power exists, the archive prefers:
- express identification in the bill and memorandum,
- a narrow subject matter,
- a clear statutory purpose,
- a stronger scrutiny track,
- time limits where practicable,
- and a review / replacement expectation if the power is used repeatedly.

### F. Skeleton bills are presumptively bad design
A framework or skeleton bill is a warning sign that the legislature is being asked to approve a legal shell and let ministers write the real scheme later.

If a bill is so insubstantial that its real operation depends in large part on later regulations, treat that as a constitutional problem, not as clever flexibility. Exceptional use requires a direct public declaration, a justification for why no better route was possible, and unusually strong scrutiny support.

### G. Publish draft instruments when broad powers are requested
Where an Act’s real operation depends heavily on future regulations, parliament should see draft instruments or close exemplars during primary-legislation scrutiny.

This is especially important when the power will determine:
- who is eligible or excluded,
- what compliance duties exist,
- how penalties or liabilities work,
- how an agency or board will actually operate,
- or how intergovernmental or private actors will be bound.

### H. Do not hide law in mandatory guidance, codes, or disguised legislative instruments
If guidance, codes, or directions are practically binding, they should be treated as delegated lawmaking devices, not as soft non-law.

The archive disfavors “must have regard to” or quasi-binding guidance used to smuggle in substantive norms without clear procedure, publication, or scrutiny.

### I. Modification or exemption instruments should be time-limited and reviewable
If delegated legislation modifies the operation of primary law or exempts persons or classes from it, the default should be:
- explicit authority,
- narrow scope,
- visible duration,
- review before renewal,
- and a presumption against indefinite operation.

A delegated exemption that becomes permanent should usually migrate back into primary legislation.

### J. Commencement and consequential powers must not become a shadow legislature
Commencement orders and consequential-amendment powers are sometimes necessary, but they should not be used to rewrite settled policy, indefinitely suppress enacted provisions, or backdoor controversial legal changes that parliament never really examined.

The safe default is:
- commencement only for sequencing,
- consequential powers limited to true consequences,
- no major policy content inside commencement instruments,
- and no indefinite non-use of enacted provisions without a visible parliamentary path.

---

## Anti-patterns to reject

Reject designs where:
- the bill resolves little and delegates almost everything later,
- a minister can define the core beneficiaries, duties, or sanctions of a scheme with almost no statutory constraint,
- the scrutiny procedure is chosen for speed rather than democratic fit,
- a Henry VIII power is broad, indefinite, and paired with weak procedure,
- draft instruments are withheld even though parliament cannot realistically understand the bill without them,
- guidance is used as covert law,
- or instrument publication, laying, and review clocks are too obscure for ordinary people to follow.

---

## Minimal archive joins

- `118-rulemaking-and-change-control.md` for the generic governance of rule changes across instruments.
- `215-legislative-process-and-drafting-rails.md` for bill packets, amendment receipts, and drafting discipline before the delegation boundary.
- `316-bill-finalization-assent-promulgation-publication-commencement-and-constitutional-referral-rails.md` for the post-passage path to legal force.
- `216-regulatory-impact-assessment-and-ex-post-review-rails.md` for alternatives analysis, ex post review, and renewal / sunset decisions.
- `208-change-management-and-release-engineering-for-government.md` for deployment into live operational systems after legal authority exists.
- `25-legal-legibility-and-rule-inventory.md` and `39-rulebook-and-instruments-registry.md` for publication, authoritative versions, and "what rule was in force when" infrastructure.
- `320-incorporation-by-reference-external-standards-dynamic-updates-and-public-access-rails.md` for the narrower seam where law imports outside documents, standards, or rates by reference rather than reproducing them in the instrument.
- `318-statutory-guidance-codes-of-practice-directions-manuals-and-shadow-law-rails.md` for the downstream boundary where guidance, codes, directions, manuals, or software-configured pseudo-rules start doing the work of law in practice.

---

## One-line design test

**If parliament cannot tell what core policy it is approving without later regulations, the bill is probably delegating too much.**
