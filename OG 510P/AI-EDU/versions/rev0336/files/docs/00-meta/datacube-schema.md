# Datacube schema and surface classification spine

This archive now needs an explicit cube shape. Without one, every careful exception can look like a
new document opportunity, and every new document can look equally canonical. The schema below is the
archive's first answer: surfaces should be classified by **what educational situation they govern**,
**who can act**, **what evidence they require**, **how much memory or proof may persist**, and
**when a branch must compress, retire, or remain local**.

This document does not replace the charter, reference model, open-question registry, or surface map
overview. It gives future passes a queryable spine so the archive can shrink and generalize rather
than only branch.

## Required axes

Every new canonical surface should be describable across these axes.

| Axis | Values to start with | Question the axis answers |
|---|---|---|
| `actor` | `student`, `teacher`, `institution`, `public_learner`, `vendor`, `assessment_body`, `support_owner`, `record_owner` | Whose agency, duty, or exposure is most directly at stake? |
| `stakes` | `practice`, `course_credit`, `gateway_exam`, `professional_gate`, `public_benefit`, `accessibility`, `discipline`, `wellbeing` | What harm follows if the system is wrong or too opaque? |
| `sector` | `primary`, `secondary`, `higher_ed`, `vet`, `adult_learning`, `public_workforce`, `library_civic`, `cross_sector` | Where does the default travel, and where must it localize? |
| `function` | `tutoring`, `feedback`, `drafting`, `grading_support`, `advising`, `routing`, `accessibility`, `assessment_proof`, `procurement`, `observability`, `memory`, `failure`, `change`, `public_recognition`, `security`, `evidence_governance` | What work is the AI or governance surface actually doing? |
| `risk_family` | `learning_loss`, `answer_dependence`, `privacy`, `surveillance`, `bias`, `access_chill`, `emotional_dependency`, `labor_shift`, `automation_opacity`, `security`, `record_error`, `contestability`, `evidence_laundering`, `construct_drift` | Which failure mode is the surface meant to prevent? |
| `memory_state` | `none`, `session`, `learner_declared_preference`, `bounded_course_continuity`, `human_owned_record_rail`, `predictive_profile`, `protected_local_record`, `minimized_residue` | What state may persist after the interaction? |
| `proof_state` | `none`, `student_disclosure`, `checkpoint`, `process_trace_excerpt`, `oral_defense`, `live_transfer`, `bundle`, `official_record`, `protected_evidence`, `local_only_residue` | What evidence supports trust without becoming surveillance? |
| `lifecycle` | `proposal`, `pilot`, `starter_default`, `promoted`, `branched`, `watched`, `repaired`, `dewatched`, `restored`, `settled`, `retired`, `residue`, `quarantine` | Where is the surface in its life? |
| `authority` | `advice_only`, `draft_for_review`, `queue_or_flag`, `reversible_action`, `record_bearing_action`, `human_only`, `prohibited` | What can the AI or workflow actually cause? |
| `owner` | `teacher`, `programme_owner`, `service_owner`, `record_owner`, `support_owner`, `assessment_owner`, `public_route_owner`, `vendor`, `joint_owner` | Who is accountable when the path fails? |
| `evidence_level` | `EV0-ASSERTION`, `EV1-DEMO`, `EV2-LOCAL-PILOT`, `EV3-COMPARATIVE-PILOT`, `EV4-EXTERNAL-STUDY`, `EV5-REPLICATED-OR-META`, `EV6-STANDARD-OR-LAW`, `EV7-OPERATIONAL-AUDIT`; legacy tags such as `external_standard`, `pilot`, `current_law_or_policy`, and `local_judgment` remain accepted | Why should the archive trust this default, and which exact claim family is supported? |
| `portability` | `canonical`, `starter`, `branch_portable`, `authority_family_portable`, `sector_local`, `route_native`, `local_only`, `quarantine` | What may travel unchanged? |

## Minimal metadata block

New long surfaces should begin to carry this optional metadata block near the top. Older surfaces
need not be backfilled immediately, but future passes should prioritize high-traffic surfaces first.

```yaml
surface_id: short-stable-slug
actor: [student, teacher]
stakes: [course_credit]
sector: [cross_sector]
function: [tutoring, assessment_proof]
risk_family: [learning_loss, answer_dependence]
memory_state: [session]
proof_state: [checkpoint, oral_defense]
lifecycle: starter_default
authority: advice_only
owner: teacher
portability: starter
evidence_level: [EV2-LOCAL-PILOT, EV6-STANDARD-OR-LAW]
related_assumptions: [AS-0001]
related_followthrough: [FT-0162]
```

The block is deliberately plain. It is not a compliance register, and it does not by itself
authorize use. It makes the surface findable and falsifiable.

## Cube views the archive should support

The archive should be queryable in at least six ways.

1. **Learner view:** What am I allowed to use, what proof is owed, what support is protected, and
   what actions are safe now?
2. **Teacher view:** What may I delegate, what must I sign off, where does AI help preserve
   learning, and where must I hold the line?
3. **Institution view:** What services are piloted, scaled, repaired, retired, or under watch, and
   who owns each failure path?
4. **Assessment view:** What construct is being measured, what assistance is compatible, what proof
   authenticates learning, and what evidence is inadmissible?
5. **Procurement view:** What systems, models, tools, memory, data flows, accessibility claims,
   security controls, and action authorities are in play?
6. **Public-route view:** What can travel between community, workforce, library, civic,
   adult-learning, and formal education nodes without turning into a hidden dossier?

## `SURFACES.json` contract

`SURFACES.json` now has two jobs. First, it must keep every Markdown surface visible to the cube.
Second, it must mark which rows are genuinely curated and which are rule-assisted placeholders that
still need human judgment.

The required row fields are:

- path;
- title;
- type;
- actor;
- stakes;
- sector;
- function;
- risk family;
- memory state;
- proof state;
- lifecycle;
- authority;
- owner;
- evidence level;
- portability;
- followthrough references where present;
- open-question references where present;
- tags;
- primary tags;
- mentioned tags;
- assumption references where present;
- and classification quality.

The first full backfill is intentionally coarse. A rule-assisted row is a retrieval and governance
affordance, not a final classification. High-load rows should be hand-tuned before major decisions
depend on them. `primary_tags` identify what a surface is; `mentioned_tags` identify retrieval
terms that appear in the surface but should not control its identity.

See [`surface-map-overview.md`](surface-map-overview.md) for the working maintenance rule and lint
contract.

## Compression rule for cube growth

A new surface should be created only when at least one of these is true:

| Gate | New surface justified when... | Otherwise... |
|---|---|---|
| `CUBE-G1` | a new actor / stakes / function combination appears | add a row to an existing table |
| `CUBE-G2` | evidence changes the default, not just the wording | update the existing assumption or bibliography note |
| `CUBE-G3` | ownership or authority changes materially | branch or add an authority row |
| `CUBE-G4` | memory, proof, or record persistence changes materially | add a bounded field set |
| `CUBE-G5` | a cycle has repeated enough that another shell would mostly restate prior shells | compress into a cycle grammar, terminal disposition, or retirement rule |
| `CUBE-G6` | implementation needs a stable, reusable machine-readable surface | add or extend `SURFACES.json` |

The fifth gate is now especially important. The hot-exam followup branch proved that the archive can
draw careful narrow distinctions. The next maturity step is proving it can stop.

## Evidence posture

The schema now points to
[`../20-governance/evidence-grade-and-claim-strength-ladder.md`](../20-governance/evidence-grade-and-claim-strength-ladder.md).
Public policy and assessment standards can justify governance floors; RCTs and quasi-experiments can
justify learning claims only within their setting; vendor product announcements can justify market
signals, not learning effectiveness; and local operational facts can justify local routes, not broad
canonical promotion.

The important rule is claim separation. A surface may have strong evidence for compliance, weaker
evidence for learning, and live audit evidence for security. Those should appear as separate
claim-family grades rather than one averaged confidence score.

This matches the archive's wider posture: the purpose of a datacube is not to make every cell
canonical. It is to show which cells are proven, which are provisional, which are local, and which
should not be filled.

See `B275`, `B276`, `B278`, and `B279`.
