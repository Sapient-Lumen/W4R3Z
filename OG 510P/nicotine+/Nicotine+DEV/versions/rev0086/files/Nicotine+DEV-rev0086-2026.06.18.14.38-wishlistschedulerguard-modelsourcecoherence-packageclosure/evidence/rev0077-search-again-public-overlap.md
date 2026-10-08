# rev0077 Search Again public-overlap review

Observed on 2026-06-18.

## Found

- Public issue #3326 requests a Search Again command and describes it as refreshing the respective search.
- The issue is closed under milestone 3.4.0.
- Discussion visible through search results recognizes that a different token may be needed for a true new search rather than simply reusing the old request identity.
- Current public raw master still records `self.token` in `_own_tokens` while sending `search.token`.

## Not found in the bounded search

No obvious public issue or pull request was found that names the exact interleaving:

```text
older self-user tab token A
newer allocator token B
Search Again sends A
_own_tokens records B
incoming A is suppressed
```

This is not a novelty claim. Search indexing is incomplete, closed/private security reports are not visible, and differently worded reports may exist.

## Routing conclusion

The demonstrated result is ordinary low-severity correctness. It should not be presented as a security vulnerability on current evidence. In addition, Nicotine+ contribution policy prohibits generated contribution material, so this cube contains research evidence only—not issue text, pull-request text, or a contribution-ready patch.
