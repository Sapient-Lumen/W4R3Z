# Resilio downstream-materialization, compensation, and unwind fragmentation evaluation

## What current Resilio gets right

Current official Resilio docs are candid that `decision approved`, `folder visible`, `placeholder present`, `RW permission granted`, `linked-device arrival`, `delete propagated`, `disconnect performed`, and `bytes still present elsewhere` are not one flat aftermath truth.
That honesty is genuinely useful.

The most valuable ingredients from the present contract are:

- linked devices can make folders automatically available everywhere under one identity
- synchronization modes distinguish visible/disconnected state from placeholder state and from full local materialization
- read-write peers can modify or remove files and those changes synchronize to connected devices
- revoking or disconnecting stops future updates but does not claw back already synchronized files
- backup and encrypted-node guides openly admit durable byte survival on other devices even when the source side changes or disappears
- local shares, archive behavior, and reconnect rules admit that one accepted state can create several later state-carrying surfaces

## Where the current contract still fragments

The problem is not that Resilio hides consequences.
The problem is that it exposes the relevant clues across too many places and still does not own the decisive question:

> what has this sentence version already changed in the world, what can still be halted, and what now requires compensation rather than simple rollback?

Today the operator can often infer only weaker facts such as:

- some device automatically received access or visibility
- some peer may already hold bytes or placeholders
- some read-write peer may have propagated a deletion or mutation
- some disconnected or revoked peer still keeps previously synchronized files
- some backup or encrypted node may still carry durable copies
- some local-share or reconnect path may preserve or recreate state under a new path

Those are helpful evidence inputs.
They are not a first-class downstream-consequence contract.

## Why that matters for AnonSync

AnonSync is trying to make stronger semantic claims than `it was used` or `the current sentence was visible`.
It needs to support claims such as:

- this sentence version was used for review, but no downstream mutation fired
- this sentence version launched a reversible filesystem mutation on cohort A only
- this sentence version triggered multi-device propagation, but the resulting world change can still be halted before public release
- this sentence version already produced irreversible external residue on cohort C and now needs compensation rather than naive rollback
- this sentence version was rolled back, but encrypted, backup, disconnected, or previously synced surfaces still carry world residue that must be acknowledged

Resilio gives clues for these judgments.
It does not provide the judgment object itself.

## Non-clone conclusion

So the line stays hard:

- borrow Resilio's candor about automatic linked-device arrival, visibility-vs-materialization modes, change propagation, durable byte survival, and non-clawback revocation
- do not clone a model where downstream mutation, haltability, compensation debt, and surviving residue still have to be reconstructed from scattered help pages and operational traces

AnonSync should therefore own a dedicated page family for downstream consequences rather than treating `decision-used` as the end of the story.
