# Scenario: review request stale head requires reissue

A manual-review request asked to carry one projected pack into stronger frozen/public use, but a newer operational head appeared in the same lineage before approval. The older request and witness stay historical, surface `stale-head` / `reissue-required`, and do not silently clear the newer head.
