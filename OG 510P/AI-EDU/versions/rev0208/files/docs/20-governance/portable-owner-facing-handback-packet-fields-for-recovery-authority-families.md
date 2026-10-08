# Portable owner-facing handback-packet fields for recovery authority families

This document closes the archive's next recovery-governance gap: **once recovery mini-codes have already hardened by authority family, which owner-facing handback-packet fields may travel with those defaults, and which must remain local merits preparation rather than portable recovery metadata?**

The archive's current bet is:

> keep the generic packet-and-signal rule, the recovery starter profiles, the child-branch map, the portability layer, the treatment mini-codes, and the authority-family defaults — but now add one still smaller packet-field rule so study or route-help surfaces can tell the right owner what kind of problem has arrived without quietly telling that owner what outcome to reach.

The point is to avoid four predictable failures at once:

- **dossier rebound** — the archive forbids durable dependence files at the support layer, then quietly rebuilds them inside owner-facing handback packets;
- **merits smuggling** — packet fields start as routing metadata and end as hidden recommendations about standing, readiness, safety, or eligibility outcomes;
- **queue pre-decision by packet shape** — a supposedly neutral handback packet quietly embeds urgency rankings, likely dispositions, or branch-specific priority nudges that the named owner should have to justify independently;
- **false family inheritance** — institutions reuse an authority-family tag while slipping in different case narratives, evidence summaries, or outcome predictions that no longer travel truthfully across the family.

Current public signals support this thinner move. OECD's 2026 outlook keeps pressing educational AI toward pedagogically purposeful design rather than generic task completion; UNESCO's current teacher/student competency framing keeps human agency and accountable pedagogy visible; OpenAI's current learning-outcomes work increases pressure for longitudinal measurement without turning support systems into hidden learner dossiers; and current ICO / DfE privacy-and-safety expectations keep minimisation, profiling restraint, and child-facing design limits in frame. See `B11`, `B17`, `B102`, `B151`, `B154`, `B155`, `B156`.

## Relationship to the existing recovery surfaces

This document does not replace:

- [`recovery-packets-and-aggregate-dependence-signals.md`](recovery-packets-and-aggregate-dependence-signals.md)
- [`portable-review-window-substitute-path-and-publication-defaults-for-recovery-branches.md`](portable-review-window-substitute-path-and-publication-defaults-for-recovery-branches.md)
- [`mini-codes-for-partially-portable-recovery-treatment-branches.md`](mini-codes-for-partially-portable-recovery-treatment-branches.md)
- [`authority-family-defaults-for-recovery-treatment-mini-codes.md`](authority-family-defaults-for-recovery-treatment-mini-codes.md)

Those surfaces already answer:

- when ordinary study support should escalate into recovery at all;
- which review-window bands, substitute-path families, and publication floors travel with named recovery branches;
- which hotter branches deserve `MC-NW`, `MC-ML`, or `MC-AH`;
- and which of those mini-codes truly harden across `AF-RECORD`, `AF-SAFETY`, `AF-ROUTE`, or stay branch-bound under `AF-LOCAL`.

This document answers one narrower operational question:

- **what may an official study, coaching, or route-help surface actually place in an owner-facing handback packet once those authority-family defaults already exist?**

## Three classes of handback-packet field

The archive now distinguishes three classes of field.

| Class | Meaning | What it is for | What it must not become |
|---|---|---|---|
| `HP-FLOOR` | portable floor field | telling the named owner what kind of governed recovery handback has occurred | outcome recommendation, merits brief, or hidden learner profile |
| `HP-FAMILY` | family-conditioned travel field | stating one additional owner-family fact that may matter to truthful interim handling | a local formula, legal conclusion, or case narrative disguised as a family default |
| `HP-LOCAL` | permanently local residue | anything that belongs to local merits preparation, regulator process, welfare/safety investigation, or queue adjudication | portable recovery metadata |

The rule is intentionally asymmetric:

> a field may travel only if it helps the next owner identify the branch, authority boundary, interim posture, and review anchor **without materially deciding the case**.

## The portable floor every authority family may inherit

If an owner-facing handback packet exists at all, only the following seven fields may travel unchanged across authority families.

| Field tag | Field | Why it may travel | What it must exclude |
|---|---|---|---|
| `HPF-1` | branch identifier and authority-family tag | tells the owner which governed branch and which authority family is in play | local subcase narratives or hidden branch synonyms |
| `HPF-2` | present constraint family | tells the owner the coarse kind of issue now governing the handback: record, safety/exposure, route/eligibility, or equivalent family-local label | causal speculation, blame language, learner-character judgments |
| `HPF-3` | currently published interim rule | states the already-legible `MC-NW`, `MC-ML`, and/or `MC-AH` posture plus the substitute-path family in force, if any | stronger unpublished promises or locally improvised side guarantees |
| `HPF-4` | named owner and next review anchor | says who now owns the case and at what next meaningful checkpoint review must occur | hidden internal priority score or implied disposition |
| `HPF-5` | non-override statement | records that the packet does not decide standing, readiness, safety, eligibility, rank, or sanction outcome | soft recommendations such as “likely approve” or “hold should usually continue” |
| `HPF-6` | challenge / explanation route | preserves the learner's route to ask what happened or contest the path | full local hearing script or office-specific advocacy notes |
| `HPF-7` | packet expiry / deletion rule | prevents handback metadata from becoming a durable shadow file after the owner process ends | open-ended retention or repurposing for later unrelated treatment |

These seven fields are the archive's new packet floor. Anything below this floor is too vague to govern. Anything above it must justify why it is still not merits preparation.

## Which additional fields may travel one step further by authority family

The archive now permits a very small `HP-FAMILY` layer. These fields travel only because the authority-family map already made clear that the same owner family controls the same durable-effect type across recurring cases.

### `AF-RECORD`

Record-owner packets may add three family-conditioned fields:

| Field tag | Allowed field | Why it may travel | What stays out |
|---|---|---|---|
| `HPR-1` | durable academic-effect family | says whether the live issue concerns ordinary participation, progression/standing, official note/flag, or comparable record family | actual grade, standing formula, aid effect, misconduct theory, or accommodation merits |
| `HPR-2` | requested continuity family | says whether the learner is asking for ordinary non-worsening hold, nearest comparable path, or explanation-only handback | recommended outcome, likely success label, or advocacy summary |
| `HPR-3` | course / programme locus | identifies the bounded locus of the record effect so the owner knows which record regime is implicated | broad learner history, prior cases, or comparative cohort data |

Why these may travel: record owners usually do need to know **what durable record family is being touched, what continuity family is being asked for, and where the record effect lives**. They do not need a pre-written merits case.

### `AF-SAFETY`

Supervisor/safety-owner packets may add three family-conditioned fields:

| Field tag | Allowed field | Why it may travel | What stays out |
|---|---|---|---|
| `HPS-1` | exposure / safety context family | says whether the live context is classroom, lab, placement, clinic, fieldwork, transport, safeguarding, welfare, or analogous local family | risk score, diagnosis, incident narrative, or protected-trait inference |
| `HPS-2` | nearest-safe substitute family, if one is already published | tells the owner whether the current interim path is simulation, supervised evidence, pause, or no substitute path | local remediation plan or implied clearance recommendation |
| `HPS-3` | immediate owner-boundary trigger | says whether the handback is happening because exposure permission, welfare action, safeguarding judgment, or formal attendance treatment now exceeds support-surface authority | hidden urgency ranking, disciplinary framing, or predicted intervention |

Why these may travel: safety owners usually do need to know **what sort of exposure or welfare context is live, which already-published substitute family is active, and why the support surface hit a hard authority boundary**. They do not need a quasi-investigative packet from the study tool.

### `AF-ROUTE`

Route-case-owner packets may add three family-conditioned fields:

| Field tag | Allowed field | Why it may travel | What stays out |
|---|---|---|---|
| `HPT-1` | route-effect family | says whether the live issue concerns slot/seat family, eligibility family, referral/dispatch family, or partner-inventory family | statutory conclusion, programme-fit recommendation, or hidden route ranking |
| `HPT-2` | continuity truthfulness state | says only whether a comparable hold is currently truthful, untruthful, or unknown under the already-published family split between `MC-NW` and `MC-ML` | queue formula, exact place in line, scarce-seat counts, or partner negotiations |
| `HPT-3` | next owner boundary | says whether the next decision sits with the home office, partner owner, statutory case owner, or mixed handback | likely disposition, escalation script, or unreviewed priority label |

Why these may travel: route owners usually do need to know **what route family is being touched, whether the packet arrives under a hold-versus-minimal-loss split, and who actually owns the next boundary**. They do not need precomputed scarcity logic disguised as metadata.

### `AF-LOCAL`

`AF-LOCAL` gets **no additional family-conditioned fields**. The packet stops at `HP-FLOOR` unless a later archive pass proves that a thinner family default really travels.

## What must remain permanently local merits preparation

The archive now makes the red line explicit. The following stay `HP-LOCAL` even when a case repeatedly recurs inside the same authority family:

1. **full transcripts, long excerpts, or holistic conversation summaries**;
2. **inferred dependence profiles, learner-type labels, or cross-function risk scores**;
3. **recommended outcomes, likely approval / denial tags, or soft queue-priority nudges**;
4. **protected-category, disability, health, welfare, or family-status details beyond what the receiving lawful owner already gathers under its own rule**;
5. **comparative cohort statements, staff impressions, or prior-case analogies**;
6. **local formulas, statutory tests, regulator thresholds, standing equations, queue logic, or sanction calendars**;
7. **investigative narratives, witness-style summaries, or office-specific merits briefs**.

Those materials may sometimes exist elsewhere under lawful, owner-controlled process. They are not portable recovery metadata and must not be smuggled in through the support surface.

## The archive's field-composition rule

An official study, coaching, or route-help surface may compose an owner-facing packet only in this order:

1. `HP-FLOOR` fields;
2. zero or more allowed `HP-FAMILY` fields for the active authority family;
3. nothing else.

If the service believes some additional field is necessary, the archive's current rule is:

> stop calling it a portable recovery handback packet and treat it instead as local owner-side process under that office's own rule.

That is how the archive keeps the support surface from quietly becoming a pre-adjudication layer.

## What institutions should publish now

For any recurring official study companion, tutoring surface, coaching workflow, or route-help service that uses owner-facing recovery handback packets, publish only five things:

1. whether the service ever emits owner-facing handback packets at all;
2. the `HP-FLOOR` fields that always travel;
3. the `HP-FAMILY` fields, if any, permitted for each authority family;
4. the fields explicitly prohibited as `HP-LOCAL`;
5. the expiry/deletion rule and explanation/challenge route.

That is enough to keep handback legible without publishing full internal office manuals.

## What counted as a real archive gain

The archive already knew three things:

- hotter recovery branches can publish shared review windows, substitute-path families, and publication floors;
- those branches can sometimes publish `MC-NW`, `MC-ML`, or `MC-AH`;
- and those mini-codes only harden fully at the level of the authority family that really owns the durable effect.

It still lacked the next narrower answer: **what may actually ride inside the handback packet once that authority-family map exists?**

This document answers that question with a deliberately small rule:

- one **portable floor** for every owner-facing packet;
- one **family-conditioned layer** for `AF-RECORD`, `AF-SAFETY`, and `AF-ROUTE`;
- and one explicit **local merits residue** that may not travel.

That is a real operating gain because it blocks three opposite mistakes at once:

- leaving owners with packets too vague to be governable;
- rebuilding learner dossiers under the name of humane continuity;
- and letting support surfaces quietly pre-decide record, safety, or route treatment.

## Current archive bet

The archive's current best guess is that **portable owner-facing packets should carry branch-and-authority metadata plus a tiny family-conditioned field layer, but should stop short of any merits recommendation, queue pre-decision, or durable learner narrative**.

That claim is now canon, and now has a companion departure-publication-and-ratchet rule. The next narrower question is when cooled, promoted, branched, or office-bound packet defaults have genuinely recovered and may harden again, and which later packets or path changes should reopen them. See [`publication-of-local-departures-from-owner-facing-recovery-packet-defaults.md`](publication-of-local-departures-from-owner-facing-recovery-packet-defaults.md) and `OQ-0031`.
