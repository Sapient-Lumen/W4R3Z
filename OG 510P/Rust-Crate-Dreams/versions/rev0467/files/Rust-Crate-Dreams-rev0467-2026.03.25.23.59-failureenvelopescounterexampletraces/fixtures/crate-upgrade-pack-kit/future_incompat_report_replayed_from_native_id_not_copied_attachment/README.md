# Scenario — stable future-incompat import is replayed from native report id rather than treated as a copied attachment

This scenario freezes the distinction between:

- a stable Cargo report that can still be re-rendered from native storage via its report id,
- and a copied snapshot that would only be inspectable as an embedded attachment.

The pack should keep that distinction explicit so a reader can tell whether the evidence is still replayable or merely bundled.
