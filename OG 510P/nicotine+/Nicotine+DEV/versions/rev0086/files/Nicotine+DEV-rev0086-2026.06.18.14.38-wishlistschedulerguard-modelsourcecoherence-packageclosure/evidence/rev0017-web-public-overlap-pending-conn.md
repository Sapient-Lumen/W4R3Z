# rev0017 web/public-overlap check: PENDING-CONN-BUDGET-01 / U-181

## Conclusion

Targeted public searching did not find a direct public report of the exact invariant: pending `PeerInit`/`GetPeerAddress` or socket-cap deferred state accumulating arbitrary outbound peer messages through `outgoing_msgs` without per-user/global budgets. The status is therefore **candidate no direct public match found, public-adjacent** rather than clean novelty.

## Captured searches

- `"pending PeerInit"` — no direct issue results found in GitHub issue search (no-direct-public-match-found). https://github.com/nicotine-plus/nicotine-plus/issues?q=%22pending+PeerInit%22
- `"GetPeerAddress" "outgoing_msgs"` — no direct issue results found in GitHub issue search (no-direct-public-match-found). https://github.com/nicotine-plus/nicotine-plus/issues?q=%22GetPeerAddress%22+%22outgoing_msgs%22
- `"outgoing_msgs"` — no direct public issue result for internal outgoing message buffer naming (no-direct-public-match-found). https://github.com/nicotine-plus/nicotine-plus/issues?q=%22outgoing_msgs%22
- `"Cannot remove peer init message"` — found issue #3631 with user logs containing indirect-connection-in-progress message and direct connection timeout (public-adjacent-connection-symptom). https://github.com/nicotine-plus/nicotine-plus/issues/3631
- `pending connections / download folder` — issue #2686 says many pending connections can make some folder-content requests time out (public-adjacent-pending-connection-ux). https://github.com/nicotine-plus/nicotine-plus/issues/2686
- `connection closed timeout queued` — issues #2978 and #2926 discuss connection closed/timeout/queued symptoms without direct pending-message-buffer root (public-adjacent-transfer-connection-symptom). https://github.com/nicotine-plus/nicotine-plus/issues/2978

## Public-adjacent interpretation

- The issue is adjacent to public connection symptoms: connection timeouts, indirect-connection-in-progress logs, stuck queued downloads, and folder-download requests timing out when many connections are pending.
- Those public issues do not appear to describe the internal pending-message-buffer invariant itself.
- The cube therefore treats U-181 as useful audited hardening, not as a strict/high-priority report candidate in rev0017.