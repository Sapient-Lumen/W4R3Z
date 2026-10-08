# Bundle Gossip Deployment Checklist

## Required
- [ ] `BundleGossipMessage` schema implemented and validated.
- [ ] Gossip messages are signed; receivers reject unsigned/invalid messages.
- [ ] Each node enforces payload and storage limits (hash caps, TTLs).
- [ ] At least **2 independent monitor operators** participate in gossip.
- [ ] At least **3 independent bundle distribution channels** are configured.
- [ ] All bundles include `EvidenceBundleManifest`, signature, `checkpoint_id`, and inclusion proof.

## Split-view drills
- [ ] Simulate a mirror serving different bundle manifests to two client groups.
- [ ] Confirm both groups produce a verifiable divergence artifact.
- [ ] Confirm divergence artifact is anchored to a checkpoint and becomes widely visible via gossip.

## Poisoning / spam drills
- [ ] Flood with invalid gossip payloads; confirm false-positive divergence stays near zero.
- [ ] Flood with valid-but-irrelevant manifests; confirm caps/TTL prevent memory exhaustion.

## Censorship / partition drills
- [ ] Block official portal; confirm clients can still obtain checkpoint hashes via alternate channels.
- [ ] Block gossip to a region; confirm missing evidence is detectable (staleness alarms) and the UI fails loud.

