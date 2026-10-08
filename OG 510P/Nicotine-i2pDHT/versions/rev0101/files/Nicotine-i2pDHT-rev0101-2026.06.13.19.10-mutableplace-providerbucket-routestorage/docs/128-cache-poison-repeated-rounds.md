# Cache poison repeated-rounds

rev0015 had explicit lookup transcripts and an aging witness cache. rev0016 joins them across repeated rounds.

A single lookup may show enough late diversity. A single witness-cache summary may show enough signed evidence. But repeated rounds can reveal replay monoculture or a captured fast window that keeps reinforcing the same cache view.

`cachepoison.py` introduces:

```text
CacheRound
CachePoisonPolicy
CachePoisonReport
analyze_cache_poison_rounds()
```

The local decisions are:

```text
accept_stable_diverse_cache
continue_more_rounds
continue_low_witness_diversity
quarantine_contradiction
quarantine_replay_monoculture
quarantine_fast_capture_reinforced
```

The strongest behavior is replay memory:

```text
same transcript digest too often -> quarantine replay monoculture
same cache view with repeated fast-window capture -> quarantine reinforced capture
witness contradiction in any round -> quarantine contradiction
```

This does not make witness evidence true. It only says that local clients and gardens should remember repeated observation shapes, because replay and fast capture are different risks from one bad response.
