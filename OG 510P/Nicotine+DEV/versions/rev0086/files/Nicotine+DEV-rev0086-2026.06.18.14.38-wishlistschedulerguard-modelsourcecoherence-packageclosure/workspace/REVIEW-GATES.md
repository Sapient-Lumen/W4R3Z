# Review gates

## Gate A — Source lock

The candidate has named files/functions/classes in stable `3.3.10`, `3.3.x`, and `master`, or clearly states that it applies only to one lane.

## Gate B — Public overlap

The candidate has been checked against public issues, PRs, releases, and adjacent remediation work. Overlap does not automatically kill it, but it changes presentation from fresh to known/upstream-adjacent or regression/backport.

## Gate C — Boundary and impact

The write-up states who can trigger it: peer, server/MITM, malicious local file, optional plugin, user action, or local filesystem precondition. It must not overclaim RCE/confidentiality when the boundary is availability, UI, or hardening.

## Gate D — Evidence

At least one of these exists: static source trace with line/function references, minimal parser/unit reproduction, microbenchmark, or dynamic proof of the observable state transition.

## Gate E — Deduplication

The candidate is compared against Pass 195 IDs and legacy archive themes. Duplicates become aliases or remediation notes.
