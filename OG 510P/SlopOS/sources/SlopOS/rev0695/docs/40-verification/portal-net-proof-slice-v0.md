# Portal.net proof slice v0 (first mediated action target)

Purpose: make one **hard, implementation-facing choice** for the first proof-bearing mediated action in the archive: the MVP-A2 portal/control-plane slice uses **`portal.net.request`** rather than leaving the first portal workflow generic.

This doc is intentionally small.
It introduces **no new schema family**, **no new ACP kind**, **no new conflict-key family**, and **no new portal family**.
It only selects one already-pinned seam as the first concrete action worth implementing, testing, and proving against the existing Hybrid/commutativity discipline.

## Decision (v0)

1. **The first mediated action target is `portal.net.request`**
   - The proof-bearing mediated action slice for MVP-A2 uses the existing ACP kind **`portal.net.request`**.
   - The exact request/receipt artifacts remain the already-pinned **CH-NETREQ v0** and **CH-NETLEASE v0** seams.
   - This decision does **not** make `portal.net.request` the only important portal family; it only makes it the first one we tighten into an implementation/verification target.

2. **Why this seam is first**
   - It already carries the right expensive choices in machine-checkable form:
     - networking is **non-ambient** and policy-killable,
     - DNS/resolver behavior is not ambient host residue,
     - conflict keys are already pinned in ACP as **`family="domain.id"`**,
     - ordering is already pinned as **ordered within a domain**,
     - the ordering witness is already **required** as **CH-ORDERTOK v0**, and
     - the serialization boundary already lives at **`svc:portal.net`**.
   - That makes it a better first proof/control slice than `portal.uri.*`, which is intentionally surrounded by many small boundary docs because browser/chooser/handler/session semantics are broader and easier to mis-specify early.
   - It also exercises all four product shapes honestly:
     - **A secure workstation** needs non-ambient networking that still feels usable,
     - **B cloud/microVM** needs explicit outbound authority and transcripted lease issuance,
     - **C embedded/separation** can keep the lane off by policy while still benefiting from the same substrate discipline,
     - **D agent/automation** needs a narrow, transcript-visible, dedupe-aware, receipt-bearing action that does not silently regrow ambient sockets.

3. **What this slice must prove/test first**
   - The first harness/prototype for the mediated control-plane slice must make the following existing semantics real:
     - lane gate `cfg.params.lane.portal.net` fails closed and is receipt-visible,
     - CH-NETREQ validation is total/canonical,
     - duplicate submissions with stable `CH-NETREQ.req_id` are handled by explicit dedupe rather than hidden retry folklore,
     - ordered-within-domain issuance records ordering evidence through **CH-ORDERTOK v0**,
     - transcript-visible accept/reject outcomes stay separate from later live lease truth,
     - any emitted **CH-NETLEASE v0** digest remains exact issued-bounds evidence only,
     - any emitted CH-NETLEASE/CH-ACPOUT evidence keeps **predicate + resolver binding** portable while exact resolved-address / selected-endpoint / route state stays portal-local (`network-lease-resolution-boundary-v0.md`), and
     - no capshell/compat wrapper may reintroduce ambient `socket()` / resolver fallback around the slice, and
     - no capshell/compat wrapper may reintroduce inherited process-bound networks, interface pinning, source-address forcing, or host-local VRF fallback around the slice (`network-lease-local-egress-boundary-v0.md`), and
     - no capshell/compat wrapper may reintroduce ambient metered / validated / captive / expensive / constrained path hints or generic host network-monitor fallback around the slice (`network-lease-path-property-boundary-v0.md`), and
    - no capshell/compat wrapper may reintroduce `$http_proxy`, PAC / WPAD, or generic “use system proxy” fallback around the slice (`network-lease-proxy-boundary-v0.md`), and
     - no capshell/compat wrapper may reintroduce ambient cert-store / certificate-exception / verifier-disable fallback around the slice (`network-lease-tls-verifier-boundary-v0.md`), and
    - no capshell/compat wrapper may reintroduce browser certificate pickers, host keychain alias reuse, PKCS#11 default-provider selection, or proxy-client-cert fallback around the slice (`network-lease-client-cert-boundary-v0.md`).
    - no capshell/compat wrapper may reinterpret leased `tls` / `quic` reachability as a portable `alpn` / `selected_alpn` / `http_version` / protocol-profile contract or hidden default ALPN / application-protocol fallback around the slice (`network-lease-application-protocol-boundary-v0.md`), and
    - no capshell/compat wrapper may reinterpret leased `tls` / `quic` reachability as a portable `server_name` / `sni_name` / `public_name` / `ech` contract or hidden SNI / server-name / ECH fallback around the slice (`network-lease-server-name-boundary-v0.md`), and
    - no capshell/compat wrapper may reinterpret leased `tls` / `quic` reachability as a portable `session_ticket` / `psk_identity` / `allow_0rtt` / `resumed_session` contract or hidden ticket / PSK / 0-RTT fallback around the slice (`network-lease-session-resumption-boundary-v0.md`).
    - no capshell/compat wrapper may reinterpret leased `tls` / `quic` reachability as a portable `tls_min_version` / `cipher_suites` / `groups` / `quic_version` / `transport_params` contract or hidden TLS-version / cipher-list / group / QUIC-version / transport-parameter fallback around the slice (`network-lease-transport-profile-boundary-v0.md`).
    - no capshell/compat wrapper may reinterpret `kind=dns` as a portable `qtype` / `qclass` / `raw_dns_reply` / `resolver_transport` contract or hidden RR-query / raw-resolver fallback around the slice (`network-lease-dns-query-boundary-v0.md`).
    - no capshell/compat wrapper may reinterpret reviewed name predicates as a portable `search_domains` / `ndots` / `hosts_file_mode` / `split_dns_view` / `mdns` / `llmnr` contract or hidden search-path / hosts-file / split-DNS / local-link resolver fallback around the slice (`network-lease-name-context-boundary-v0.md`).
    - no capshell/compat wrapper may reinterpret reviewed name predicates as a portable `unicode_host` / `u_label` / `idna_profile` / `uts46` / `casefolded_host` / `trailing_dot_ok` contract or hidden Unicode-to-ASCII / trailing-dot canonicalization fallback around the slice (`network-lease-name-normalization-boundary-v0.md`).
    - no capshell/compat wrapper may reinterpret reviewed connect/listen host-or-IP predicates as a portable `default_port` / `service_name` / `uri_scheme` / `getservbyname` contract or hidden default-port / service-name fallback around the slice (`network-lease-port-inference-boundary-v0.md`).
    - no capshell/compat wrapper may reinterpret reviewed exact-name predicates as a portable `srv_service` / `svcb` / `https_rr` / `service_binding` / `alternate_endpoint` contract or hidden SRV / SVCB / HTTPS fallback around the slice (`network-lease-service-binding-boundary-v0.md`).
    - no capshell/compat wrapper may reinterpret reviewed exact-name predicates as a portable `address_family_preference` / `ipv6_first` / `happy_eyeballs` / `candidate_order` / `selected_family` contract or hidden RFC 6724 sorting / Happy-Eyeballs fallback around the slice (`network-lease-address-selection-boundary-v0.md`).
    - no capshell/compat wrapper may reinterpret CH-NETREQ `req_id` as a mutable upsert handle; same scoped `req_id` with different canonical CH-NETREQ bytes MUST reject before effect rather than replace/merge/broaden authority under one key (`../30-architecture/network-request-idempotency-boundary-v0.md`).
    - no capshell/compat wrapper may reinterpret `kind=listen` as bind-by-hostname, DNS publication, mDNS advertisement, NAT/public-endpoint allocation, or loopback-callback capture; `kind=listen` stays a local bind/exposure subject and `dns_name` / `dns_suffix` listener predicates reject (`../30-architecture/network-request-listen-subject-boundary-v0.md`).

4. **Why this reduces entropy**
   - Leaving the first mediated action generic keeps reopening the same choice every pass.
   - Pinning `portal.net.request` now lets follow-on work converge on one exact ACP row, one exact schema pair, one exact serialization owner, and one exact set of negative tests.
   - Future portal work can still choose other families, but it no longer has to answer “which portal do we prove first?” from scratch.

## Phase 1 non-goals (explicitly deferred)

- Declaring `portal.uri.*` or any other portal family as a co-equal first proof target.
- Inventing a new general portal-priority registry or scorecard.
- Widening D-NETLEASE into ambient sockets, ambient DNS, PAC / WPAD / system-proxy fallback, browser fallback, or generic session continuity.
- Adding any new schema, ACP kind, conflict-key family, or receipt type for this decision.

## Profile effect (A–D)

- **Secure workstation (A):** picks one realistic everyday authority seam without importing browser/session folklore as the first proof target.
- **Cloud micro-VM substrate (B):** keeps the first mediated action close to hosted-compute reality: explicit outbound networking, lease issuance, and clear ordering/kill switches.
- **Embedded / separation appliance (C):** keeps the same substrate/specs available while allowing strict profiles to leave `cfg.params.lane.portal.net=false`.
- **Agent/automation OS (D):** gives LLM/automation flows one narrow action family whose authority, dedupe key, receipt shape, and ordering story are already explicit.

## Wiring

This decision must remain wired from:
- `README.md`
- `docs/README.md`
- `docs/00-meta/llm-runbook.md`
- `docs/00-meta/trajectory-map.md`
- `docs/40-verification/minimum-viable-proof-slice.md`
- `docs/30-architecture/network-lease-posture-v0.md`
- `docs/30-architecture/network-request-schema-v0.md`
- `docs/30-architecture/network-lease-schema-v0.md`
- `docs/30-architecture/network-lease-local-egress-boundary-v0.md`
- `docs/30-architecture/network-lease-application-protocol-boundary-v0.md`
- `docs/30-architecture/network-lease-server-name-boundary-v0.md`
- `docs/30-architecture/network-lease-transport-profile-boundary-v0.md`
- `docs/30-architecture/network-lease-dns-query-boundary-v0.md`
- `docs/30-architecture/network-lease-path-property-boundary-v0.md`
- `docs/30-architecture/network-lease-name-context-boundary-v0.md`
- `docs/30-architecture/network-lease-name-normalization-boundary-v0.md`
- `docs/30-architecture/network-lease-port-inference-boundary-v0.md`
- `docs/30-architecture/network-lease-service-binding-boundary-v0.md`
- `docs/30-architecture/network-lease-address-selection-boundary-v0.md`
- `docs/70-llm-control/acp-action-kind-registry.md`
- `docs/30-architecture/serialization-boundary-registry.md`
- `tools/README.md`
- `CHANGELOG.md`

## Evidence hook

- `tools/check_portal_net_proof_slice.py` fails `make lint` if this decision stops being discoverable, if MVP/trajectory docs stop naming **`portal.net.request`** as the first mediated action target, or if the doc drops its Phase 1 **no new schema / no new ACP / no new conflict-key family / existing `domain.id` + CH-ORDERTOK + `svc:portal.net` reuse** posture (**EVID-2026-629**).

## References

- REF-CAPSICUM.
- REF-FREEBSD-LIBCASPER.
- REF-XDG-PORTAL.
- REF-XDG-PORTAL-REQUEST.
