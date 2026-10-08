# Commitment stages and breach semantics are world contracts, not preplay flavor

Recent work adds a missing layer to Concord's future cooperation worlds: **words can change the institution before any action is taken**.

- `RS-GR-172` shows that non-binding public pledges are not generically helpful; they raise cooperation only when others have reason to believe the pledger is trustworthy.
- `RS-GR-173` shows that joint commitment can change how third parties score the very same cooperative and defective actions, because cooperation is judged relative to whether a commitment existed.
- `RS-GR-175` shows that actively making a promise can raise the moral cost of later dishonesty, while passive or merely ambient trust cues do not do the same work.

## Why this matters for Concord

A world with a pledge stage, vow stage, or commitment handshake is not the same world with a little extra chat.

There is a real institutional difference between:
1. no preplay commitment at all;
2. non-binding public pledges;
3. private or bilateral commitments;
4. commitments whose breach changes reputation scoring or sanction logic.

Those choices do not merely change dialogue style.
They change what counts as justified defection, what observers think was owed, and whether "cooperation" comes from action policy or from a promise-backed expectation structure.

## Minimal implementor handoff

If Concord adds promises, pledges, vows, or commitment handshakes, publish at least:

1. whether commitments exist before action and who may issue or accept them;
2. whether they are public, private, bilateral, group-wide, optional, or mandatory;
3. whether they are binding, merely expressive, or indirectly enforced through reputation or sanction;
4. whether observers score later actions relative to the commitment state;
5. whether breach is tracked separately from ordinary defection.

Without that compact contract, future inheritors can mistake commitment-enabled cooperation for generic Golden-Rule conduct.
