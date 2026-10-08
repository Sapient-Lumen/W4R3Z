# Research — rev0169

## Research question

Can the gift recipient run Lacuna's acceptance checks without encountering an ambiguous monolithic test hang, and can scenario experiments refuse unedited generated templates before they create apparently valid runs?

## Result in this revision

Operationally, yes. Rev0169 converts the risky close-time SQLite cleanup from a blocking truncating WAL checkpoint to bounded passive cleanup, adds a per-module acceptance runner, and makes generated scenario capsules fail closed until placeholder player inputs and model-policy placeholders are replaced.

## Why this matters for the Gwern gift

Gwern's likely first filter is whether the artifact's own custody claims are falsifiable and mechanically checkable. A release that says “pass” while the documented command hangs creates a trust failure before the retcon-planning idea is even evaluated. Rev0169 narrows the claim: it is still not evidence that retcon planning improves fiction, but the package now gives a recipient clear commands whose failures identify the exact layer at fault.

## Experimental implication

The next evidence-bearing step remains a live pilot: run the preregistered conditions with actual fresh contexts/API/subagents, retain exact transport declarations, export rater-level observations, and report mechanical custody outcomes separately from aesthetic ratings.

## Immediate next step

Send the artifact with the modest claim. Ask the recipient to run `tools/run_acceptance.py`, `artifact check`, and the manifest check before looking at the research claim.
