# Ingress gate announcement pressure

A public garden announcement creates a tempting bug: inbound requests start to
look authorized merely because the service was advertised. rev0037 adds an
`ingressgate` surface that joins the accepted catalog, accepted announcement,
load-sheath policy, request replay memory, family pressure, and raw-key exposure
budget before a request can enter handler work.

The gate tests:

- missing or failed announcements do not authorize ingress;
- announcement/catalog/report digest drift quarantines the window;
- replayed request IDs are hard failures;
- requests for hidden or unannounced services are quarantined;
- requester/path-family floods are held before expensive handler work;
- raw-key exposure budget overflow quarantines the window;
- load-sheath holds remain holds, while load-sheath quarantine remains quarantine.

The point is to keep service discovery, ingress admission, scheduling, ticketing,
and receipts as separate boundaries.
