# Decisions — rev0168

## D168-01 — treat the public README opening as release-surface custody

**Decision.** The README opening must name the current revision and summarize the actual retained capability stack.

**Why.** For this gift, first-contact legibility is part of the artifact. A stale opening undermines the honest nonclaims even when the code and tests are correct.

## D168-02 — add a regression for stale summary wording

**Decision.** Release-surface tests now check the README opening against the current `REVISION.json` and reject the stale phrases that triggered the polish pass.

**Why.** Documentation drift should fail in the same package QA path as version/root drift.

## D168-03 — make rev0168 a polish revision, not a feature revision

**Decision.** Do not widen schemas, grants, checkpoint authority, scenario state machines, or provider routes in this pass.

**Why.** The artifact was already send-ready except for the cosmetic/coherence issue. A final polish should reduce risk, not add another experimental surface.

## D168-04 — retain prior revision records instead of rewriting them

**Decision.** Add current rev0168 records and leave rev0167/rev0166 records as historical project memory.

**Why.** The release history is evidence. Correcting current pointers should not erase the path that led here.

## D168-05 — keep the scientific claim modest

**Decision.** The rev0168 framing says Lacuna is a runnable, falsifiable instrument for testing retcon planning, not evidence that retcon planning improves fiction.

**Why.** This is the distinction most important to preserve when sending the gift.
