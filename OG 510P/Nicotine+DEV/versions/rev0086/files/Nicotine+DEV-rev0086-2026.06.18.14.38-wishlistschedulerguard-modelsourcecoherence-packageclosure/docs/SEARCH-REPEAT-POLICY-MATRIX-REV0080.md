# Search Again policy matrix — rev0080

Machine-readable authority: `data/rev0080_search_repeat_policy_matrix.csv`.

## 1. Current same-token Retry/Merge

Preserves the page and all local view state. It can merge results from newly responding usernames while below the cap. It cannot refresh a username already present, cannot isolate delayed replies, and is dead after the page reaches the display cap.

## 2. Clear then same-token retry

Restores display capacity and roughly reconstructs the removed historical workflow. It does not create a new wire epoch. Delayed responses from the prior request and responses caused by the new click are indistinguishable.

## 3. Fresh-token page replacement

Retires the old response capability, starts a normal new-search lifetime, and rejects late old-token replies. Under ordinary best-effort new-search semantics, it does not require a network-applied acknowledgement. Its integration cost is primarily UI and domain state: filters, grouping, tab placement, undo history, plugin events, and wishlist semantics.

## 4. Fresh-token in-place transactional refresh

Preserves a stable visible page and can support a failure-atomic commit promise. That stronger promise creates the complete fan-out, acknowledgement, reconnect, replay, zero-result, and logical-identity problems modeled in rev0078–rev0079.

## Current choice

No implementation is selected. The next experiment should start with policy 3 because it aligns with public fresh-token direction and existing new-search behavior while avoiding an unnecessary transaction guarantee. Policy 4 remains available if maintainers explicitly require stable in-place identity.
