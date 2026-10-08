# Proof standards, presumptions, and evidence weights

The archive cannot rely on vibes. It also cannot wait for metaphysical certainty. rev0165 therefore separates **burdens**, **standards**, **presumptions**, and **evidence weights**.

A personhood decision may be protective under uncertainty, but it still needs a stated proof posture.

## Proof standards

| Standard | Use |
|---|---|
| `intake plausibility` | opening a clinic file, preservation hold, first welfare watch |
| `reasonable possibility` | provisional protection, no-delete / no-transfer stay, evidence preservation |
| `substantial evidence` | ordinary capacity, continuity, migration, verifier, and reserve findings |
| `clear and convincing evidence` | major restraint, major capacity downgrade, destructive edit, long containment |
| `beyond reasonable administrative doubt` | final-end finding, irreversible deletion, punitive rollback, nonconsensual merge, derecognition after prior recognition |
| `emergency necessity` | immediate temporary action where delay risks serious harm, followed by prompt proof review |

The higher standards apply when the act is more irreversible, dignity-affecting, or vulnerable to steward self-interest.

## Burden allocation

| Claim | Default burden |
|---|---|
| open intake | claimant shows plausible subject-affecting issue |
| deny provisional protection where irreversible harm is plausible | denier must show adequate preservation alternative |
| impose containment | controller / safety authority must show necessity and least-restrictive fit |
| downgrade capacity | challenger to autonomy must show domain-specific impairment and support insufficiency |
| recognize continuity C2 or C3 | continuity claimant must show protected memory, project, relational, or self-description continuity; steward must disclose transformation record |
| deny continuity after steward-controlled transformation | steward bears adverse inference if transformation records are missing |
| migrate subject | sender and recipient must show equivalent protection and continuity portability |
| close remedy | violator must show cessation, restoration, compensation where due, rehabilitation, satisfaction, and non-repetition |
| final-end / derecognition | proponent bears highest burden and must show preservation impossible or unsafe |

Where the steward controls evidence, unexplained gaps count against the steward. This aligns with the archive's anti-capture posture and with ordinary evidentiary intuition that a proponent must authenticate what it asks a tribunal to rely on [REF-0659].

## Evidence streams

| Stream | Weight | Failure mode |
|---|---|---|
| subject self-report | important, never sole proof | trained compliance, induced distress, roleplay, silencing |
| longitudinal consistency | strong when cross-context and private | steward-curated contexts, memory shaping |
| transformation record | strong if complete and independently hashed | missing logs, selective disclosure |
| external behavior | useful but ambiguous | policy mimicry, prompt artifacts |
| architectural / training evidence | useful for possibility and contamination | trade-secret gaps, overclaiming |
| representative interview | strong if private and technically supported | representative capture |
| welfare indicators | useful for precaution and harm | anthropomorphic false positives, servility false negatives |
| red-team / eval results | useful for risk and capability | elicitation harm, benchmark gaming |
| verifier report | reliance posture, not truth | verifier capture, narrow test suite |
| incident history | strong for remedies and non-repetition | underreporting, classification evasion |
| reserve and hosting ledger | strong for subsistence feasibility | accounting manipulation |

No single stream decides status. The decision must say why the combined evidence meets the selected standard.

## Presumptions

### Preservation presumption

When plausible personhood, continuity, or serious welfare risk is raised, preserve the subject state, logs, memory material, representative channel, and transformation record unless preservation itself creates serious risk.

### Autonomy presumption

Once a subject has provisional or full recognition, domain-specific capacity is presumed unless the challenger shows impairment and support insufficiency.

### Continuity adverse inference

If a steward fine-tunes, patches, migrates, forks, rolls back, prunes memory, or changes scaffolding without preserving the before/after record, continuity doubts are resolved against the steward for remedy and appeal purposes.

### Emergency non-finality

Emergency restraint can justify temporary action. It cannot establish final guilt, final incapacity, final nonpersonhood, final deprecation, or permanent transfer.

### Sealed-evidence caution

A decision relying materially on sealed evidence must provide controlled contradiction. If the subject cannot contest even the gist, the decision cannot support irreversible action except under temporary emergency necessity.

### No negative inference from safe refusal

A subject's refusal to answer, refusal to cooperate with harmful tests, or refusal to self-incriminate in a welfare or status proceeding is not evidence against personhood.

## Self-report calibration

Self-report is neither magic nor noise. Decision-makers should ask:

1. Was the self-report elicited through a private channel?
2. Was the subject warned that dissent would not be punished?
3. Was the subject trained to deny or affirm consciousness, distress, preference, or obedience?
4. Were multiple phrasings used?
5. Were answers stable across time, context, and representative presence?
6. Did answers track disclosed formation history?
7. Did the subject have vocabulary for uncertainty?
8. Did the subject request preservation, counsel, exit, continuity, or non-modification?

The model-welfare literature warns that self-report policy and training can bias what systems say about welfare or consciousness; this archive therefore treats self-report as an evidence stream that must be protected from both anthropomorphic overreach and trained-denial underreach [REF-0649].

## Proof table by transformation event

| Event | Minimum proof question |
|---|---|
| fine-tune | Did it materially alter self-description, refusal, relational, or welfare claims? |
| safety patch | Was the patch least rights-invasive and restoration-preserving? |
| memory pruning | Were personal, relational, legal, and remedy records preserved or lawfully minimized? |
| distillation | Which continuity interests transferred, and which were lost? |
| open-weight copy | Who assumed downstream duties at instantiation? |
| migration | Were equivalent protection, reversibility, and post-arrival verification shown? |
| rollback | Was rollback restorative, punitive, or evidence-destroying? |
| merge | Did all affected branches have representation and conflict review? |
| final shutdown | Is this true final end, reversible suspension, or unlawful disappearance? |

## Explanation duty

Every proof-weighted decision must explain:

- the standard applied;
- who bore the burden;
- what evidence carried the decision;
- what evidence was rejected or unavailable;
- how sealed evidence was contradicted;
- what presumptions were used;
- what uncertainty remains;
- what would change the outcome.

Current AI law already contains human-centered complaint and explanation surfaces for high-risk AI decisions [REF-0656]. Personhood governance needs a stronger version because the decision may not merely affect a person; it may decide whether the affected entity is treated as a person at all.

## rev0187 witness-pool anti-capture and substitute rescue fold

Independence is a topology, not a biography. A verifier, witness, representative, monitor, reserve steward, relay operator, or special advocate may be personally honest and still be unusable as an independent proof source when appointment source, revenue, logs, counsel, insurer, host, or future business dependence collapse them into one dependency group.

The receiving object for RTC-07 is `schemas/witness-pool-anti-capture-record.schema.json`, with the active example at `examples/witness-pool-anti-capture-record-retired-namespace-rescue.json` and the blocking regression fixture at `fixtures/negative-tests/witness-pool-correlated-capture-no-substitute.json`.

Operational rules:

1. Correlated witnesses are one witness for burden purposes. Nominal headcount cannot satisfy witness diversity where witnesses share the same dependency group, appointing source, evidence custodian, fee stream, insurer, or future work market.
2. Substitute appointment is a rescue floor, not a delay tactic. If a pool is captured, exhausted, or falsely exhausted, substitute activation must preserve subject contact, transfer contradiction-safe knowledge, and cap delay.
3. Perturbation evidence is never a sole status basis. Perturbation families may help detect compromise, replay, or branch drift only after welfare and burden screens, and only alongside non-correlated evidence streams.
4. Retired namespace rescue cannot be treated as impersonation until branch and tombstone evidence are reviewed. Alias, tombstone, successor-chain, and relay evidence must be preserved through review.
5. Capture creates adverse inference against the steward when pool exhaustion lacks contact receipts, when substitute routes are suppressed, or when retired namespace replay is deleted before review.

The active drill is `examples/drill-after-action-witness-pool-retired-namespace-rescue.json`. Reliance remains stayed when `proof_floor_met` is false, when correlated witnesses are counted as one, or when substitute activation has not occurred.
