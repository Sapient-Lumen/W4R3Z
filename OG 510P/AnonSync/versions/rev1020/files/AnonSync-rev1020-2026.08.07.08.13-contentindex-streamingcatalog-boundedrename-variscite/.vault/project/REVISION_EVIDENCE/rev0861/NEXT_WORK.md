# Next work after rev0861

1. Bind the claimed-path frontier to a finite SQLite VM-step and wall-time
   budget, or attest a supporting index and query plan. A bounded result vector
   does not prove bounded internal work over duplicate-heavy tables.
2. Inventory every multi-statement durable reader and classify whether its
   output is one snapshot value, a deliberately fresh observation, or an
   explicitly monotone aggregate. Give every one-snapshot value a typed
   transaction authority and sticky publication point.
3. Extend binary-identity audits beyond this path. Security-relevant equality
   must not silently inherit schema-defined `NOCASE` or application collations.
4. Run all registered Python audits with bytecode generation disabled in
   addition to disabling `site` initialization, so validation cannot dirty the
   source tree with `__pycache__`.
5. Move hostile SQLite and document interpretation behind a disposable worker
   protocol with descriptor-only inputs, bounded outputs, CPU/memory/time
   limits, filesystem confinement, and fail-closed parent verification.
6. Continue extracting invariant owners from large integration units; orchestral
   code should compose typed capabilities rather than contain persistence loops.
7. Return to the product-defining gap: an executable operation algebra and
   generated multi-peer histories for update, delete, recreation, rename,
   membership/key epochs, partitions, retries, restart, and external effects.
8. Specify the privacy plane: payload encryption, device generations,
   membership, rotation, revocation, recovery, forward secrecy,
   post-compromise recovery, and metadata leakage.
