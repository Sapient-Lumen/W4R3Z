# CHANGELOG

## rev0032 — 2026-03-28 09:20 America/New_York

This revision tests whether the `local_private` anchor category should split.

### Added
- `LOCAL-PRIVATE-TEST.md`

### Tightened
- `TRACEABILITY-SEMANTICS.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- local clocks and holdover states vary in important ways
- but the current differences are better described by regime, holdover capability, and evidence posture than by splitting the anchor family itself
- `local_private` therefore survives as one category for now
- the reduced traceability hook now looks stable enough to begin feeding back into the greenfield track

### Character of the revision
- more conservative
- more reduction-protective
- less likely to confuse operational degradation with anchor identity

## rev0033 — 2026-03-28 09:37 America/New_York

This revision feeds the stabilized traceability hook back into the greenfield track.

### Added
- `GREENFIELD-TRACEABILITY.md`

### Tightened
- `TRACKS.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- current mechanisms surface identity, timescale, uncertainty, and malfeasance evidence in different places
- but they still do not jointly surface a compact native traceability posture
- in the greenfield track, this changes source-admission and exported-state boundaries before it justifies anything larger
- aggregation also wants a simple non-upgrade rule for traceability posture

### Character of the revision
- cross-track
- boundary-focused
- still conservative about core growth

## rev0034 — 2026-03-28 09:56 America/New_York

This revision tests whether the greenfield traceability hook must be default-visible.

### Added
- `DEFAULT-VISIBILITY-TEST.md`

### Tightened
- `EXTENSION-HOOKS.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- P5 wants traceability-adjacent state at the live measurement boundary
- P4 wants status / quality state by default inside synchronization control paths
- P3 still often carries its strongest traceability pressure at service and audit boundaries
- the best current fit is therefore not core promotion, but a distinction between globally native and profile-default visibility

### Character of the revision
- comparison-driven
- less binary
- still reduction-protective

## rev0035 — 2026-03-28 10:14 America/New_York

This revision tests whether the archive's new middle case deserves a named tier.

### Added
- `PROFILE-DEFAULT-TIER-TEST.md`

### Tightened
- `EXTENSION-HOOKS.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- `traceability_posture` is not the only hook that is stronger than optional without being archive-core
- `sync_dimension` now shows the same profile-default pattern at some P4/P5 boundaries
- `holdover_class` and `validity_scope` still do not clearly show the same pattern
- the archive now has enough evidence to name a tiny `profile_default` tier

### Character of the revision
- architecture-light
- hook-comparative
- still resistant to core growth

## rev0036 — 2026-03-28 10:31 America/New_York

This revision tests whether `holdover_class` should join the archive's new middle tier.

### Added
- `HOLDOVER-CLASS-TEST.md`

### Tightened
- `EXTENSION-HOOKS.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- demanding profiles repeatedly require visible holdover state, degraded regime, and timing quality
- but they still do not clearly require a richer reusable `holdover_class` to be default-visible across multiple boundaries
- this keeps the new `profile_default` tier smaller and more disciplined

### Character of the revision
- negative-result-friendly
- tier-stabilizing
- more careful about state versus class

## rev0037 — 2026-03-28 10:49 America/New_York

This revision tests whether `validity_scope` should join the archive's new middle tier.

### Added
- `VALIDITY-SCOPE-TEST.md`

### Tightened
- `EXTENSION-HOOKS.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- telecom material still presses status/selection semantics more strongly than reusable locality scope
- critical-infrastructure material supports honest degraded operation and relative-versus-absolute distinction, but not yet one repeated default-visible validity hook
- P6 remains the strongest home of `validity_scope`, yet that pressure is still too concentrated for tier admission
- the new `profile_default` tier now looks stabilized with two members

### Character of the revision
- negative-result-friendly
- tier-stabilizing
- ready to return to greenfield design work

## rev0038 — 2026-03-28 11:08 America/New_York

This revision sketches the thinnest greenfield response/state split the archive can currently justify.

### Added
- `GREENFIELD-RESPONSE-SKETCH.md`

### Tightened
- `TRACKS.md`
- `TIMESTATE.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- NTPv5 is increasingly explicit about the wire contract while leaving client-side algorithms out of scope
- NTS separates authenticated setup from later time-synchronization packets
- Roughtime shows how a compact signed bounded-time claim can travel on the wire
- TrueTime-like systems show why local client-facing state can still be richer than the wire
- the archive therefore now has a clean reason to distinguish a thin wire claim from a richer local assessed state

### Character of the revision
- architecture-light
- greenfield-forward
- still conservative about core growth

## rev0039 — 2026-03-28 11:27 America/New_York

This revision classifies `traceability_posture` across the archive's greenfield split.

### Added
- `TRACEABILITY-SPLIT-TEST.md`

### Tightened
- `EXTENSION-HOOKS.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- P5-like synchrophasor boundaries expect traceability to UTC, time accuracy, and leap-second status in the live time-status path
- P3-like finance boundaries still lean heavily on continuous comparison to UTC(NIST), documented uncertainty, synchronization procedure, logging, and certification
- `traceability_posture` therefore does not fit cleanly as source-claim only or local-assessment only
- the archive now treats it as the first clear dual-surface member of the `profile_default` tier

### Character of the revision
- profile-comparative
- greenfield-sharpening
- still conservative about core growth

## rev0040 — 2026-03-28 11:46 America/New_York

This revision classifies `sync_dimension` across the archive's greenfield split.

### Added
- `SYNC-DIMENSION-SPLIT-TEST.md`

### Tightened
- `EXTENSION-HOOKS.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- telecom timing material distinguishes explicit frequency and time/phase profiles and defines profile choices as part of the mechanism set needed for a given application
- smart-grid timing material likewise keeps time, phase, and frequency as distinct requirement families
- `sync_dimension` therefore looks less like a private local inference and less like a raw source claim than a profile-declared semantic
- the archive's two `profile_default` hooks now have different placement patterns

### Character of the revision
- classification-focused
- reduction-friendly
- still conservative about core growth

## rev0041 — 2026-03-28 12:05 America/New_York

This revision tests whether `profile_default` hooks need a discovery/request surface.

### Added
- `PROFILE-DEFAULT-DISCOVERY-TEST.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- NTPv5 uses extension fields for optional features and future extensibility, which supports optional native surfaces without widening the core header
- telecom timing uses explicit unicast negotiation in at least one frequency-profile setting, which shows request behavior can be real but narrow and profile-shaped
- some demanding boundaries still want default-visible status rather than negotiation
- the archive therefore now prefers a small discovery/request surface, not a broad negotiation subsystem

### Character of the revision
- interface-focused
- reduction-protective
- still resisting protocol bloat

## rev0042 — 2026-03-28 12:24 America/New_York

This revision sketches the thinnest discovery/request surface the archive can currently justify.

### Added
- `DISCOVERY-REQUEST-SKETCH.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- NTPv5 extension fields support optional native surfaces without enlarging the core exchange
- telecom unicast negotiation shows that explicit request behavior can be real while still narrow and profile-shaped
- Roughtime version discovery shows a lightweight compatibility surface can remain small
- the archive therefore now has enough justification for one shared exposure vocabulary plus one optional request list

### Character of the revision
- architectural
- vocabulary-tightening
- still resisting grammar bloat

## rev0043 — 2026-03-28 12:43 America/New_York

This revision sketches the smallest relay/aggregation rule family the archive can currently justify.

### Added
- `RELAY-AGGREGATION-RULES.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- NTPv5 requirements acknowledge intermediates that may modify timing packets without breaking protected behavior
- boundary-clock style telecom timing regenerates downstream timing from a locally recovered reference rather than merely forwarding an upstream flow
- telecom protection behavior shows downstream chains may need an explicit weaker state when stronger traceability no longer holds
- the archive therefore now has enough justification for a four-rule family: preserve, downgrade, restate, unknown

### Character of the revision
- boundary-focused
- honesty-first
- still resisting provenance sprawl

## rev0044 — 2026-03-28 13:02 America/New_York

This revision tests whether relay/restatement needs a tiny reason vocabulary.

### Added
- `REASON-VOCABULARY-TEST.md`

### Tightened
- `RELAY-AGGREGATION-RULES.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`
- `README.md`
- `START_HERE.md`

### Research effect
Further source reading sharpened:
- telecom timing already carries compact failure distinctions such as lossSync, lossAnnounce, and unusable
- NTP and related timing systems use compact reason-coded status in some error/degraded cases
- Roughtime gives an explicit inconsistency / malfeasance path
- the archive therefore now has enough justification for a very small optional reason layer without moving toward a status registry or fault tree

### Character of the revision
- explanation-tightening
- still reduction-protective
- still resisting status sprawl

## rev0045 — 2026-03-28 13:18 America/New_York

This revision tests whether `unknown` needs a tiny downstream consequence rule for `applicability`.

### Added
- `UNKNOWN-CONSEQUENCE-TEST.md`

### Tightened
- `TIMESTATE.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `RELAY-AGGREGATION-RULES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- integrity and warning-oriented timing guidance do not support leaving `unknown` consequence-free
- known uncertainty / quality is repeatedly tied to downstream usability decisions
- telecom failure semantics support withdrawing stronger decisions rather than silently preserving them
- the archive therefore now gives `unknown` one narrow rule: it may not sustain a stronger hook-dependent `applicability` claim by default
- the exact fallback still remains profile-local

### Character of the revision
- consequence-clarifying
- still reduction-protective
- no policy lattice

## rev0046 — 2026-03-28 13:34 America/New_York

This revision tests where the archive's tiny optional reason layer should live.

### Added
- `REASON-PLACEMENT-TEST.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `RELAY-AGGREGATION-RULES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- some ecosystems do carry compact direct-source reasons on the wire
- but the stronger recurring case is that reasons arise or change at boundaries during selection, failover, holdover, downgrade, and restatement
- NTPv5's narrow wire scope reinforces keeping the broader reason layer out of the minimal wire claim
- the archive therefore now treats reasons as boundary-first, local-state-readable, and only wire-admissible when a profile already has a compact source-originated status path

### Character of the revision
- placement-clarifying
- still reduction-protective
- thin-wire preserving

## rev0047 — 2026-03-28 13:52 America/New_York

This revision tests whether boundary metadata now needs a named tiny surface.

### Added
- `BOUNDARY-CONTEXT-SURFACE-TEST.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `RELAY-AGGREGATION-RULES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- some downstream behaviors depend on retained boundary context, not only on the recomputed timing state
- protection, path-trace, synchronization-uncertain, and loop-detection style signals all push in that direction
- the archive therefore now names one tiny wrapper, `boundary_context`, rather than leaving the pattern fully implicit
- the wrapper remains deliberately minimal: `action` plus optional `reason`

### Character of the revision
- wrapper-not-subsystem
- boundary-separating
- still reduction-protective

## rev0048 — 2026-03-28 14:07 America/New_York

This revision tests whether `boundary_context` needs its own expiry rule.

### Added
- `BOUNDARY-CONTEXT-EXPIRY-TEST.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `RELAY-AGGREGATION-RULES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- boundary explanation matters while a changed state remains in force
- but richer forwarding/convergence behavior belongs to chain-context signals outside the current wrapper
- the archive therefore now keeps `boundary_context` state-coupled instead of giving it its own timer or retention ladder
- future chain-context surfaces may still need richer lifetime semantics, but this wrapper does not earn them yet

### Character of the revision
- lifetime-conservative
- wrapper-protective
- still reduction-first

## rev0049 — 2026-03-28 14:24 America/New_York

This revision tests how visible `boundary_context` should be.

### Added
- `BOUNDARY-CONTEXT-VISIBILITY-TEST.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `RELAY-AGGREGATION-RULES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- some profiles need boundary explanation by default because downstream control behavior changes immediately
- many other consumers still mainly need current state and quality, not the explanation every time
- request/response style retrieval remains a good fit for extra chain/boundary context in thinner protocols
- the archive therefore now treats `boundary_context` as requestable by default, with profile-default export only in narrower control-path cases

### Character of the revision
- visibility-narrowing
- still reduction-protective
- profile-sensitive without being profile-heavy

## rev0050 — 2026-03-28 14:42 America/New_York

This revision tests whether `boundary_context` can reuse the archive's existing discovery/request surface.

### Added
- `DISCOVERY-REUSE-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- optional chain context is already retrieved through existing request/response patterns in contemporary timing design work
- narrow signaling/negotiation surfaces are enough for extra synchronization service/context in telecom profiles
- the archive therefore now treats the remaining issue as subject-level separation, not mechanism-level duplication
- one shared discovery/request surface survives; a second channel does not earn itself

### Character of the revision
- reuse-preferring
- still channel-thin
- semantics-separated without mechanism sprawl

## rev0051 — 2026-03-28 14:58 America/New_York

This revision tests whether the shared discovery/request surface needs explicit namespaces.

### Added
- `DISCOVERY-NAMESPACE-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- typed optional fields and tagged items already carry most of the needed separation in contemporary timing-related designs
- telecom signaling practice likewise does not force a second namespace hierarchy for each semantic category
- the archive therefore now keeps the shared discovery/request surface flat
- distinct item names survive the ambiguity test; explicit namespaces do not earn themselves yet

### Character of the revision
- hierarchy-resistant
- still reduction-first
- semantics-kept-by-names not machinery


## rev0052 — 2026-04-26 13:59 America/New_York

This revision tests whether profiles need named request bundles.

### Added
- `REQUEST-BUNDLE-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `PROBLEM-FRAME.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- current timing protocol work continues to favor typed fields, tagged items, and specific service requests at the exchange boundary
- PTP profiles can bundle choices at the profile/configuration layer without making those bundles native request aliases
- synchrophasor timing clusters traceability, accuracy, leap status, and time quality as default measurement semantics rather than as optional request shorthand
- the archive therefore keeps the shared request surface item-level and treats aliases as local conveniences that must lower to explicit item names

### Character of the revision
- alias-resistant
- item-level
- convenience-tolerant without adding a second policy layer

## rev0053 — 2026-04-26 14:10 America/New_York

This revision tests whether operator-facing aliases need their own boundary.

### Added
- `OPERATOR-ALIAS-BOUNDARY-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `REQUEST-BUNDLE-TEST.md`
- `PROBLEM-FRAME.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- current protocol work keeps optional behavior and compatibility item- or tag-level rather than operator-intention-level
- profile and management material can carry configuration/operator concerns without making them exchange subjects
- local aliases are likely useful enough to document, but only as expansion sheets outside the shared request surface
- the archive therefore adds a small alias boundary as a quarantine, not as a new semantic layer

### Character of the revision
- human-layer-aware
- alias-quarantining
- still item-level
- documentation boundary, not protocol surface

## rev0054 — 2026-04-26 14:32 America/New_York

This revision tests request lifetime for the optional item-level request list.

### Added
- `REQUEST-LIFETIME-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `OPERATOR-ALIAS-BOUNDARY-TEST.md`
- `REQUEST-BUNDLE-TEST.md`
- `PROBLEM-FRAME.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- current NTPv5 and Roughtime patterns keep ordinary optional request content attached to concrete exchanges and item identities
- NTS shows that setup/session state can exist, but should be explicit and separated from ordinary time-packet request semantics
- PTP profile material shows that persistent or forbidden behaviors belong in explicit profile/signaling rules, not in a silently remembered request list
- the archive therefore makes the ordinary request list exchange-scoped and reserves sticky behavior for a future explicit lease/subscription surface if pressure earns it

### Character of the revision
- lifecycle-tightening
- stateless-by-default
- profile/default separated from request persistence
- sticky behavior allowed only by explicit lease



## rev0055 — 2026-04-26 15:09 America/New_York

This revision tests response result shape for explicitly requested optional items.

### Added
- `REQUEST-RESULT-SHAPE-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `REQUEST-LIFETIME-TEST.md`
- `OPERATOR-ALIAS-BOUNDARY-TEST.md`
- `REQUEST-BUNDLE-TEST.md`
- `PROBLEM-FRAME.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- NTPv5 makes absence of an expected extension meaningful in a narrow item-level way, but does not require a broad error object
- Roughtime deliberately avoids protocol error reporting for malformed or unsupported request edges, warning against universal negative signaling
- PTP profile material keeps many allowed/forbidden/default choices at profile/configuration level rather than in every timing packet
- the archive therefore adopts a negative-only item-level result envelope for explicit optional requests, while keeping silence legitimate at invalid, unauthenticated, unrequested, and non-result-capable edges

### Character of the revision
- accountability-focused
- error-taxonomy-resistant
- item-level
- keeps success implicit in returned item content


## rev0056 — 2026-04-26 17:20 America/New_York

This revision tests required/default absence consequence.

### Added
- `REQUIRED-DEFAULT-ABSENCE-TEST.md`

### Tightened
- `DISCOVERY-REQUEST-SKETCH.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `REQUEST-RESULT-SHAPE-TEST.md`
- `REQUEST-LIFETIME-TEST.md`
- `OPERATOR-ALIAS-BOUNDARY-TEST.md`
- `REQUEST-BUNDLE-TEST.md`
- `PROBLEM-FRAME.md`
- `TIMESTATE.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- current protocol patterns distinguish well-formed exchange validity from optional extension absence and profile/configuration constraints
- PTP profile material makes required/allowed/forbidden behavior a profile contract rather than ordinary request negotiation
- signed/tagged response systems show that response satisfaction can be contract-shaped without requiring a broad error-reporting layer
- the archive therefore treats missing profile-required/default visibility as profile-nonconforming by default and locally downgrade-triggering, while still allowing weaker local use or explicit profile fallback

### Character of the revision
- profile-contract-focused
- local-downgrade-aware
- still error-taxonomy-resistant
- preserves the optional/request versus required/default boundary

## rev0057 — 2026-04-27 12:55 America/New_York

This revision tests whether profile satisfaction needs a compact local marker.

### Added
- `PROFILE-CONFORMANCE-MARKER-TEST.md`

### Tightened
- `GREENFIELD-RESPONSE-SKETCH.md`
- `DISCOVERY-REQUEST-SKETCH.md`
- `REQUIRED-DEFAULT-ABSENCE-TEST.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- profile satisfaction is real enough that downstream consumers should not have to rediscover hidden validation logic
- current protocol patterns do not justify a universal wire error object or manifest layer
- local assessed state now carries one small marker: `profile_conformance = satisfied | fallback | unsatisfied`
- fallback is explicit and weaker than full satisfaction

### Character of the revision
- local-state-focused
- reduction-protective
- makes rev0056 operational without widening the wire surface

## rev0058 — 2026-04-27 13:32 America/New_York

This revision tests whether fallback needs a shared weakened-applicability vocabulary.

### Added
- `FALLBACK-APPLICABILITY-VOCABULARY-TEST.md`

### Tightened
- `START_HERE.md`
- `README.md`
- `PROBLEM-FRAME.md`
- `TIMESTATE.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `DISCOVERY-REQUEST-SKETCH.md`
- `PROFILE-CONFORMANCE-MARKER-TEST.md`
- `REQUIRED-DEFAULT-ABSENCE-TEST.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- existing protocols and profiles support local/profile consequence mapping more strongly than a universal fallback label set
- Roughtime and NTPv5 both warn against widening ordinary exchanges into broad diagnostic surfaces
- PTP profile material supports profile-local required/default/fallback behavior
- application domains still need explicit downstream use boundaries, so fallback must not be bare
- the archive therefore keeps fallback in `profile_conformance` and puts the weakened use boundary in existing `applicability`

### Character of the revision
- consequence-lane-preserving
- fallback-explicit but vocabulary-resistant
- profile-local
- downstream-safety guard without a policy lattice

## rev0059 — 2026-04-27 14:47 America/New_York

This revision tests whether profile conformance needs explicit profile identity.

### Added
- `PROFILE-IDENTITY-EXPOSURE-TEST.md`

### Tightened
- `START_HERE.md`
- `README.md`
- `PROBLEM-FRAME.md`
- `TIMESTATE.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `DISCOVERY-REQUEST-SKETCH.md`
- `PROFILE-CONFORMANCE-MARKER-TEST.md`
- `FALLBACK-APPLICABILITY-VOCABULARY-TEST.md`
- `REQUIRED-DEFAULT-ABSENCE-TEST.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- current NTPv5 keeps protocol support and extension behavior explicit while leaving local assessment outside the core wire protocol
- NTS shows that setup/profile-like context can be explicitly established outside the later time-packet path
- Roughtime keeps message interpretation bound to compact tag/key identities without broad manifests
- RFC 9760 reinforces that profiles are real constraints/defaults, not mere labels
- the archive therefore adds `assessed_profile` as local/export scope for `profile_conformance`, while rejecting a profile manifest or negotiation layer

### Character of the revision
- profile-scope-focused
- export-boundary-aware
- manifest-resistant
- keeps the minimal wire claim small


## rev0060 — 2026-04-27 15:41 America/New_York

This revision tests how strong an explicit `assessed_profile` reference must be.

### Added
- `PROFILE-REFERENCE-GRANULARITY-TEST.md`

### Tightened
- `START_HERE.md`
- `README.md`
- `PROBLEM-FRAME.md`
- `TIMESTATE.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `DISCOVERY-REQUEST-SKETCH.md`
- `PROFILE-IDENTITY-EXPOSURE-TEST.md`
- `PROFILES.md`
- `QUESTIONS.md`
- `SOURCES.md`

### Research effect
Further source reading sharpened:
- NTPv5 uses explicit version/draft identification where ambiguity would matter, while still keeping local algorithms outside the wire protocol
- NTS shows that setup context can bind later time exchanges without repeating all parameters in every packet
- Roughtime uses compact tags, known keys, and signed delegation/evidence where stronger binding is needed
- RFC 9760 gives PTP profiles explicit identity fields, including profile name, number, version, identifier, and specifying authority
- the archive therefore uses boundary-tiered profile-reference strength: id+version, plus authority, digest, or signed binding only when the consuming boundary requires it

### Character of the revision
- reference-strength-focused
- digest-when-needed
- signed-binding-resistant by default
- keeps profile distribution separate from assessed-state export
