# D-NAMECERT label-atom boundary v0 (labels are opaque atoms; no hierarchy/wildcards/path grammar)

Purpose: narrow the **label/query grammar** seam of **D-NAMECERT** so Phase 1 local naming does not
quietly grow a path language, wildcard syntax, suffix/prefix matcher, or dotted hierarchy merely because
`Binding.name` / `Delegation.role` permit punctuation in their exact-byte ASCII profile.

This boundary deliberately stays on already-reviewed seams: **D-NS** still owns any authority-bearing
materialization, **D-COMMUTE** still owns conflict keys/ordering where live state changes, and
**D-REPL** still carries signed bundle evidence rather than a distributed namespace grammar.

The archive already says that **CH-NAMECERT** is issuer-local user-space evidence, that evaluation is
closed-world and bounded, that multiple admissible candidates remain set-valued, and that labels use a
tiny ASCII identifier profile. This doc closes the next ambiguity: **does punctuation inside a valid
label imply path structure, wildcard matching, or hierarchical lookup semantics?**

Phase 1 makes a small, hard choice: **`Binding.name` and `Delegation.role` are single opaque atoms after validation**. The bytes `.` / `_` / `-` are allowed characters in the string profile, but they remain
ordinary bytes, not separators, path operators, wildcard markers, or suffix/prefix match triggers.

## Boundary (v0)

1) **One admitted label = one opaque atom**
   - In Phase 1, each admitted `Binding.name` or `Delegation.role` is one validated exact-byte label atom.
   - Equality/matching is exact byte equality after validation under the existing lowercase ASCII profile.
   - The presence of `.` / `_` / `-` inside an admitted label does **not** split it into multiple components.

2) **No path grammar, hierarchy, or implicit chained lookup inside one label**
   - `CH-NAMECERT v0` defines **no** slash-separated, dot-separated, quoted, escaped, rooted, relative, or multi-segment path grammar for `Binding.name` / `Delegation.role`.
   - A label such as `ops.admin`, `svc-cache`, or `team_alpha` is one atom, not a hierarchy of sublabels.
   - SDSI/SPKI compound-name machinery is therefore a useful historical contrast, not imported Phase 1 semantics.

3) **No wildcard / prefix / suffix / glob semantics**
   - `*`, `?`, bracket expressions, prefix search, suffix search, substring search, and glob-like matching are all out of scope for `D-NAMECERT v0`.
   - Evaluators MUST NOT infer wildcard-like behavior from punctuation, repeated separators, empty-looking segments, or application-specific naming conventions.
   - Candidate membership remains an exact-label question, not a pattern-matching question.

4) **Search stays bounded because labels are not recursively parsed**
   - The existing closed-world bounded-search posture stays smaller: evaluators search over explicit bundle statements, not over hidden subcomponents extracted from one label.
   - A lookup for `ops.admin` consults only statements for the exact atom `ops.admin`; it does not implicitly try `ops` then `admin`, nor any suffix/prefix variants.
   - This keeps PO-NAMECERT-CHAIN honest: search complexity depends on explicit statements in the bundle set, not on an unreviewed label parser.

5) **Projection remains exact-label and exact-source**
   - If a live `view.slot` mutation is justified by a naming result, the target-seam proposal/receipt still records the exact chosen candidate and the exact supporting `digest(CH-NAMECERT v0)` evidence.
   - A receipt may not justify an attach by saying a label “obviously matched the same subtree / prefix / wildcard family”.
   - Projection therefore stays exact-label and source-digest-bound instead of relying on implied hierarchy.

6) **All four product shapes benefit from the smaller rule**
   - **Secure workstation (A):** prevents convenient dotted labels from turning into hidden admin/path semantics.
   - **Cloud micro-VM substrate (B):** avoids service naming conventions becoming an ambient hierarchical resolver language.
   - **Embedded / separation-kernel-ish appliance (C):** keeps the evaluator tiny and offline-capable by declining wildcard/path parsing.
   - **Agent/automation OS (D):** gives LLM- and workflow-driven tooling a crisp rule: match exact atoms only unless a future explicit query/path seam exists.

## Phase 1 non-goals (explicitly deferred)

- Slash-separated or dot-separated hierarchical lookup semantics on `Binding.name` / `Delegation.role`.
- Wildcard, glob, prefix, suffix, substring, or regex matching on D-NAMECERT labels.
- Path-normalization / escaping / quoting rules for local names or roles.
- Any structured query language or browsing grammar over CH-NAMECERT statement sets.
- Importing SDSI compound-name chaining syntax directly into the Phase 1 `Binding.name` / `Delegation.role` fields.
- Treating punctuation or repeated separators as authority-bearing structure.

## Wiring

- Core posture: `namecert-posture-v0.md`
- Schema seam: `namecert-schema-v0.md`
- String-profile seam: `namecert-string-profile-v0.md`
- Search boundary: `namecert-search-boundary-v0.md`
- Selection boundary: `namecert-selection-boundary-v0.md`
- Projection boundary: `namecert-projection-boundary-v0.md`
- RFC source seam: `rfcs/0023-local-naming-certificates-spki-sdsi.md`
- Threat model: `docs/10-threat-model/abuse-cases.md` (**AC-029**)
- Assurance hooks:
  - `docs/20-assurance/invariant-registry.md` (**I-NAME-1**, **I-NAME-2**)
  - `docs/20-assurance/proof-obligation-registry.md` (**PO-NAMECERT-VALIDATE**, **PO-NAMECERT-CHAIN**, **PO-NAMECERT-PROJECT**)

CI drift gate:
- `tools/check_namecert_label_atom_boundary.py` fails `make lint` if this boundary stops being discoverable, loses its **opaque atom / no path grammar / no wildcard semantics / exact-label match only** stance, or drops its assurance / REF wiring.

## References

- REF-SDSI-RL96.
- REF-SPKI-RFC2693.
