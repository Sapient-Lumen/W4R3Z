
# ADR 0030: Witnessed rollback detection, not global consensus

Status: accepted-for-rev0008-guessing

Decision: clients and gardens should keep local highest-seen sequence memory and same-sequence fork evidence for mutable heads.

Reason: a valid old signature can be harmful. Detecting rollback and equivocation is necessary, but a global consensus mechanism would contradict the DHT's substrate goals.

Implementation hint: garden witness receipts are evidence, not truth authority.
