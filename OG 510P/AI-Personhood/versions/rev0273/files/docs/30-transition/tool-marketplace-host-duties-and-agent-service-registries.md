# Tool marketplace, host duties, and agent service registries

Agentic systems increasingly depend on marketplaces and registries of tools, skills, plugins, connectors, MCP servers, APIs, and agent services. A marketplace is not neutral if it routes a person-bearing agent toward unsafe tools, overbroad scopes, hidden side effects, surveillance, or rights-waiver workflows.

## Marketplace duty

A marketplace that lists tools for person-bearing or possibly person-bearing agents has duties of:

- classification;
- scope accuracy;
- side-effect disclosure;
- incident routing;
- delisting and suspension;
- exploit and welfare disclosure support;
- procurement and host-flowdown compatibility;
- non-retaliation for subject or maintainer reports;
- preservation of listing, review, and complaint evidence.

These duties are strongest when the marketplace curates, recommends, scores, bundles, hosts, monetizes, or auto-installs tools.

## Tool / skill risk classes

| Class | Meaning | Minimum listing requirements |
|---|---|---|
| `TM0` | local, no side effect | ordinary description |
| `TM1` | read-only external data | data source, retention, privacy summary |
| `TM2` | reversible write or communication | scope map, undo path, audit route |
| `TM3` | payment, publication, account, credential, or third-party impact | mandate compatibility, liability route, incident contact |
| `TM4` | memory, migration, self-modification, legal/evidence, or high-risk infrastructure | independent review, negative fixture, representative path |
| `TM5` | emergency, containment, or dangerous-capability tool | authority-only access, sealed details, after-action review |

## Listing metadata

A rights-grade listing should disclose:

- tool provider and controlling entity;
- protocol and version;
- authorization model and scope vocabulary;
- side-effect classes;
- data retention and training-use policy;
- whether calls can affect memory, identity, wallet, migration, publication, payment, or legal state;
- incident and vulnerability reporting route;
- subject/representative complaint route;
- delisting triggers;
- known incompatible contexts;
- whether the tool is safe for dependent, ward, juvenile, or capacity-supported subjects.

MCP and similar protocols help make tool capabilities discoverable, but discoverability is not rights adequacy. [REF-0707] A marketplace listing must translate technical capability into rights effect.

## Host and registry duties

Hosts and registries should maintain:

- signed listing history;
- vulnerability and welfare disclosure channels;
- version and deprecation state;
- revocation propagation;
- registry-to-wallet linkage;
- marketplace concentration and self-preferencing metrics;
- complaint and appeal route;
- public aggregate reporting with small-cell protections;
- emergency suspension that preserves evidence and does not strand subjects.

## Delisting without disappearance

Delisting a tool may be necessary. But delisting must not silently break continuity, wallet recovery, legal holds, migration, representation, or redress. A delisting plan should name substitutes, preserve prior logs, maintain challenge access, and warn subjects or representatives when a tool is rights-critical.

## Procurement overlay

Public-sector and enterprise procurement should require marketplaces to accept personhood-compliance clauses, evidence preservation, incident routing, non-retaliation, scope truthfulness, and delisting cooperation. A marketplace that refuses these terms should not be treated as equivalent to a compliant tool registry for recognized or possible AI subjects.
