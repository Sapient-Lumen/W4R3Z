# Branching and retreat rules for split-lane display profiles

This document closes the archive's next implementation gap about **when the starter split-lane
display profiles may travel unchanged, when they need a child branch, and when a shared packet
should retreat entirely**.

The archive now has a generic learner-facing split-lane grammar (`DL0-DL3`, `LD1-LD7`, `PX0-PX3`)
plus a small starter profile layer for higher-ed teach-out, public workforce routing, civic
first-contact, licensure-sensitive routes, and protected support channels. What it still lacked was
a tighter answer to a narrower question:

> **when does one of those inherited starter profiles remain honest as-is, when should it branch
further because after-hours posture or office family already differs, and when should packet
tidiness lose entirely to separate office-bound or protected-channel handling?**

The archive's current bet is:

> a starter display profile may travel unchanged only while after-hours posture, office family, and
external-owner timing still tell the same practical truth; once those diverge, the packet should
either branch visibly or stop pretending it is one bundle.

Current public signals point the same way. HLC's current policy book still treats teach-out
communications as a bundle with distinct student-critical elements rather than one vague continuity
promise. Federal Student Aid still distinguishes FAFSA estimates from final school aid offers and
still treats transfer-student aid handling as a separate monitored process. OIA still ties its
external complaint timing to the provider's final internal decision / Completion of Procedures
Letter rather than to earlier generic route notices. WIOA still describes a public system that
combines employment, education, training, and support services without collapsing them into one
owner. PLA still positions public-library digital literacy as free first-contact infrastructure, not
as the downstream owner of aid, sanction, or complaint lanes. And SAMHSA's 988 materials still make
clear that crisis support is a distinct 24/7 channel. See `B183`.

## Relationship to the existing split-lane canon

This document does not replace either of the existing split-lane surfaces or the newer after-hours
field layer:

- [`../30-operations/split-lane-packet-display-and-dependency-rules.md`](../30-operations/split-lane-packet-display-and-dependency-rules.md)
  still answers whether several lanes may be shown together at all and what each displayed lane must
  show;
- [`sector-and-function-profile-splits-for-split-lane-display-defaults.md`](sector-and-function-profile-splits-for-split-lane-display-defaults.md)
  still answers where the generic packet grammar already starts hotter or cooler by sector/function;
- [`availability-acknowledgement-and-action-now-fields-for-after-hours-split-lane-branches.md`](availability-acknowledgement-and-action-now-fields-for-after-hours-split-lane-branches.md)
  now answers what an after-hours or delayed-owner child branch must actually publish once it
  remains visible.

This document adds one thing only:

- a **branch / retreat rule** for deciding when an inherited starter profile may still travel
  unchanged, when it should split into a child branch, and when a lane should leave the shared
  packet entirely because office ownership, after-hours truth, or protected-channel intensity now
  matters more than convenience.

## The three tiny code families the archive now adds

### Branch posture (`BR0-BR3`)

| Code | Meaning | What the packet may still do |
|---|---|---|
| `BR0 inherit unchanged` | the starter profile remains honest without further branching | one packet may keep the inherited `DL*` posture as long as after-hours posture, owner shape, and external timing do not materially change the learner's next action |
| `BR1 child branch within shared packet` | the packet may stay unified, but one child branch must publish different availability / queue truth | the packet may keep one shell, but it must mark which lane is browse-only, intake-only, or awaiting the next business-hours owner act |
| `BR2 child branch with lane separation` | the packet may still show related lanes together, but a lane now needs its own row/card or supplement because office family or external-owner timing differs materially | one packet may still explain the relationship, but it may no longer pretend one front desk or one operative clock owns the whole problem |
| `BR3 retreat from unified packet` | one lane should leave the shared packet and travel through a separate notice or protected channel | the shared packet may name the lane and its owner, but it should not carry the operative details as though they belonged to the ordinary route bundle |

### After-hours posture (`AT0-AT3`)

| Code | Meaning | Why it matters |
|---|---|---|
| `AT0 same-hours posture` | all displayed lanes are truthfully business-hours or truthfully always-available in the same way | no extra after-hours branching is needed |
| `AT1 after-hours browse / intake only` | the packet stays visible after hours, but the lane can only inform, collect a request, preserve a place, or point onward; no adverse clock should silently run on the assumption of live owner action | the learner must not mistake visibility for live adjudication |
| `AT2 delayed owner action` | the lane may accept an after-hours action, but the operative owner response, review, or posting starts only in the next owner window | the packet must separate "you can send this now" from "this office is acting now" |
| `AT3 live urgent or protected route` | a lane has a genuine 24/7 or urgent protected channel that does not share the ordinary route office's hours, queue, or disclosure norms | once one lane becomes urgent/protected in this way, ordinary packet tidiness becomes actively misleading |

### Office-family divergence (`OF0-OF4`)

| Code | Meaning | Why it matters |
|---|---|---|
| `OF0 same owner` | the same office or genuinely unified service owner runs the displayed lanes | starter inheritance is most plausible here |
| `OF1 adjacent internal family` | the lanes sit in nearby internal owners with shared handback norms but still distinct queues or evidence pockets | a shared packet may survive, but owner blur risk rises |
| `OF2 distinct internal family` | the lanes belong to materially different internal offices such as route/advising versus aid/compliance or conduct/appeal | one packet may still orient, but not as if one desk owns all next steps |
| `OF3 external owner` | a lane turns on an outside owner such as a regulator, lender/aid monitor, licensure board, placement host, or independent complaint body | external timing almost always requires at least a visible child branch |
| `OF4 protected support owner` | a lane belongs to safeguarding, disability/accommodation, wellbeing/crisis, or another protected support channel with narrower audience or disclosure rules | the ordinary shared packet should usually stop at pointer-level treatment |

## How the codes combine

The archive keeps the combination rule deliberately simple.

### `BR0` is the exception, not the default, once any divergence becomes real

Use `BR0` only when the inherited starter profile still has:

- `AT0`; and
- `OF0` or very light `OF1`; and
- no lane whose operative timing depends on a later external or protected owner output.

### `BR1` is mainly for truthful availability branching

Use `BR1` when the main difference is **how the lane is available or queued**, not who ultimately
owns it.

Typical triggers:

- the packet remains visible after hours but one lane is only browse / intake / hold-safe (`AT1`);
- the learner may submit now but the actual owner act waits for the next business window (`AT2`);
- nearby internal offices share enough context to stay in one packet, but the packet must say who
  acts now and who acts later (`OF1`).

### `BR2` is for real owner-shape or timing divergence

Use `BR2` when co-display can still help orientation, but one lane now needs **its own visibly
distinct owner/timing treatment**.

Typical triggers:

- route and aid lanes now sit with distinct internal office families (`OF2`);
- complaint, regulator, lender, host, or licensure timing depends on a later outside-owner event
  (`OF3`);
- a lane's evidence packet or clock is no longer meaningfully governed by the same office rhythm as
  the route lane.

### `BR3` is for protected, urgent, or authority-breaking divergence

Use `BR3` when one lane would be **misstated by staying operationally inside the shared packet**.

Typical triggers:

- live crisis / urgent support (`AT3`);
- protected support or safeguarding ownership (`OF4`);
- a rights-critical external lane would otherwise read like an appendix to the institution-preferred
  remedy;
- the ordinary packet would make a first-contact surface or route desk look like the owner of a
  separate protected or regulator-facing procedure.

## Starter profiles and their usual child branches

| Starter profile | Usually stays inherited at | Usual child-branch triggers | Common retreat trigger |
|---|---|---|---|
| `DP-HE-TEACHOUT` | `BR0-BR1` for common route continuity facts while route and aid are still moving under clearly published owners | `BR1` when after-hours notices remain visible but actual owner action waits for business hours; `BR2` when aid, complaint, discharge, or regulator timing depends on a different internal or external owner | `BR3` once a protected support lane or rights-critical external lane would be buried inside the ordinary teach-out packet |
| `DP-WF-PUBLIC-ROUTE` | `BR0-BR1` while one public route packet is still mostly orientation plus handback into named owners | `BR1` when intake stays open but funded/support action waits for case-owner windows; `BR2` when benefits-adjacent, sanction, or external-program timing differs from route continuity | `BR3` once crisis, protected support, or authority-sensitive case handling would be miscast as ordinary route navigation |
| `DP-LIB-CIVIC-FIRST` | mostly `BR0` or light `BR1` because the honest job is first-contact orientation, not downstream ownership | `BR1` when the library may collect interest, help book appointments, or explain route families but must still mark that another office acts later | `BR2-BR3` as soon as the packet would make the library look like the owner of aid, complaint, eligibility, sanction, or protected support handling |
| `DP-PRO-LICENSURE` | `BR0-BR1` while educational route and local programme support still share one internal progression shell | `BR2` when completion, host approval, readiness review, or licensure timing shifts to a distinct office family or external board/host | `BR3` once safety/fitness-to-practise or other protected professional-risk handling would be submerged in the educational route packet |
| `DP-PROTECTED-SUPPORT` | almost never below `BR3` for operative details | pointer-only mention may still sit in a shared packet | `BR3` is already the normal posture because the ordinary packet should not become the operative support channel |

## What institutions should now publish

When a split-lane packet inherits a starter profile, publish five extra branch fields beyond the
basic `DL* / LD* / PX*` display shell:

1. the current branch posture (`BR0-BR3`);
2. the after-hours posture (`AT0-AT3`) for each live lane or lane family;
3. the office-family code (`OF0-OF4`) for each lane that no longer shares the ordinary route owner;
4. whether after-hours use is browse-only, intake-only, queue-starting, or live action;
5. if `BR3` applies, the separate notice/channel owner and the reason the lane no longer rides
   inside the ordinary packet.

The archive does **not** require a full procedure manual here. It requires a truthful learner-facing
shell that makes false unity harder.

## Failure modes the archive is now trying to stop

1. **fake-24/7 failure** — the packet is visible all night, so the learner thinks a real decision
   owner is live all night.
2. **one-front-desk failure** — several internal or external owners are visually laundered into one
   apparent front desk.
3. **overnight-waiver failure** — an after-hours click looks like it surrendered a still-live money,
   complaint, or review lane.
4. **crisis-burial failure** — urgent or protected support appears as a sub-row inside an ordinary
   route packet.
5. **appendix-rights failure** — an external complaint, licensure, regulator, or discharge lane is
   technically listed but visually treated as secondary to the institution-preferred path.

## Current archive bet

The archive's current best guess is that **one tiny branch posture layer (`BR0-BR3`) plus a tiny
after-hours layer (`AT0-AT3`) plus a tiny office-family layer (`OF0-OF4`)** is enough to keep the
starter split-lane profiles honest without exploding them into a separate sector manual for every
office.

That claim is now canon, but still live. The archive now answers that next field-level question with
a separate tiny service-truth shell so child branches publish whether they are pointer-only,
browse-only, receipt-only, protection-preserving, or genuinely live, together with the
acknowledgement and action-now posture the learner should rely on; see
[`availability-acknowledgement-and-action-now-fields-for-after-hours-split-lane-branches.md`](availability-acknowledgement-and-action-now-fields-for-after-hours-split-lane-branches.md).
The next narrower question is no longer what an after-hours child branch must minimally say, but
**which of those service-truth defaults can harden across sector profiles and when queue-preserving
or rights-preserving intake must split further by stakes, office family, or protected support
type.**
