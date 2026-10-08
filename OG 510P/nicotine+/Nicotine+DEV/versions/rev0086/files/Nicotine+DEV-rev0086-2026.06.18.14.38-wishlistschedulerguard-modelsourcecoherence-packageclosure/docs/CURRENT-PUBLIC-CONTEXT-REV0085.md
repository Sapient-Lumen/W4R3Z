# Current public context — rev0085

Observed on 2026-06-18:

- visible public master head: `a96406e7aa285a3fb2a3e35900686d164a22bf02`;
- bundled master base: `f4e17d59783dbc48ea31d2e899a681e2dd1ed500`;
- the public head is six commits and eight changed files ahead of that base;
- all eight old/new file identities are pinned by complete Git blob SHA-1;
- an exact public-head file-content tree is now materialized and executed;
- the public delta and the six-file rev0085 candidate are disjoint and commute.

Exact file content is not described as an independently acquired Git commit
object. The distinction is retained in `data/current_source_contract.json` and
`data/current_public_head_contract.json`.

Public provenance matters to the product interpretation:

- issue #3326 requested Search Again as a refresh of the corresponding search;
- issue #2522 requested durable exclusion of already-seen wishlist results and
  a separate way to clear that state;
- PR #3561 merged the wishlist overhaul on 2026-01-10 and closed #2522 and
  #3170.

Rev0085 makes no novelty claim for Search Again, persistent seen-state, or the
wishlist overhaul. Its contribution is the request-owner split, the
scheduler-at-cap counterexample, exact-head executable closure, and the cube's
source/evidence authority refactor.
