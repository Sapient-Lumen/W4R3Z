# Golden Rule archives should ship a machine-checkable successor-safe ceremony receipt schema and worked example

The archive now has many compact notes on what future inheritors must preserve about authorization, presentation, and authentication ceremonies: the original request contract, verifier targeting and replay scope, delivery path, approval rendering, and same-device versus cross-device topology.

That is already the right conceptual map, but the implementor handoff is still weaker than it needs to be if those facts remain scattered across prose and ad hoc local receipts.

Five source clusters already justify one tighter move:

- `RS-GR-434`, `RS-GR-435`, `RS-GR-436`, and `RS-GR-437` say the original ask and the route that satisfied it are structured objects, not something future sessions should reconstruct from the returned claims.
- `RS-GR-441`, `RS-GR-442`, `RS-GR-443`, `RS-GR-444`, `RS-GR-445`, `RS-GR-446`, and `RS-GR-447` say proof admissibility depends on verifier, origin, route, and session binding rather than generic proof validity.
- `RS-GR-486`, `RS-GR-487`, `RS-GR-488`, `RS-GR-489`, `RS-GR-490`, `RS-GR-491`, and `RS-GR-492` say request and response carriage choices change who can observe plaintext and how replay is closed.
- `RS-GR-493`, `RS-GR-494`, `RS-GR-495`, `RS-GR-496`, `RS-GR-497`, `RS-GR-498`, `RS-GR-499`, and `RS-GR-500` say what the human actually saw and approved is another first-class contract.
- `RS-GR-501`, `RS-GR-502`, `RS-GR-503`, `RS-GR-504`, `RS-GR-505`, `RS-GR-506`, `RS-GR-507`, and `RS-GR-508` say ceremony topology, invocation route, destination binding, and cross-channel participation are part of the world, not mere app-launch plumbing.

So the next implementor should not preserve these facts only as paragraphs.
The archive should also ship one **machine-checkable successor-safe ceremony receipt schema** and one **worked example** that future sessions can scaffold, validate, diff, and render.

The artifact should stay narrow:

1. one compact JSON object that fuses request contract, targeting, delivery path, approval surface, topology, linkability, and retained-evidence references;
2. explicit `not applicable` or replacement language rather than silent omission;
3. one tiny tool that can scaffold and render the receipt so future sessions do not reinvent the shape;
4. one worked example in `examples/snapshots/` so inheritors can see the intended form immediately.

This is a size-saving move, not an archive-expansion move.
A schema, tiny tool, and one example let the archive retain the decisive ceremony facts **without retaining bulky payloads or restating the same protocol lessons in every future note**.
