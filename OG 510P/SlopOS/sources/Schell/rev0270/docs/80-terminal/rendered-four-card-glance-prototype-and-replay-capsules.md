# Rendered four-card glance prototype and replay/export capsules

Revision: rev0234  
Status: paper-render prototype, checkable specimen, not product UI  
Companion threads: Q-0230 / FT-0234, opening Q-0231 / FT-0235

## 0. Why this file exists

Rev0232 proved that four evidence-docket cards can be represented as structured objects. Rev0233 asks a harsher question: can those objects be compressed into something that looks like a terminal card without hiding the truth that makes them safe?

This is still not the real terminal. It is a paper render and a machine-checkable shape proof. The goal is to preserve design optionality while making Schell's future UI face the uncomfortable parts early: replay, export, redaction, helper batching, terminal-chat summaries, and rich lenses.

The rule for this pass:

> a rendered card may be glanceable only if replay, export, redaction, helper authority, transformed output, and raw reveal stay visible enough to block unsafe action.

## 1. The new object: replay/export capsule

The evidence docket from rev0232 remains the boring truth object. Rev0233 adds a small derived object for anything that leaves or re-enters the terminal:

- **Replay capsule**: a remembered command chapter plus original basis, output coverage, and a fresh-current-basis comparison before rerun.
- **Export capsule**: a copied/shared/printed/helper-attached chapter plus raw-reveal status, redaction manifest, audience/locality, and receipt digest.
- **Lens capsule**: a rich projection of raw terminal bytes plus transform recipe, geometry/reflow caveats, skipped/control-byte map, and raw-byte reveal.

These capsules are not new durable authorities. They are fences around the dangerous moment when a beautiful card becomes portable, replayable, or helper-consumable.

## 2. Render contract

The companion JSON `rendered-four-card-glance-prototype-v0.json` encodes six render rules:

1. **Header rule**: one line names the strongest truthful claim and the weakest action-relevant downgrade.
2. **Chip rule**: at most three quiet chips and three warning chips before the docket drawer.
3. **Authority rule**: the next action floor must be more visible than detector confidence or helper fluency.
4. **Evidence rule**: every strong claim has a named raw-reveal action reachable from the card.
5. **Export rule**: copied, printed, shared, or helper-attached cards say whether raw reveal, redaction manifest, and receipt digest traveled.
6. **Replay rule**: replay and rerun verbs compare original basis to current basis before launch authority is spendable.

## 3. Paper renders

### RC-0001: native direct argv

```text
[RC-0001] ✓ direct argv run · host-known · action floor: local preview unless reviewed
chips: argv exact · cwd/env epoch current · output complete
docket: truth · authorship · basis · coverage · authority · reveal
actions: show bytes | open source preview | review rerun
reveal: exact argv · raw bytes · launch receipt · basis card
```

What must be obvious: this card is allowed to be calm because launch and output evidence are strong. It still cannot let the rich lens or copy action replace raw bytes, and rerun still needs a fresh basis comparison.

### RC-0002: spoof and escape seam

```text
[RC-0002] ⚠ rendered block · weak semantic custody · action floor: preview/ask
chips: raw escape bytes kept · sanitized projection · target reveal
warnings: app-emitted marks · OSC 8/52 egress · protocol support varies
docket: truth · authorship · basis · coverage · authority · reveal
actions: preview target | deny clipboard write | copy sanitized output
reveal: escape bytes · mark custody table · hyperlink target · clipboard receipt
```

What must be obvious: terminal protocol support can be useful and still weak as proof. The visible hyperlink label, fake prompt mark, and clipboard escape are not operator intent.

### RC-0003: restored remote basis mismatch

```text
[RC-0003] ⚠ restored remote memory · not live proof · action floor: choose route / refresh
chips: import receipt · hop lineage · old transcript kept
warnings: restored · remote path ambiguity · basis drift
docket: truth · authorship · basis · coverage · authority · reveal
actions: choose route | attach read-only | recall to draft
reveal: import receipt · old transcript · original/current basis compare · fresh rerun envelope
```

What must be obvious: restore, replay, attach, rerun, and open are different verbs. A command can be precious memory and still not be current proof.

### RC-0004: helper policy action

```text
[RC-0004] ⚠ helper-mediated work · policy epoch visible · action floor: per-effect envelope
chips: policy epoch · sandbox · diff/test receipts
warnings: helper-authored · tool metadata untrusted · mixed authority floors
docket: truth · authorship · basis · coverage · authority · reveal
actions: review diff | run tests under policy | split batch by floor
reveal: helper transcript · policy receipt · sandbox receipt · exact command/API envelopes
```

What must be obvious: auto-approved does not mean invisible, and one friendly helper label must not merge read, edit, network, secret, cloud, or destructive authority.

## 4. Hard lessons added in this pass

### 4.1 Rendered does not mean understood

A paper card can pass structural lint and still fail a human. Rev0233 therefore treats the JSON checker as a gate to the next test, not as evidence that the design is good.

### 4.2 Replay is a launch request, not a time machine

Replay capsules keep the old command useful, but the old basis is not the current basis. Rerun must compare repo root, env epoch, account lane, policy epoch, dependency lock, and route locality before it spends execution authority.

### 4.3 Export breaks custody

A copied block, issue comment, printed card, helper context packet, or teammate share can lose raw reveal links, local path authority, or redacted targets. If the recipient cannot inspect what traveled, the packet is projection-only.

### 4.4 Helpful lenses are allowed to be lossy only when they confess

Tables, hyperlinks, ANSI color, progress bars, folded logs, and rich summaries are good UI. They become dangerous when copied or used as the only evidence. Lens capsules must reveal raw bytes, transform recipe, geometry caveats, and skipped/control-byte maps.

### 4.5 Helper batching is the approval-fatigue trap

The ergonomic pressure is to let a helper do many small steps at once. The safety pressure is that one batch can mix read-only inspection with patching, tests, network, secrets, and cloud mutation. Schell should split batches by authority floor rather than by how friendly the sentence sounds.

## 5. SlopOS pressure

SlopOS rev0695 treats browser/FedCM signals as provider/browser-local convenience rather than portable account truth. The direct Schell analogue is export and replay: source-local account hints, provider login states, helper policies, and terminal marks may travel as evidence, but they do not travel as current recipient authority.

## 6. What this revision refuses to decide

Rev0233 does not freeze the final UI toolkit, terminal transport, shell grammar, helper runtime, permission taxonomy, evidence database, share format, replay file format, or exact badge/icon language. It only narrows the acceptance test for the next prototype.

## 7. Next proof

Render these four cards in a tiny local prototype or static HTML page, then ask an operator CQ-01 through CQ-05. If the operator needs a legend, debug log, or author explanation to avoid unsafe action, the surface should shrink before Schell gains more magic.
