# SOURCES

This archive stores citations and reasons for keeping them, not bulky source bodies.

## Core sources
- RFC 5905 — NTP root delay, root dispersion, reference timestamp, and synchronization distance
- RFC 8915 — secure NTP and delay-attack limits
- NIST Internet Time Service
- NIST Authenticated NTP Service
- BIPM / CGPM Resolution 4 (2022) — UTC continuity / 2035 edge
- GPS.gov resilience guidance for responsible use of PNT
- NIST IR 8323r1 Foundational PNT Profile
- NIST Technical Note 2189 — critical-infrastructure timing dependencies
- GPS.gov: GPS and Financial Institutions — traceability / timestamping signal
- NIST Technical Note 2187 — resilient GNSS-independent UTC architecture
- NIST: How UTC(NIST) Works — ensemble and holdover signal
- NIST: Reliability of UTC(NIST) — redundancy and continuity signal
- NIST glossary entry for holdover
- CISA time guidance / resilient timing guidance — enterprise resilience and testing signal
- chrony documentation / FAQ — practical maximum-error, minsources, and source-selection policy signals
- Roughtime draft — timestamp + radius and multi-server inconsistency signal
- Spanner / TrueTime paper — interval semantics and bounded uncertainty

## Newly load-bearing in rev0014
- NIST power-profile / substation material — sub-microsecond alignment pressure and known-uncertainty timestamps
- NIST telecom timing material — phase, frequency, and time-of-day demanded together, but not always symmetrically
- packet-synchronization research — one-way frequency vs two-way time/phase distinction
- clock-metric material — frequency behavior often manifests operationally through accumulated time/phase error

## Newly load-bearing in rev0015
- NIST clock-characterization material — some programs need syntonization rather than synchronization to UTC
- NIST telecom / mobile standards material — frequency accuracy can be a first-class deployment requirement
- NIST IEEE 1588 / ITU profile material — frequency profile and one-way support create a real alternate lane
- NIST stratum material — frequency-offset quality maps directly into continuity over time
- NIST TN 2189 — frequency syntonization is a distinct timing-dependency category

## Newly load-bearing in rev0016
- NIST telecom / IEEE 1588 materials — P4 contains both telecom frequency-only / frequency-first and phase/time-alignment pathways
- SyncE-oriented timing material — physical-layer frequency continuity has distinct deployment assumptions and failure modes
- mobile-network timing material — frequency accuracy and phase/time alignment are both required, but not for the same immediate reasons

## Newly load-bearing in rev0017
- telecom-profile family material — packet-based frequency delivery and packet-based phase/time delivery still sit inside one broader telecom timing family
- mobile / PTP deployment material — the same endpoints and network stacks can carry both rate and phase/time concerns
- SyncE plus IEEE-1588 deployment material — the combined stack is itself evidence of profile cohesion

## Newly load-bearing in rev0018
- NIST frequency-metrology material — offset and stability are distinct, so the promoted field should not pretend one alone is the whole story
- telecom performance material — clock performance is often carried by bounded quality/accuracy claims rather than a single raw offset value
- holdover material — rate trust degrades over a validity window, which supports a bound-oriented field rather than a naked point estimate

## Newly load-bearing in rev0019
- loop-control / clock-control material — residual frequency error can remain even in controlled loops
- holdover and telecom path-switch material — the trustworthiness of the claim changes under holdover and recovery
- timing-test material — holdover, stability, clock drift, and phase change rate are measured separately, which justifies keeping the field narrow and context-dependent

## Newly load-bearing in rev0020
- NIST timing-architecture material — frequency can be provided by an individual clock, which reduces pressure for extra network-facing semantics in some Lane A cases
- UTC(NIST) holdover material — stability estimates are already used to estimate holdover performance, supporting the current division between the bound and neighboring semantics
- CPS timing material — stability, holdover capability, traceability, and switchover time all matter, but not yet in a way that clearly forces a second promoted Lane A field

## Newly load-bearing in rev0021
- NIST CPS timing glossary/material — time error is the phase-side quantity, synonymous with phase error but expressed in time units
- packet-clock testing material — time error can contain static and dynamic components without yet forcing two first-class phase fields
- measurement and clock-comparison material — phase-side trust naturally presents as a time-domain bound

## Newly load-bearing in rev0022
- telecom time-error accumulation material — constant and dynamic time-error structure exists, but does not yet force two promoted archive fields
- domain-specific time-quality signaling — detailed usability indicators can remain profile-local
- phase/time metrics material — time-side statistics still depend partly on frequency behavior, reinforcing the value of the paired field view

## Newly load-bearing in rev0023
- profile-local time-quality signaling — real systems already separate usability judgment from underlying time-error ranges
- telecom/base-station requirement material — rate-facing tolerances already function as threshold-bearing reasons, not just categorical labels
- smart-grid timing guidance — end applications benefit from real-time time-uncertainty values for deciding required degree of accuracy

## Newly load-bearing in rev0024
- systems such as Spanner / TrueTime — uncertainty-bearing interfaces can affect application behavior directly
- secure time protocols such as Roughtime — exported bounded time information can be part of the client contract
- but the archive still lacks enough cross-profile interface pressure to harden the provisional pair into its own object

## Newly load-bearing in rev0025
- Spanner / TrueTime API shape — interval semantics already satisfy the main P2 uncertainty-bearing client contract
- synchrophasor / power-profile timing material — time quality and maximum-time-error style signals can be boundary-bearing rather than merely explanatory
- P5 thus becomes the first clear profile-local widened boundary for `time_error_bound`
- but one widened boundary is still not enough recurrence for archive-wide promotion

## Newly load-bearing in rev0026
- NIST financial-market timing material — finance strongly pressures traceability, verifiability, calibration, and audit-facing timing evidence
- telecom synchronization-control material — status messaging, holdover, and path rearrangement are boundary-bearing but not yet a clean repetition of the same widened runtime contract
- this weakens the case for false recurrence while strengthening the case that `traceability_posture` may become the next boundary-bearing hook

## Newly load-bearing in rev0027
- NIST fair-stock-trades material — stock-market timing is explicitly traceable to NIST standards and treated as a live requirement, not just background metrology
- synchrophasor / PMU traceability material — time quality and time status explicitly indicate traceability to UTC, time accuracy, and leap-second status
- this gives `traceability_posture` a same-shape cross-profile recurrence stronger than the current broader-object recurrence

## Newly load-bearing in rev0028
- NIST TN 2189 terminology framing — traceability is discussed alongside accuracy, stability, and resolution rather than being collapsed into them
- finance timing material — keeps pressing accurate, traceable, verifiable synchronization rather than a giant provenance vocabulary
- synchrophasor traceability material — bundles traceability with accuracy and leap-status, which supports adjacency rather than a collapsed mega-hook

## Newly load-bearing in rev0029
- telecom timing material — UTC-traceable network sync quality and PRTC-traceable reference state fit the existing `reference_anchor` axis
- telecom protection / rearrangement material — loss of traceability is propagated and drives holdover / backup-path behavior, which supports keeping control semantics adjacent rather than inside the hook
- the thin two-axis model therefore survives a P4 pass provisionally

## Newly load-bearing in rev0030
- NIST metrology material — a measurement made using a NIST reference with known and documented uncertainty is already traceable, which makes `traceable` a substantive hook state
- finance timing material — stronger verification appears as an additional confirmation layer near the customer rather than proof that the minimal hook needs a dedicated `verified` state
- the archive can therefore demote `verified` to an overlay and keep the minimal evidence axis smaller

## Newly load-bearing in rev0031
- UTC(k) and named laboratory realizations remain meaningful in finance / metrology contexts and justify a distinct named-UTC category
- telecom profile references such as PRTC justify a distinct profile-reference category
- generic UTC claims still matter separately from named realizations, so the anchor axis can be reduced but not collapsed too far

## Newly load-bearing in rev0032
- holdover is explicitly an operating condition after loss of a controlling reference, which supports modeling much of `local_private` variation outside the anchor axis
- local oscillators and local clocks vary in capability, but current evidence still points to regime / holdover semantics as the main place for that variation
- no concrete boundary yet forces a split of `local_private`, so the category survives for now

## Source discipline
- cite briefly
- paraphrase tightly
- keep only sources that sharpen the archive's shape

## Newly load-bearing in rev0033
- NTPv5 design material — timescale is becoming an explicit wire-level concept, including multiple supported timescales and separate leap handling
- NTS (RFC 8915) — server authentication and key establishment are explicit, but delay attacks remain possible and authentication is not the same as traceability
- Roughtime draft — signed replies, uncertainty radius, delegated keys, and malfeasance evidence show what a native evidence-bearing time contract can look like
- NIST traceability material — traceability requires an unbroken chain to a reference with documented uncertainty, which supports keeping anchor/evidence semantics distinct from mere identity
- TrueTime / interval APIs — a client-visible bounded-time contract is useful, which strengthens the case for surfacing traceability as a native adjacent hook rather than a side channel

## Newly load-bearing in rev0034
- synchrophasor / PMU time-quality material — traceability to UTC, time accuracy, and leap-second status are expected at the measurement boundary, which makes omission too lossy there
- telecom synchronization-status material — quality/status messaging is used live for loop avoidance, reference selection, and holdover behavior, which makes traceability-adjacent state default-visible in the synchronization control plane
- finance timing material — strong traceability and verifiability pressure often lands on service, calibration, and audit boundaries rather than on the thinnest generic runtime client state
- NTPv5 and related requirements material — making time semantics visible on the wire does not automatically imply that every adjacent semantic belongs in the minimal core

## Newly load-bearing in rev0035
- telecom timing material — frequency transfer and phase/time transfer are explicitly separated in deployed precision-network architectures, which strengthens `sync_dimension` as a default-visible boundary concern in P4
- smart-grid / critical-infrastructure timing material — time, phase, and frequency remain distinct requirement categories, which strengthens `sync_dimension` as more than a descriptive note in P5-like boundaries
- synchrophasor and telecom status material together — support a middle classification in which some hooks are not universal but still default-visible where omission would mislead live control or measurement participants

## Newly load-bearing in rev0036
- telecom synchronization-status material — downstream participants must learn when references are unacceptable, holdover has begun, and backup selection is underway, but this still looks more like state/quality visibility than a reusable holdover class
- power-profile timing-quality material — unlocked/holdover indication and time-quality signaling are boundary-bearing, again supporting state+quality more strongly than a richer class
- local oscillator / GPSDO holdover material — holdover behavior varies strongly with oscillator type, steering method, and learned behavior, which makes `holdover_class` look useful but still too context-bound for `profile_default`

## Newly load-bearing in rev0037
- telecom recovery/status material — keeps pressing control-plane status and selection semantics more strongly than a reusable locality/validity hook
- PNT profile material — distinguishes full versus partial timing solutions and absolute versus relative timing needs, which supports honest degraded operation but still does not force `validity_scope` into `profile_default`
- local continuity pressure — remains the strongest reason to keep `validity_scope` alive, but still concentrated enough that the hook stays an extension rather than a tier member

## Newly load-bearing in rev0038
- NTPv5 draft — now clearly frames itself as an on-the-wire protocol while leaving source selection, filtering, and clock discipline out of scope; this supports a wire-claim / local-assessment split
- NTPv5 draft — explicit timescale fields and alternate-timescale extension support reinforce that some semantics belong natively on the wire without forcing every client judgment there too
- RFC 8915 (NTS) — authenticated setup is separated from later synchronization packets, which supports keeping identity/auth state distinct from later assessed timing state
- Roughtime draft — compact signed responses with `MIDP` and `RADI`, plus delegated-key certificates, show a small bounded-time claim can travel with evidence on the wire
- Spanner / TrueTime — a client-visible interval API with uncertainty shows why the local assessed state may still need to be richer than the wire claim

## Newly load-bearing in rev0039
- NIST / PMU traceability material — synchrophasor boundaries explicitly expect time status to indicate traceability to UTC, time accuracy, and leap-second status; this is strong pressure for a live claim/status surface
- NIST TMAS material — customers continuously compare their local standard to UTC(NIST) and must be able to state uncertainty relative to UTC(NIST), which strengthens the assessed/service-side form of traceability
- NIST finance material — stock markets receive real-time remote calibration traceable to NIST standards, which reinforces that finance traceability often lives through monitored service and calibration boundaries
- FINRA Rule 6820 — firms must synchronize to NIST within stated tolerances and maintain procedures, logs, and certification, which reinforces the local/audit-assessed side of the same hook

## Newly load-bearing in rev0040
- telecom profile material — distinguishes explicit frequency and time/phase profiles and defines a PTP profile as a selected set of options/features to meet an application requirement; this supports `sync_dimension` as profile-declared first
- telecom profile material — the frequency profile and time/phase profile differ in allowed mechanisms and assumptions, reinforcing that the dimension changes the synchronization arrangement itself
- NIST smart-grid timing material — explicitly calls for assured precision time, phase, and frequency synchronization, supporting the view that these are requirement/profile families rather than merely local inferences

## Newly load-bearing in rev0041
- NTPv5 draft — uses extension fields for optional features and future extensibility, supporting optional native surfaces without widening the core header
- telecom frequency-profile material — uses unicast message negotiation, showing that explicit request behavior can be real but still narrow and profile-shaped
- Roughtime draft — version-list request/response behavior offers an example of lightweight compatibility/discovery without a broad negotiation subsystem
- PMU / synchrophasor traceability material — still supports keeping some boundaries profile-fixed rather than request-driven

## Newly load-bearing in rev0042
- NTPv5 draft — extension fields continue to justify optional native surfaces without enlarging the core exchange
- telecom frequency-profile material — narrow unicast negotiation supports request behavior without implying a broad capability subsystem
- Roughtime draft — version-list discovery supports the archive's preference for lightweight discovery/compatibility surfaces
- PMU / synchrophasor boundary expectations — continue to justify keeping some surfaces profile-fixed by default

## Newly load-bearing in rev0043
- NTPv5 requirements material — intermediates may modify timing packets without breaking protected operation, supporting the need to name cross-boundary honesty behaviors explicitly
- telecom boundary-clock material — boundaries can terminate an incoming timing flow, recover timing locally, and generate a new downstream flow, supporting `restate`
- telecom protection material — downstream chains may need to be told that a stronger upstream traceability condition no longer holds, supporting `downgrade`
- the archive's earlier non-upgrade rule — still supports keeping preservation and restatement from becoming silent upgrade paths

## Newly load-bearing in rev0044
- telecom profile material — compact failure distinctions such as lossSync, lossAnnounce, and unusable justify a tiny cause layer without justifying a large registry
- NTP reason/status coding — shows that compact coded causes can be useful without becoming a full workflow system
- Roughtime malfeasance/inconsistency reporting — supports keeping conflict as a distinct small reason category
- the archive's own relay verbs — remain primary, which keeps the new reason layer optional rather than structural

## Newly load-bearing in rev0045
- NIST IR 8323r1 / NIST glossary material — integrity includes timely warnings when PNT data should not be used; this supports giving `unknown` some explicit downstream consequence rather than treating it as a harmless descriptive state
- NIST smart-grid timing guidance — real-time uncertainty values help an application decide whether the required degree of accuracy is still met; this supports withdrawing stronger applicability claims when the needed hook state is no longer known
- telecom PTSF / unusable material — explicit lossSync / lossAnnounce / unusable states drive alternate-master selection or holdover rather than silent preservation of the stronger downstream judgment
- IEEE C37.238 / synchrophasor time-quality material — usability is tied to known time-error ranges, which supports keeping `unknown` from silently preserving a stronger hook-dependent applicability label

## Newly load-bearing in rev0046
- RFC 5905 / NTP registry update material — compact kiss-o'-death signaling shows that some direct-source reasons can legitimately travel on the wire
- NTPv5 draft — the on-wire protocol remains intentionally narrow and leaves algorithms / local judgments out of scope, supporting a non-wire-primary placement for the broader reason layer
- telecom PTP profile / protection material — failure distinctions such as lossSync, lossAnnounce, and unusable are deeply tied to master selection, protection, and holdover behavior at boundaries, supporting boundary-first placement
- Roughtime draft — compact wire evidence remains useful, but it still does not justify making every local or relay-generated reason a universal wire object

## Newly load-bearing in rev0047
- telecom protection material — downstream devices are explicitly informed that a reference is no longer PRTC traceable and change behavior while a backup path is selected, supporting retained boundary context alongside recomputed state
- IEEE-1588 / telecom timing tutorial material — path-trace and synchronization-uncertain style signals show that chain/boundary context can matter downstream without being the time estimate itself
- NTPv5 draft — reference-ID exchange for loop detection is chain context rather than time state, reinforcing the case for a tiny named boundary wrapper instead of smearing such context into core timing fields

## Newly load-bearing in rev0048
- telecom protection material — loss of PRTC traceability changes downstream behavior during rearrangement and then yields to a new steady state once a backup path is selected, supporting state-coupled rather than independently retained boundary explanation
- PTP path-trace material — forwarding and dropping behavior exists for richer chain-context signals, which supports keeping those semantics outside the tiny `boundary_context` wrapper for now
- NTPv5 reference-ID propagation — temporary loop-detection context has its own convergence behavior, reinforcing the distinction between richer chain context and the archive's minimal action+reason wrapper

## Newly load-bearing in rev0049
- telecom protection material — downstream devices must be informed that traceability is lost so that holdover and path-selection behavior can change, supporting profile-default export in some control-path cases
- PMU / measurement-oriented timing material — strongly pressures default visibility of timing state and quality, but not equally strong pressure for always exporting the boundary explanation itself
- NTPv5 reference-ID exchange — chain context can be exchanged when needed rather than pushed in every minimal response, supporting requestable-by-default visibility

## Newly load-bearing in rev0050
- NTPv5 optional reference-ID exchange material — extra chain context can be retrieved through the existing optional extension/request pattern rather than through a separate discovery plane
- telecom unicast negotiation material — extra synchronization service/context is requested through a narrow signaling surface, supporting reuse of one small mechanism rather than proliferation of visibility channels
- the archive's own current layering — the remaining difference is semantic subject matter (state versus explanation), which supports subject-level separation instead of mechanism-level duplication

## Newly load-bearing in rev0051
- NTPv5 extension-field format — typed optional fields already separate meanings without an extra namespace hierarchy, supporting a flat shared request surface
- telecom signaling/TLV practice — distinct item/type identities are enough for optional request and signaling within one surface, again supporting flatness
- Roughtime tagged-item design — meaning is carried by stable item identity rather than by an extra namespace layer above the tags


## Newly load-bearing in rev0052
- NTPv5 draft-08 — specific extension fields and request/response inclusion rules support item-level optionality rather than bundle aliases
- Roughtime draft-19 — tag-based request/response structure and version tags support explicit item identity without a bundle layer
- PTP telecom profile material — profiles can bundle application choices above the exchange surface while unicast/signaling behavior remains specific
- RFC 9760 PTP Enterprise Profile — a profile may forbid optional mechanisms directly, which supports profile policy without request bundles
- IEEE C37.118.1 synchrophasor material — traceability, time quality, accuracy, leap status, and measurement semantics are default reporting requirements rather than request aliases

## Newly load-bearing in rev0053
- NTPv5 draft-08 — the specification is scoped to on-wire exchange and keeps optional behavior at concrete extension-field/item level, supporting local expansion before shared requests rather than operator aliases as native syntax: <https://datatracker.ietf.org/doc/draft-ietf-ntp-ntpv5/>
- Roughtime draft-19 — mandatory and registered tags carry request/response identity while unknown tags are ignored, supporting explicit item identity rather than human-facing intention names: <https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/>
- RFC 9760 PTP Enterprise Profile — profile constraints, message rates, forbidden options, and management/security guidance sit outside ordinary timing exchange subjects, supporting a separate operator/configuration layer without alias promotion: <https://datatracker.ietf.org/doc/html/rfc9760>
- NTPv5 requirements draft-04 — remote monitoring is excluded from the core protocol while separate extension specifications remain possible, supporting a boundary between operational surfaces and core synchronization exchange: <https://datatracker.ietf.org/doc/html/draft-ietf-ntp-ntpv5-requirements-04>

## Newly load-bearing in rev0054
- NTPv5 draft-08 — per-poll request formation, item/extension-level handling, and stateless basic server operation support exchange-scoped optional requests rather than implicit sticky request state: <https://datatracker.ietf.org/doc/draft-ietf-ntp-ntpv5/>
- Roughtime draft-19 — nonce-bound requests, tag-level identity, ignored unknown tags, and lack of authenticated error reporting support treating each request as the accountable unit: <https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/>
- RFC 8915 NTS — separates setup/key establishment from ordinary time synchronization and keeps required server-side per-client state out of the time-packet path, supporting explicit setup state rather than implicit request persistence: <https://www.rfc-editor.org/rfc/rfc8915.html>
- RFC 9760 PTP Enterprise Profile — defines profiles as explicit constraints on required/allowed/forbidden PTP behavior, sets profile defaults, and forbids unicast negotiation in that profile; this supports separating profile-fixed defaults from request lifetime: <https://datatracker.ietf.org/doc/html/rfc9760>



## Newly load-bearing in rev0055
- NTPv5 draft-08 — request extension fields normally echo by item unless the field specification says otherwise or the server lacks support; excluded fields use padding for length symmetry, and clients may interpret expected-field absence as lack of support, supporting narrow item-level absence meaning rather than a broad error object: <https://datatracker.ietf.org/doc/html/draft-ietf-ntp-ntpv5/>
- NTPv5 draft-08 — compact authentication failure signaling through the Authentication NAK flag supports small targeted result signals when they are truly protocol-bearing: <https://datatracker.ietf.org/doc/html/draft-ietf-ntp-ntpv5/>
- Roughtime draft-19 — deliberately provides no error-reporting mechanism for malformed requests, unsupported versions, or unknown server-key selectors, supporting silence at invalid or unauthenticated protocol edges rather than universal negative results: <https://datatracker.ietf.org/doc/html/draft-ietf-ntp-roughtime/>
- RFC 9760 PTP Enterprise Profile — pairs Delay Request and Delay Response behavior directly while treating unicast negotiation as profile-forbidden/ignored in this profile and discouraging insecure PTP management messages, supporting profile/configuration handling instead of a general timing-packet error taxonomy: <https://datatracker.ietf.org/doc/html/rfc9760>


## Newly load-bearing in rev0056
- NTPv5 draft-08 — separates a compact on-wire protocol from client algorithms, treats extension-field absence as narrow item-level support information, and defines server-maintained core response values; this supports separating packet validity, optional item absence, and profile satisfaction: <https://datatracker.ietf.org/doc/html/draft-ietf-ntp-ntpv5/>
- Roughtime draft-19 — mandatory request/response tags and signed `SREP` contents make response validity contract-shaped without adding a broad error-reporting surface; this supports treating required/default absence as contract failure rather than generic optional silence: <https://datatracker.ietf.org/doc/html/draft-ietf-ntp-roughtime/>
- RFC 9760 PTP Enterprise Profile — defines PTP profiles as constraints on required, allowed, and forbidden options/values, sets profile defaults, and forbids or requires specific behavior; this supports profile nonconformance as distinct from ordinary message parsing: <https://datatracker.ietf.org/doc/html/rfc9760>
- NTPv5 requirements draft-04 — favors data minimization, extensions for optional data, ignored unknown extensions, and keeping remote monitoring out of the core; this supports not adding a universal profile-error object while still preserving explicit profile/local consequence handling: <https://datatracker.ietf.org/doc/html/draft-ietf-ntp-ntpv5-requirements-04>

## Newly load-bearing in rev0057
- NTPv5 draft — still supports keeping the ordinary wire exchange narrow and separating local algorithms / judgments from the core protocol surface.
- NTPv5 algorithms draft — says algorithms need explicit behavior when required extension fields are not present, strengthening the need for an explicit local outcome without forcing a wire error layer.
- Roughtime draft — compact signed evidence plus the absence of general protocol error reporting supports local conformance assessment rather than broad response diagnostics.
- RFC 9760 — defines a PTP profile as constraints over required, allowed, and forbidden options / attributes, supporting profile-shaped satisfaction distinct from packet well-formedness.

## Newly load-bearing in rev0058
- NTPv5 draft-08 — keeps the protocol scoped to on-wire exchange, leaves algorithms and local judgments outside the core, and treats extension fields item-specifically; this supports not creating a universal fallback-applicability vocabulary: <https://datatracker.ietf.org/doc/draft-ietf-ntp-ntpv5/>
- Roughtime draft-19 — compact signed responses, required tags, ignored unknown tags, and deliberate exclusion of general error reporting support keeping fallback assessment local/profile-shaped rather than response-diagnostic-shaped: <https://datatracker.ietf.org/doc/html/draft-ietf-ntp-roughtime-19>
- RFC 9760 PTP Enterprise Profile — profiles set required, permitted, and prohibited options and profile-specific defaults, supporting profile-local fallback semantics instead of global fallback labels: <https://datatracker.ietf.org/doc/html/rfc9760>
- NIST Precision Timing for Smart Grid Systems — application requirements include uncertainty values and loss-of-reference behavior, supporting explicit lowered applicability for downstream use rather than a bare fallback marker: <https://www.nist.gov/programs-projects/precision-timing-smart-grid-systems>
- NIST TMAS and FINRA Rule 6820 material — traceability, uncertainty, tolerance, synchronization, logging, and certification demands differ by application boundary, reinforcing that fallback applicability is profile/domain-defined rather than universal: <https://www.nist.gov/programs-projects/time-measurement-and-analysis-service-tmas> and <https://www.finra.org/rules-guidance/rulebooks/finra-rules/6820>

## Newly load-bearing in rev0059
- NTPv5 draft-08 — the current draft keeps the on-wire protocol separate from local algorithms and makes protocol-version / extension support explicit where needed; this supports profile identity as local/export scope rather than a mandatory wire field: <https://datatracker.ietf.org/doc/draft-ietf-ntp-ntpv5/>
- RFC 8915 NTS — NTS-KE explicitly negotiates parameters and supplies cookies before ordinary NTP synchronization, showing that context can be established outside the time-packet path when the boundary is explicit: <https://datatracker.ietf.org/doc/html/rfc8915>
- Roughtime draft-19 — compact tag identity, server-key selection, nonce binding, and signed response structure support resolvable interpretation without a broad profile manifest: <https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/>
- RFC 9760 PTP Enterprise Profile — PTP profiles specify required, permitted, prohibited, and default behavior, supporting profile identity as semantically load-bearing for conformance judgments: <https://datatracker.ietf.org/doc/html/rfc9760>
- IETF NTP working-group document list — as of this revision, NTPv5 draft-08 and Roughtime draft-19 are the current relevant NTP WG drafts, so the archive keeps citations to current draft pages rather than storing draft PDFs: <https://datatracker.ietf.org/group/ntp/documents/>

## Newly load-bearing in rev0060
- NTPv5 draft-08 — the draft still keeps the on-wire protocol separate from client algorithms, but its draft-identification extension requires a full draft name including version and refuses unrecognized draft identifiers; this supports versioned identity where interpretation would otherwise drift without requiring a profile manifest in every packet: <https://datatracker.ietf.org/doc/html/draft-ietf-ntp-ntpv5>
- RFC 8915 NTS — NTS-KE negotiates parameters and supplies cookies before ordinary time synchronization, supporting explicit setup/context binding outside the later time-packet path: <https://datatracker.ietf.org/doc/html/rfc8915>
- Roughtime draft-19 — response validation depends on compact tags, nonce/Merkle evidence, delegated public keys, and a long-term public key known by other means; this supports stronger binding where needed without broad manifests: <https://datatracker.ietf.org/doc/html/draft-ietf-ntp-roughtime>
- RFC 9760 PTP Enterprise Profile — profile identification includes profile name, number, version, identifier, and specifying authority, reinforcing that profile references need enough identity to recover profile rules: <https://datatracker.ietf.org/doc/html/rfc9760>
- IETF NTP working-group document list — as of this revision, NTPv5 draft-08 and Roughtime draft-19 remain current relevant NTP WG documents, so the archive cites current document pages rather than storing drafts or PDFs: <https://datatracker.ietf.org/group/ntp/documents/>

