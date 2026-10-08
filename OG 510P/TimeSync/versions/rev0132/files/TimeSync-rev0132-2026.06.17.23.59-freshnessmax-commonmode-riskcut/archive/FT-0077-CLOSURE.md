# FT-0077 closure — lifecycle-authority rotation, delegation, and compromise-response boundaries

rev0078 closes FT-0077 by adding `rotation_delegation_status` to `policy_lifecycle_authority_reference`.

The accepted design is deliberately narrow:

- rotation state is summarized by digest-bound posture only;
- delegated status/revocation publication must be scoped and digest-bound;
- unresolved or unknown authority compromise cannot support current replay visibility;
- contained compromise may remain current only with recovery/successor digest, response digest, and no current replay-visibility effect;
- cross-operator equivalence is replay-visibility-only and cannot export authority rosters, key material, delegation chains, incident forensics, trust anchors, or policy language.

The feature stays outside TimeState, profile assessment, transport, and ordinary evidence-obligation satisfaction.
