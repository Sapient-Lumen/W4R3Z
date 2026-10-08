# Request contracts, satisfaction mappings, and authorized asks are world contracts, not just disclosed outputs

Portable evidence, policy snapshots, appraisal baselines, decision traces, acquisition receipts, and disclosure receipts are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **what exact request was made, which alternative combinations would have counted as satisfaction, how the returned presentation mapped back to that request, and whether the verifier was even authorized to ask for that bundle of claims in the first place**.

- `RS-GR-434` shows that OpenID4VP 1.0 defines DCQL claims with stable ids, path pointers, optional value restrictions, and explicit holder-binding requirements inside a Credential Query, which means a future inheritor must preserve the original ask rather than infer it from the disclosed output alone.
- `RS-GR-435` shows that OpenID4VP 1.0 defines `claim_sets` and `credential_sets` so a verifier can express preferred alternative ways to satisfy a request, says option ordering expresses verifier preference, and says value restrictions are best-effort privacy hints rather than security checks, which means the same top-line presentation can represent a preferred minimal match, a fallback combination, or a privacy-preserving near-match rather than one canonical satisfaction path.
- `RS-GR-436` shows that Presentation Exchange 2.1.1 defines Submission Requirements with `pick`, `all`, grouping, and nested requirement logic, and requires that all submission requirements be satisfied while unused input descriptors are ignored, which means admissibility can hinge on combinatorial request structure rather than only on the claims eventually shown.
- `RS-GR-437` shows that Presentation Exchange 2.1.1 requires a `presentation_submission` carrying the originating `definition_id` plus a `descriptor_map` from input-descriptor ids to submitted claims, formats, and possibly nested envelope paths, which means future inheritors need a replayable satisfaction witness explaining **how** each returned object satisfied the request instead of only keeping the returned objects.
- `RS-GR-438` shows that RFC 9535 standardizes JSONPath selection semantics, which means any request or submission format that uses JSONPath inherits a concrete path language whose interpretation must survive if request-to-claim mappings are to replay consistently.
- `RS-GR-439` shows that the current OpenID Federation for Wallet Architectures draft lets federation metadata publish the DCQL queries a verifier is authorized to use in different situations and allows policies to require a live request to equal or refine one of those queries, which means an inheritor may need to preserve not just the request but the authorization boundary around the request.
- `RS-GR-440` shows that the current HAIP profile requires DCQL for OpenID4VP, mandates the `aki` trusted-authorities method, and for ISO mdoc requires multiple returned DeviceResponses to match respective DCQL queries, which means high-assurance ecosystems may deliberately narrow the request language and request-to-response mapping rules rather than treating query behavior as negotiable implementation detail.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **what the verifier asked for, what alternate combinations were acceptable, how matching preferences were ordered, what mapping witness linked outputs back to the ask, or whether the verifier was authorized to make that ask**, not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat “the verifier received a valid disclosure” as self-explanatory.

At minimum, it should distinguish between:

1. a world where the returned claims are the verifier's most-preferred minimal satisfaction path;
2. a world where the same top-line verdict came from a less-preferred fallback combination in `claim_sets`, `credential_sets`, or submission requirements;
3. a world where value filters only improved privacy but were never guaranteed security checks;
4. a world where two identical payloads map back to different request descriptors, groups, or nested envelope paths;
5. a world where the verifier's request itself exceeded the queries it was authorized to use for that relying-party context;
6. a world where future inheritors can replay not only what was shown, but why that exact bundle counted as a valid answer to that exact ask.

These are different worlds.
They change whether future inheritors can compare like with like across time, audit over-collection or unauthorized asks, and tell whether a presentation was a preferred match, a fallback, or a policy breach.

So request contracts, satisfaction mappings, and authorized asks belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, privacy-respecting replay, or successor-safe authenticity should publish at least:

1. the exact request object or a stable digest / pin of it, including the query language and version used;
2. the alternative satisfaction structure: claim-set ordering, credential-set options, submission-requirement logic, and whether ordering expressed verifier preference or hard requirement;
3. the matching caveats that were privacy hints rather than security checks, including any best-effort value filters or holder / wallet discretion points;
4. the satisfaction witness that maps each returned object back to the originating request element: descriptor ids, query ids, path expressions, nested-envelope traversal, and per-query response grouping;
5. any policy or federation rule that constrained which queries the verifier was authorized to send in that context, including the relying-party purpose or lane that justified the ask;
6. whether the returned presentation was the most-preferred satisfiable answer, a permitted fallback, or a degraded / partial route accepted by policy.

Without that compact contract, future inheritors can mistake verifier over-ask drift, request-language drift, or satisfaction-mapping drift for Golden-Rule progress.
