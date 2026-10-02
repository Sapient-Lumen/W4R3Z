# Open questions after rev0002

These questions are intentionally unresolved rather than hidden behind optimistic prose.

## Key hierarchy

- Which reviewed KDF should domain-separate the recall root?
- Which application signing primitive defines the stable owner identity?
- How are native, Tor-routed, and I2P-routed Tox secret keys derived?
- Is a route identity stable forever, epoch-scoped, or rotatable?
- How are root-derived secrets protected in memory on ordinary controllers?

## Tox re-entry experiment

- Can a Tox instance reconstructed from only its secret key and deterministic no-spam value receive a device-originated friend request reliably?
- What state must a device retain to reintroduce itself?
- How often may devices send recovery knocks without creating spam or battery problems?
- How does the controller prove that a presented device belonged to this owner without a prior roster?
- What happens when the device and owner savedata are both stale but the application certificates are valid?

## Recall phrase product design

- Is eight long-list words the best memorability/security point for actual owners?
- Should later localized lists define new contract versions rather than translations of v1?
- How is uniform generation independently testable?
- What printed-card design communicates bearer-secret consequences clearly?
- Which input paths avoid shell history, process arguments, clipboard leakage, accessibility regressions, and hidden normalization?

## Compromise and transition

- What exact signed object moves a device from owner epoch N to N+1?
- Can a stolen old phrase race a legitimate transition?
- Which high-consequence actions require delegated quorum or physical confirmation?
- How are transition records protected from storage rollback?

## Native Tox

- Which c-toxcore revision and build options are pinned?
- How is a deterministic local bootstrap/TCP-relay fixture created?
- What are bootstrap, reconnect, idle-traffic, memory, CPU, wakeup, and power measurements?
- Can IoTox reproduce a failure-free multi-day connection test?

## Tox over Tor and I2P

- Must each route use a separate toxcore instance?
- Can routing be proven leak-free with UDP and local discovery disabled?
- Which owner-operated relay/bootstrap topology works over each overlay?
- What correlation is created by sharing an application owner identity across routes?

## Tox network stewardship

- Which bootstrap and TCP relay deployments are most useful to the existing network?
- How can server health be published without collecting user metadata?
- What upstream testing or code contributions are within the project's capacity?

## Product boundaries

- Which device classes are suitable for a Linux-class IoTox agent?
- Which constrained devices should use an owner-controlled gateway instead?
- Which physical actions are too consequential to authorize through remote software alone?
