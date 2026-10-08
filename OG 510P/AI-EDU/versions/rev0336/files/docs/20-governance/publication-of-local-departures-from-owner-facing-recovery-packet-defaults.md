# Publication of local departures from owner-facing recovery-packet defaults

This document closes the archive's next recovery-governance gap: **once the archive has a portable
owner-facing packet floor and a tiny authority-family field layer, what must a service publish when
it departs from those defaults?**

The archive's current bet is:

> keep the packet floor, the family-conditioned field layer, and the red line against merits
smuggling — but add one still smaller departure-publication rule so local services cannot inflate
packets, suppress family fields, or claim that a family default is untruthful without making that
departure legible.

The point is to avoid four predictable failures at once:

- **silent override drift** — a service claims to use the portable packet rule while quietly adding
  or withholding fields that materially change what the owner sees;
- **rebuttal-field creep** — a supposedly narrow local correction slot becomes a hidden
  merits-preparation layer or mini-appeal dossier;
- **fake untruthfulness claims** — a service says a family default is “not truthful here” when the
  real issue is simply local preference, queue convenience, or a desire for more pre-decision
  material;
- **publication asymmetry** — the learner, teacher, or auditor can see the portable packet floor in
  public docs but not the live departures that actually govern treatment.

Current public signals support this thinner move. OECD's 2026 outlook keeps pressing educational AI
toward pedagogically purposeful design rather than generic task completion; OpenAI's 2026
learning-outcomes work increases pressure for longitudinal educational measurement without turning
support systems into hidden learner dossiers; UNESCO's current teacher/student competency framing
keeps human agency and accountable pedagogy visible; and current ICO / DfE privacy-and-safety
expectations keep minimisation, design-by-default, and child-facing design limits in frame. See
`B11`, `B17`, `B151`, `B152`, `B153`, `B154`, `B155`, `B156`.

## Relationship to the existing recovery surfaces

This document does not replace:

- [`portable-owner-facing-handback-packet-fields-for-recovery-authority-families.md`](portable-owner-facing-handback-packet-fields-for-recovery-authority-families.md)
- [`authority-family-defaults-for-recovery-treatment-mini-codes.md`](authority-family-defaults-for-recovery-treatment-mini-codes.md)
- [`portable-review-window-substitute-path-and-publication-defaults-for-recovery-branches.md`](portable-review-window-substitute-path-and-publication-defaults-for-recovery-branches.md)

Those surfaces already answer:

- which fields may travel in every owner-facing packet as `HP-FLOOR`;
- which additional `HP-FAMILY` fields may travel one step further for `AF-RECORD`, `AF-SAFETY`, and
  `AF-ROUTE`;
- and which recovery branches already carry shared publication floors, review-window bands, or tiny
  treatment mini-codes.

This document answers one narrower operational question:

- **what must a service publish when it does not simply inherit those packet defaults unchanged?**

## Three departure families

The archive now distinguishes three departure families.

| Departure family | Meaning | Why it may happen | What it must not hide |
|---|---|---|---|
| `DP-ADD` | the service adds one local field beyond `HP-FLOOR` or `HP-FAMILY` | a regime-local owner boundary, legally required local routing fact, or narrow rebuttal/correction slot may need a local field | a merits brief, outcome recommendation, or durable profile disguised as “extra context” |
| `DP-WITHHOLD` | the service suppresses an otherwise available `HP-FAMILY` field | the family field may be inapplicable, structurally absent, or untruthful before owner review in that regime | secret downgrading of learner visibility, continuity, or owner accountability |
| `DP-UNTRUTHFUL` | the service claims that a portable family default misdescribes the live local regime | the default could be false in a recurring local arrangement even though it is generally portable | preference-driven exception language that should really be local process, not a challenge to the default |

The archive keeps the asymmetry strict:

> departures may be local, but they may not be silent.

## What counts as a real departure rather than ordinary local process

A service is using a **portable owner-facing packet** only if every live packet for the relevant
branch still contains the full `HP-FLOOR` and then either:

1. stops there; or
2. adds only the already-authorised `HP-FAMILY` fields for that authority family.

Anything else counts as a departure and must be published under this document.

If a service cannot honestly emit the full `HP-FLOOR`, the archive's rule is:

> stop calling that output a portable owner-facing recovery packet for that branch/family, publish
that the packet floor does not travel there, and treat the process as local owner-side handling.

That rule matters because a missing floor field is not a small variation. It means the service is no
longer inheriting the portable packet floor at all.

## The seven-field departure publication floor

Whenever a service uses `DP-ADD`, `DP-WITHHOLD`, or `DP-UNTRUTHFUL`, it must publish a small
departure record containing exactly seven fields.

| Tag | Field | Why it matters | What it must exclude |
|---|---|---|---|
| `PD-1` | source default being departed from | says which `HPF-*`, `HPR-*`, `HPS-*`, or `HPT-*` field or family default is affected | vague prose such as “local packet differs a bit” |
| `PD-2` | departure family | makes clear whether the service added, withheld, or claimed untruthfulness | blended justifications that hide the real direction of change |
| `PD-3` | narrow reason family | names the bounded reason: local owner-boundary mismatch, legally required local routing fact, correction/rebuttal slot, structural non-applicability, or regime-untruthfulness claim | broad appeals to convenience, risk appetite, or staff preference |
| `PD-4` | learner-visibility status | says whether the departure is learner-visible at handback, learner-visible on request, or only auditor-visible with a published explanation route | hidden packet variation with no challenge path |
| `PD-5` | no-travel and expiry rule | states that the departure remains local, names where it stops, and says when the added/withheld field or claim expires | open-ended retention or downstream reuse across unrelated functions |
| `PD-6` | effect boundary statement | records what the departure does **not** decide: standing, readiness, safety, eligibility, rank, sanction, or queue outcome | soft merits advice or implied likely disposition |
| `PD-7` | review / promotion trigger | states when repeated use of the departure must be reviewed for retirement, branch split, or family-default revision | endless local residue with no ratchet toward simplification |

That is the whole floor. If a service needs more than these seven publication fields to explain a
recurring departure, the archive's current presumption is that the departure is either too broad to
be a packet variation or ripe for a new branch or family split.

## The only three kinds of `DP-ADD` the archive currently treats as presumptively admissible

The archive now allows only three generic `DP-ADD` families.

### `DPA-BOUNDARY`

A local field may be added to clarify a **regime-local owner boundary** that the portable floor does
not already name, such as a dual-owner handback where the published branch remains truthful but the
next local owner split is not fully captured by `HPF-4`, `HPS-3`, or `HPT-3`.

What this may do:

- identify the extra local owner boundary;
- clarify whether the packet stops with the first owner or immediately forks to a second named local
  owner;
- publish that this field is local-only and does not travel beyond that regime.

What this may not do:

- rank the urgency of the case;
- recommend the outcome that either owner should reach;
- predict which owner will prevail.

### `DPA-ROUTING-FACT`

A local field may be added to state one **legally required local routing fact** that determines
where the packet must go but does not decide the case.

What this may do:

- name a mandatory local office class or statutory destination;
- state that the destination is fixed by regime, not by packet evaluation;
- expire when the owner takes control.

What this may not do:

- import the local legal test;
- summarize the merits under that test;
- imply that routing itself proves the learner should lose ordinary standing or opportunity.

### `DPA-REBUTTAL`

A local field may be added as a **narrow rebuttal / correction slot** when the receiving owner or
learner needs to register disagreement with a portable packet label before the owner process fully
unfolds.

What this may do:

- record that the learner, teacher, or receiving owner contests a packet label, field value, or
  family tag;
- point to the challenge route already required by `HPF-6`;
- expire when the owner reaches the first meaningful review point.

What this may not do:

- become a general free-text merits narrative;
- store prior-case analogies, staff impressions, or advocacy summaries;
- survive as a durable sidecar after the owner process closes.

## When `DP-WITHHOLD` is truthful

Withholding an otherwise available `HP-FAMILY` field is permitted only when one of three things is
true:

1. **structural absence** — the local regime genuinely lacks the concept named by the portable
   field;
2. **pre-review untruthfulness** — the field would assert something not yet truthfully knowable
   before owner review;
3. **owner-boundary mismatch** — the field would collapse two local owners into one misleading
   packet fact.

`DP-WITHHOLD` may not be used merely because:

- the service prefers a shorter packet;
- the owner would rather infer the field privately;
- the field makes the local process more challengeable or legible.

If withholding becomes the normal state across many sites or across the whole authority family, the
archive should stop treating it as local residue and instead reconsider the portable family field
itself.

## When a `DP-UNTRUTHFUL` claim is strong enough to publish

A service may claim that a portable family default is locally untruthful only when it can say
something narrower than “our process is different.”

A publishable `DP-UNTRUTHFUL` claim must state:

1. **which portable field or family default would misdescribe the regime**;
2. **whether the problem is semantic, structural, or timing-based**;
3. **why that misdescription would matter to the receiving owner or learner**;
4. **what thinner truthful statement replaces it locally**.

A `DP-UNTRUTHFUL` claim is not justified when the real situation is only that:

- the regime prefers more internal detail;
- the office uses a stricter review culture;
- staff want earlier queue triage or merits preparation.

Those are local process preferences, not evidence that the portable default is false.

## The learner-visibility rule for departures

The archive now draws a sharper line between publication and secrecy.

| Case | Minimum visibility |
|---|---|
| `DP-ADD` that changes what the owner sees about the live branch, owner boundary, or challenge route | learner-visible at handback or learner-visible on request through the published challenge route |
| `DP-WITHHOLD` of any family-conditioned field that would otherwise be available for that authority family | learner-visible on request with a plain-language reason |
| `DP-UNTRUTHFUL` claim about a portable family default | publicly listed at service level and learner-visible on request for the affected handback |
| local auditor-only operational detail about how the departure was implemented | may remain auditor-visible only, but only if the departure itself is still publicly listed and challengeable |

This keeps the archive from publishing abstract packet rights while hiding the actual live
exceptions.

## What must remain forbidden even when departures are published

Publication does not legalise the following additions or suppressions. These remain out of bounds:

1. **predicted outcomes or likely dispositions**;
2. **queue-rank numbers, scarcity counts, or partner negotiations**;
3. **full transcripts, long excerpts, or narrative case summaries**;
4. **protected-category, disability, health, welfare, or family-status detail beyond what the lawful
   local owner separately gathers under its own rule**;
5. **cross-function joins to performance, discipline, welfare, or route history**;
6. **staff impression fields, confidence scores, or learner-type labels**.

A service may not rescue those fields by publishing them as local departures. They remain
non-portable merits material.

## What institutions should publish now

For any recurring official study companion, tutoring surface, coaching workflow, or route-help
service that uses owner-facing recovery handback packets, publish only six things:

1. whether the service inherits the portable packet floor unchanged for each relevant branch/family;
2. any active `DP-ADD`, `DP-WITHHOLD`, or `DP-UNTRUTHFUL` departures;
3. the bounded reason family for each departure;
4. whether a local rebuttal / correction slot exists and who may use it;
5. the learner-visibility and challenge route for each departure;
6. the expiry and review / promotion trigger for each departure.

That is enough to keep departures legible without publishing local manuals, statutory annexes, or
full owner-side procedures.



## When repeated departure publication now forces default revision, field promotion, branch split, or local retirement

The archive can now close `FT-0060` directly. A departure profile is for **truthfully publishing
variance**, not for protecting a false inherited packet rule forever. Once the same departure starts
repeating in a patterned way, the repetition itself becomes governance evidence.

Five tests now decide that threshold.

1. **same-default test** — the packets concern the same live branch, authority family (and family
   variant if one is already named), source default, and departure family rather than only loosely
   similar local notices;
2. **independent-repeat test** — the same departure and the same learner-facing consequence
   difference now appear across **3 independent owners / sites**, or across **2 independent owners /
   sites** when the reason family is already structural enough that local preference is implausible
   (for example structural absence, owner-boundary mismatch, legally fixed routing, or
   regime-untruthfulness);
3. **persistence test** — inside one owner, the same departure survives its own published review /
   expiry trigger and reappears at the next materially comparable cycle, review point, or allocation
   event;
4. **reason-lock test** — the packet keeps citing the same bounded reason family rather than
   rotating through convenience language, staff preference, or other moving justifications;
5. **sibling-asymmetry test** — the repeat cluster concentrates in one patterned sub-branch, owner
   arrangement, or route shape while sibling cases keep inheriting the published default without
   packets.

The thresholds stay intentionally low. These packets already sit in the archive's hotter
consequence-bearing recovery zone, so the archive is not going to wait for large-`n` program
evaluation before admitting that a published packet default is overclaiming what actually travels.

| Repeat pattern | Archive move now required | What the move means |
|---|---|---|
| same-default + independent-repeat + reason-lock across the whole live family default, especially through `DP-WITHHOLD` or `DP-UNTRUTHFUL` | **cool or revise the inherited default** | weaken the source default to the strongest truthful floor that actually travels, or convert it into a narrower conditional family rule |
| same-default + sibling-asymmetry concentrated in one patterned sub-branch | **branch** | stop forcing the whole family to carry departures and create or strengthen the narrower branch where the different packet rule is genuinely patterned |
| repeated narrow `DP-ADD` across independent owners, with the added field still passing the no-merits / no-dossier red lines | **promote the field** | revise the portable packet rule so the field becomes a new bounded family-conditioned field or a named branch-conditioned field instead of an endless local add-on |
| persistence inside one owner after the packet's own review / expiry trigger, but without wider cross-owner spread | **retire the portable packet claim for that owner-path** | stop presenting that owner's packet as inherited portable behaviour and publish it as office-bound / local-only until remediation or wider evidence says otherwise |
| packet disappears by the first named review trigger, or the owner adopts the same or stronger learner protection with no consequence-path loss | **keep as local departure only** | transient repair or genuinely stronger local protection does not yet change the inherited default |

Three consequences follow.

1. **Repeated publication is no longer enough.** Once the cluster tests are met, the archive expects
   the inherited packet rule to change rather than living forever behind a growing list of local
   departure notices.
2. **`DP-ADD` does not get promoted automatically.** A repeated local field deserves promotion only
   if it stays narrow, owner-boundary-safe, and free of merits preparation, prediction, or durable
   profiling.
3. **Single-owner persistence is already a governance failure.** If one owner keeps republishing the
   same departure after its own review trigger, the archive should stop advertising that path as
   portable even before broader sector evidence arrives.

## Why this counted as a real archive gain

The archive already knew which owner-facing packet fields may travel, which must remain local merits
residue, and what a service has to publish when it departs from those defaults. But it still lacked
the next narrower answer:

- when does a departure profile remain honest local residue;
- and when does the repeating packet itself become evidence that the inherited default is wrong,
  incomplete, or overbroad?

This document now answers that narrower question with one small ratchet:

- five repeat-cluster tests;
- four archive moves — cool / revise, branch, promote, or retire to local-only;
- and an explicit refusal to let publication by itself protect an overclaimed portable default
  forever.

That is a real operating gain because it blocks three opposite mistakes at once:

- letting the same consequence-bearing omission repeat forever just because it is now formally
  disclosed;
- branching or universalizing too early when a packet is only a transient repair;
- and silently promoting a repeated local field into the packet canon without checking whether it
  still respects the archive's anti-dossier and anti-pre-adjudication red lines.

## When repaired packet defaults genuinely recover and may harden again

The archive can now close `FT-0061` directly. **Packet repair is not the absence of departures for a
while.** A cooled, promoted, branched, or office-bound packet default has earned harder travel again
only when the archive can now point to a causal fix, the same packet-bearing event passing cleanly,
and live monitoring evidence that the quieter picture is not just underuse, diversion, or hidden
local owner handling.

Five tests now decide that threshold.

1. **cause-fixed test** — the structural reason that produced the downgrade has been changed,
   constrained to a narrower branch, or explicitly removed; a packet rule does not recover merely
   because staff now write a tidier departure notice for the same unchanged gap.
2. **same-event clean-run test** — the same live branch / authority-family variant / source default
   pairing that previously generated the departure now passes without that departure through **2
   materially comparable cycles** or **1 full comparable cycle across 2 independent owners /
   sites**.
3. **independent-confirmation test** — where the archive wants family-level travel again, at least
   **2 independent owners / sites** using the same live branch and authority-family variant now emit
   the recovered element without a new departure; single-owner quiet is not enough for family
   recovery.
4. **truthful-substitute test** — the previously cooled field, floor, visibility promise, or family
   default is now genuinely back in force; a weaker local workaround, lower-visibility explanation
   route, or informal mercy path does not count as recovery.
5. **live-monitoring test** — the owner or provider is still carrying out regular checks,
   review-interval monitoring, or post-deployment analysis, and the apparently cleaner picture is
   not explained only by suppressed use, rerouting away from the branch, or temporary closure of the
   underlying owner path.

These thresholds are intentionally small. The archive is not asking for a fresh large-`n` evaluation
before a packet default may recover. It is asking for enough evidence to show that the same
consequence-bearing packet path is now being governed truthfully again.

| Downgraded state | What now counts as recovery evidence | Archive move now allowed |
|---|---|---|
| **cooled family default** | cause fixed + same-event clean run + independent confirmation + no active departure on the same field / family claim | **re-harden one rung** to the strongest truthful family default that now travels |
| **promoted narrow field** | the promoted field now appears without fresh `DP-ADD` explanation, through comparable cycles and independent owners, while still respecting the no-merits / no-dossier red lines | **treat the field as an ordinary bounded packet field** rather than a still-fragile promotion |
| **branched sub-branch** | sibling branches now show the same packet behaviour through comparable cycles, and the branch-specific departure disappears without leaving a weaker truthful substitute behind | **merge upward** only if the branch distinction has actually stopped mattering |
| **office-bound / local-only reclassification** | a second independent owner / office using the same authority shape now runs the same element cleanly, or one owner runs it cleanly through repeated comparable cycles and the original structural blocker has been removed rather than merely tolerated | **promote back to authority-family or branch-level travel**; single-owner quiet alone is not enough |
| **packet only, never downgraded** | the departure disappears by its own review trigger and no repeat-cluster threshold is met | **retire the departure** with no archive-level change |

Four consequences follow.

1. **Time alone never re-hardens a packet default.** A quiet interval without the same live
   packet-bearing event, or without active monitoring, is not recovery evidence.
2. **Recovery is causal, not cosmetic.** The archive wants evidence that the old reason no longer
   governs the same path, not merely a cleaner public note.
3. **Recovery happens one layer at a time.** A cooled family default does not jump straight back to
   a stronger cross-family claim, and an office-bound packet rule does not become a sector-wide
   inheritance in one move.
4. **False quiet does not count.** If the branch is now rarely used because access was narrowed,
   learners were diverted elsewhere, or the route was administratively frozen, the archive treats
   that as changed exposure, not successful packet repair.

## Why this packet-recovery rule now travels

This is still an archive inference, not a claim that any one regulator publishes these exact
packet-recovery thresholds. The official signals nevertheless line up. OECD's 2026 outlook keeps
pressing educational AI toward purpose-built, pedagogically intentional use rather than unexamined
convenience. ICO guidance says organisations should provide simple ways to request human
intervention or challenge a decision and carry out regular checks to make sure systems affecting
people still work as intended. The AI Act's current official service-desk materials add two more
lifecycle signals from the same post-deployment stack: risk management for high-risk AI is a
continuous iterative process requiring regular review and updating, and post-market monitoring
should actively and systematically collect and analyse relevant data throughout the system's
lifetime. Together those signals support the archive's narrower move: once a packet rule has already
been cooled, promoted, branched, or reclassified for honest governance reasons, it should recover
only on monitored evidence that the same consequence-bearing path now runs cleanly again. See `B11`,
`B143`, `B147`, `B146`, `B150`, `B151`.

## When re-hardened packet defaults automatically reopen, and when later departures stay local

**Recovery does not buy infinite grace.** Once a packet default has been re-hardened, the archive no
longer treats every later packet departure as equal. Some later signals now automatically reopen the
recovered element; others stay as ordinary local variance unless they start repeating again.

Five relapse tests now decide the first cut.

1. **same-structural-relapse test** — the same live branch, authority-family variant, source
   default, and previously recovered pairing or field now fail again for the same structural reason
   family before the archive has seen another clean comparable run through the same event family.
2. **rights-shell-loss test** — the recovered element loses one of the pieces that made recovery
   truthful in the first place: the named authority / owner tag, explanation or challenge route,
   review anchor, truthful expiry rule, learner-visibility floor, or effect-boundary statement.
3. **serious-incident test** — the same consequence path is now tied to a serious incident,
   safeguarding-stage escalation, or other reportable exposure-to-harm event rather than an ordinary
   local packet departure.
4. **monitoring-blindness test** — the owner or provider can no longer show the regular checks,
   post-deployment monitoring, or review-trigger evidence that made the recovered state believable;
   a recovered packet rule cannot stay hardened once its monitoring evidence disappears.
5. **material-path-change test** — a later model, workflow, authority-owner, governance-regime, or
   rights-shell change means the old clean-run evidence no longer speaks to the live packet path,
   even if no new departure has yet repeated.

These tests are deliberately narrower than the repeat-cluster rule. They do **not** automatically
cool the family default all the way back down. They first decide whether the recovered element must
be reopened immediately for renewed scrutiny rather than continuing to enjoy recovered status.

| Later signal after re-hardening | Archive treatment now | Why |
|---|---|---|
| same structural reason returns on the same branch / authority-family variant before another clean comparable run | **automatic reopen** | the recovery evidence has not survived the first comparable reuse |
| owner tag, learner visibility, explanation / challenge route, review anchor, truthful expiry, or effect boundary disappears | **automatic reopen** | the recovered element has lost the rights-compatible shell that justified recovery |
| serious incident, safeguarding-stage escalation, or other reportable harm tied to the same path | **automatic reopen** | consequence-bearing harm is no longer ordinary local variance |
| relevant model / workflow / authority-owner / governance-regime change makes the old clean-run evidence stale | **automatic reopen** | recovery evidence does not travel unchanged across a materially different packet path |
| one-off `LOCAL-LOGISTICS` departure with same or stronger visibility, same effect boundary, same or earlier review anchor, and same challenge route | **ordinary local departure only** | this remains truthful local variance rather than structural relapse |
| stronger local learner protection or earlier owner review point than the recovered default promised | **ordinary local departure only** | stronger protection does not itself defeat recovery |
| isolated departure that disappears by its own next review trigger and does not recur across the same event family | **ordinary local departure only** | transient local repair is not yet relapse evidence |

A later departure may remain **ordinary local variance** only while all five of these stay true at
once: the same recovered branch and authority-family variant are still correctly named; the same or
stronger explanation / challenge route is still live; the same or stronger visibility /
effect-boundary / expiry shell still holds; no serious incident or safeguarding-stage escalation has
attached to the same path; and the departure disappears by the next named review trigger without
repeating the same structural reason.

Four consequences follow.

1. **Recovered status is conditional, not permanent.** The archive now distinguishes between a
   harmless new local departure and a relapse that reopens the recovered default immediately.
2. **One serious rights or harm signal is enough to reopen.** The archive does not wait for
   repeat-cluster thresholds once the same path has produced a serious incident, a
   safeguarding-stage escalation, or a visible rights-shell loss.
3. **Ordinary local departures still exist.** A recovered default does not collapse just because one
   site publishes a local logistics packet while preserving the same explanatory and challenge
   shell.
4. **Reopening is not yet full downgrade.** Once reopened, the archive reuses the existing cool /
   branch / promote / retire tools if repeat evidence accumulates again, rather than inventing a
   second enforcement tree.

## Why this packet-relapse rule now travels

This remains an archive inference rather than a claim that any one regulator publishes these exact
relapse thresholds. The official signals nevertheless line up in the same direction. OECD's 2026
outlook argues that pedagogical value depends on intentional design rather than generic convenience.
ICO guidance keeps simple routes for human intervention and challenge plus regular checks squarely
in view. The AI Act service-desk materials make post-market monitoring and serious-incident
reporting visible enough that consequence-bearing packet failures should not be treated as ordinary
local noise. And `Working together to safeguard children 2026` sharpens the same point for
child-safety routes: once a packet path has moved into a real safeguarding stage, the archive should
not treat that as just another local departure on a recovered default. Together those signals
support the archive's narrower move: after packet recovery, the first question is no longer only
whether departures are repeating, but whether the recovered default has lost the very conditions
that justified trusting it again. See `B11`, `B102`, `B143`, `B146`, `B148`, `B142`.

## When post-recovery extra sensitivity expires, and which later changes reset it

**Reopened once does not mean watched forever.** After a re-hardened packet default has survived the
first relapse rule, the archive now allows that extra sensitivity to earn down again — but only
after enough clean comparable reuse under the same live path, with active monitoring still running,
and without a hidden reset.

Five tests now decide whether the extra watch may expire.

1. **same-path survival test** — after recovery and after the first relapse screen, the same branch
   / authority-family variant / source default now survives either **2 additional materially
   comparable event cycles** or **1 additional full cycle across 2 independent owners / sites** with
   no automatic reopen signal.
2. **watch-monitoring test** — at least **1 named review interval or post-deployment monitoring
   checkpoint** actually closes during that watch window; missing monitoring evidence means the
   watch cannot expire.
3. **packet-shell continuity test** — the same named authority / owner tag, explanation / challenge
   route, review anchor, truthful expiry rule, learner-visibility floor, and effect-boundary
   statement remain in force, or become stronger, through the watch window.
4. **no-hidden-reset test** — no substantial modification, intended-purpose shift, authority-owner
   swap, governance-regime change, workflow / model / memory change, or packet-shell redesign that
   would materially alter the path has occurred without starting a fresh watch.
5. **no-repeat-return test** — no same-path repeat cluster has rebuilt beneath the threshold;
   isolated `LOCAL-LOGISTICS` departures may still exist only if they disappear by the next named
   review trigger while preserving the same or stronger packet shell.

These thresholds stay intentionally small. The archive is not demanding a new large-scale study
before extra sensitivity can earn down. It is asking for enough monitored comparable reuse to show
that the recovered packet path is no longer living on probation simply because the archive once
distrusted it.

| Re-hardened element | What now counts as watch expiry | Archive move now allowed |
|---|---|---|
| **family default or authority-family variant** | same-path survival + watch monitoring + packet-shell continuity + no hidden reset | **expire the special relapse watch**; later departures return to the archive's ordinary local / relapse / repeat-cluster rules unless a reset trigger occurs |
| **promotion from office-bound / local-only back to authority-family or branch-level travel** | same-path survival at the promoted level, with at least **1** clean comparable cycle under the live owner/authority arrangement that will now inherit the rule | **treat the promoted rule as an ordinary recovered variant** rather than a still-fragile exception |
| **restored packet floor, family field, or visibility promise** | the stronger truthful element survives the same named anchor through **2 additional comparable anchor uses** without a new same-reason departure | **let the restored element travel without extra relapse sensitivity** |

Six later changes now **reset the watch immediately**, even if no new departure has yet appeared.

1. **substantial-modification / intended-purpose reset** — the system or service undergoes a
   substantial modification, or its intended purpose / use case changes, in a way that could affect
   the governed packet path.
2. **authority-owner reset** — lawful exposure authority, queue owner, or the named decision owner
   changes in a way that makes the old clean-run evidence no longer speak to the live packet route.
3. **governance-regime reset** — batch offer becomes rolling slot, provider suitability screening
   becomes partner release control, provider-led safeguarding review becomes a formal multi-agency
   protective stage, or some similar regime change alters what the packet is really governing.
4. **material workflow / model / memory reset** — the live path now depends on a different workflow
   architecture, model family, memory regime, or automation boundary than the one that earned
   recovery.
5. **packet-shell redesign reset** — the explanation / challenge route, review anchor, expiry rule,
   learner-visibility floor, effect boundary, or authority-tag layer is redesigned rather than
   merely preserved or strengthened.
6. **monitoring-basis reset** — the monitoring plan, review-interval structure, or observable event
   family used to support recovery changes enough that the old watch evidence is no longer directly
   comparable.

Not every change resets the watch. **Staff turnover, copy edits, bug fixes, or pre-determined
documented maintenance inside the same intended purpose and same governed path do not reset it by
themselves.** The archive only resets when the change would make inherited trust about the same
packet path misleading.

Four consequences follow.

1. **Extra sensitivity expires on comparable reuse, not on elapsed time alone.** Quiet calendar time
   without the same live path or without an actual monitoring checkpoint does not earn it down.
2. **A reset is not yet a downgrade.** It restarts the watch because old evidence no longer cleanly
   transfers, but it does not by itself prove that the recovered default has failed again.
3. **History is not erased when the watch expires.** If the same structural reason returns later,
   the ordinary relapse and repeat-cluster rules still apply; expiry only removes the special
   hair-trigger status.
4. **The archive now distinguishes between path-preserving maintenance and trust-breaking path
   change.** That keeps the rule from collapsing into either infinite vigilance or careless
   inheritance.

## Why this packet-watch rule now travels

This remains an archive inference rather than a claim that any one regulator publishes these exact
expiry thresholds. The official signals nevertheless line up. OECD's 2026 outlook keeps pedagogical
intent and purposeful tool design at the center. ICO guidance expects challenge routes and regular
checks that systems are working as intended. The EU's current AI Act materials sharpen the reset
side: intended purpose shapes risk classification in sensitive domains such as education, deployers
must monitor operation and act on identified risks or serious incidents, and substantial
modifications or intended-purpose changes can require renewed conformity work. Together those
signals support the archive's narrower move: once a repaired packet default has survived its first
relapse screen, the extra sensitivity may earn down on monitored comparable reuse, but only until a
later path-changing event makes older recovery evidence no longer trustworthy. See `B11`, `B143`,
`B146`, `B149`, `B150`, `B151`.

## When individually non-reopening micro-changes accumulate into a fresh packet reset cluster

The archive can now close `FT-0062` directly. **A repaired packet path does not keep expired watch
evidence forever merely because each later edit looks too small to reopen on its own.** Once several
individually non-reopening edits compound on the same packet path, old clean-run evidence can stop
being a truthful basis for trust even though no single edit counts as substantial modification,
immediate rights-shell loss, or automatic reopen by itself.

A **qualifying packet micro-change** means a live change that:

1. affects the owner-facing packet shell, field logic, learner-visibility posture, review-anchor
   handling, effect-boundary statement, expiry handling, or challenge-route presentation;
2. does **not** by itself already trigger automatic reopen or immediate watch reset under the
   existing rule;
3. is more than copy-editing, typo repair, pure formatting cleanup, or pre-declared bug fixing that
   leaves the packet meaning unchanged.

The archive now tracks six packet micro-change families.

| Family tag | What changed | Why it matters |
|---|---|---|
| `PMC-VIS` | learner visibility or on-request visibility handling | older clean-run evidence no longer says what the learner can actually see |
| `PMC-ANCHOR` | review anchor wording, timing window, or first meaningful review handling | the packet may now hit a different real checkpoint even if the branch name stayed the same |
| `PMC-ROUTE` | challenge-route presentation, explanation route wording, or who receives the first contest | the same packet may now travel through a different practical route even when the formal owner did not change |
| `PMC-EFFECT` | effect-boundary wording about what the packet does not decide | a formerly thin handback shell can quietly become more outcome-shaped or more ambiguous |
| `PMC-EXPIRY` | expiry, carry-forward, or retirement handling | older watch evidence may no longer tell the truth about how long the packet remains live |
| `PMC-FIELD` | field labels, family-conditioned field inclusion rules, or local packet-shell additions that remain below ordinary departure thresholds when taken one by one | several small shell changes can add up to a different live packet even if no single field change justifies immediate reopen |

## The five tests for a fresh packet reset cluster

Several non-reopening edits now force a **fresh packet reset cluster** when all five tests below are
met.

1. **same-path basket test** — the edits concern the same live branch, authority-family variant,
   source default, and repaired packet element rather than loosely similar packet maintenance on
   unrelated paths;
2. **multi-family density test** — within **2 adjacent comparable cycles / review intervals** or one
   named maintenance window on that same path, the service accumulates either:
   - **3 qualifying packet micro-changes across at least 2 families**; or
   - **2 qualifying packet micro-changes** where **one** touches `PMC-VIS`, `PMC-ROUTE`, or
     `PMC-EXPIRY` and **one** touches `PMC-ANCHOR`, `PMC-EFFECT`, or `PMC-FIELD`;
3. **comparability-loss test** — a reasonable learner, teacher, owner, or auditor could no longer
   rely on the old clean-run evidence to know what packet shell arrives, when the first meaningful
   review happens, how challenge/explanation routing behaves, or how long the packet remains live;
4. **persistence-or-spread test** — the same basket either survives the next named review checkpoint
   on one owner-path or appears in materially the same pattern across **2 independent owners /
   sites** using the same repaired path;
5. **no-full-compensation test** — any stronger learner protection introduced by one change does
   **not** fully preserve or strengthen the same practical visibility, challenge, anchor, expiry,
   and effect shell once the whole basket is taken together.

The archive keeps this threshold low on purpose. Once a packet default has already needed repair,
many small shell edits should not get infinite inheritance merely because each individual tweak sits
just below the existing reopen or reset line.

## What does **not** count as a packet reset cluster

The archive does **not** force a fresh cluster merely because:

- one qualifying micro-change appears and disappears by the next named review trigger;
- several edits are only plain-language clarifications, formatting, or implementation bug fixes with
  no change in meaning;
- the packet shell becomes strictly stronger for the learner or owner on every relevant dimension
  and that stronger shell is publicly legible;
- a documented maintenance action was already pre-announced, path-preserving, and leaves the same or
  stronger visibility / route / anchor / expiry / effect shell in force.

A reset cluster is for **compound shell drift**, not for every small maintenance action.

## What the archive now requires once the cluster threshold is met

| Cluster outcome | Archive move now required | Why |
|---|---|---|
| threshold met and the practical rights shell is now weaker or more ambiguous | **fresh packet reset cluster + fresh watch immediately** | older clean-run evidence no longer transfers honestly to the live path |
| threshold met but the shell remains broadly equivalent or stronger overall | **fresh packet reset cluster + fresh comparable-reuse watch, without automatic cooling** | the archive should stop inheriting expired watch evidence even if it need not yet cool the default |
| same basket appears across 2 independent owners / sites on the same repaired family variant | **family/branch-level packet reset review** | this may already be evidence that the live maintenance basket is not merely local |
| basket persists through the next named checkpoint inside one owner-path | **owner-path packet reset cluster** | single-owner persistence is enough to break stale inheritance on a repaired path |

Whenever the threshold is met, the service should publish one small **packet reset-cluster notice**
naming only:

1. the source default / repaired element now losing stale watch inheritance;
2. the packet micro-change families in the basket;
3. the comparable window or maintenance window in which they accumulated;
4. whether the live shell is preserved, strengthened, weakened, or ambiguous overall;
5. the first new checkpoint that will count toward fresh watch evidence.

That is enough. The archive does not want a second giant maintenance annex.

## Why this accumulation rule now travels

This is still an archive inference rather than a claim that any one regulator publishes these exact
packet micro-change thresholds. The official signals nevertheless line up. OECD's 2026 outlook keeps
pressing educational AI toward intentional pedagogical design rather than convenience drift. ICO
guidance expects regular checks, effective challenge routes, and systems that still work as intended
after deployment. OpenAI's current learning-outcomes work underscores the need for longitudinal
rather than momentary evaluation. Together those signals support the archive's narrower move: once a
packet default has already been repaired and re-hardened, old trust should not silently transfer
across a compound shell drift merely because no single later edit is dramatic enough to trigger the
existing reopen line on its own. See `B11`, `B143`, `B146`, `B149`, `B150`, `B151`.

## Why this counted as a real archive gain

The archive already knew when repaired packet defaults recover, which later same-path signals reopen
them, and when extra watch sensitivity may expire or reset. But it still lacked the next tighter
answer:

- when several individually non-reopening packet-shell edits are still harmless maintenance;
- and when the basket itself becomes evidence that inherited trust is now stale.

This revision now answers that narrower question with one small accumulation rule:

- six packet micro-change families;
- five tests for a fresh packet reset cluster;
- a refusal to treat compound shell drift as harmless merely because each edit is individually
  small;
- and a tiny publication notice for the new cluster rather than a second giant process annex.

That is a real operating gain because it blocks three opposite mistakes at once:

- letting recovered packet defaults inherit stale watch evidence across many small shell edits;
- overreacting to every bug fix, wording cleanup, or stronger local protection as though it were
  fresh rights loss;
- and hiding compound packet redesign inside the phrase “ordinary maintenance”.

## When recurring same-basket packet maintenance changes may use a named pre-declared envelope

The archive can now close `FT-0063` directly. **A pre-declared packet maintenance envelope** is a
very small public notice saying that one already repaired packet path may undergo a narrow,
prospectively named class of shell-preserving edits during one short maintenance window without each
edit being counted ad hoc toward a fresh packet reset cluster.

An envelope is therefore a convenience rule for **honest batching**, not a loophole for quiet
redesign. It exists only because the archive already has the hotter rule beneath it: packet defaults
recover only on monitored comparable reuse, later serious same-path relapse reopens them, and
several individually non-reopening shell edits can already accumulate into a fresh reset cluster.
The envelope answers a still narrower problem: when the service already knows that the next few
changes are same-basket calendar, contact-route, or label harmonisation work, should it really
pretend to rediscover that fact one edit at a time?

## The three maintenance baskets that may even be considered for an envelope

The archive keeps this starter list intentionally short.

| Envelope tag | Admissible basket | What may change | What may not change |
|---|---|---|---|
| `PME-CALENDAR` | review-anchor / expiry housekeeping | calendar alignment, review-window wording clean-up, carry-forward wording, retirement wording that leaves the same or earlier meaningful review point and the same or shorter truthful expiry | new review authority, later real review point, longer silent carry-forward, hidden auto-renewal |
| `PME-ROUTE` | route / contact upkeep | named inbox, portal, office label, first-contact channel, or explanation-contact wording where the same owner, same escalation floor, and same challenge ladder remain live | different owner, lower challenge floor, removed explanation path, rerouting into a weaker queue or opaque bot-only first contact |
| `PME-LABEL` | label / plain-language harmonisation of already-permitted packet fields | field labels, visibility wording, ordering, or public-facing plain-language explanations for already-live floor or family-conditioned fields | new field inclusion logic, field removal, family-conditioned scope change, predicted outcomes, queue cues, merits narratives |

`PMC-EFFECT` changes do **not** qualify for an envelope in the starter canon. Once the
effect-boundary statement changes substantively, the service is already too close to redesigning
what the packet actually means rather than merely keeping the shell current.

## Five tests for whether a pre-declared envelope is truthful

A service may use a named pre-declared packet maintenance envelope only when all five tests hold at
once.

1. **same-repaired-path test** — the envelope covers one already repaired packet path: the same live
   branch, authority-family variant, source default, and repaired packet element, not a loose family
   of related services.
2. **pre-declared-basket test** — the envelope is published before the first covered change and
   names exactly one of the starter baskets above, the maximum number of covered edits, the
   maintenance window, and the post-window checkpoint that will test whether the path still deserves
   inherited trust.
3. **invariant-shell test** — the same branch tag, authority / owner tag, non-override statement,
   same or stronger learner visibility, same or stronger explanation / challenge route, same or
   earlier meaningful review point, and same or narrower truthful expiry all remain in force through
   the whole envelope.
4. **low-density-window test** — the envelope covers only one short maintenance window and at most
   **3 covered edits** before the named checkpoint; it is for bounded housekeeping, not rolling
   redesign.
5. **no-hot-overhang test** — no active `DP-WITHHOLD` or `DP-UNTRUTHFUL` departure, no serious
   incident or safeguarding-stage escalation on the same path, no open repeat-cluster review, and no
   owner / regime / workflow / model / rights-shell change that would already reset or reopen the
   path under the existing canon.

If any one of these fails, the service is back inside the ordinary departure, reopen, reset, and
cluster rules.

## The publication floor for an envelope notice

A truthful envelope notice should publish only seven things:

1. the `PME-*` tag and human-readable basket name;
2. the exact repaired packet path and source default it covers;
3. the allowed micro-change family inside that basket;
4. the shell invariants that may not weaken while the envelope is live;
5. the maximum covered edit count;
6. the opening and closing dates or the single named maintenance checkpoint;
7. the breach trigger and the first checkpoint that will count toward fresh watch evidence
   afterward.

That is enough. The archive does not want a rolling maintenance annex or a second miniature legal
code.

## What the envelope changes — and what it does not

A live truthful envelope changes only one thing: **qualifying covered edits do not have to be
counted ad hoc toward a fresh packet reset cluster while the envelope remains inside its declared
basket and invariants**.

Three things stay unchanged.

1. **Departure publication still applies.** If a covered edit becomes a real `DP-ADD`,
   `DP-WITHHOLD`, or `DP-UNTRUTHFUL` departure, the service must publish it under the ordinary rule;
   the envelope does not swallow departures.
2. **Automatic reopen still applies.** If the rights shell weakens, a serious incident appears, or
   the governed path materially changes, the service uses the existing reopen/reset rule first; the
   envelope does not defer that judgment.
3. **Fresh watch evidence still has to be earned later.** An envelope window does not itself count
   as clean comparable reuse. It only says that a small predicted basket of shell-preserving upkeep
   need not be rediscovered as drift one edit at a time.

## When an envelope collapses and the service must reset trust again

| Breach signal | Archive move now required | Why |
|---|---|---|
| the service touches a forbidden family, especially substantive `PMC-EFFECT` or field-inclusion logic | **envelope void + ordinary reset/cluster analysis immediately** | the basket is no longer shell-preserving |
| any shell invariant weakens in practice | **automatic reopen or watch reset under the existing canon** | the truthful rights shell is no longer intact |
| the service exceeds the declared edit cap or rolls the same envelope through another window without republishing it | **fresh packet reset cluster** | bounded housekeeping has become rolling redesign |
| the same path picks up an active `DP-WITHHOLD` / `DP-UNTRUTHFUL`, serious incident, or safeguarding-stage escalation while the envelope is live | **freeze the envelope and revert to the hotter packet rules** | a live consequence-bearing problem now outranks batching convenience |
| owner, regime, workflow, model, or rights-shell conditions change underneath the envelope | **envelope void + ordinary watch reset** | the path is no longer the same governed object |

The archive is intentionally asymmetric here. A truthful envelope may save a service from repetitive
ad hoc cluster counting, but it never protects the service from a fresh rights problem, a live
packet departure, or a hidden path redesign.

## Why this maintenance-envelope rule now travels

This remains an archive inference rather than a claim that any one regulator publishes these exact
maintenance-envelope tags. The official signal nevertheless lines up in the same direction. OECD's
2026 outlook continues to press educational AI toward intentional design rather than convenience
drift. ICO guidance keeps simple challenge routes, regular checks, and privacy-by-default squarely
in view. OpenAI's current learning-outcomes work points toward longitudinal monitoring rather than
one-off success snapshots. Together those signals support the archive's narrower move: where a
service can predeclare a tiny maintenance basket, hold fixed the rights shell, and publish an
explicit breach point, honest batching is better than either hidden drift or ritualised
pseudo-surprise at the same tiny class of edits every cycle. See `B11`, `B143`, `B146`, `B149`,
`B150`, `B151`.

## Why this counted as a real archive gain

The archive already knew when repaired packet defaults recover, which later same-path signals reopen
them, when extra watch sensitivity expires or resets, and when several individually non-reopening
edits accumulate into a fresh packet reset cluster. But it still lacked the next tighter answer:

- when the service may honestly batch recurring same-basket shell upkeep prospectively;
- and when it must still fall back to ordinary reset-cluster counting because the basket is no
  longer truly maintenance.

This revision now answers that narrower question with one small ratchet:

- three admissible starter envelope baskets;
- five tests for whether an envelope is truthful at all;
- a seven-field publication floor;
- and explicit breach rules that collapse the envelope back into the hotter packet-governance canon
  the moment it stops being path-preserving.

That is a real operating gain because it blocks three opposite mistakes at once:

- forcing services to rediscover the same tiny calendar, route, or label basket as though it were
  novel drift every cycle;
- letting “maintenance” become a cover story for silent rights-shell weakening or rolling redesign;
- and treating predeclared batching as though it were itself recovery evidence rather than merely a
  bounded convenience rule inside an already governed path.

## Current archive bet

The archive's current best guess is that **most owner-facing packet departures should begin as very
small public departure profiles, repeated departures should quickly force default repair, repaired
packet defaults should re-harden only on monitored comparable reuse, reopen on rights-shell loss or
serious same-path relapse, lose their special watch only after further clean comparable reuse under
the same governed path, stop inheriting that expired watch evidence once several individually
non-reopening packet-shell edits accumulate into a fresh reset cluster, and allow recurring
same-basket calendar, route, or label upkeep to batch prospectively only inside a tiny pre-declared
envelope with published invariants and explicit breach resets**.

That claim is now canon, but still live. The archive now has a starter portability answer too: see
[`portable-defaults-for-predeclared-packet-maintenance-envelopes.md`](portable-defaults-for-predeclared-packet-maintenance-envelopes.md).
The archive now has a starter quantitative answer too: see
[`portable-quantitative-bands-for-promoted-packet-maintenance-envelopes.md`](portable-quantitative-bands-for-promoted-packet-maintenance-envelopes.md).
The archive now has a starter checkpoint / breach answer too: see
[`portable-checkpoint-and-breach-defaults-for-promoted-packet-maintenance-envelopes.md`](portable-checkpoint-and-breach-defaults-for-promoted-packet-maintenance-envelopes.md).
The archive now has a starter republication / recurrence answer too: see
[`portable-republication-and-recurrence-defaults-for-promoted-packet-maintenance-envelopes.md`](portable-republication-and-recurrence-defaults-for-promoted-packet-maintenance-envelopes.md).
The archive now has a starter cumulative-cycle answer too: see
[`portable-cumulative-cycle-ceilings-and-fatigue-defaults-for-promoted-packet-maintenance-envelopes.md`](portable-cumulative-cycle-ceilings-and-fatigue-defaults-for-promoted-packet-maintenance-envelopes.md).
The archive now has a starter re-promotion answer too: see
[`portable-re-promotion-and-cooldown-exit-defaults-for-promoted-packet-maintenance-envelopes.md`](portable-re-promotion-and-cooldown-exit-defaults-for-promoted-packet-maintenance-envelopes.md).
The archive now has a starter first-post-repromotion watch answer too: see
[`portable-first-post-repromotion-watch-and-immediate-re-cooling-defaults-for-promoted-packet-maintenance-envelopes.md`](portable-first-post-repromotion-watch-and-immediate-re-cooling-defaults-for-promoted-packet-maintenance-envelopes.md).
The next narrower question is which re-promoted-and-watched portable maintenance envelopes, if any,
can safely carry one shared probation-expiry / ordinary-status restoration package after a clean
watched cycle, and which should keep restoration-to-ordinary trust local even after portable
re-entry survives one monitored reuse. See `OQ-0041`.
