# Python surface — rev0028

New modules:

```text
journallane.py       signed journal frames and crash-cut replay
    JournalFrame
    replay_journal
    JournalReplayPolicy
    JournalReplayReport

generatorfuzz.py     deterministic generated malformed-input corpus
    generate_fuzz_corpus
    assess_generated_fuzz
    GeneratedFuzzReport

refusalschedule.py   refusal-loop evidence joined to next scheduling pressure
    join_refusal_loop_to_schedule
    RefusalScheduleReport

foldspine.py         current-revision audit spine
    audit_fold_spine
```

Primary tests:

```text
tests/test_rev0028_journal_generator_refusal_sam_fold.py
```
