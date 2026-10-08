# Scenario — same-lane imports share a single session family

A pack can join several imported receipts without pretending they came from unrelated review moments.
This scenario keeps that join honest:

- one reviewed lane imports several artifacts,
- the imported artifacts either share one native Cargo session id or stay within one explicit capture family,
- and the summary is allowed to speak about the lane as one coherent review moment.

That way the pack can say more than "these receipts exist"; it can also say why they are safe to read as one lane-level witness family.
