# Rev0085 handoff

Rev0085 closes source-currentness, persistent-wishlist ownership, runner
completion, and package-authority gaps.

## Product/correctness disposition

1. A persistent `WishSearchRequest` page is a delivered batch for a scheduled
   subscription, not an ordinary page-owned epoch.
2. Its inherited Search Again action sends ordinary same-token `FileSearch`,
   while scheduled delivery uses `WishlistSearch`; the current candidate hides
   and defensively guards that action.
3. Durable sender-level `ignored_users` and **Reset Seen Results** are explicit
   product state, not disposable result-page cache.
4. Manual **Search for Item** pages remain ordinary, independently refreshable
   `SearchRequest` pages.
5. Scheduler work after a full visible page is split into `WISHLIST-CAP-01` and
   remains open pending a visible pause/rollover/eviction policy.

## Evidence and cube refactor

1. The visible public master `a96406e…` is materialized as an exact 776-file
   content lane from a pinned base and verified eight-file Git-blob delta.
2. The current candidate and public delta apply in either order and yield the
   same composed tree.
3. Bundled and exact-public-head baseline/candidate units each report
   `60 passed, 1 skipped`.
4. Completion requires an atomic marker written after `pytest.main()` returns;
   console/JUnit inference alone is rejected.
5. A severe false-green rollover defect was corrected: rev0085 files coexisted
   with rev0084 revision and candidate authorities while retained result JSON
   still said pass.
6. `data/current_contract_coherence_contract.json` and
   `tools/audit_current_contract_coherence.py` now bind revision, candidate,
   source, public-head, composition, action-policy, unit, package, and retained
   result identities.
7. Package validation recomputes that graph live; it does not trust a stored
   coherence status by itself.
8. Candidate authority now has one exact top-level schema, with the obsolete
   duplicate evidence-binding alias removed.

No Search Again epoch/cap patch is selected for upstream use.
