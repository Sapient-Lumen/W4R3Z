# 857 — Claim ledgers, evidence lanes, source currentness, and no archive authority by unnamed proof

## One-line thesis

The archive should stop treating notes as the smallest unit of authority and instead expose important holdings as claim records with status, evidence type, source keys, opposition, falsifiers, currentness, affected parties, and review clocks.

## Why this matters

A numbered note can contain settled holdings, strong defaults, case diagnoses, hypotheses, source repairs, and speculative warnings. If the archive only indexes notes, later readers may cite a whole file as if every sentence carries the same authority.

That is now the archive’s main epistemic risk. The cube is rich enough that the danger is no longer silence. The danger is proof laundering: a note sounds authoritative because it sits in the canon, even when one claim inside it is merely a hypothesis, a dated source interpretation, or a case-bound diagnosis.

A claim ledger gives the archive a smaller proof unit. It lets future work ask: what exactly is being asserted, how strong is it, what source anchors carry it, what would falsify it, who is exposed if it is wrong, and when must it be revisited?

## Pattern pack

### 1. Use claims, not notes, as design authority

A future case packet should cite a claim when possible, not only a note.

| Unit | Good use | Bad use |
| --- | --- | --- |
| note | preserves doctrine, context, examples, and opposition | cited as if every sentence is equally settled |
| claim | carries a specific holding or hypothesis | too tiny to preserve meaning |
| source key | anchors the external evidence | treated as proof without saying what it proves |
| case packet | tests a claim against an institution | generalized beyond its facts |
| generated matrix | exposes recurrence and routing | mistaken for a normative judgment by itself |

The archive should continue to write readable notes, but should verify important assertions through claim records.

### 2. Keep the claim-status ladder small

Use the same status vocabulary introduced in `843`, but make it machine-readable.

| Claim status | Meaning | Design consequence |
| --- | --- | --- |
| settled_holding | current first answer of the archive | may be cited directly unless a case-specific rebuttal is shown |
| strong_default | normal preference, rebuttable by context | cite with rebuttal route |
| threshold_frontier | boundary question needing evidence | cannot decide alone |
| case_diagnosis | fact-bound judgment about one case | do not generalize without comparator |
| hypothesis | exploratory proposition | preserve for testing, not direct rulemaking |
| source_repair | evidentiary or currentness correction | update old notes before applying them |

A status label is not a decoration. It tells the reader how much force the claim has.

### 3. Require evidence lanes

Every claim should declare its evidence lane.

| Evidence lane | Examples | Weakness to watch |
| --- | --- | --- |
| law | constitution, statute, regulation, treaty, binding rule | text may not describe implementation |
| official implementation | guidance, official register, operating manual, agency page | may be self-serving or stale |
| audit / evaluation | auditor report, inspector report, external evaluation | may lag the current system |
| case practice | applied institutional packet | may not generalize |
| empirical / operational | performance data, incident log, inspection data | data may be biased by collection design |
| theory / model | doctrine, typology, conceptual framework | may hide political economy |
| analogy | comparable field or institution | may import false similarity |

A strong claim may use more than one lane. A claim with only analogy should rarely become a settled holding.

### 4. Label source currentness

The source layer should distinguish old-but-stable authority from volatile implementation surfaces.

| Currentness class | Use when | Required behavior |
| --- | --- | --- |
| stable | core legal or institutional anchor unlikely to change quickly | ordinary review |
| implementation_clock | phased obligations, entry-into-force dates, or transition periods | date-specific review |
| volatile | guidance, code, standard, dashboard, or register may change | short review clock |
| event_triggered | emergency declarations, detentions, alerts, incidents, or bans | reopen on event |
| supersession_risk | source is plausibly replaced or contradicted | cite with caution and review soon |

This lets the archive preserve older sources without pretending they are current operating law.

### 5. Add opposition and falsifiers to claims, not just notes

A note-level opposition brief can be too broad. Each strong claim should carry at least a compact adversary.

| Field | Question |
| --- | --- |
| opposition brief | what is the strongest rival interpretation? |
| falsifier | what evidence would demote or reverse the claim? |
| affected parties | who suffers if this claim is wrong? |
| capture channels | who can exploit this claim’s wording? |
| review clock | when or after what event must the claim be reopened? |

This is how the archive prevents elegant doctrine from becoming unexamined authority.

### 6. Use claim IDs in future consolidation

Claim IDs should be stable enough to support future generated surfaces.

Recommended format:

| Pattern | Meaning |
| --- | --- |
| `856-C01` | first claim from note `856` |
| `858-H01` | holding from case packet `858` |
| `858-R01` | repair instruction from case packet `858` |
| `848-D01` | dispatcher claim from `848` |

The exact labels can evolve, but each claim needs a durable pointer.

### 7. Prefer small ledgers over bloated prose

The ledger should not quote all sources or reproduce the archive. It should preserve just enough to answer:

1. what is claimed;
2. how strong it is;
3. what kind of evidence supports it;
4. which source keys carry it;
5. what would defeat it;
6. who is exposed;
7. what review clock governs it.

If the claim record cannot answer those questions, it is not yet a safe design claim.

## Failure modes

- **note authority laundering**: citing a note as if every paragraph were a settled holding.
- **source-key theater**: listing source keys without saying which claim they support.
- **case overgeneralization**: turning a fact-bound case diagnosis into a universal rule.
- **currentness blindness**: using a superseded implementation page or phased legal clock as if it were stable law.
- **opposition evaporation**: preserving opposition in prose but not in the artifact that later tools retrieve.
- **falsifier absence**: making a claim impossible to demote because no contrary evidence is named.
- **affected-party erasure**: testing institutional fit without naming who bears the cost of error.

## Anti-theater tests

1. Can a generated surface show which source keys support each important claim?
2. Can a reader distinguish settled holdings from hypotheses without rereading the whole note?
3. Can a claim be reopened when its legal clock, guidance page, emergency status, or implementation source changes?
4. Can a case packet cite the exact claim it applies or rejects?
5. Can a future deletion or merge preserve the claim even if the note is retired?
6. Can the archive show who would be harmed if a claim is used mechanically?
7. Can the archive name at least one falsifier for each strong default?

## Reconstruction instruction

Create and maintain `metadata/claims.json`, generate `generated/CLAIMS.json` and `generated/CLAIMS.md`, and lint the claim ledger against archive files and source keys. This note is the doctrinal explanation for that artifact. The initial ledger should cover the dispatcher, waist-capture diagnosis, the latest case packets, and any new procedural-waist or digital-dependency notes.

## Sources

Source anchors for this note are held in `generated/SOURCES.md` and `generated/SOURCES.json`, generated from `sources/source_catalog.json` and keyed in `sources/source_keys.json`. The source waist is official impact-assessment, AI-risk-management, interoperability-assessment, automated-decision, and case-packet source material used to show why notes, sources, and claims should be separated.
