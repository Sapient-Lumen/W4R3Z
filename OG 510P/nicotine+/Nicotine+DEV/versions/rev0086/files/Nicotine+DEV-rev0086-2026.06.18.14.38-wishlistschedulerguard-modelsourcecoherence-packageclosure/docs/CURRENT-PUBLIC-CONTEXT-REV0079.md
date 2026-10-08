# Current public context — rev0079

Captured on 2026-06-18.

## Source state

Public `master` visibly remains at `a96406e7aa285a3fb2a3e35900686d164a22bf02`, dated 2026-06-15. The bundled executable proxy is `f4e17d59783dbc48ea31d2e899a681e2dd1ed500`, dated 2026-06-12. The intervening visible changes do not alter the search, GUI, queue, or server-output flow relied on here.

References:

- <https://github.com/nicotine-plus/nicotine-plus/commits/master/>
- <https://github.com/nicotine-plus/nicotine-plus/compare/f4e17d59783dbc48ea31d2e899a681e2dd1ed500...a96406e7aa285a3fb2a3e35900686d164a22bf02>
- <https://github.com/nicotine-plus/nicotine-plus/blob/master/pynicotine/search.py>
- <https://github.com/nicotine-plus/nicotine-plus/blob/master/pynicotine/slskproto.py>

Executable claims remain scoped to the bundled proxy. Public-head statements are relevant-flow review rather than whole-tree execution.

## Public overlap

Issue #3326 asked for Search Again as a refresh and was closed under milestone 3.4.0. The broad fresh-token direction is public prior discussion. Rev0079 makes no novelty claim for it.

Reference: <https://github.com/nicotine-plus/nicotine-plus/issues/3326>

The narrower rev0079 work is a failure-atomic local-publication model: complete per-recipient fan-out, prepacking, explicit success/rejection, generation-tagged acknowledgement, and the residual post-ack disconnect policy.

## Contribution boundary

Nicotine+ permits AI tooling for learning and guided codebase research but disallows generated or AI-coauthored contribution content. Every generated test, model, script, patch, and document in this cube remains research-only.

Reference: <https://github.com/nicotine-plus/nicotine-plus/blob/master/CONTRIBUTING.md>
