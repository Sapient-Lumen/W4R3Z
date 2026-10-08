# Git provenance coherence refactor — rev0065

rev0065 separates source provenance layers that had become easy to blur:

| layer | rev0065 status | separate from | notes |
|---|---|---|---|
| Source ZIP intake safety | inherited/pass | Git object provenance | rev0064 remains the source path-safety and extraction gate. |
| Git worktree identity | added/pass | source-lane file manifest | Validates `.git` pointer shape, worktree `HEAD`/`ORIG_HEAD`, `commondir`, and reverse `gitdir` pointer. |
| Git ref binding | added/pass | current-web marker snapshots | Validates archived bundled `packed-refs` for tag/branch refs. |
| Commit object provenance | added/pass | report claim capsules | Records commit object type, tree, parent, timestamp, and subject. |
| Git tree file match | added/pass | safe extraction roundtrip | Compares tracked Git blobs to archived source-tree files. |
| Materialized symlink rows | added/classified | non-symlink source drift | Ten Git mode `120000` rows are source-bundle packaging deviations, all outside strict/front touched files. |
| Strict touched-file exactness | added/pass | general tree equivalence | The 15 strict/front touched files match exact Git tree blobs. |
| Fresh current checkout | pending/not performed | archived provenance proof | Still required before live-current external filing. |

The key refactor is that rev0065 no longer treats the uploaded source bundle merely as a ZIP of files. It records a three-part provenance chain:

```text
source ZIP identity -> source lane tree -> bundled Git commit/ref/tree object
```

The symlink materialization exception is intentionally not promoted to a packet and not treated as source drift for the strict/front claims. It is a packaging-shape note for reviewers who compare Git tree objects directly.
