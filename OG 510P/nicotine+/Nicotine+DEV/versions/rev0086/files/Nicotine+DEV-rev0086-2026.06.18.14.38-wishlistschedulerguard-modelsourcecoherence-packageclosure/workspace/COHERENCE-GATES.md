# Coherence gates

A finding may not enter the strict document unless its proposed fix passes these gates:

1. **Same-family merge check:** all aliases and sibling findings in `data/rev0006_coherence_map.csv` have been reviewed.
2. **Protocol-field check:** the recommended binding uses fields that exist in the protocol message or is explicitly framed as a protocol extension/backward-compatible policy.
3. **Lifecycle check:** timers, queued messages, active maps, file handles, sockets, and UI state are not left orphaned by the proposed fix.
4. **Compatibility check:** direct/indirect peer connection races and legacy clients have an explicit behavior decision.
5. **Upstream partial-fix check:** current and future source lanes are checked for partial mitigations so the item is not misrepresented as fresh.
