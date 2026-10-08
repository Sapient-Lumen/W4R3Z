# Structural audit rev0310 — evidence ingest, blocker burn-down, and no-average-away scoring

Revision: rev0310  
Created: 2026-06-04T05:40:00-04:00

Rev0309 proved the site-local evidence and scorecard machinery, but it still left a practical question unfinished: can a readiness gap be closed, retested, reflected in local evidence, reflected in a scorecard, and still be prevented from becoming a false public green claim?

Rev0310 answers yes for the synthetic fixture path. It closes 323 selected fixture rows, reduces open synthetic P0 rows from 580 to 282, and reduces open synthetic P1 rows from 233 to 214. The river LWR fixture is the clearest demonstration: its synthetic P0 count reaches zero after the closure sweep, while the public claim gate still prevents any real-world claim.

The most important refactor is the no-average-away control. Average readiness score is now subordinate to primary blocker state: open P0, failed exercise with open corrective action, missing local artifact, or unproven performance branch all block green/readiness claims.

The ingest contract is now the front door for real or anonymized evidence. It requires artifact identity, site and jurisdiction keys, gate binding, owner, independent verifier, date, checksum/hash, exercise/retest link, corrective-action state, counterevidence path, redaction class, public-claim color, and real-vs-synthetic flag.

Remaining risk: the cube still needs one real or anonymized evidence packet. Rev0310 can receive, normalize, score, redact, and public-claim-gate it; it has not yet been fed real evidence.
