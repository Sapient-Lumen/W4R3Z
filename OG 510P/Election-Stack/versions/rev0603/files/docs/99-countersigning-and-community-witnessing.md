# 99 — Countersigning & Community Witnessing

**Track:** A (Deployable core)


## Why countersign
A single election authority signature is easy to dispute politically.
Countersigning by multiple independent entities (media, parties, NGOs, universities, courts)
creates a wider trust base and makes history rewrite harder.

## Countersign objects
- ObserverKitManifest
- ResultsReleasePackage
- EPB + checkpoint feed digests

## Workflow (conceptual)
1) Authority publishes artifact + signature.
2) Independent party verifies, then countersigns the signature or the artifact hash.
3) Countersignatures are published and anchored (timestamps / logs).

## Governance
- Publish who is eligible to countersign and the rules for recognizing countersignatures.
- Make countersigning optional but easy; treat it as “community witnessing.”