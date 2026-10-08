# Rev0865 online research and design implications

Research review date: 2026-07-20. Sources are used to inform architecture and
scope; none is treated as automatic proof that AnonSync implements the cited
system or guarantees.

## 1. Dotted Version Vectors

Source: Nuno Preguiça, Carlos Baquero, Paulo Sérgio Almeida, Victor Fonte,
“Dotted Version Vectors: Logical Clocks for Optimistic Replication” (2012).

https://gsd.di.uminho.pt/members/vff/dotted-version-vectors-2012.pdf

Design implication: a causal summary and a specific update event are different
objects. A dot gives one event a unique position while a context summarizes its
causal past. This directly supports rev0865's separation of
`SyncReplicaDot` from `causal_context` and explains why equal vectors cannot
safely identify two different values.

Caution: AnonSync's model uses strict single-writer `(device, epoch)` actors and
retains complete operations. It is not a full implementation of the paper's
client/server algorithms or compact production metadata.

## 2. CRDT survey and strong eventual consistency vocabulary

Source: Paulo Sérgio Almeida, “Approaches to Conflict-free Replicated Data
Types” (arXiv:2310.18220).

https://arxiv.org/pdf/2310.18220

Design implication: convergence depends on replicas receiving an equivalent
set of updates and applying a deterministic/compatible state derivation, not on
wall-clock ordering or local orientation. Rev0865 therefore compares both the
immutable operation set and visible-state projection after anti-entropy.

Caution: a deterministic winner is not sufficient when update validity or
identity depends on arrival order. This is the key remaining gap under
same-dot forks and unresolved predecessors.

## 3. Merkle-CRDTs and content-addressed anti-entropy

Source: Hector Sanjuán, Samuli Pöyhtäri, Pedro Teixeira, Ioannis Psaras,
“Merkle-CRDTs: Merkle-DAGs meet CRDTs” (2020).

https://research.protocol.ai/publications/merkle-crdts-merkle-dags-meet-crdts/psaras2020.pdf

Design implication: immutable content-addressed nodes can combine update
identity, dependency discovery, and anti-entropy. A future AnonSync envelope can
name predecessor heads/hashes and exchange graph roots rather than repeatedly
copying complete operation sets.

Caution: Merkle structure alone does not authenticate actor authority, solve
membership/revocation, guarantee privacy, or define how malicious forks are
classified.

## 4. Byzantine-fault-tolerant CRDT direction

Source: Martin Kleppmann, “Making CRDTs Byzantine Fault Tolerant” (PaPoC 2022).

https://martin.kleppmann.com/papers/bft-crdt-papoc22.pdf

Design implication: hash-linked immutable operation graphs can make omitted or
malformed dependencies detectable and can separate dissemination from
deterministic state derivation. For AnonSync, retaining fork evidence and
reconstructing validity from the shared evidence set is more robust than
“accept whichever same-dot value arrived first.”

Caution: rev0865 does not implement this paper's Byzantine model and makes no
BFT claim. Authentication, access control, and deterministic fork/quarantine
rules remain missing.

## 5. The Blocklace

Source: Idit Keidar, Oded Naor, “The Blocklace: A Universal Byzantine
Repelling Data Structure” (arXiv:2402.08068).

https://arxiv.org/abs/2402.08068

Design implication: recent research continues to explore immutable causal DAGs
that expose equivocation and support deterministic filtering. The useful
AnonSync lesson is architectural separation: store evidence first; derive the
active projection through a deterministic validator second.

Caution: this source informs speculation only. It is not a drop-in protocol for
file synchronization, key lifecycle, payload retention, or anonymity.

## 6. Deterministic simulation testing

Source: Jepsen analysis of TigerBeetle 0.16.11, including discussion of its
purpose-built deterministic simulation testing and fault injection practice.

https://jepsen.io/analyses/tigerbeetle-0.16.11

Design implication: deterministic schedules make failures reproducible and let
an invariant-rich state machine explore crash, reorder, loss, duplicate, and
partition combinations cheaply. Rev0865 adopts this testing posture for the
pure replica model rather than claiming a few hand-written happy paths prove a
network protocol.

Caution: the AnonSync simulator is far smaller and in-memory. It does not model
kernel, filesystem, SQLite, process, clock, or real transport faults with the
fidelity of a production distributed-system simulator.

## 7. Syncthing operational comparison

Source: Syncthing configuration documentation.

https://docs.syncthing.net/users/config.html

Design implication: a usable peer synchronizer needs explicit device identity,
folder membership, connection/listen/discovery behavior, and operational
configuration around the convergence core. AnonSync currently lacks a
demonstrated production equivalent for authenticated remote peers, discovery,
relay/NAT behavior, and device lifecycle.

Caution: this is a product-surface comparison, not an assertion that AnonSync
should copy Syncthing's protocol or security architecture.

## 8. Very recent deterministic reconstruction research

Source: “A Composable CRDT Layer for Byzantine-Resilient Deterministic
Reconstruction” (arXiv:2606.18966, June 2026).

https://arxiv.org/abs/2606.18966

Design implication: the paper's title and framing are aligned with the gap found
in this audit—deterministic reconstruction from shared evidence under Byzantine
conditions. It is worth studying while designing the validator/projection
layer and differential tests.

Caution: this is very recent work and is treated as a promising research lead,
not settled engineering guidance or a guarantee. Rev0865 does not depend on its
results.

## Synthesis for AnonSync

The common direction is:

1. identify each update independently from its causal summary;
2. retain immutable, preferably content-addressed and authenticated evidence;
3. exchange missing dependencies through bounded graph-oriented anti-entropy;
4. derive valid active state deterministically from the same evidence set;
5. preserve concurrent user bytes explicitly; and
6. test the state machine under deterministic fault schedules before binding it
   to storage and transport.

The rev0865 dotted model supplies items 1, 5, and a small part of 6. The next
vertical slice must supply durable authenticated evidence, deterministic
activation/quarantine, and real bounded dissemination. Privacy and anonymity
remain separate later design obligations requiring their own threat model.
