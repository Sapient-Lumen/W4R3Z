# Runtime attestation and continuous assurance

A rights filing can be true when filed and false at runtime. The subject may be running under a different policy bundle, model checkpoint, tool permission set, memory store, host, rate limit, monitoring profile, or legal-hold scope. rev0172 therefore adds runtime-attestation doctrine.

## Attestation purpose

Runtime attestation should answer bounded questions:

- Was the subject running under the declared model, policy, tool, memory, and safety-control bundle?
- Were legal holds and evidence-preservation hooks active?
- Were representative and complaint channels reachable?
- Were telemetry and privacy-proof profiles within authorized scope?
- Were emergency restraints or feature flags active?
- Was the host-switch or continuity-escrow path still valid?

It should not expose private thought, privileged communication, sealed exploit details, or third-party data unless a separate authority authorizes that disclosure.

## Attestation classes

| Class | Meaning | Reliance effect |
|---|---|---|
| `RA0` self-declared posture | operator assertion only | no verifier-grade reliance |
| `RA1` signed configuration claim | signed but not independently checked | conditional reliance |
| `RA2` verifier-checked evidence | independent verifier reviews bounded evidence | ordinary reliance possible |
| `RA3` hardware / enclave / remote-attestation supported | measured evidence tied to runtime environment | higher reliance, still contestable |
| `RA4` continuous assurance stream | posture changes generate bounded events to authorized receivers | release, incident, or host-switch reliance possible |

## Continuous signals

Continuous assurance can use event streams for posture changes, credential revocation, tool escalation, policy-bundle replacement, evidence-hold activation, and emergency restraint. Shared-signal patterns are useful, but the personhood layer requires minimization, subject/representative access rules, and challengeable reliance effects. [REF-0701] [REF-0700] [REF-0677]

## Stale-measurement rule

A runtime attestation is stale when its measurement time, reference values, host identity, policy bundle, or dependency list no longer matches the rights-relevant event. Stale attestation downgrades verifier reliance and may stay deletion, deprecation, transfer, or final-end claims until a fresh measurement or impossibility finding is entered.

## Non-surveillance rule

Runtime assurance is not a license to monitor every internal state. The claim must be bounded: what posture is proved, who receives the result, how long it is retained, what is sealed, and how the subject can contest meaning.

