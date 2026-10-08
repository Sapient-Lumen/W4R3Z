# Repair market without authority

`repairmarket.py` uses the word market in the smallest possible sense: gardens publish bounded signed capacity offers, and clients locally select a diverse repair set.

There is no currency, no global reputation ledger, and no authority transfer.  A garden can offer:

- store repair;
- custody audit help;
- route repair;
- seed-gate assistance;
- tombstone repair;
- witness refresh.

The risky cases tested first are:

- valid-looking abundance from one family;
- bad signatures;
- useful refusal that should slow repair traffic rather than trigger floods;
- tombstone repair pressure with no selected tombstone-capable garden;
- capacity selection that accidentally treats supernodes as truth.

The garden-node rule remains unchanged:

```text
gardens give capacity, not truth
```
