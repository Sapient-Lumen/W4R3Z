# Native admission held

Admission is intentionally weaker than selection.  A settled shadow result can enter a held shadow slot only when the component is allowed, side-effect-free, bounded, and backed by Python fallback.

Forbidden surfaces still quarantine:

- untrusted byte parsing;
- crypto or secret material;
- transport/session work;
- persistence/finality;
- policy/moderation;
- any request for native call permission or native result selection.
