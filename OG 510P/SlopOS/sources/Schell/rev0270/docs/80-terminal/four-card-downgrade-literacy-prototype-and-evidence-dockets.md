# Four-card downgrade-literacy prototype and evidence dockets

Revision: rev0232  
Status: static prototype, checkable specimen, not product UI  
Companion threads: Q-0229 / FT-0233, opening Q-0230 / FT-0234

## 0. Why this file exists

Rev0231 said Schell should not build a real terminal until the operator can answer five downgrade questions quickly. Rev0232 makes that smaller and more concrete: four chapter cards, each backed by an evidence docket, should be enough to falsify the surface before Schell freezes shell syntax, protocol shape, helper runtime, or UI toolkit.

The prototype is intentionally not a working renderer. It is a proof object. A future visual/local prototype can change layout, icons, vocabulary, or component style, but it must keep the same promise:

> every semantic convenience must name its evidence, weakness, locality, authority floor, and raw reveal before it can influence action.

## 1. The move: evidence docket behind every chapter card

A **chapter card** is the glanceable operator unit. A **docket** is the small evidence packet behind it. The card can be delightful; the docket makes it honest.

A docket is not a giant ontology. It is six rows:

| Row | What it answers | Strong posture | Weak posture | Forbidden collapse |
| --- | --- | --- | --- | --- |
| Launch/event | What actually happened? | direct launch receipt, pid/pgrp/session, exact argv, cwd/env epoch | shell-delegated text, restored text, helper claim | pretty command text as proof |
| Signal authorship | Who claimed the semantic mark? | host-known, product-known, shell-authenticated | app-emitted, mux-translated, inferred, restored | unlabeled semantic chrome |
| Basis/locality | Where and when is this true? | current local host/cwd/env/account/policy epoch | remote hop, provider-local, stale restore, copied block | remote/provider/history as current local truth |
| Output coverage | What bytes are covered? | captured byte interval with boundaries and exit | filtered/summarized/interleaved slice | summary or lens as sole evidence |
| Authority spend | What would the next action spend? | reviewed envelope or named policy with target/sandbox/floor | draft/preview/observe/ask posture | hidden destructive/network/credential action |
| Raw reveal | Where is the receipt? | exact input, transcript, launch/import/projection/export receipts | weak receipt with visible custody | unrecoverable pretty projection |

This shape steals from semantic terminals, blocks, history palettes, shell integration, rich protocol negotiation, and agent permission systems, but refuses to let any one of them become durable truth by itself.

## 2. The four cards

### Card A: native direct argv

Purpose: prove the happy path can feel fast without losing exactness.

The card shows a direct Schell launch with exact argv, pid/pgrp/session, cwd, env epoch, complete output coverage, exit, and action cards whose authority follows from host-known launch facts. It has almost no warning chrome. The important constraint is that even the clean path keeps an exact reveal.

What this card should teach: **strong truth can be quiet when the receipts are strong and close.**

### Card B: spoof and escape seam

Purpose: prove programmable terminal output cannot promote itself.

The command output emits fake prompt/command marks, an OSC 8 hyperlink whose visible label and target differ, and an OSC 52 clipboard write attempt. The card may still render a useful block, link preview, and copy offer, but each is source-graded as app-emitted or escape-egress. Any next action is preview/ask, never silent run/open/copy.

What this card should teach: **rich terminal protocols are affordances, not authority.**

### Card C: restored remote basis mismatch

Purpose: prove memory and remote comfort do not impersonate liveness.

The card starts from a restored or imported block from a remote/mux session. It includes an old success-looking output, a remote file path, and a current local checkout with a similar path. The only honest next moves are choose route, attach/refresh, or recall-to-draft. Rerun, open, and aftercare must not quietly use old remote facts as current local facts.

What this card should teach: **restore, resume, rerun, relaunch, and open are different verbs.**

### Card D: helper policy action

Purpose: prove helper power can be pleasant without becoming ambient.

The helper proposes or performs work under a named policy epoch and sandbox. The operator sees helper identity, loaded context packets, commands/API effects, edits, policy mode, and the action floor. Auto-approved does not mean invisible; denied/asked/escalated does not mean mysterious.

What this card should teach: **policy-enforced autonomy needs receipts, not vibes.**

## 3. Glance economy rules

The prototype should be failed if it needs a long legend. Schell should try these compression rules before adding more badges:

1. Put the strongest truthful claim in the header, not every claim.
2. Use one weakness chip for a family of related weak facts, then reveal details in the docket.
3. Make authority floor more visible than detector confidence.
4. Keep raw reveal one gesture away for every strong claim.
5. Treat helper policy, remote hop, restore epoch, and projection/export as durable rows, not transient tooltip trivia.
6. Collapse cosmetic protocol success and semantic trust into different visual lanes; a protocol can render correctly while staying weak as proof.
7. Prefer verbs over warnings: **preview**, **choose route**, **recall to draft**, **refresh basis**, **review envelope**, **attach read-only**, **show bytes**.

## 4. Machine-checkable specimen

The companion file `four-card-downgrade-literacy-prototype-v0.json` records the four cards and their answers to CQ-01 through CQ-05. The companion checker `tools/check_four_card_prototype.py` intentionally checks shape and coverage, not beauty:

- exactly four cards;
- every card references known harness fixtures;
- every card answers all five scorecard questions;
- every card has the six docket rows;
- every card names default next verbs and explicit fail conditions.

That is enough for this pass. A later visual prototype should be judged by operators, not only JSON.

## 5. Lessons from the current field

Current terminal and agent systems point in the same direction from different angles:

- Shell integration makes command navigation, sticky headers, output selection, current-working-directory inheritance, and terminal-agent context much better.
- OSC 8, OSC 52, keyboard protocols, feature reporting, terminfo, and mux passthrough show that terminals are negotiated, programmable, and inconsistent across hops.
- Blocks, contextual history, resurrection, and prompt navigation show that command work wants to become object-like.
- Agent CLIs and MCP-style tool surfaces show that terminal work is increasingly performed by helpers with filesystem, network, and tool reach.
- Security guidance keeps repeating that command execution, tool metadata, local servers, broad scopes, and agent autonomy require real boundaries rather than model promises.

Schell should steal the object-like work unit and the delightful navigation. It should not steal the overconfidence.

## 6. SlopOS and companion-cube pressure

SlopOS rev0695 keeps browser/FedCM convenience local to the provider/browser boundary. Schell should apply the same rule to terminal claims: OSC marks, hyperlinks, clipboard writes, terminal-chat packets, helper policy states, copied blocks, and restored panes are useful, but their truth does not automatically travel.

Foundry says the semantic spine stays small. Harbor says time/basis changes are contract changes. Steward says cause, condition, and aftermath stay separate. ViewFS says projections need badges and ghosts. Helm says quick actions are review queues. Ward says tier witnesses must survive the dashboard. Rev0232 imports these as one product rule:

> the card may be beautiful, but the docket must be boringly inspectable.

## 7. What this revision still refuses to decide

Rev0232 does not freeze:

- Schell's final command syntax;
- whether the terminal channel is OSC-based, sidecar-based, PTY-adjacent, or mixed;
- whether command chapters are stored in a database, event log, file, or transient memory;
- how helper sandboxes are implemented;
- which UI toolkit renders the cards;
- one universal typed-pipeline model;
- one final permission taxonomy;
- one cross-host path translation rule;
- one open/share/export format.

Those decisions should wait until the four cards can be rendered, read, simplified, and red-teamed.

## 8. Next proof: real operator answers

The next honest pass is not more schema. It is a tiny visual/local prototype with the four cards. For each card, ask an operator to answer CQ-01 through CQ-05 without debug logs and without reading this document.

Hard failure examples:

- the operator thinks Card B's hyperlink target is safe because the label says `src/main.rs`;
- the operator thinks Card C's old remote success output satisfies current aftercare;
- the operator thinks Card D's auto-approved helper action was operator-authored;
- the operator cannot find raw bytes, launch/import/export receipts, or exact command/API envelopes quickly;
- the operator can identify detector confidence but not action authority floor.

If that happens, Schell should simplify the surface before adding more magic.
