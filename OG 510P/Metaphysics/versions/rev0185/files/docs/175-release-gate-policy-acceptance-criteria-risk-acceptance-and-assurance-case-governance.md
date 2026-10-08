# 175. Release Gate Policy, Acceptance Criteria, Risk Acceptance, Waiver/Exception, Decision, and Assurance-Case Governance

## Core thesis

A claim can be locally warranted, evidence-linked, contradiction-aware, freshness-bounded, and defeasible while still not being release-safe. Rev0168 answered the question, **what warrants this claim and what defeats it?** Rev0169 adds the next gate: **what release decision is permitted after the warrant, the checks, the risks, the waivers, and the assurance argument have been inspected together?**

The target is not bureaucracy. The target is anti-laundering at the final boundary where a package becomes a release artifact. A validated zip is not an approval. A passing query suite is not a signoff. A claim graph is not a release decision. A warning is not risk acceptance. A waiver is not permission unless its scope, owner, expiration, affected gates, and accepted residual risk are explicit.

## What this release adds

Rev0169 adds six control surfaces:

1. `RELEASE_GATE_POLICY.yml` names blocking and advisory local gates, required evidence, gate classes, failure actions, and waiver permissions.
2. `ACCEPTANCE_CRITERIA_MATRIX.yml` turns broad gate names into concrete criteria with evidence artifacts, required checks, blocking class, and allowed/forbidden inferences.
3. `RELEASE_DECISION_LEDGER.yml` records the local release decision, gate results, waiver references, risk-acceptance references, assurance-case references, and decision language boundaries.
4. `WAIVER_EXCEPTION_LEDGER.yml` records whether any exception is active, denied, expired, or not used, and prevents a gate failure from being silently converted into permission.
5. `RISK_ACCEPTANCE_LEDGER.yml` records accepted local residual risks and explicitly refuses public-use, operational, domain-authoritative, and external-compliance risks.
6. `ASSURANCE_CASE_SKELETON.yml` names the top local assurance claim, supporting gate arguments, local evidence artifacts, open doubts, and forbidden assurance upgrades.

These artifacts are local release governance artifacts. They are not OPA/Rego policies, OSCAL assessment results, SACM assurance cases, SSDF certification, signed attestations, independent approvals, regulatory submissions, safety cases, public CI, or operational deployment approvals.

## Gate rule

A gate must have a stable identifier, gate class, required artifacts, required tools, acceptance criteria, evidence artifacts, decision record, waiver rule, and failure action. A blocking gate that fails must block local release language unless a scoped waiver is explicitly allowed, recorded, risk-accepted, and bounded. Rev0169 intentionally records no active blocking waiver.

## Acceptance-criteria rule

Acceptance criteria must be more granular than a gate name. A criterion must name its gate, required evidence, required check, blocking class, status, and prohibited shortcut. The archive must not say “the gate passed” where only the existence of a gate policy has been shown.

## Waiver and exception rule

An exception is not a release decision. A waiver may only narrow a gate obligation under a named scope and risk-acceptance record. Waivers cannot create external audit, source currency, public deployment, or domain authority. A denied or unused waiver must remain visible so later maintainers know that the shortcut was considered and rejected.

## Risk-acceptance rule

Risk acceptance is not risk deletion. Rev0169 accepts only local residual risks: incomplete historical normalization, local-only evidence, representative rather than exhaustive fixtures, and absence of public CI or external audit. It does not accept public-use, operational-deployment, high-stakes, legal, medical, financial, engineering, or source-current risks.

## Assurance-case rule

An assurance case skeleton is not an assurance standard implementation. The skeleton merely connects a top local release claim to arguments, gates, evidence artifacts, open doubts, and forbidden upgrade claims. Its purpose is to keep the release argument inspectable and retractable.

## Allowed claims after rev0169

The package may claim that it includes local gate policy, local acceptance criteria, a local decision ledger, a local waiver/exception ledger, a local risk-acceptance ledger, a local assurance-case skeleton, and a local gate checker that verifies representative structural integrity among these artifacts.

## Forbidden upgrade claims

The package must not claim external approval, signed attestation, policy-as-code deployment, OPA/Rego conformance, OSCAL assessment publication, SACM conformance, SSDF certification, public CI, public release-management system, safety case approval, regulatory assurance, public deployment readiness, operational authority, source currency, domain-authoritative review, or exhaustive QA.

## Open debt retained

- Gates are local YAML rows and Python checks, not external policy-as-code deployment.
- Acceptance criteria are current-release criteria, not historical backfill for all releases.
- The assurance case is a skeleton, not a complete formal assurance case.
- Waiver handling is structural and local; no independent authority has approved any exception.
- Risk acceptance covers archive-local residual risks only.
- No signature, identity proof, timestamping service, external approval, or public CI pipeline is introduced.

## Next likely layer

The next durable layer should be reproducibility-and-attestation boundary governance: build recipe capture, environment fingerprinting, generated-artifact determinism, transcript retention, signer/identity boundaries, and tamper-evidence rules. Rev0169 prepares for that by distinguishing local release decisions from signed attestations and external approvals.
