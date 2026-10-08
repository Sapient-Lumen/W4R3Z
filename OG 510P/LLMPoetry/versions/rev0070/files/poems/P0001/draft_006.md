# P0001 draft_006 — Glitch States / GLITCH

## Prompt
Make a glitch a state change rather than a decoration. The closed poem must survive alone; the opened poem must return changed.

## Closed state
G4 Glass forgets the hand that cooled it.
L4 Less light arrives than leaves the room.
I4 In the hinge, a small noise learns to stay.
T4 Twice-cut paper remembers neither blade.
C4 Cold margins ask the reader for a pulse.
H4 Here, opening is the damage done.

## Shadow sentence from external apparatus
error is not decoration it is the reader entering the proof through the cut and returning changed again

## Open state generated from branch loss
G4 Glass forgets the hand that cooled it. ⇢ error is not
L4 Less light arrives than leaves the room. ⇢ decoration it is
I4 In the hinge, a small noise learns to stay. ⇢ the reader entering
T4 Twice-cut paper remembers neither blade. ⇢ the proof through
C4 Cold margins ask the reader for a pulse. ⇢ the cut and
H4 Here, opening is the damage done. ⇢ returning changed again

## State-switch pointer
Closed: six selected lines without their rejected endings.
Open `poems/P0001/verification/state_switch_006.json`: the selected lines return with six triplets appended from loss.
Open `poems/P0001/verification/selector_vector_006.json`: exact character spans bind selected lines to those slices.
Open `poems/P0001/branches/branch_packet_006.json`: eighteen omitted branch endings supply the open-state words.
Open `poems/P0001/verification/selector_map_006.json`: the closed-state selected path is anchored by exact text plus character start/end positions.
Glitch is treated as state transition: the closed surface survives, but opening the apparatus changes its tense.

## External apparatus pointer
The residue lattice, selector map, selector vector, loss budget, and state-switch receipt are required parts of this draft object.

## Machine-readable non-claim
This packet validates branch bookkeeping, shadow-word construction, selected-line addressability, selector-vector construction, loss-budget metrics, and state-switch consistency only; it is not a poem-quality claim.

## Disclosure condition
This draft is machine-authored, branch-generated, packet-rendered, and state-switch dependent. Disclosure is the operation that moves the poem from closed to open state.
