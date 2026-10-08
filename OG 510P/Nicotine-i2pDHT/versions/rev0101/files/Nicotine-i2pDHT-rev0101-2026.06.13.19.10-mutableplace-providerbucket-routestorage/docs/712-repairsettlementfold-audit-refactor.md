# repairsettlementfold audit/refactor

`repairsettlementfold.py` is the rev0067 current-path fold audit.

It checks that these active surfaces are visible and needle-pinned:

```text
repairsettlement
closurearchive
repairprune
repairsettlementfold
```

It also preserves rev0066 `repairpublishfold` as predecessor history. The audit/refactor goal is to prevent the new settlement/archive/prune lane from becoming detached from the previous repair-publish/ACK/duplicate-closure lane.
