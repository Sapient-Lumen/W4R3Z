# 55 — Parameter & Key Transparency (PKT)

**Track:** A (Deployable core)


## Why this exists (paranoid assumption)
If an attacker can **substitute election parameters** (ballot definition, election public key, trustee set, disclosure policy, verifier suites), they can often cause:
- *silent vote redirection* (voters encrypt to an attacker key)
- *selective denial* (some voters see a different ballot style)
- *post-election disputes* that cannot be resolved cleanly

Therefore, **parameter distribution** must be treated as a first-class transparency problem, similar in spirit to transparency systems used for key distribution.

## Design goal
Make it *cryptographically and operationally hard* for anyone to show different “official parameters” to different people without producing publicly verifiable evidence.

## Core object: `ElectionParameterBundle` (EPB)
An EPB is a signed, content-addressed bundle that includes (at minimum):
- Election identifiers (jurisdiction, contest set, dates)
- Canonical ballot definition(s) + style rules
- Election public key material and crypto suite policy (incl. PQC/hybrid policy)
- Trustee roster + threshold policy
- Witness roster + checkpoint policy
- Receipt policy (states, deadlines)
- DisclosurePolicy (tally granularity; privacy budget)
- Client/verifier compatibility declarations

### Normative requirements
1. **EPB MUST be published to the PBB** as log entries before voting begins.
2. **EPB MUST be referenced by hash** in all ballot submissions and receipts.
3. **Clients MUST verify EPB inclusion + witness-quorum checkpoint** before allowing CAST.
4. **Any EPB update MUST create a new version** with strict monotonic versioning and explicit effective times.
5. **EPB changes during voting are prohibited** except for emergency actions explicitly declared in the EPB policy (and such actions MUST be publicly logged and auditable).

## Key Transparency patterns applied
Use a **Merkle-log transparency service** to distribute sensitive public data (keys and parameters) with:
- inclusion proofs
- consistency proofs
- independent monitoring

This spec uses the PBB as the primary transparency log. Optionally, run a separate **Key/Parameter Transparency log** (PKT log) with independent operators, and cross-checkpoint the PBB into it.

### Monitoring
- At least 2 independent monitors MUST continuously:
  - fetch the latest tree heads
  - validate consistency proofs
  - alert on conflicting views
  - archive checkpoints

## Hardening against “ballot-style discrimination”
- Ballot styles MUST be content-addressed and listed in the EPB.
- Clients MUST display EPB hash and ballot style hash (human-friendly short fingerprint) during verification.
- “Style selection” inputs MUST be validated via privacy-preserving eligibility logic (see `15-privacy-and-eligibility-tokens.md`).

## Evidence for disputes
- EPB hash + inclusion proof + checkpoint proof are admissible “what was official” evidence.
- If a voter presents a different EPB hash than the public archive, that is immediate evidence of substitution or client compromise.

## Open question
How to safely support last-minute ballot definition corrections without enabling discrimination? Recommendation: treat any correction as a **separate election instance** with explicit legal triggers.