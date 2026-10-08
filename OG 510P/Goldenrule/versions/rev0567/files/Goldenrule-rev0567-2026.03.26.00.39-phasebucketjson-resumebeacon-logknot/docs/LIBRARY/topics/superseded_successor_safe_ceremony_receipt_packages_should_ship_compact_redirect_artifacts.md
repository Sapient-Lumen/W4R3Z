# Superseded successor-safe ceremony receipt packages should ship compact redirect artifacts

Once the archive has package manifests, supersession records, heads, and status cards, there is still one cheap steward question left:

> I landed on an **older package root**. What should I use instead **right now**?

The lineage and supersession records already contain the raw answer, but they make a future steward reconstruct it from several files.

A tiny **package redirect** artifact should collapse that reconstruction into one machine-checkable object:

- the superseded package manifest
- the preferred current package-reference target
- the successor package manifest
- the live status card backing the current package
- the continuity and reason codes from the supersession record
- the current locator-level citation guidance

The redirect should use registered relation semantics instead of archive-local labels:

- `cite-as` for the preferred current package-reference target
- `successor-version` for the successor manifest in the version chain
- `latest-version` for the current authoritative manifest
- `status` for the live package-status-card resource
- `describedby` for the supersession record explaining the replacement

That keeps the archive small while making superseded package roots self-explanatory.
A steward who lands on an old manifest does not need the entire lineage story first; they need one explicit redirect telling them which live package root to trust now and where its current citation posture lives.
