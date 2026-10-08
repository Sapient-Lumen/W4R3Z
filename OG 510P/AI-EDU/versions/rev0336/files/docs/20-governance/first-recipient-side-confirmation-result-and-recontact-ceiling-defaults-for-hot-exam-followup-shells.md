# First recipient-side confirmation-result and recontact-ceiling defaults for hot-exam followup shells

The archive already has a very small post-send truth grammar for the hottest exam-like
learner-request routes.

It can now say:

- what concrete request family exists;
- what object that request actually touches;
- what the strongest official effect ceiling is;
- whether the route truthfully publishes ordinary `processing`, `accepted / fulfillable`, `completed
  / reflected`, or `ineligible / no-tracker` state at all;
- whether the ordinary close-out truth is requester-mailed fulfillment, a results letter, online AP
  score-report reflection, or only downstream recipient-confirmation residue;
- what owner-side delivery-evidence token can truthfully travel; and
- when that transfer evidence is still inside a published window, when it has aged into mere
  residue, and when the next honest step is `confirm directly with recipient`.

That is still not enough.

The archive still lacked the next tighter answer: **once the learner has reached the recipient side
at all, what recipient-side result counts as a new ordinary shell fact, when should the learner
simply wait through a local intake or posting window, when may a recipient truthfully direct a
resend/correction or a temporary bridge, and when does repeated contact stop counting as new
proof?**

This document adds one thing only:

- a **tiny recipient-side confirmation-result / recontact-ceiling field set** for those already
  named hot-exam followup shells.

That means the archive now asks a different question than before. It no longer asks only **what send
residue exists and whether direct recipient confirmation is the next ordinary step**. It now asks
**what the recipient side actually says next, whether that next state is confirmed receipt,
still-unconfirmed wait, recipient-directed correction/workaround, or no new proof at all, and where
repeated chase must stop masquerading as fresh evidence**.

## Small field set for recipient-side confirmation-result / recontact-ceiling defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `RC0-NO-UNIVERSAL-RECIPIENT-TRACKER-OR-CHASE-CLOCK` | no one universal recipient-side tracker, posting clock, or chase cadence governs every hot downstream-proof shell | keep recipient followup route-bounded instead of collapsing everything into one `still waiting? click here again` workflow |
| `RC1-PUBLISH-CONFIRMED-RECEIPT-SEPARATELY-FROM-LOCAL-POSTING-OR-CODING` | publish confirmed recipient receipt separately from local posting, coding, or degree-audit reflection when current recipient materials make that separation visible | distinguish `received` from `posted to your account` rather than treating arrival and local coding as the same fact |
| `RC2-PUBLISH-RECIPIENT-WAIT-WINDOWS-FOR-STILL-UNCONFIRMED-OR-STILL-PROCESSING-STATES-WHEN-NAMED` | publish a recipient-side wait window only when current recipient materials actually name one for still-unconfirmed or still-processing states | distinguish `wait through the recipient's stated window` from `follow up now` rather than assuming every unposted score is already overdue |
| `RC3-PUBLISH-RECIPIENT-DIRECTED-RESEND-CORRECTION-OR-TEMPORARY-BRIDGE-ONLY-WHEN-EXPLICITLY-NAMED` | publish resend/correction or temporary bridge steps only when current recipient materials explicitly name them | keep temporary score-copy use, corrected-recipient resends, and office-specific bridge paths smaller than official receipt or posted credit |
| `RC4-TREAT-REPEATED-CHASE-WITHOUT-NEW-RECIPIENT-STATE-AS-NO-NEW-PROOF` | treat repeated calls, emails, or reuse of the same sent-date / delivery-status residue as no new proof unless the recipient provides a new state | stop reminder loops from laundering unchanged uncertainty into fresh confirmation |

## Field values that now travel together

When this layer is used, the shell should publish only four concrete fields:

1. `recipient_confirmation_result` — `confirmed received`, `still unconfirmed / still processing`,
   `temporary bridge accepted`, `corrected send or resend requested`, `no new recipient state`, or
   `not published`;
2. `recipient_wait_or_action_posture` — `posting pending`, `wait through recipient window`, `use
   named temporary bridge`, `correct recipient / resend as directed`, `no further routine chase
   invited`, or `not published`;
3. `recipient_surface` — `student portal or degree audit`, `registrar or admissions office`,
   `placement office`, `College Board resend path`, `not applicable`, or `not published`;
4. `recontact_ceiling` — `repeat contact before a new recipient state adds no new proof`, `same sent
   / delivery residue is still not receipt proof`, `temporary bridge is provisional not official
   receipt`, `resend only on recipient-identified mismatch or missing official report`, `not
   applicable`, or `not published`.

That is deliberately small. It is enough to distinguish confirmed receipt from posted credit, live
recipient-side waiting from actual resend/correction instructions, and a real new recipient-side
state from mere repetition of the same unresolved transfer evidence.

## First recipient-side confirmation-result / recontact-ceiling assignments

| Route or family | Recipient confirmation result now admitted | Recipient wait or action posture now admitted | Recipient surface now admitted | Recontact ceiling now admitted | Why |
|---|---|---|---|---|---|
| ordinary AP ambiguity / error question forms | `not published` | `not published` | `not applicable` | `not applicable` | current ambiguity guidance still exposes a bounded before-score-release reporting route rather than an ordinary recipient-side receipt, posting, or recontact shell the archive can safely harden |
| `SR-WRITE-RHET-01B1` same-device digital or hybrid free-response late-outcome shells where a booklet-copy route exists | `not published` | `not published` | `not applicable` | `not applicable` | current booklet-copy guidance remains requester-facing fulfillment rather than downstream recipient-side confirmation or posting truth |
| paper or hybrid comparator routes where a machine-scored multiple-choice answer sheet exists | `not published` | `not published` | `not applicable` | `not applicable` | current paper multiple-choice rescore guidance still closes through a requester-facing results letter, not recipient-side posting or chase truth |
| score-send or withhold-linked recipient routes once the recipient confirms the official report reached the office but says coding/posting may take additional time | `confirmed received` | `posting pending` | `student portal or degree audit` or `registrar or admissions office` | `repeat contact before a new recipient state adds no new proof` | current recipient materials now make a thin but real distinction visible between office receipt and later coding/posting to the student's account or transcript |
| score-send recipient routes where the recipient instead publishes a local intake / processing window or says the score may not yet be visible | `still unconfirmed / still processing` | `wait through recipient window` | `student portal or degree audit` or `registrar or admissions office` | `same sent / delivery residue is still not receipt proof` | current recipient pages now make local processing windows real enough that the archive can publish `wait` without pretending that College Board sent dates or delivery-status views prove recipient-side completion |
| prerequisite-sensitive score routes where the recipient names a corrected-send path or accepts a temporary score-copy bridge while official transmission is still in flight | `temporary bridge accepted` or `corrected send or resend requested` | `use named temporary bridge` or `correct recipient / resend as directed` | `placement office` or `College Board resend path` | `temporary bridge is provisional not official receipt` and `resend only on recipient-identified mismatch or missing official report` | current recipient guidance now makes two exceptional but public next steps visible: some offices name a wrong-recipient / resend correction path, while some prerequisite-sensitive offices accept a bounded temporary bridge that does not equal official receipt or posted credit |
| already-contacted recipient routes where no new recipient-side state is provided and the learner only repeats the same reminder or the same owner-side send residue | `no new recipient state` | `no further routine chase invited` | `registrar or admissions office` | `repeat contact before a new recipient state adds no new proof` | current AP and recipient materials now make it visible enough that unchanged owner-side sent/delivery residue never upgrades itself into recipient proof, and some recipients explicitly say delay alone does not require new calls or emails |
| `SR-WRITE-RHET-01B2` AP Capstone performance-task / local-record branches beyond whole-score withhold/cancel control | `not published` | `not published` | `not applicable` | `not applicable` | current AP Capstone performance-task and local-record branches still expose local retention, authenticity, and owner-initiated review rather than an ordinary recipient-side score-posting shell the archive can safely harden |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | `not published` | `not published` | `not applicable` | `not applicable` | current reading-access and ELP-validity regimes still vary too much by state, content area, accommodation route, and local review structure for one shared recipient-side confirmation-result shell to travel honestly |

## `RC1` — confirmed receipt is smaller than posted credit

`RC1-PUBLISH-CONFIRMED-RECEIPT-SEPARATELY-FROM-LOCAL-POSTING-OR-CODING` is the archive's smallest
anti-fake-completion rule for the recipient side.

Current recipient materials already make the distinction visible:

- some institutions say official AP scores may be received while credit coding still takes several
  weeks;
- some tell students to confirm official receipt with the registrar if the credit is not yet visible
  on the account; and
- some say the equivalency appears only after later transcript or portal posting.

That is enough for one tiny recipient-result field. It is not enough for the archive to pretend
`received`, `matched`, `coded`, and `visible to the learner` are one universal state.

## `RC2` — recipient windows govern still-unconfirmed or still-processing states

`RC2-PUBLISH-RECIPIENT-WAIT-WINDOWS-FOR-STILL-UNCONFIRMED-OR-STILL-PROCESSING-STATES-WHEN-NAMED` is
the archive's smallest anti-false-overdue rule once the learner has crossed to the recipient side.

Current recipient materials already publish local wait signals such as:

- AP scores may not even be scheduled to arrive until July;
- large summer volumes can mean 2–3 weeks or several weeks before scores are processed or posted
  locally; and
- some institutions say students will not be penalized for the ordinary AP timing lag and do not
  need to notify the office just because the score is still in transit.

That is enough for one tiny wait-window posture. It is not enough for one universal chase clock.

## `RC3` — resend, correction, or temporary bridge only when the recipient names it

`RC3-PUBLISH-RECIPIENT-DIRECTED-RESEND-CORRECTION-OR-TEMPORARY-BRIDGE-ONLY-WHEN-EXPLICITLY-NAMED` is
the archive's smallest anti-fake-workaround rule.

Current recipient materials already make two bounded exceptions visible:

- some recipient pages say a wrong school code or mismatched score routing requires a corrected send
  or another College Board order; and
- some prerequisite-sensitive offices say an unofficial AP score copy may be used as a temporary
  bridge for placement while the official transmission is still being processed.

That is enough for one tiny exceptional-action field. It is not enough for the archive to pretend
every delayed score authorizes a generic unofficial workaround or a generic resend.

## `RC4` — repeated chase without a new recipient state is not new proof

`RC4-TREAT-REPEATED-CHASE-WITHOUT-NEW-RECIPIENT-STATE-AS-NO-NEW-PROOF` is the archive's smallest
anti-loop rule for these shells.

Current official materials already keep three boundaries visible at once:

- College Board's sent dates and delivery-status views still do not prove recipient-side arrival or
  processing;
- some recipient pages explicitly tell students to wait through local processing windows or say they
  do not need another email/call merely because AP score timing is delayed; and
- if no recipient-side state has changed, another reminder does not itself become a new confirmation
  token.

So the archive now treats repeated chase as operational followup only, not as fresh proof, unless
the recipient supplies a new result such as confirmed receipt, a named local delay state, a resend
direction, or a temporary bridge.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these hot followup shells, it should now
add only the following where truthful:

1. whether the recipient side has actually confirmed receipt, is still unconfirmed or still
   processing, has named a temporary bridge/correction path, or has supplied no new state;
2. whether the next ordinary step is to wait, to look for local posting, to use a named temporary
   bridge, or to correct/resend through the named path;
3. which recipient-side surface owns that next step; and
4. what the recontact ceiling is, including when repeated reminders no longer count as new proof.

That is enough to make recipient-side followup legible without inventing one universal recipient
tracker.

## What counted as a real archive gain

The archive already knew what downstream evidence existed, how old it was, and when the next
ordinary step had become `confirm directly with recipient`. It still lacked the next tighter answer:
**what the recipient side actually says after that and when repeated followup should stop pretending
to be new evidence**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- confirmed receipt from posted credit;
- live recipient wait windows from actual resend/correction instructions;
- bounded temporary bridges from official receipt; and
- real new recipient-side states from reminder loops that add no new proof.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every delayed score as already overdue;
- treating every recipient acknowledgment as if credit were already posted;
- treating every late score as if unofficial workaround or resend were automatically allowed; and
- treating repeated contact as if it were itself a growing proof trail.
