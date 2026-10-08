# Discovery publication and identity-disclosure spec

## Purpose

The archive already has discovery policy, publication profiles, known-host records, route leases, exposure reports, and control-access posture.
What it still lacked was one durable public contract for a more privacy-critical operator question:

> what identifiers, endpoints, share facts, or reachability facts am I publishing right now, to which audience, by which mechanism, with what residual leakage if I narrow it later?

This document answers that question.
It exists so AnonSync does not recreate a common sync-product failure mode where discovery settings talk only about connection success while the real disclosure boundary remains scattered across tracker toggles, LAN search, pinned hosts, cached endpoints, and support-article memory.

## Resilio-derived motivation

Current Resilio docs still distribute disclosure truth across several separate surfaces:

- the ports/protocols article says Sync connects to tracker infrastructure and communicates its public and local IP addresses plus the list of shares it has so peers can learn each other's addresses
- the key-flow article says LAN discovery packets contain associated `ShareID`s plus `IP:port`
- the same key-flow article says predefined hosts receive the local peer's `ShareID` information and IP when contacted
- folder preferences then place tracker, relay, LAN search, and predefined hosts together as convenience toggles for finding peers
- mobile docs repeat that predefined hosts can still be used even with relay, tracker, and LAN search off

That is useful documentation.
It is not one trustworthy disclosure contract.
An operator still has to reconstruct:

- whether a setting changes who can discover the node versus only how the node dials out
- whether the published fact is a stable device identity, a share identifier, a local/public endpoint, or only a willingness to relay
- whether narrowing the policy stops future publication only or also clears old learned/cached state
- whether one manually pinned path still discloses self to that endpoint even when ambient discovery is otherwise off

Syncthing's security docs are a useful contrast point because they explicitly say that global discovery reveals device ID and listening ports to discovery servers and that local discovery reveals device ID and listening port on the LAN, with explicit trade-offs when disabled.
AnonSync should be at least that explicit, and more receipt-bearing.

## Core rule

Discovery publication is a first-class disclosure boundary, not a side effect of route preference.
The product must let the operator answer, from one surface:

- which audience classes can currently learn anything about this subject
- which fact classes each audience can learn
- which publication is durable policy versus temporary widening
- what residue remains after narrowing or endpoint rotation
- what receipt proves the widening, narrowing, or residue-clear step later

If the operator still has to infer those answers from transport icons, tracker toggles, or support notes about cache clearing, the model is still too implicit.

## Public objects

### Disclosure profile

A first-class summary of the audiences and fact classes a subject is willing to publish.
This is related to route/discovery policy, but it is not the same thing.

Fields:

- `disclosure_profile_id`
- `scope_type` (`system`, `policy`, `share`, `peer`, `constellation`)
- `scope_id` nullable
- `publication_profile_ref`
- `audience_classes[]` (`none`, `local-broadcast-domain`, `approved-peer`, `named-endpoint`, `private-infra`, `public-infra`)
- `identity_fact_classes[]` (`device-stable-id`, `ephemeral-device-alias`, `member-class`, `share-membership`, `share-label`, `share-class`)
- `endpoint_fact_classes[]` (`listen-port`, `local-ip`, `public-ip`, `overlay-endpoint`, `known-host-address`, `relay-reachability`)
- `query_behaviors[]` (`announce`, `lookup`, `dial-only`, `accept-only`, `cache-retain`)
- `residual_disclosure_policy` (`none`, `ttl-bound`, `provider-defined`, `until-cleared`, `rotate-required`)
- `narrowing_requirements[]` (`none`, `clear-cache`, `wait-ttl`, `rotate-endpoint`, `rotate-share-artifact`, `review-required`)
- `baseline_policy_refs[]`
- `active_override_refs[]`
- `active_findings[]`
- `updated_at`
- `receipt_refs[]`

### Disclosure report

A first-class explanation object answering what is actually being disclosed right now and what would widen or narrow that boundary.

Fields:

- `disclosure_report_id`
- `subject_ref`
- `baseline_disclosure_profile_ref`
- `effective_disclosure_profile_ref`
- `effective_audiences[]`
- `effective_fact_matrix[]`
- `residual_findings[]`
- `widening_steps[]`
- `narrowing_steps[]`
- `cache_or_residue_refs[]`
- `generated_at`
- `decision_trace_ref` nullable

Each `effective_fact_matrix[]` entry should at least name:

- `audience_class`
- `fact_classes[]`
- `mechanisms[]` (`lan-broadcast`, `private-discovery`, `public-tracker`, `known-host-dial`, `relay-registration`, `overlay-publish`, `manual-artifact`)
- `freshness`
- `source_refs[]`

### Residual disclosure finding

A first-class warning that earlier publication may still be inferable even though future publication has narrowed.

Fields:

- `residual_disclosure_id`
- `subject_ref`
- `cause` (`cached-endpoint`, `provider-retention`, `share-artifact-still-valid`, `peer-memory`, `manual-known-host`, `recent-lan-announcement`)
- `affected_audiences[]`
- `affected_fact_classes[]`
- `clearance_actions[]`
- `expected_decay` (`immediate`, `ttl-bound`, `manual-only`, `unknown`)
- `severity`
- `generated_at`

### Disclosure receipt

A durable record proving that publication posture changed or that residual disclosure was reviewed/cleared.

Fields:

- `disclosure_receipt_id`
- `subject_ref`
- `action` (`widen-publication`, `narrow-publication`, `clear-residue`, `rotate-publication-endpoint`, `rotate-share-artifact`, `acknowledge-residual-risk`)
- `before_summary`
- `after_summary`
- `residual_delta_summary`
- `actor_ref`
- `created_at`

## Rules

1. **Publication is not dialing.**  
   A policy may allow dialing a named endpoint without publicly announcing anything broader. Those must remain separate answers.

2. **Local discovery still counts as publication.**  
   Broadcasting on a LAN may feel private enough in practice, but it is still disclosure to an audience class and should render that way.

3. **Known hosts and manual endpoints still disclose to those targets.**  
   “Tracker off” does not mean “no one learns anything.” If the daemon dials a named endpoint and presents share- or endpoint-related facts there, the model should say so explicitly.

4. **Share membership and endpoint facts are separate fact classes.**  
   An operator should be able to distinguish `this audience can learn I exist` from `this audience can learn this share exists here` from `this audience can learn where to reach me directly`.

5. **Narrowing can stop future publication without erasing residue.**  
   The product must distinguish `new disclosure stopped` from `old learned state may still decay or require clearing/rotation`.

6. **Widening and narrowing should emit the same class of receipt.**  
   Later audit should be able to prove both the intended posture change and any acknowledged leftover residue.

7. **Every surface should preserve the same disclosure truth.**  
   GUI, web workbench, TUI, CLI, and headless automation should not get to invent different meanings for `LAN only`, `named endpoint only`, `public discovery`, or `residual exposure`.

## CLI contract

Minimal commands:

```text
anonsync disclosure show
anonsync disclosure show --share photos
anonsync disclosure explain --policy travel-quiet
anonsync disclosure preview --share photos --announce-via private-discovery --dial-via known-host,private-discovery
anonsync disclosure preview --policy travel-quiet --disable-lan --clear-cache
anonsync disclosure residue list
anonsync disclosure residue show rdr_01J...
anonsync disclosure receipt show dsr_01J...
```

These commands should answer:

- which audiences can currently learn anything about this subject
- which fact classes are exposed to each audience
- which publication comes from durable policy versus temporary widening
- whether narrowing still leaves cached or provider-retained residue
- which receipt proves a publication or residue-clearing change later

## Workbench contract

The workbench should expose a `Disclosure` page distinct from `Policies`, `Transfers`, and `Access`.
Its job is not to become another routing screen.
Its job is to answer:

- what audiences currently learn about this daemon, share, or constellation
- whether the exposed fact is identity, share-membership, endpoint, or relay-reachability information
- what residue remains after a recent narrowing change
- what exact step would widen or narrow exposure next

The page should support:

- filtering by subject, audience class, fact class, and residual-risk state
- opening one disclosure report drawer that shows audience/fact matrix, mechanisms, and decay/clearance truth
- comparing baseline and effective disclosure when temporary exceptions are active
- preparing a reviewed widening/narrowing change without leaving the workbench
- jumping directly to receipts for publication changes or residue acknowledgement/clearance

## Report-language integration

The shared report language should support at least these families here:

- `disclosure-scope` — what audiences currently learn which facts and by what mechanisms
- `disclosure-residue` — what older or cached exposure still remains after narrowing
- `disclosure-widening-risk` — why a proposed policy or exception would reveal materially more than the baseline posture

These reports should behave like any other report-backed finding: severity, freshness, scope, and safest next action remain explicit.

## Design tests

The model is not explicit enough if any of the following remains true:

- disabling tracker or LAN search still leaves the operator guessing what discovery facts were previously published
- manual known-host or named-endpoint dialing still looks like “no publication” because the UI only renders ambient discovery toggles
- the operator cannot tell whether a change widens share-membership disclosure, endpoint disclosure, or both
- a residue-clearing action such as cache clear or endpoint/artifact rotation still lives only in support lore
- one client calls something `LAN only` while another quietly preserves a wider disclosure meaning

## Outcome

A mature AnonSync surface should let the operator move from `what am I disclosing right now?` to `which audience learns which facts?` to `preview a narrower or wider disclosure boundary` to `acknowledge or clear remaining residue with receipts` without leaving the public model or re-learning tracker/relay/LAN folklore.
That is what this document locks in.
