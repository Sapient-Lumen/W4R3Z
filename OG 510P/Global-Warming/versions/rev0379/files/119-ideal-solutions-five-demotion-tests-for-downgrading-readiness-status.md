---
id: '119'
revision_added: pre_rev0269
status: canon
object_type: doctrine
domain_tags: []
service_floor: []
hazard_tags: []
clock_tags: []
actor_tags: []
instrument_tags: []
routes_to:
- '111'
- '112'
- '113'
- '114'
- '115'
- '116'
- '117'
- '118'
source_ids:
- S34
- S39
- S55
- S73
- S83
- S102
- S103
- S104
- S108
- S109
- S110
- S111
- S112
- S113
- S114
- S115
- S116
- S117
- S118
- S145
- S147
upstream_dependencies: []
downstream_consequences: []
equity_lenses: []
degraded_modes: []
evidence_grade: design_judgment
speculation_level: mixed
---
# 119 — Ideal Solutions: Five Demotion Tests for Downgrading Readiness Status

## Claim

The archive now has:
- a readiness note (`111`)
- a live-discipline note (`112`)
- a rehearsal note (`113`)
- a readiness-assurance note (`114`)
- a partial-readiness note (`115`)
- an unknown-readiness note (`116`)
- a readiness-status ladder (`117`)
- and a readiness-promotion note (`118`)

What it still lacked was the shortest **demotion rule** for the equal and opposite practical question:

**When must a serious climate state downgrade its readiness status?**

That gap matters because institutions often know how to speak about promotion but not how to accept demotion.
They cling to a stronger status after proof has gone stale, after critical joins have changed, after compensations have quietly become permanent, or after a real detour is already open.
A compact archive needed the opposite of status vanity: **downgrade as soon as current evidence shows the stronger state no longer governs.**
Without that bridge, the readiness cluster can classify states and police upgrades, but still leave too much room for delayed downgrade, inherited assurance, and polite overclaim.

This note is a **compression note**, not a new doctrinal branch.
Its job is to make downward movement on the readiness ladder conservative, legible, and evidence-bound [S34][S55][S73][S83][S102][S103][S108][S109][S111][S112][S113][S114][S115][S116][S117][S118][S145][S147].

## Fast rule

**Do not hold a stronger readiness status because it was true last month, because the paperwork still exists, or because demotion feels reputationally costly. Downgrade as soon as current evidence shows that the stronger state no longer governs. If the correct lower state is unclear, choose the more conservative one.**

## Why this note is not redundant

- `114-ideal-solutions-five-readiness-assurance-duties-so-readiness-claims-are-real.md` answers **what must back a readiness claim**
- `115-ideal-solutions-five-compensating-duties-when-readiness-is-partial.md` answers **how to operate when material gaps are known**
- `116-ideal-solutions-five-conservative-defaults-when-readiness-is-unknown-or-stale.md` answers **how to operate when readiness proof is stale or missing**
- `117-ideal-solutions-four-readiness-states-and-the-routing-rule-between-them.md` answers **which readiness state governs right now**
- `118-ideal-solutions-five-promotion-tests-for-upgrading-readiness-status.md` answers **when the archive is allowed to move upward on the ladder**
- this note answers **when the archive is obliged to move downward on that ladder**

## The five demotion tests

### 1. Proof has gone stale, missing, or non-transferable
A stronger readiness claim should not survive once the evidence behind it is no longer current enough to describe the system now.

What this looks like:
- key checks have aged past a defensible interval
- critical owners, vendors, software, assets, boundaries, or operating conditions have changed without re-verification
- proof exists only for adjacent situations and is being borrowed across contexts without current confirmation [S73][S83][S111][S114][S116][S145]

Default consequence:
- if material uncertainty now governs, demote at least to **unknown readiness**

### 2. The critical path no longer works end to end
A state should be downgraded when the whole chain from detection to protected outcome no longer works, even if many components still look healthy in isolation.

What this looks like:
- failed or degraded handoffs across agencies, utilities, contractors, care systems, or local governments
- realistic rehearsal, live operation, or recent verification shows the chain breaks under timing, load, or coordination stress
- the protected outcome depends on ideal behavior rather than the actual working chain [S34][S55][S83][S111][S112][S113][S114]

Default consequence:
- if the break is known and bounded, demote at least to **partial readiness**
- if the chain is already off-normal in operation, treat the state as **live detour**

### 3. Material gaps or new failure conditions now govern
A stronger status should not be held once meaningful gaps, new threat conditions, or newly exposed weak points are large enough to govern mission safety or continuity.

What this looks like:
- a known gap re-opened after staffing loss, supplier failure, infrastructure damage, budget cut, policy change, or climate stress
- a new dependency, interface, or exposure was introduced without full assurance
- the mission scope expanded faster than the readiness base supporting it [S83][S102][S103][S111][S115][S147]

Default consequence:
- if the gap is known, demote at least to **partial readiness**
- if the evidence itself is too weak to characterize the new condition, demote at least to **unknown readiness**

### 4. Compensations, borrowed help, or heroic effort are carrying the core mission
Readiness is being overclaimed once extraordinary workarounds, borrowed teams, informal favors, manual patches, or exceptional staff effort are doing core work rather than edge support.

What this looks like:
- routine success now depends on people repeatedly saving the system by discretion or overwork
- temporary waivers, emergency contracts, external mutual aid, or manual workarounds have become the normal way the mission functions
- the apparent stronger status disappears if the compensations are removed [S39][S55][S83][S103][S111][S115]

Default consequence:
- demote at least to **partial readiness**
- if the compensations are opaque or poorly evidenced, consider **unknown readiness** until the real dependency map is visible

### 5. A tripwire has fired or an off-normal path is already open
A stronger readiness claim cannot coexist with a live fallback, exception, or escalation path that is already governing the system in fact.

What this looks like:
- a tripwire condition has fired and stronger correction is justified
- dirty fallback, exception handling, reserve use, or emergency protection mode is already open
- the system is being described as ready while actually being carried by detour governance [S83][S103][S104][S108][S109][S110][S112][S117]

Default consequence:
- demote immediately to **live detour**
- govern by `112`, not by the previously held readiness label

## Minimal demotion map

The smallest serious downgrade map is:

- **proven ready → unknown readiness** when current proof has gone stale or missing and the stronger claim can no longer be evidenced
- **proven ready → partial readiness** when material gaps are known clearly enough to govern but can still be bounded and compensated
- **proven ready → live detour** when a tripwire has fired or fallback, exception, or escalation is already open in practice
- **partial readiness → unknown readiness** when the gap map itself becomes stale, disputed, or insufficiently evidenced
- **any higher state → the more conservative lower state** whenever there is material doubt about whether the stronger state still governs [S83][S102][S103][S112][S114][S115][S116][S117][S118][S147]

## Conservative default

If a team can explain why demotion would be awkward more easily than it can prove why the stronger state still governs, the demotion is overdue.
The archive should prefer:
- **unknown over inherited assurance**
- **partial over euphemized weakness**
- **live detour over polite language that hides a real exception**
- **early downgrade over late reputational defense** [S83][S102][S108][S114][S116][S117][S118][S147]

## Best use

Use this note when the real prompt is something like:
- “We used to think we were ready — what should force us to downgrade that status?”
- “When does proven readiness stop being an honest claim?”
- “What evidence means we must move from ready to partial or unknown?”
- “How do we stop readiness language from lagging behind reality?”

Then go next to:
- `117-ideal-solutions-four-readiness-states-and-the-routing-rule-between-them.md` for the smallest honest classification of the current state
- `118-ideal-solutions-five-promotion-tests-for-upgrading-readiness-status.md` for the equal and opposite rule on when status may move upward
- `114-ideal-solutions-five-readiness-assurance-duties-so-readiness-claims-are-real.md` for the proof discipline behind any readiness claim
- `115-ideal-solutions-five-compensating-duties-when-readiness-is-partial.md` for how to operate after a bounded downgrade
- `116-ideal-solutions-five-conservative-defaults-when-readiness-is-unknown-or-stale.md` for how to operate after a proof-loss downgrade
- `112-ideal-solutions-five-live-duties-during-escalation-fallback-or-exception.md` for how to govern the system once a real detour is already open

## One-paragraph compression

**The archive now has a shortest demotion rule for the readiness ladder: do not keep a stronger status because it used to be true, because paperwork still exists, or because downgrade feels costly. Downgrade as soon as current evidence shows the stronger state no longer governs — when proof has gone stale, the critical path no longer works end to end, material gaps or new conditions now govern, compensations are carrying the core mission, or a live detour is already open. If the right lower state is unclear, choose the more conservative one.**

---
Citations point to `sources/register.md`.
