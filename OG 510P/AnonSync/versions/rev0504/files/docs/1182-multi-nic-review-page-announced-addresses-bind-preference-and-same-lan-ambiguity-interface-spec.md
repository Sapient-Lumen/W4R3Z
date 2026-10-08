# Multi-NIC review page — announced addresses, bind preference, and same-LAN ambiguity interface spec

## Purpose

This page exists because multi-NIC trouble is not one generic `network issue`.
AnonSync should require a **Multi-NIC review** whenever peer discovery or direct path establishment can plausibly differ across interfaces, bridges, VPNs, Wi-Fi/Ethernet pairs, or service-visible adapters.

## Core review questions

The page must answer, in order:

1. which interfaces are live candidates
2. which addresses were likely announced or used for discovery
3. whether the requested interface preference narrows the actual candidate set
4. whether same-LAN assumptions are unsafe because peers may see different subnets or adapters
5. what remediation changes route truth versus merely changing luck

## Object model

### `multi_nic_review`

- `multi_nic_review_id`
- `scope_ref`
- `candidate_interfaces[]`
- `candidate_addresses[]`
- `requested_interface_handle`
- `effective_interface_handle` nullable
- `same_lan_assumption_grade` (`strong`, `weak`, `broken`, `unknown`)
- `multicast_viability_by_interface[]`
- `direct_path_viability_by_interface[]`
- `preferred_remediation_ladder[]`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`

## Required sections

### 1) Candidate interfaces and addresses

List every relevant interface with:

- friendly name
- address family / subnet summary
- live state
- whether multicast/LAN discovery is plausible there
- whether the interface is only bridge/VPN/virtual/auxiliary if known

### 2) Requested versus effective preference

Show:

- requested interface
- whether it is present
- whether evidence suggests another interface is actually carrying the traffic
- whether the operator is looking at current evidence only

### 3) Same-LAN ambiguity

This section must explicitly say when `same LAN` is:

- strong
- only partly true
- wrong enough that tracker/predefined-host behavior is doing the real work

### 4) Remediation ladder

Allowed remediations may include:

- switch to another NIC
- enforce hard cutoff
- fix multicast / routing / firewall on the intended NIC
- use predefined hosts with stable addresses
- revisit runtime class / service audience

Each step must say whether it changes evidence, route policy, or host topology.

## Interaction rules

1. Do not collapse Wi-Fi, Ethernet, VPN, bridge, and virtual adapters into one `network`.
2. Do not let `connected now` stand in for `interface ambiguity resolved`.
3. The review must show when switching NICs is a diagnostic tactic rather than a durable policy answer.
4. Suggested remediations must be ordered from narrowest scope to widest scope.

## Acceptance bar

The page is good enough when a cautious operator can answer:

- which interfaces are actually in contention
- whether LAN discovery assumptions are safe
- whether current success might be happening on the wrong NIC
- which next change narrows the ambiguity instead of merely retrying
