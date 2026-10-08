# Cooperation benchmark programs should ship a taxonomy registry for compact-card reason codes, action kinds, and execution lanes

Once compact-card governance grows into inventories, head registers, review queues, citation surfaces, handoff packs, first-reentry selectors, and execution lanes, the archive starts depending on many tiny stable identifiers.

That is exactly when a program should stop treating those strings as incidental implementation details.

A good compact benchmark stack should publish one small generated taxonomy registry that:

- catalogs the stable warning / citation / review / execution tokens that appear across the compact-card surfaces,
- explains what each token means,
- points to the report fields where those tokens are authoritative,
- carries the first-reentry priority policy in machine-readable form, and
- fails closed when a live surface emits a token that the registry does not recognize.

This is a low-byte change, but it matters.
Without it, inheritors slowly start learning token semantics from session memory or scattered builder code.
With it, the archive can say which compact-card identifiers are stable **and what they are supposed to mean**.
