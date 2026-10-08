# rev0047 policyportfolio/publicationguard branchfold

This sibling rev0047 path pins the policy-source portfolio and publication-guard lane beside the appeal/publication/quench path. The design question is whether a public bridge side effect can become sticky because one local policy source, one bridge ledger, or one publication capsule looked valid in isolation.

Risk-first additions:

- `policyportfolio.py` treats subjective policy as a source portfolio, not a singleton authority.
- `publicationguard.py` gates public-bridge publication capsules against bridge ledger, policy portfolio, egress, exact scope/request, exposure class, TTL, replay, forks, and family/path diversity.
- `publicationfold.py` keeps this policy/publication path visible while the richer appeal/publication/quench path is also active.

Strong rule: public publication is not permission just because a bridge ledger passed.
