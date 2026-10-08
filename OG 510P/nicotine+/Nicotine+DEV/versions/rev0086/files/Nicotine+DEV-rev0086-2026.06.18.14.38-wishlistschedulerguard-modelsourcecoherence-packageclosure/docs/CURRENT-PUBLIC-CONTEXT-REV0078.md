# Current public context — rev0078

Captured on 2026-06-18.

## Source state

Public `master` visibly points to `a96406e7aa285a3fb2a3e35900686d164a22bf02`, committed on 2026-06-15. The bundled executable proxy is `f4e17d59783dbc48ea31d2e899a681e2dd1ed500` from 2026-06-12. GitHub's comparison reports six commits and eight changed files between them. The visible intervening commits concern contributor/website links, translation, and a Windows PangoCairo setting; current public `search.py`, `gtkgui/search.py`, and `slskproto.py` retain the relevant flow reviewed here.

References:

- <https://github.com/nicotine-plus/nicotine-plus/commits/master/>
- <https://github.com/nicotine-plus/nicotine-plus/compare/f4e17d59783dbc48ea31d2e899a681e2dd1ed500...a96406e7aa285a3fb2a3e35900686d164a22bf02>
- <https://github.com/nicotine-plus/nicotine-plus/blob/master/pynicotine/search.py>
- <https://github.com/nicotine-plus/nicotine-plus/blob/master/pynicotine/gtkgui/search.py>
- <https://github.com/nicotine-plus/nicotine-plus/blob/master/pynicotine/slskproto.py>

This does not convert the proxy into an exact whole-tree checkout of public head. Executable results remain scoped to `f4e17d5…`; public-head statements are relevant-flow review.

## Public overlap

Issue #3326 requested Search Again as a refresh and was closed under milestone 3.4.0. Search indexing exposes a maintainer response explaining that a real repeat requires removal and a different token so peers send results again. The broad fresh-token requirement is therefore public prior discussion, not a cube novelty claim.

Reference: <https://github.com/nicotine-plus/nicotine-plus/issues/3326>

Rev0078 narrows its claim to a source-backed owner map and executable countermodels for partial re-keying, late responses, page closure, network-control lag, publication rejection, and buddy-recipient policy.

## Contribution boundary

Nicotine+ permits AI tools for learning and guided codebase research but excludes generated or AI-coauthored contribution content. Every generated model, test, script, and document in this cube remains research-only.

Reference: <https://github.com/nicotine-plus/nicotine-plus/blob/master/CONTRIBUTING.md>

## Queue lifecycle boundary

Current source routes control and ordinary network messages through the same `queue-network-message` callback. The callback has no rejection result while disabled. Disconnect handling disables and drains that queue and separately clears allowed message responses. Rev0078 therefore distinguishes enqueue acceptance from network application; this is a source-flow observation, not a claim that user-visible loss is always reachable.
