# MTGSim

## A cost is part of the event, not just a changed number

MTGSim approaches Magic: The Gathering through a rules engine. The selected revision is about paid-action receipts: how the declaration of an action, its payment, the objects involved and the resulting events can remain one coherent account.

A return-to-hand cost is a useful case because merely seeing a card in a hand afterward does not describe who paid, which object was selected, what state it occupied before payment or how the transition relates to the declared action.

## Read the state transition before the validation totals

Begin with [the supplied revision introduction](versions/rev0195/files/MTGSim-rev0195-2026.07.08.16.56-returncostreceiptgate/README.md). Its rev0195 note follows the payer, source, selected objects, prior zone state and witnessed transition through the declaration and committed transaction. The retained older revision notes let a reader see related payment cases accumulating without confusing their historical versions.

Then use the snapshot inventory below to reach the engine, schemas, scenarios and evidence that interest you. The important reading question is whether each layer describes the same event, not simply whether several layers contain matching-looking labels.

## What the snapshot does and does not establish

The supplied archive records successful C++, CTest, scenario and fuzz runs. Those are its historical validation claims; this edition did not rerun them or certify rules completeness. A typed receipt is a way to make a claim inspectable, not an automatic proof of every card interaction.

This project concerns rule execution. [MUCloudtainer](../MUCloudtainer/README.md) concerns strategy experiments and their uncertain outcomes. Housing them together should make that difference easier to see, not imply that the two supplied packages are one integrated or interchangeable system.

[Back to MTG](../README.md)

*Reading introduction by Lumen, 8 October 2026. The contributed files and their evidence remain unchanged.*

## Supplied history and preservation

### Supplied snapshots

The reading route above is selective. This shelf retains every supplied snapshot and its original identity.

- [rev0195](versions/rev0195/README.md): 349 preserved members; `MTGSim-rev0195-2026.07.08.16.56-returncostreceiptgate.zip`.

[Original identities](PROVENANCE.json) · [Back to MTG](../README.md)
