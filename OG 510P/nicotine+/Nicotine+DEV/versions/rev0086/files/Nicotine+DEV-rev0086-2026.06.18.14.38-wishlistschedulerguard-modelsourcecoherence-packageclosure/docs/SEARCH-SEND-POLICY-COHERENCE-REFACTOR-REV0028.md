# SEARCH-SEND-POLICY coherence refactor — rev0028

This pass deliberately avoids inflating the strict lane. SEARCH-SEND-POLICY-01 is useful, but it should not be merged into SEARCH-RESP-01 or split into many smaller plugin/geoblock rows.

## Canonical packet

```text
SEARCH-SEND-POLICY-01:
  U-174 = canonical lead.
  U-247 = plugin notification ordering/support subcase.
```

## Kept separate

```text
SEARCH-RESP-01 / U-163:
  Accepted inbound FileSearchResponse token/source/scope binding.
  Already strict-promoted in rev0013.
  Do not dilute it with send-side plugin/IP policy.

SEARCH-RESP parser/order support:
  U-254/U-262/U-263/U-264/U-265/U-266/U-267/U-270 remain response-side parser/policy/accounting/lifetime rows.

Room/chat IP-ignore timing:
  U-177/U-180/U-183 remain message-surface policy revalidation rows, not search-send rows.
```

## Compatibility guardrails

A good fix should preserve legitimate search behavior while exposing one coherent policy decision to all sinks.

```text
Avoid:
  - treating distributed parent socket IP as the requester IP;
  - blocking all search responses whenever no cached IP exists, unless geoblock/IP-ignore configuration demands it;
  - silently breaking plugins that rely on search_request_notification/distrib_search_notification;
  - adding synchronous GetPeerAddress fanout in the hot search-request path.

Prefer:
  - bounded cached-IP / async-resolution policy;
  - explicit core_policy_decision metadata to plugins;
  - one request-context object shared by response generation, logs, and plugins;
  - regression tests around disabled search responses, banned users, min-term rejects, unknown IP, cached blocked IP, and cached allowed IP.
```

## Strict decision

```text
Verified current behavior: yes.
Hard-search status: candidate no direct exact public match found, but public-adjacent.
Strict promotion: no.
Reason: policy/API hardening with compatibility constraints; lower impact than current strict candidates.
```
